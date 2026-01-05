from django import forms
from django.forms import inlineformset_factory

from .models import Transaction, TransactionItem, Item, Inventory, Partner


# ========= Items ==========
class ItemForm(forms.ModelForm):
    inventory = forms.ModelChoiceField(
        queryset=Inventory.objects.all(),
        label='Kho lưu trữ',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    item_name = forms.CharField(
        max_length=250,
        label='Tên mặt hàng',
        widget=forms.TextInput(attrs={'class': 'form-textinput', 'placeholder': 'Naivita'})
    )
    brand = forms.CharField(
        max_length=100,
        required=False,
        label='Nhãn hiệu',
        widget=forms.TextInput(attrs={'class': 'form-textinput', 'placeholder': 'dP Stemkos'})
    )
    packaging = forms.CharField(
        max_length=100,
        required=False,
        label='Đóng gói',
        widget=forms.TextInput(attrs={'class': 'form-textinput', 'placeholder': '10ml'})
    )
    unit = forms.ChoiceField(
        choices=Item.UNIT_CHOICES,
        label='Đơn vị tính',
        widget=forms.Select(attrs={'class': 'form-textinput'})
    )
    category = forms.CharField(
        max_length=50,
        label='Phân loại',
        widget=forms.TextInput(attrs={'class': 'form-textinput', 'placeholder': 'Mỹ phẩm'})
    )
    description = forms.CharField(
        required=False,
        label='Mô tả',
        widget=forms.Textarea(attrs={'class': 'form-textinput', 'rows': 2})
    )

    class Meta:
        model = Item
        fields = ['inventory', 'item_name', 'brand', 'packaging', 'unit', 'category', 'description']


# ========= Transactions ==========
class TransactionForm(forms.ModelForm):
    # Existing fields
    inventory = forms.ModelChoiceField(
        queryset=Inventory.objects.all(),
        label='Kho lưu trữ',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    transaction_type = forms.ChoiceField(
        choices=Transaction.TRANSACTION_TYPES,
        label='Loại giao dịch',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Selection for existing partners
    partner = forms.ModelChoiceField(
        queryset=Partner.objects.all(),
        label='Chọn đối tác có sẵn',
        required=False,
        empty_label="--- Chọn đối tác (Hoặc điền thông tin mới bên dưới) ---",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'partner_select'})
    )

    # --- New Partner Info Fields (Not in Transaction Model) ---
    new_partner_name = forms.CharField(
        label='Tên đối tác mới',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-textinput new-partner-field', 'placeholder': 'Công ty A'})
    )
    new_partner_tax_code = forms.CharField(
        label='Mã số thuế',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-textinput new-partner-field'})
    )
    new_partner_phone = forms.CharField(
        label='Số điện thoại',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-textinput new-partner-field'})
    )
    new_partner_email = forms.EmailField(
        label='Email',
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-textinput new-partner-field'})
    )
    new_partner_address = forms.CharField(
        label='Địa chỉ',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-textinput new-partner-field'})
    )
    new_partner_contact_person = forms.CharField(
        label='Người liên hệ',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-textinput new-partner-field'})
    )

    # Standard Transaction Fields
    partner_bill = forms.CharField(
        max_length=200,
        label='Hóa đơn của đối tác',
        widget=forms.TextInput(attrs={'class': 'form-textinput', 'placeholder': 'Số hóa đơn...'})
    )
    completion_deadline = forms.DateTimeField(
        label='Hạn hoàn thành',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-datetime'}, format='%Y-%m-%dT%H:%M')
    )
    extra_cost = forms.DecimalField(
        max_digits=12, decimal_places=2, initial=0, label='Chi phí phát sinh',
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-number'})
    )
    notes = forms.CharField(required=False, label='Ghi chú', widget=forms.Textarea(attrs={'rows': 3}))

    class Meta:
        model = Transaction
        fields = ['inventory', 'transaction_type', 'partner', 'partner_bill', 'completion_deadline', 'extra_cost', 'notes']

    def clean(self):
        cleaned_data = super().clean()
        partner = cleaned_data.get('partner')

        if not partner:
            required_fields = ['new_partner_name', 'new_partner_tax_code', 'new_partner_phone', 'new_partner_address', 'new_partner_contact_person']
            missing = [f for f in required_fields if not cleaned_data.get(f)]

            if missing:
                raise forms.ValidationError(
                    "Vui lòng chọn đối tác có sẵn hoặc điền đầy đủ thông tin đối tác mới (Tên, MST, SĐT, Địa chỉ, Người liên hệ).")

        return cleaned_data

# ========= Transaction Items FormSet ==========
class BaseTransactionItemFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        transaction_type = self.instance.transaction_type
        if transaction_type == 'Export':
            for form in self.forms:
                if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                    item = form.cleaned_data.get('item')
                    qty = form.cleaned_data.get('quantity')
                    if item and qty > item.total_stock:
                        form.add_error('quantity', f"Only {item.total_stock} units available.")

TransactionItemFormSet = inlineformset_factory(
    Transaction,
    TransactionItem,
    formset=BaseTransactionItemFormSet,
    fields=['item', 'quantity', 'unit_cost', 'discount', 'notes'],
    extra=1,
    widgets={
        'item': forms.Select(attrs={'class': 'item-selector'}),
        'quantity': forms.NumberInput(attrs={
            'type': 'number',
            'step': '0.1',
            'min': '0',
            'class': 'form-number'
        }),
        'unit_cost': forms.NumberInput(attrs={
            'type': 'number',
            'min': '0',
            'class': 'form-number'
        }),
        'discount': forms.NumberInput(attrs={
            'type': 'number',
            'min': '0',
            'class': 'form-number'
        }),
        'notes': forms.TextInput(attrs={
            'class': 'form-textinput',
        })
    },
    labels={
        'item': 'Mặt hàng',
        'quantity': 'Số lượng',
        'unit_cost': 'Đơn giá',
        'discount': 'Chiếu khấu (%)',
        'notes': 'Ghi chú',
    }
)