from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render
from ivm.models import Inventory, Transaction, Partner


@login_required(login_url='/users/login/')
def list_inventories(request):
    invs = Inventory.objects.all()
    return render(request, 'ivm/list_inventories.html', {'inventories': invs})

@login_required(login_url='/users/login/')
@permission_required('ivm.view_transaction', raise_exception=True)
def list_transactions(request):
    txs = Transaction.objects.all().order_by('-creation_date')
    return render(request, 'ivm/list_transactions.html', {'transactions': txs})

@login_required(login_url='users:login')
@permission_required('ivm.view_partner', raise_exception=True)
def list_partners(request):
    partners_list = Partner.objects.all().order_by('name')
    return render(request, 'ivm/list_partners.html', {'partners': partners_list})

__all__ =[
    'list_inventories',
    'list_transactions',
    'list_partners',
]
