from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404
from ivm.models import Transaction

@login_required(login_url='/users/login/')
@permission_required('ivm.view_transaction', raise_exception=True)
def file_pdf_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, transaction_id=transaction_id)
    return render(request, 'ivm/file_pdf_transaction.html', {'transaction': tx})

__all__ = [
    'file_pdf_transaction',
]