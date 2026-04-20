from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
import calendar

from .models import Property, Unit, Tenant, Payment, Announcement, MaintenanceRequest, LeaseEvent, Agreement
from .forms import (
    LandlordRegistrationForm, LoginForm, PropertyForm, UnitForm, TenantForm,
    PaymentForm, AnnouncementForm, MaintenanceRequestForm, AgreementForm
)


# ─────────────────────── AUTH ───────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LandlordRegistrationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name}! Your account is ready.")
        return redirect('dashboard')
    return render(request, 'core/auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.first_name or user.username}!")
        return redirect(request.GET.get('next', 'dashboard'))
    return render(request, 'core/auth/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ─────────────────────── DASHBOARD ───────────────────────

@login_required
def dashboard(request):
    landlord = request.user
    today = date.today()

    properties = Property.objects.filter(landlord=landlord)
    units = Unit.objects.filter(prop__landlord=landlord)
    tenants = Tenant.objects.filter(landlord=landlord, is_active=True)
    payments_this_month = Payment.objects.filter(
        landlord=landlord,
        period_month=today.month,
        period_year=today.year
    )

    total_collected = payments_this_month.filter(status='paid').aggregate(
        total=Sum('amount_paid'))['total'] or 0
    total_expected = payments_this_month.aggregate(
        total=Sum('amount_expected'))['total'] or 0
    pending_count = payments_this_month.filter(status__in=['due', 'late', 'partial']).count()
    late_count = payments_this_month.filter(status='late').count()

    vacant_units = units.filter(status='vacant').count()

    # Upcoming move-outs in next 30 days
    upcoming_moveouts = tenants.filter(
        move_out_date__gte=today,
        move_out_date__lte=today + timedelta(days=30)
    ).order_by('move_out_date')

    # Recent announcements
    announcements = Announcement.objects.filter(landlord=landlord).order_by('-created_at')[:5]

    # Open maintenance
    open_maintenance = MaintenanceRequest.objects.filter(
        landlord=landlord, status__in=['open', 'in_progress']
    ).count()

    # Late tenants
    late_tenants = payments_this_month.filter(status='late').select_related('tenant')[:5]

    context = {
        'total_properties': properties.count(),
        'total_tenants': tenants.count(),
        'total_units': units.count(),
        'vacant_units': vacant_units,
        'occupied_units': units.filter(status='occupied').count(),
        'total_collected': total_collected,
        'total_expected': total_expected,
        'pending_rent': total_expected - total_collected,
        'pending_count': pending_count,
        'late_count': late_count,
        'upcoming_moveouts': upcoming_moveouts,
        'announcements': announcements,
        'open_maintenance': open_maintenance,
        'late_tenants': late_tenants,
        'current_month': today.strftime('%B %Y'),
    }
    return render(request, 'core/dashboard.html', context)


# ─────────────────────── PROPERTIES ───────────────────────

@login_required
def property_list(request):
    properties = Property.objects.filter(landlord=request.user).prefetch_related('units')
    return render(request, 'core/properties/list.html', {'properties': properties})


@login_required
def property_create(request):
    form = PropertyForm(request.POST or None)
    if form.is_valid():
        prop = form.save(commit=False)
        prop.landlord = request.user
        prop.save()
        messages.success(request, f"Property '{prop.name}' created successfully.")
        return redirect('property_detail', pk=prop.pk)
    return render(request, 'core/properties/form.html', {'form': form, 'title': 'Add Property'})


@login_required
def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk, landlord=request.user)
    units = prop.units.prefetch_related('tenants').all()
    announcements = prop.announcements.all()[:5]
    context = {'property': prop, 'units': units, 'announcements': announcements}
    return render(request, 'core/properties/detail.html', context)


@login_required
def property_edit(request, pk):
    prop = get_object_or_404(Property, pk=pk, landlord=request.user)
    form = PropertyForm(request.POST or None, instance=prop)
    if form.is_valid():
        form.save()
        messages.success(request, "Property updated.")
        return redirect('property_detail', pk=pk)
    return render(request, 'core/properties/form.html', {'form': form, 'title': 'Edit Property', 'property': prop})


@login_required
def property_delete(request, pk):
    prop = get_object_or_404(Property, pk=pk, landlord=request.user)
    if request.method == 'POST':
        prop.delete()
        messages.success(request, f"Property '{prop.name}' deleted.")
        return redirect('property_list')
    return render(request, 'core/confirm_delete.html', {'object': prop, 'type': 'Property'})


# ─────────────────────── UNITS ───────────────────────

@login_required
def unit_create(request, property_pk):
    prop = get_object_or_404(Property, pk=property_pk, landlord=request.user)
    form = UnitForm(request.POST or None)
    if form.is_valid():
        unit = form.save(commit=False)
        unit.property = prop
        unit.save()
        messages.success(request, f"Unit {unit.unit_number} added.")
        return redirect('property_detail', pk=property_pk)
    return render(request, 'core/units/form.html', {'form': form, 'property': prop, 'title': 'Add Unit'})


@login_required
def unit_edit(request, pk):
    unit = get_object_or_404(Unit, pk=pk, property__landlord=request.user)
    form = UnitForm(request.POST or None, instance=unit)
    if form.is_valid():
        form.save()
        messages.success(request, f"Unit {unit.unit_number} updated.")
        return redirect('property_detail', pk=unit.prop.pk)
    return render(request, 'core/units/form.html', {'form': form, 'property': unit.property, 'title': 'Edit Unit'})


@login_required
def unit_delete(request, pk):
    unit = get_object_or_404(Unit, pk=pk, property__landlord=request.user)
    prop_pk = unit.prop.pk
    if request.method == 'POST':
        unit.delete()
        messages.success(request, "Unit deleted.")
        return redirect('property_detail', pk=prop_pk)
    return render(request, 'core/confirm_delete.html', {'object': unit, 'type': 'Unit'})


# ─────────────────────── TENANTS ───────────────────────

@login_required
def tenant_list(request):
    tenants = Tenant.objects.filter(landlord=request.user).select_related('unit__prop')
    status_filter = request.GET.get('status', 'active')
    if status_filter == 'inactive':
        tenants = tenants.filter(is_active=False)
    else:
        tenants = tenants.filter(is_active=True)
    return render(request, 'core/tenants/list.html', {'tenants': tenants, 'status_filter': status_filter})


@login_required
def tenant_create(request):
    form = TenantForm(landlord=request.user, data=request.POST or None)
    if form.is_valid():
        tenant = form.save(commit=False)
        tenant.landlord = request.user
        tenant.save()
        # Update unit status
        if tenant.unit:
            tenant.unit.status = 'occupied'
            tenant.unit.save()
        # Create move-in event
        LeaseEvent.objects.create(
            tenant=tenant,
            landlord=request.user,
            event_type='move_in',
            event_date=tenant.move_in_date,
            notes=f"Tenant {tenant.full_name} moved in."
        )
        messages.success(request, f"Tenant {tenant.full_name} added.")
        return redirect('tenant_detail', pk=tenant.pk)
    return render(request, 'core/tenants/form.html', {'form': form, 'title': 'Add Tenant'})


@login_required
def tenant_detail(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk, landlord=request.user)
    payments = tenant.payments.all()
    lease_events = tenant.lease_events.all()
    maintenance = tenant.maintenance_requests.all()
    context = {
        'tenant': tenant,
        'payments': payments,
        'lease_events': lease_events,
        'maintenance': maintenance,
        'current_status': tenant.get_current_month_payment_status(),
    }
    return render(request, 'core/tenants/detail.html', context)


@login_required
def tenant_edit(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk, landlord=request.user)
    old_unit = tenant.unit
    form = TenantForm(landlord=request.user, data=request.POST or None, instance=tenant)
    if form.is_valid():
        tenant = form.save()
        # Handle unit status changes
        if old_unit and old_unit != tenant.unit:
            old_unit.status = 'vacant'
            old_unit.save()
        if tenant.unit:
            tenant.unit.status = 'occupied'
            tenant.unit.save()
        messages.success(request, "Tenant updated.")
        return redirect('tenant_detail', pk=pk)
    return render(request, 'core/tenants/form.html', {'form': form, 'title': 'Edit Tenant', 'tenant': tenant})


@login_required
def tenant_move_out(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk, landlord=request.user)
    if request.method == 'POST':
        move_out_date = request.POST.get('move_out_date')
        notes = request.POST.get('notes', '')
        tenant.move_out_date = move_out_date
        tenant.is_active = False
        tenant.save()
        if tenant.unit:
            tenant.unit.status = 'vacant'
            tenant.unit.save()
        LeaseEvent.objects.create(
            tenant=tenant,
            landlord=request.user,
            event_type='move_out',
            event_date=move_out_date,
            notes=notes
        )
        messages.success(request, f"{tenant.full_name} has been marked as moved out.")
        return redirect('tenant_list')
    return render(request, 'core/tenants/move_out.html', {'tenant': tenant})


@login_required
def tenant_delete(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk, landlord=request.user)
    if request.method == 'POST':
        tenant.delete()
        messages.success(request, "Tenant deleted.")
        return redirect('tenant_list')
    return render(request, 'core/confirm_delete.html', {'object': tenant, 'type': 'Tenant'})


# ─────────────────────── PAYMENTS ───────────────────────

@login_required
def payment_list(request):
    today = date.today()
    payments = Payment.objects.filter(landlord=request.user).select_related('tenant__unit__prop')

    # Filters
    month = request.GET.get('month', today.month)
    year = request.GET.get('year', today.year)
    status = request.GET.get('status', '')

    try:
        payments = payments.filter(period_month=int(month), period_year=int(year))
    except (ValueError, TypeError):
        pass

    if status:
        payments = payments.filter(status=status)

    total_collected = payments.filter(status='paid').aggregate(t=Sum('amount_paid'))['t'] or 0
    total_expected = payments.aggregate(t=Sum('amount_expected'))['t'] or 0

    context = {
        'payments': payments,
        'total_collected': total_collected,
        'total_expected': total_expected,
        'months': [(i, calendar.month_name[i]) for i in range(1, 13)],
        'selected_month': int(month),
        'selected_year': int(year),
        'selected_status': status,
        'years': range(2020, today.year + 2),
    }
    return render(request, 'core/payments/list.html', context)


@login_required
def payment_create(request):
    form = PaymentForm(landlord=request.user, data=request.POST or None)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.landlord = request.user
        payment.save()
        messages.success(request, f"Payment recorded. Receipt: {payment.receipt_number}")
        return redirect('payment_receipt', pk=payment.pk)
    return render(request, 'core/payments/form.html', {'form': form, 'title': 'Record Payment'})


@login_required
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk, landlord=request.user)
    form = PaymentForm(landlord=request.user, data=request.POST or None, instance=payment)
    if form.is_valid():
        form.save()
        messages.success(request, "Payment updated.")
        return redirect('payment_list')
    return render(request, 'core/payments/form.html', {'form': form, 'title': 'Edit Payment'})


