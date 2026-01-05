from django.utils import timezone
from ivm.models import Inventory, Transaction


def inventory_monthly_revenue(inventory, month, year):
    transactions = Transaction.objects.filter(
        inventory=inventory,
        transaction_status='Completed',
        transaction_type='Export',
        completion_date__year=year,
        completion_date__month=month
    )
    return sum(t.value for t in transactions)

def inventory_monthly_cost(inventory, month, year):
    transactions = Transaction.objects.filter(
        inventory=inventory,
        transaction_status='Completed',
        completion_date__year=year,
        completion_date__month=month
    )
    total = sum(t.extra_cost for t in transactions)
    total += sum(t.value for t in transactions if t.transaction_type == 'Import')
    return total

def inventory_monthly_profit(inventory, month, year):
    revenue = inventory_monthly_revenue(inventory, month, year)
    cost = inventory_monthly_cost(inventory, month, year)
    return revenue - cost

def all_inventory_monthly_revenue(month, year):
    return sum(inventory_monthly_revenue(inventory, month, year) for inventory in Inventory.objects.all())

def all_inventory_monthly_cost(month, year):
    return sum(inventory_monthly_cost(inventory, month, year) for inventory in Inventory.objects.all())

def all_inventory_monthly_profit(month, year):
    return sum(inventory_monthly_profit(inventory, month, year) for inventory in Inventory.objects.all())

def inventory_yearly_revenue(inventory, year):
    transactions = Transaction.objects.filter(
        inventory=inventory,
        transaction_status='Completed',
        transaction_type='Export',
        completion_date__year=year
    )
    return sum(t.value for t in transactions)

def inventory_yearly_cost(inventory, year):
    transactions = Transaction.objects.filter(
        inventory=inventory,
        transaction_status='Completed',
        completion_date__year=year
    )
    total = sum(t.extra_cost for t in transactions)
    total += sum(t.value for t in transactions if t.transaction_type == 'Import')
    return total

def inventory_yearly_profit(inventory, year):
    revenue = inventory_yearly_revenue(inventory, year)
    cost = inventory_yearly_cost(inventory, year)
    return revenue - cost

def all_inventory_yearly_revenue(year):
    return sum(inventory_yearly_revenue(inventory, year) for inventory in Inventory.objects.all())

def all_inventory_yearly_cost(year):
    return sum(inventory_yearly_cost(inventory, year) for inventory in Inventory.objects.all())

def all_inventory_yearly_profit(year):
    return sum(inventory_yearly_profit(inventory, year) for inventory in Inventory.objects.all())

def get_all_inventories_summary(date=timezone.now()):
    all_inventory = Inventory.objects.all()
    inventories_summary = {
        'inventories': all_inventory,
        'count': all_inventory.count(),
        'value': sum(inventory.value for inventory in all_inventory),
        'total_cost': sum(inventory.total_cost for inventory in all_inventory),
        'total_revenue': sum(inventory.total_revenue for inventory in all_inventory),
        'total_profit': sum(inventory.total_profit for inventory in all_inventory),
        'monthly_revenue': all_inventory_monthly_revenue(date.month, date.year),
        'monthly_cost': all_inventory_monthly_cost(date.month, date.year),
        'monthly_profit': all_inventory_monthly_profit(date.month, date.year),
        'yearly_revenue': all_inventory_yearly_revenue(date.year),
        'yearly_cost': all_inventory_yearly_cost(date.year),
        'yearly_profit': all_inventory_yearly_profit(date.year),
    }
    return inventories_summary