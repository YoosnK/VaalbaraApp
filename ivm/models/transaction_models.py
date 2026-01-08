from __future__ import annotations
from django.db import models, transaction as db_transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from typing import TYPE_CHECKING
from django.conf import settings

from .item_models import ItemBatch

User = get_user_model()

class Transaction(models.Model):
    class Meta:
        permissions = [
            ("authorize_transaction", "Can authorize or reject a transaction"),
            ("complete_transaction", "Can complete transaction"),
        ]
    TRANSACTION_TYPES = [
        ('Import', 'Nhập'),
        ('Export', 'Xuất'),
    ]

    STATUS_CHOICES = [
        ('Rejected', 'Không được duyệt'),
        ('Pending', 'Chờ duyệt'),
        ('Authorized', 'Đã duyệt, chờ hoàn thành'),
        ('Completed', 'Đã hoàn thành'),
    ]

    transaction_id = models.AutoField(primary_key=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    inventory = models.ForeignKey('Inventory', on_delete=models.CASCADE, related_name='transactions')

    partner = models.ForeignKey('Partner', on_delete=models.PROTECT, related_name='transactions')
    partner_bill = models.CharField(max_length=200, default="")
    extra_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)

    creation_date = models.DateTimeField(default=timezone.now)
    completion_deadline = models.DateTimeField(null=True, blank=False)
    authorization_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_transactions')
    authorized_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='authorized_transactions')
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='performed_transactions')

    transaction_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')

    if TYPE_CHECKING:
        transaction_items: models.Manager['TransactionItem']

    @property
    def is_overdue(self):
        if self.completion_deadline and self.transaction_status != 'Completed':
            return timezone.now() > self.completion_deadline
        return False

    @property
    def value(self):
        return sum(t_item.value for t_item in self.transaction_items.all())

    @property
    def report_value(self):
        return sum(t_item.report_value for t_item in self.transaction_items.all())

    @property
    def report_value_vn(self):
        return self.inventory.convert_number_to_vietnamese(int(self.report_value))

    @property
    def code(self):
        if not self.transaction_id:
            return "New"

        prefix = 'NK' if self.transaction_type == 'Import' else 'XK'
        return f"{prefix}{self.transaction_id:05d}"

    @property
    def is_authorized(self):
        return self.transaction_status == 'Authorized'

    @property
    def is_rejected(self):
        return self.transaction_status == 'Rejected'

    @property
    def is_completed(self):
        return self.transaction_status == 'Completed'

    @property
    def date_for_pdf(self):
        return f"{self.completion_date.strftime('Ngày %d tháng %m năm %Y')}"

    def process_transaction(self):
        """Processes inventory impact and updates Item active status."""
        with db_transaction.atomic():
            # Refresh items from DB to ensure we have the latest formset saves
            for t_item in self.transaction_items.all():
                if self.transaction_type == 'Import':
                    self._create_import_batch(t_item)
                elif self.transaction_type == 'Export':
                    # Add a check here for safety
                    if t_item.quantity > t_item.item.total_stock:
                        raise ValidationError(f"Insufficient stock for {t_item.item.item_name}")
                    self._consume_batches_fifo(t_item)

                # Automatically reactivates item if stock is now > 0
                t_item.item.update_active_status()

    def _create_import_batch(self, t_item: TransactionItem):
        if not self.completion_date:
            return
        ItemBatch.objects.create(
            transaction=self,
            item=t_item.item,
            unit_cost=t_item.unit_cost,
            quantity=t_item.quantity,  # Positive
            creation_date=self.completion_date,
        )
        t_item.report_value = t_item.unit_cost * t_item.quantity
        t_item.save()

    @staticmethod
    def _consume_batches_fifo(t_item):
        qty_to_reduce = t_item.quantity

        # Gets available batches, oldest first
        available_batches = ItemBatch.objects.filter(
            item=t_item.item
        ).order_by('creation_date')

        for batch in available_batches:
            if qty_to_reduce <= 0:
                break

            if batch.quantity <= qty_to_reduce:
                t_item.report_value += batch.value
                qty_to_reduce -= batch.quantity
                batch.delete()
            else:
                t_item.report_value += batch.unit_cost * qty_to_reduce
                batch.quantity -= qty_to_reduce
                qty_to_reduce = 0
                batch.save()
        t_item.save()

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        old_status = None

        if not is_new:
            # Fetch the previous status from the database to detect transitions
            old_status = Transaction.objects.get(pk=self.pk).transaction_status

        # 2. Safety Check: Prevent editing Completed transactions
        if old_status == 'Completed' and self.transaction_status == 'Completed':
            # Allow saving only if we aren't changing core inventory data
            # Or simply raise an error to lock it entirely
            pass

        # 3. Handle specific dates based on status
        if self.transaction_status == 'Authorized' and not self.authorization_date:
            self.authorization_date = timezone.now()

        if self.transaction_status == 'Completed' and not self.completion_date:
            self.completion_date = timezone.now()

        # Save the record
        super().save(*args, **kwargs)

        # 4. Inventory Trigger: Only when moving TO Completed
        if old_status != 'Completed' and self.transaction_status == 'Completed':
            self.process_transaction()

    def __str__(self):
        result = f"ID: {self.transaction_id}, "
        if self.completion_date:
            result += f"completed on {self.completion_date.strftime('%d/%m/%Y')} "
        else:
            result += f"status: {self.transaction_status}"
        return result


class TransactionItem(models.Model):
    # Link to Transaction (The "List" container)
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='transaction_items')

    item = models.ForeignKey('Item', on_delete=models.PROTECT)
    # item_name is retrieved via the 'item' foreign key (item.item_name)

    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    notes = models.TextField(blank=True)

    report_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

    @property
    def value(self):
        return self.quantity * self.unit_cost * (1 - self.discount / 100)

    @property
    def report_unit_cost(self):
        return self.report_value / self.quantity
    
    def __str__(self):
        ret = "Import" if self.transaction.transaction_type == 'Import' else "Export"
        ret += f" | Item: {self.item.item_name} | Qty: {self.quantity}"
        return ret