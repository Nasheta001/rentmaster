from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date
import uuid


class Property(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def total_units(self):
        return self.units.count()

    @property
    def vacant_units(self):
        return self.units.filter(status='vacant').count()

    @property
    def occupied_units(self):
        return self.units.filter(status='occupied').count()


class Unit(models.Model):
    STATUS_CHOICES = [
        ('occupied', 'Occupied'),
        ('vacant', 'Vacant'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
    ]

    prop = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="units")
    unit_number = models.CharField(max_length=50)
    unit_type = models.CharField(max_length=100, default='Apartment')
    floor = models.CharField(max_length=20, blank=True)
    size_sqft = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='vacant')
    available_from = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['unit_number']
        unique_together = ['prop', 'unit_number']

    def __str__(self):
        return f"{self.prop.name} - Unit {self.unit_number}"

    @property
    def current_tenant(self):
        return self.tenants.filter(move_out_date__isnull=True).first()


class Tenant(models.Model):
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tenants')
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True, related_name='tenants')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30)
    national_id = models.CharField(max_length=50, blank=True)
    move_in_date = models.DateField()
    move_out_date = models.DateField(null=True, blank=True)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    rent_due_day = models.PositiveSmallIntegerField(default=5)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deposit_paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_current_month_payment_status(self):
        today = date.today()
        payment = self.payments.filter(
            period_month=today.month,
            period_year=today.year
        ).first()
        if payment:
            return payment.status
        due_day = min(self.rent_due_day, 28)
        due_date = date(today.year, today.month, due_day)
        if today > due_date:
            return 'late'
        return 'due'


class Payment(models.Model):
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('due', 'Due'),
        ('late', 'Late'),
        ('partial', 'Partial'),
        ('waived', 'Waived'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('other', 'Other'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    amount_expected = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    period_month = models.PositiveSmallIntegerField()
    period_year = models.PositiveIntegerField()
    due_date = models.DateField()
    date_paid = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='due')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    mpesa_transaction_code = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_year', '-period_month']
        unique_together = ['tenant', 'period_month', 'period_year']

    def __str__(self):
        import calendar
        return f"{self.tenant} - {calendar.month_name[self.period_month]} {self.period_year} ({self.status})"

    def get_period_display_str(self):
        import calendar
        return f"{calendar.month_name[self.period_month]} {self.period_year}"

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCP-{uuid.uuid4().hex[:8].upper()}"
        today = date.today()
        if self.amount_paid >= self.amount_expected:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif today > self.due_date:
            self.status = 'late'
        super().save(*args, **kwargs)

    @property
    def balance(self):
        return self.amount_expected - self.amount_paid

    @property
    def days_late(self):
        if self.status in ['late', 'partial'] and date.today() > self.due_date:
            return (date.today() - self.due_date).days
        return 0


class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'All Tenants'),
        ('property', 'Specific Property'),
    ]
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('info', 'Information'),
    ]

    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    message = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    property = models.ForeignKey(
        Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='announcements'
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('emergency', 'Emergency'),
    ]

    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests')
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_requests')
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    reported_date = models.DateField(default=date.today)
    resolved_date = models.DateField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.unit} - {self.title}"


class LeaseEvent(models.Model):
    EVENT_CHOICES = [
        ('move_in', 'Move In'),
        ('move_out', 'Move Out'),
        ('renewal', 'Lease Renewal'),
        ('notice', 'Notice Given'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='lease_events')
    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lease_events')
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    event_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.tenant} - {self.get_event_type_display()} on {self.event_date}"


class Agreement(models.Model):
    AGREEMENT_TYPE_CHOICES = [
        ('rental', 'Rental Agreement'),
        ('terms', 'Terms of Service'),
        ('privacy', 'Privacy Policy'),
        ('rules', 'House Rules'),
        ('other', 'Other'),
    ]

    landlord = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agreements')
    title = models.CharField(max_length=200)
    agreement_type = models.CharField(max_length=20, choices=AGREEMENT_TYPE_CHOICES)
    description = models.TextField(blank=True)
    document = models.FileField(upload_to='agreements/', null=True, blank=True)
    content = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
