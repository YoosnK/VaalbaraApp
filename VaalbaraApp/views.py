from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ivm.models import Inventory, Transaction, Partner
from ivm import my_functions

@login_required(login_url='/users/login/')
def dashboard(request):
    inventories_summary = my_functions.get_all_inventories_summary()
    pending_transactions = Transaction.objects.exclude(transaction_status='Completed')
    return render(request, "dashboard.html", {
            'inventories_summary': inventories_summary,
            'pending_transactions': pending_transactions,
            'today':  timezone.now(),
        })

@login_required(login_url='/users/login/')
def about(request):
    partners = Partner.objects.all()
    return render(request, "about.html", {'partners': partners})