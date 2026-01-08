from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction as db_transaction
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ValidationError
from ivm.models import Item, Partner, Transaction
from ivm.forms import TransactionForm, TransactionItemFormSet
import json

def _handle_partner_creation(form):
    """Helper to create a partner if one isn't selected."""
    if form.cleaned_data.get('partner'):
        return form.cleaned_data.get('partner')
        
    return Partner.objects.create(
        name=form.cleaned_data.get('new_partner_name'),
        tax_code=form.cleaned_data.get('new_partner_tax_code'),
        phone=form.cleaned_data.get('new_partner_phone'),
        email=form.cleaned_data.get('new_partner_email'),
        address=form.cleaned_data.get('new_partner_address'),
        contact_person=form.cleaned_data.get('new_partner_contact_person')
    )

@login_required(login_url='/users/login/')
@permission_required('ivm.add_transaction', raise_exception=True)
def add_transaction(request):
    stock_map = {item.item_id: str(item.total_stock) for item in Item.objects.all()}

    if request.method != 'POST':
        return render(request, 'ivm/form_add_transaction.html', {
            'form': TransactionForm(),
            'formset': TransactionItemFormSet(prefix='items'),
            'stock_json': json.dumps(stock_map),
        })

    form = TransactionForm(request.POST)
    formset = TransactionItemFormSet(request.POST, prefix='items')

    if form.is_valid() and formset.is_valid():
        try:
            with db_transaction.atomic():
                transaction_obj = form.save(commit=False)
                transaction_obj.partner = _handle_partner_creation(form)
                transaction_obj.created_by = request.user
                transaction_obj.save()

                formset.instance = transaction_obj
                transaction_items = formset.save()

                for t_item in transaction_items:
                    t_item.item.update_active_status()

            return redirect('ivm:transaction_detail', transaction_id=transaction_obj.transaction_id)

        except Exception as e:
            form.add_error(None, f"Error saving transaction: {e}")

    return render(request, 'ivm/form_add_transaction.html', {
        'form': form,
        'formset': formset,
        'stock_json': json.dumps(stock_map),
    })

@login_required(login_url='/users/login/')
@permission_required('ivm.change_transaction', raise_exception=True)
def edit_transaction(request, transaction_id):
    # 1. Fetch the transaction or 404
    transaction_obj = get_object_or_404(Transaction, transaction_id=transaction_id)

    # 2. Business Logic Guard: Block editing if transaction is already 'Completed'
    if transaction_obj.transaction_status == 'Completed':
        messages.error(request, f"Transaction {transaction_obj.code} is completed and locked.")
        return redirect('ivm:transaction_detail', transaction_id=transaction_id)

    # 3. Preparation for JavaScript
    stock_map = {item.item_id: str(item.total_stock) for item in Item.objects.all()}
    stock_json = json.dumps(stock_map)

    # 4. Handle GET request early
    if request.method != 'POST':
        return render(request, 'ivm/form_edit_transaction.html', {
            'transaction': transaction_obj,
            'form': TransactionForm(instance=transaction_obj),
            'formset': TransactionItemFormSet(instance=transaction_obj, prefix='items'),
            'stock_json': stock_json,
        })

    # 5. Initialize POST data
    form = TransactionForm(request.POST, instance=transaction_obj)
    formset = TransactionItemFormSet(request.POST, instance=transaction_obj, prefix='items')

    # 6. Process Validation and Saving
    if form.is_valid() and formset.is_valid():
        try:
            with db_transaction.atomic():
                transaction_obj = form.save(commit=False)
                
                # Use the same helper function from your create view
                transaction_obj.partner = _handle_partner_creation(form)
                
                transaction_obj.save()

                formset.instance = transaction_obj
                transaction_items = formset.save()

                for t_item in transaction_items:
                    t_item.item.update_active_status()

            messages.success(request, f"Transaction {transaction_obj.code} updated.")
            return redirect('ivm:transaction_detail', transaction_id=transaction_id)

        except Exception as e:
            form.add_error(None, f"Error saving transaction: {e}")

    # 7. Fallback for invalid forms or exceptions
    return render(request, 'ivm/form_edit_transaction.html', {
        'transaction': transaction_obj,
        'form': form,
        'formset': formset,
        'stock_json': stock_json,
    })

@login_required(login_url='/users/login/')
@permission_required('ivm.delete_transaction', raise_exception=True)
@require_POST
def delete_transaction(request, transaction_id):
    # Fetch the transaction
    tx = get_object_or_404(Transaction, pk=transaction_id)

    # Safety Check: Do not allow deleting processed transactions
    if tx.transaction_status == 'Completed':
        messages.error(request,f"Transaction {tx.code} is completed and cannot be deleted to maintain inventory integrity.")
        return redirect('ivm:transaction_detail', transaction_id=tx.transaction_id)

    # Perform deletion
    transaction_code = tx.code
    tx.delete()

    messages.success(request, f"Transaction {transaction_code} has been successfully deleted.")
    return redirect('ivm:transactions')

@login_required(login_url='/users/login/')
@permission_required('ivm.authorize_transaction', raise_exception=True)
@require_POST
def authorize_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, pk=transaction_id)

    # Safety check: Only allow authorizing if not already completed/rejected
    if tx.transaction_status not in ['Rejected', 'Pending']:
        messages.error(request, f"Giao dịch {tx.code} {tx.get_transaction_status_display()}.")
        return redirect('ivm:transaction_detail', transaction_id=tx.transaction_id)

    try:
        tx.transaction_status = 'Authorized'
        tx.authorized_by = request.user

        # This call triggers Transaction.save(), which detects status change to 'Completed'
        # and runs the inventory FIFO logic automatically.
        tx.save()

        messages.success(request, f"Transaction {tx.code} authorized.")
    except ValidationError as e:
        messages.error(request, f"Authorization failed: {e.message}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")

    return redirect('ivm:transaction_detail', transaction_id=tx.transaction_id)


@login_required(login_url='/users/login/')
@permission_required('ivm.authorize_transaction', raise_exception=True)
@require_POST
def reject_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, pk=transaction_id)

    if tx.transaction_status == 'Completed':
        messages.error(request, "Cannot reject a transaction that has already been completed.")
    else:
        tx.transaction_status = 'Rejected'
        tx.save()
        messages.warning(request, f"Transaction {tx.code} has been rejected.")

    return redirect('ivm:transaction_detail', transaction_id=tx.transaction_id)

@login_required(login_url='/users/login/')
@permission_required('ivm.complete_transaction', raise_exception=True)
@require_POST
def complete_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, pk=transaction_id)

    # Safety check: Only allow authorizing if not already completed/rejected
    if tx.transaction_status == 'Completed':
        messages.error(request, f"Giao dịch {tx.code} {tx.get_transaction_status_display()}.")
        return redirect('ivm:transaction_detail', transaction_id=tx.transaction_id)

    try:
        # We transition directly to 'Completed' to trigger the built-in process_transaction()
        tx.transaction_status = 'Completed'
        tx.performed_by = request.user

        # This call triggers Transaction.save(), which detects status change to 'Completed'
        # and runs the inventory FIFO logic automatically.
        tx.save()

        messages.success(request, f"Transaction {tx.code} completed, inventory updated.")
    except ValidationError as e:
        messages.error(request, f"Completion failed: {e.message}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")

    return redirect('ivm:transaction_detail', transaction_id=tx.transaction_id)

__all__ = [
    'add_transaction',
    'edit_transaction',
    'delete_transaction',
    'authorize_transaction',
    'reject_transaction',
    'complete_transaction'
]