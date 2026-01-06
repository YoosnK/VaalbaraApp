from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from ivm.models import Item, Inventory
from ivm.forms import ItemForm


@login_required(login_url='/users/login/')
@permission_required('ivm.add_item', raise_exception=True)
def add_item(request, inventory_slug=None):
    inventory = None
    if inventory_slug:
        inventory = get_object_or_404(Inventory, slug=inventory_slug)

    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('ivm:inv_page', inventory_slug=item.inventory.slug)
    else:
        # If we came from a specific inventory, pre-select it in the dropdown
        initial_data = {}
        if inventory:
            initial_data['inventory'] = inventory
        form = ItemForm(initial=initial_data)

    return render(request, 'ivm/form_add_item.html', {'form': form, 'inventory': inventory})

@login_required(login_url='/users/login/')
@permission_required('ivm.change_item', raise_exception=True)
def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        # passing instance=item tells Django to UPDATE the record, not create a new one
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('ivm:inv_page', inventory_slug=item.inventory.slug)
    else:
        form = ItemForm(instance=item)

    return render(request, 'ivm/form_edit_item.html', {'form': form, 'item': item})

@login_required(login_url='/users/login/')
@permission_required('ivm.delete_item', raise_exception=True)
@require_POST
def delete_item(item_id):
    item = get_object_or_404(Item, pk=item_id)
    inventory_slug = item.inventory.slug

    if item.total_stock <= 0:
        item.is_active = False  # The "Soft Delete"
        item.save()

    return redirect('ivm:inv_page', inventory_slug=inventory_slug)

__all__ =[
    'add_item',
    'edit_item',
    'delete_item'
]