@login_required
def payment_receipt(request, pk):
    payment = get_object_or_404(Payment, pk=pk, landlord=request.user)
    return render(request, 'core/payments/receipt.html', {'payment': payment})


@login_required
def payment_receipt_pdf(request, pk):
    """Generate a simple text/HTML receipt for printing."""
    payment = get_object_or_404(Payment, pk=pk, landlord=request.user)
    return render(request, 'core/payments/receipt_print.html', {'payment': payment})


# ─────────────────────── ANNOUNCEMENTS ───────────────────────

@login_required
def announcement_list(request):
    announcements = Announcement.objects.filter(landlord=request.user)
    return render(request, 'core/announcements/list.html', {'announcements': announcements})


@login_required
def announcement_create(request):
    form = AnnouncementForm(landlord=request.user, data=request.POST or None)
    if form.is_valid():
        ann = form.save(commit=False)
        ann.landlord = request.user
        ann.save()
        messages.success(request, "Announcement created.")
        return redirect('announcement_list')
    return render(request, 'core/announcements/form.html', {'form': form, 'title': 'Create Announcement'})


@login_required
def announcement_detail(request, pk):
    ann = get_object_or_404(Announcement, pk=pk, landlord=request.user)
    return render(request, 'core/announcements/detail.html', {'announcement': ann})


