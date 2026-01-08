from django.urls import path
from . import views

app_name = 'ivm'

urlpatterns = [
    # Displays all inventories: /ivm/
    path('', views.list_inventories, name='inventory_manager'),

    path('partners/', views.list_partners, name='page_partners'),
    path('partners/<int:partner_id>/', views.partner_detail_panel, name='partner_detail'),
    path('partners/add', views.add_partner, name='add_partner'),
    path('partners/edit/<int:partner_id>/', views.edit_partner, name='edit_partner'),
    path('partners/delete/<int:partner_id>', views.delete_partner, name='delete_partner'),

    path('transactions/', views.list_transactions, name='transactions'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('transactions/authorize/<int:transaction_id>/', views.authorize_transaction, name='authorize_transaction'),
    path('transactions/reject/<int:transaction_id>/', views.reject_transaction, name='reject_transaction'),
    path('transactions/complete/<int:transaction_id>/', views.complete_transaction, name='complete_transaction'),
    path('transactions/pdf/<int:transaction_id>/', views.file_pdf_transaction, name='transaction_pdf'),
    path('transactions/<int:transaction_id>/', views.transaction_details, name='transaction_detail'),

    path('items/add/', views.add_item, name='add_item'),
    path('items/add/<slug:inventory_slug>/', views.add_item, name='add_item_with_slug'),
    path('items/edit/<int:item_id>/', views.edit_item, name='edit_item'),
    path('items/delete/<int:item_id>/', views.delete_item, name='delete_item'),

    path('item-detail-panel/<int:item_id>/', views.item_detail_panel, name='item_detail_panel'),
    path('<slug:inventory_slug>/', views.inventory_details, name='inv_page'),
    path('<slug:inventory_slug>/<int:item_id>/', views.item_details, name='item_page'),
]