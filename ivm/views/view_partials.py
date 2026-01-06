from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from ivm.models import Item, Partner


@login_required(login_url='/users/login/')
@permission_required('ivm.view_inventory',raise_exception=True)
def item_detail_panel(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'ivm/partials/item_detail_panel.html', {'item': item})

@login_required(login_url='users:login')
@permission_required('ivm.view_partner', raise_exception=True)
def partner_detail_panel(request, partner_id):
    partner = get_object_or_404(Partner, pk=partner_id)
    return render(request, 'ivm/partials/partner_detail_panel.html', {'partner': partner})

__all__ = [
    'item_detail_panel',
    'partner_detail_panel',
]