@login_required
def announcement_delete(request, pk):
    ann = get_object_or_404(Announcement, pk=pk, landlord=request.user)
    if request.method == 'POST':
        ann.delete()
        messages.success(request, "Announcement deleted.")
        return redirect('announcement_list')
    return render(request, 'core/confirm_delete.html', {'object': ann, 'type': 'Announcement'})


# ─────────────────────── MAINTENANCE ───────────────────────

@login_required
def maintenance_list(request):
    requests = MaintenanceRequest.objects.filter(landlord=request.user).select_related('unit__prop', 'tenant')
    status_filter = request.GET.get('status', '')
    if status_filter:
        requests = requests.filter(status=status_filter)
    return render(request, 'core/maintenance/list.html', {'requests': requests, 'status_filter': status_filter})


@login_required
def maintenance_create(request):
    form = MaintenanceRequestForm(landlord=request.user, data=request.POST or None)
    if form.is_valid():
        maint = form.save(commit=False)
        maint.landlord = request.user
        maint.save()
        messages.success(request, "Maintenance request logged.")
        return redirect('maintenance_list')
    return render(request, 'core/maintenance/form.html', {'form': form, 'title': 'Log Maintenance Request'})


@login_required
def maintenance_edit(request, pk):
    maint = get_object_or_404(MaintenanceRequest, pk=pk, landlord=request.user)
    form = MaintenanceRequestForm(landlord=request.user, data=request.POST or None, instance=maint)
    if form.is_valid():
        form.save()
        messages.success(request, "Maintenance request updated.")
        return redirect('maintenance_list')
    return render(request, 'core/maintenance/form.html', {'form': form, 'title': 'Edit Maintenance Request'})


