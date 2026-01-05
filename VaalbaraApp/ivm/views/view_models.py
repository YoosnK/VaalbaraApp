from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404

from ivm.models import Item, Inventory, Partner, Transaction

@login_required(login_url='/users/login/')
@permission_required('ivm.view_inventory',raise_exception=True)
def inventory_details(request, inventory_slug):
    # Matches <slug:inventory_slug>
    inventory = get_object_or_404(Inventory, slug=inventory_slug)
    active_items = inventory.items.filter(is_active=True)
    return render(request, 'ivm/details_inventory.html', {
        'inventory': inventory,
        'items': active_items
    })

@login_required(login_url='/users/login/')
@permission_required('ivm.view_inventory',raise_exception=True)
def item_details(request, inventory_slug, item_id):
    item = get_object_or_404(Item, item_id=item_id, inventory__slug=inventory_slug)
    return render(request, 'ivm/details_item.html', {'item': item})

@login_required(login_url='/users/login/')
@permission_required('ivm.view_transaction', raise_exception=True)
def transaction_details(request, transaction_id):
    tx = get_object_or_404(Transaction, transaction_id=transaction_id)
    return render(request, 'ivm/details_transaction.html', {'transaction': tx})


__all__ = [
    'inventory_details',
    'item_details',
    'transaction_details',
]