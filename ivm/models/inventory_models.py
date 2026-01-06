from django.db import models
from typing import TYPE_CHECKING


class Inventory(models.Model):
    class Meta:
        verbose_name_plural = "Inventories"

    # Fields
    inventory_name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    if TYPE_CHECKING:
        from .item_models import Item
        from .transaction_models import Transaction
        items: models.Manager['Item']
        transactions: models.Manager['Transaction']

    @property
    def num_unique_items(self):
        return self.items.count()
    
    @property
    def value(self):
        return sum(item.value for item in self.items.all())

    @property
    def num_transactions(self):
        return self.transactions.count()

    @property
    def total_cost(self):
        total = 0
        for transaction in self.transactions.filter(transaction_status='Completed'):
            total += transaction.extra_cost
            if transaction.transaction_type == 'Import':
                total += transaction.value
        return total

    @property
    def total_revenue(self):
        return sum(transaction.value for transaction in self.transactions.filter(transaction_status='Completed', transaction_type='Export'))

    @property
    def total_profit(self):
        profit = self.total_revenue - self.total_cost
        return profit

    @staticmethod
    def convert_number_to_vietnamese(number):
        if number == 0:
            return "Không"

        vietnamese_digits = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
        # Vietnamese scale: thousand, million, billion, then repeats (thousand billion, million billion, etc.)
        units_scale = ["", "nghìn", "triệu", "tỷ"]

        def read_three_digits(num, is_highest_group=False):
            hundreds = num // 100
            tens = (num % 100) // 10
            ones = num % 10
            result = ""

            # Handle hundreds
            if not is_highest_group or hundreds > 0:
                result += vietnamese_digits[hundreds] + " trăm "

            # Handle tens
            if tens > 1:
                result += vietnamese_digits[tens] + " mươi "
            elif tens == 1:
                result += "mười "
            elif tens == 0 and ones > 0 and (hundreds > 0 or not is_highest_group):
                result += "linh "

            # Handle ones
            if ones == 1 and tens > 1:
                result += "mốt"
            elif ones == 5 and tens > 0:
                result += "lăm"
            elif ones > 0:
                result += vietnamese_digits[ones]

            return result.strip()

        # Split number into groups of 3 digits
        groups = []
        temp_num = number
        while temp_num > 0:
            groups.append(temp_num % 1000)
            temp_num //= 1000

        final_segments = []
        num_groups = len(groups)

        for i in range(num_groups - 1, -1, -1):
            current_group = groups[i]

            if current_group == 0:
                # Special case: still need to say "tỷ" for multiples of 10^12
                if i % 3 == 0 and i > 0:
                    final_segments.append(units_scale[3])
                continue

            # Read the 3-digit group
            is_highest = (i == num_groups - 1)
            group_text = read_three_digits(current_group, is_highest)
            final_segments.append(group_text)

            # Add unit (nghìn, triệu, tỷ)
            unit_index = i % 3
            if i > 0:
                if unit_index == 0:  # This handles the "tỷ" level
                    final_segments.append(units_scale[3])
                else:
                    final_segments.append(units_scale[unit_index])

        # Clean up and format
        raw_res = " ".join(final_segments)
        # Fix redundant "tỷ tỷ" if any and normalize spaces
        formatted_res = " ".join(raw_res.replace("tỷ tỷ", "tỷ").split())
        return formatted_res.capitalize()

    def __str__(self):
        return self.inventory_name