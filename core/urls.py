from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='home'),

    # Properties
    path('properties/', views.property_list, name='property_list'),
    path('properties/add/', views.property_create, name='property_create'),
    path('properties/<int:pk>/', views.property_detail, name='property_detail'),
    path('properties/<int:pk>/edit/', views.property_edit, name='property_edit'),
    path('properties/<int:pk>/delete/', views.property_delete, name='property_delete'),

    # Units
    path('properties/<int:property_pk>/units/add/', views.unit_create, name='unit_create'),
    path('units/<int:pk>/edit/', views.unit_edit, name='unit_edit'),
    path('units/<int:pk>/delete/', views.unit_delete, name='unit_delete'),

    # Tenants
    path('tenants/', views.tenant_list, name='tenant_list'),
    path('tenants/add/', views.tenant_create, name='tenant_create'),
    path('tenants/<int:pk>/', views.tenant_detail, name='tenant_detail'),
    path('tenants/<int:pk>/edit/', views.tenant_edit, name='tenant_edit'),
    path('tenants/<int:pk>/move-out/', views.tenant_move_out, name='tenant_move_out'),
    path('tenants/<int:pk>/delete/', views.tenant_delete, name='tenant_delete'),

    # Payments
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/record/', views.payment_create, name='payment_create'),
    path('payments/<int:pk>/edit/', views.payment_edit, name='payment_edit'),
    path('payments/<int:pk>/receipt/', views.payment_receipt, name='payment_receipt'),
    path('payments/<int:pk>/receipt/print/', views.payment_receipt_pdf, name='payment_receipt_pdf'),

    # Announcements
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/create/', views.announcement_create, name='announcement_create'),
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),

    # Maintenance
    path('maintenance/', views.maintenance_list, name='maintenance_list'),
    path('maintenance/log/', views.maintenance_create, name='maintenance_create'),
    path('maintenance/<int:pk>/edit/', views.maintenance_edit, name='maintenance_edit'),
    path('maintenance/<int:pk>/delete/', views.maintenance_delete, name='maintenance_delete'),

    # Reports
    path('reports/', views.reports, name='reports'),

    # Agreements
    path('agreements/', views.agreement_list, name='agreement_list'),
    path('agreements/add/', views.agreement_create, name='agreement_create'),
    path('agreements/<int:pk>/', views.agreement_detail, name='agreement_detail'),
    path('agreements/<int:pk>/edit/', views.agreement_edit, name='agreement_edit'),
    path('agreements/<int:pk>/delete/', views.agreement_delete, name='agreement_delete'),
    path('legal/agreements/', views.agreements_public, name='agreements_public'),
]
