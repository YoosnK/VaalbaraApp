from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from ivm.models import Partner
from ivm.forms import PartnerForm

@login_required(login_url='/users/login/')
@permission_required('ivm.add_partner', raise_exception=True)
def add_partner(request):
    if request.method != 'POST':
        return render(request, 'ivm/form_add_partner.html', {
            'form': PartnerForm()
        })

    form = PartnerForm(request.POST)
    if form.is_valid():
        new_partner = form.save()
        new_partner.save()
        return redirect('ivm:page_partners')

@login_required(login_url='/users/login/')
@permission_required('ivm.delete_partner', raise_exception=True)
@require_POST
def delete_partner(request, partner_id):
    partner = get_object_or_404(Partner, pk=partner_id)
    partner.delete()
    return redirect('ivm:page_partners')

@login_required(login_url='/users/login/')
@permission_required('ivm.change_partner', raise_exception=True)
def edit_partner(request, partner_id):
    partner = get_object_or_404(Partner, pk=partner_id)
    
    if request.method != 'POST':
        return render(request, 'ivm/form_edit_partner.html', {
            'form': PartnerForm(instance=partner),
            'partner': partner
        })

    form = PartnerForm(request.POST, instance=partner)
    if form.is_valid():
        updated_partner = form.save()
        updated_partner.save()
        return redirect('ivm:page_partners')

__all__ = [
    'add_partner',
    'edit_partner',
    'delete_partner',
]