@login_required
def maintenance_delete(request, pk):
    maint = get_object_or_404(MaintenanceRequest, pk=pk, landlord=request.user)
    if request.method == 'POST':
        maint.delete()
        messages.success(request, "Request deleted.")
        return redirect('maintenance_list')
    return render(request, 'core/confirm_delete.html', {'object': maint, 'type': 'Maintenance Request'})


# ─────────────────────── REPORTS ───────────────────────

@login_required
def reports(request):
    today = date.today()
    landlord = request.user

    # Monthly income for last 6 months
    monthly_data = []
    for i in range(5, -1, -1):
        month = today.month - i
        year = today.year
        if month <= 0:
            month += 12
            year -= 1
        payments = Payment.objects.filter(
            landlord=landlord, period_month=month, period_year=year
        )
        collected = payments.filter(status='paid').aggregate(t=Sum('amount_paid'))['t'] or 0
        expected = payments.aggregate(t=Sum('amount_expected'))['t'] or 0
        monthly_data.append({
            'month': calendar.month_abbr[month],
            'year': year,
            'collected': float(collected),
            'expected': float(expected),
        })

    # Current month summary
    current_payments = Payment.objects.filter(
        landlord=landlord, period_month=today.month, period_year=today.year
    )
    total_expected = current_payments.aggregate(t=Sum('amount_expected'))['t'] or 0
    total_collected = current_payments.filter(status='paid').aggregate(t=Sum('amount_paid'))['t'] or 0

    # Vacancy
    units = Unit.objects.filter(prop__landlord=landlord)
    vacancy_data = {
        'occupied': units.filter(status='occupied').count(),
        'vacant': units.filter(status='vacant').count(),
        'reserved': units.filter(status='reserved').count(),
        'maintenance': units.filter(status='maintenance').count(),
    }

    context = {
        'monthly_data': monthly_data,
        'total_expected': total_expected,
        'total_collected': total_collected,
        'total_pending': total_expected - total_collected,
        'vacancy_data': vacancy_data,
        'current_month': today.strftime('%B %Y'),
    }
    return render(request, 'core/reports.html', context)


# ─────────────────────── AGREEMENTS ───────────────────────

@login_required
def agreement_list(request):
    agreements = Agreement.objects.filter(landlord=request.user)
    return render(request, 'core/agreements/list.html', {'agreements': agreements})


@login_required
def agreement_create(request):
    form = AgreementForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        agreement = form.save(commit=False)
        agreement.landlord = request.user
        agreement.save()
        messages.success(request, "Agreement saved.")
        return redirect('agreement_list')
    return render(request, 'core/agreements/form.html', {'form': form, 'title': 'Add Agreement'})


@login_required
def agreement_detail(request, pk):
    agreement = get_object_or_404(Agreement, pk=pk, landlord=request.user)
    return render(request, 'core/agreements/detail.html', {'agreement': agreement})


@login_required
def agreement_edit(request, pk):
    agreement = get_object_or_404(Agreement, pk=pk, landlord=request.user)
    form = AgreementForm(request.POST or None, request.FILES or None, instance=agreement)
    if form.is_valid():
        form.save()
        messages.success(request, "Agreement updated.")
        return redirect('agreement_list')
    return render(request, 'core/agreements/form.html', {'form': form, 'title': 'Edit Agreement'})


@login_required
def agreement_delete(request, pk):
    agreement = get_object_or_404(Agreement, pk=pk, landlord=request.user)
    if request.method == 'POST':
        agreement.delete()
        messages.success(request, "Agreement deleted.")
        return redirect('agreement_list')
    return render(request, 'core/confirm_delete.html', {'object': agreement, 'type': 'Agreement'})


# Public agreements page (footer link)
def agreements_public(request):
    agreements = Agreement.objects.filter(is_public=True)
    return render(request, 'core/agreements/public.html', {'agreements': agreements})
