from django.db import models
from typing import TYPE_CHECKING


class Item(models.Model):
    UNIT_CHOICES = [
        ("None", ""),
        ("Piece", "Cái"),
        ("Box", "Hộp"),
        ("Bottle", "Chai"),
        ("Jar", "Lọ"),
        ("Tube", "Tuýp"),
        ("Bag", "Túi"),
        ("Sack", "Bao"),
        ("Blister", "Vỉ"),
        ("Pill", "Viên")
    ]

    item_id = models.AutoField(primary_key=True)

    inventory = models.ForeignKey('Inventory', on_delete=models.CASCADE, related_name='items')

    item_name = models.CharField(max_length=250)
    brand = models.CharField(max_length=100, blank=True)
    packaging = models.CharField(max_length=100, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    category = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    if TYPE_CHECKING:
        batches: models.Manager['ItemBatch']

    @property
    def total_stock(self):
        return sum(batch.quantity for batch in self.batches.all())

    @property
    def value(self):
        return sum(batch.value for batch in self.batches.all())

    @property
    def full_name(self):
        return f" {self.get_unit_display()} {self.item_name} {self.packaging}"

    def update_active_status(self):
        """Checks total stock and reactivates item if > 0."""
        if self.total_stock > 0 and not self.is_active:
            self.is_active = True
            self.save(update_fields=['is_active'])

    def __str__(self):
        return self.full_name


class ItemBatch(models.Model):
    batch_id = models.AutoField(primary_key=True)
    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='batches')
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='batches')

    creation_date = models.DateTimeField()
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    notes = models.TextField(blank=True)

    @property
    def value(self):
        return self.quantity * self.unit_cost

    def __str__(self):
        result = f"Số lượng: {self.quantity} | Ngày nhập: {self.creation_date.strftime('%d/%m/%Y')}"
        return result