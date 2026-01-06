from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Inventory)
admin.site.register(Item)
admin.site.register(Transaction)
admin.site.register(TransactionItem)
admin.site.register(ItemBatch)
admin.site.register(Partner)