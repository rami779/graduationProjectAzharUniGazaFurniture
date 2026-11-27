from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.db.models import F, Q

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        ADMIN = 'admin', 'Admin'
        SUPER_ADMIN = 'super_admin', 'Super Admin'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'

    email = models.EmailField(unique=True, blank=False)
    phone_number = models.CharField(max_length=20, blank=True)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    failed_login_count = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class DesignerStatus(models.TextChoices):
        NONE = 'none', 'Not a designer'
        APPROVED = 'approved', 'Approved'
        SUSPENDED = 'suspended', 'Suspended'

    designer_status = models.CharField(max_length=20, choices=DesignerStatus.choices, default=DesignerStatus.NONE)
    designer_intro = models.TextField(blank=True)
    designer_services = models.TextField(blank=True)
    time_zone = models.CharField(max_length=64, default='UTC')
    is_profile_published = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)   # platform-verified badge, admin only
    specializations = models.ManyToManyField('Specialization', blank=True, related_name='designers')
    styles = models.ManyToManyField('DesignStyle', blank=True, related_name='designers')


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    def __str__(self):
        return self.country + self.province
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.PROTECT, related_name='children')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color_hexa = models.CharField(max_length=7)  # e.g. "#1A1A1A"

    def __str__(self):
        return self.name
    
class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
class Shape(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        DEACTIVATED = 'deactivated', 'Deactivated'
        ARCHIVED = 'archived', 'Archived'

    class Currency(models.TextChoices):
        USD = 'USD', 'USD'

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    sku = models.CharField(max_length=64, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    length = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    width = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)
    material = models.ForeignKey(Material, null=True, blank=True, on_delete=models.SET_NULL)
    shape = models.ForeignKey(Shape, null=True, blank=True, on_delete=models.SET_NULL)
    stock_quantity = models.PositiveIntegerField(default=0)
    has_variants = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_discontinued = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=64, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=50, blank=True)
    color = models.ForeignKey(Color, null=True, blank=True, on_delete=models.SET_NULL)
    material = models.ForeignKey(Material, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.product.name} ({self.sku})"
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
    def __str__(self):
        return f"Image of {self.product.name}"
# ------------------

class Cart(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='cart')
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Cart {self.pk} ({self.user or 'guest'})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product', 'variant'], condition=Q(variant__isnull=False), name='unique_cart_item_with_variant'),
            models.UniqueConstraint(fields=['cart', 'product'], condition=Q(variant__isnull=True), name='unique_cart_item_no_variant'),
        ]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class ShippingZone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class ShippingZoneDestination(models.Model):
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name='destinations')
    country = models.CharField(max_length=100)
    province = models.CharField(max_length=100, blank=True)  # blank = whole country

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['country', 'province'], name='one_zone_per_destination'),
        ]
    def __str__(self):
        return f"{self.zone.name}: {self.country} {self.province}".strip()

class WeightBracket(models.Model):
    zone = models.ForeignKey(ShippingZone, on_delete=models.CASCADE, related_name='brackets')
    min_weight = models.DecimalField(max_digits=8, decimal_places=2)  # kg
    max_weight = models.DecimalField(max_digits=8, decimal_places=2)  # kg
    fee = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Product.Currency.choices, default=Product.Currency.USD)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(min_weight__lt=F('max_weight')), name='bracket_min_less_than_max'),
        ]

    def clean(self):
        # Reject conflicting (overlapping) ranges inside the same zone.
        overlapping = WeightBracket.objects.filter(
            zone=self.zone,
            min_weight__lt=self.max_weight,
            max_weight__gt=self.min_weight,
        ).exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError('This weight range overlaps an existing bracket in the zone.')
    def __str__(self):
        return f"{self.zone.name}: {self.min_weight}-{self.max_weight} kg"

# ----------
class OrderHeader(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        SHIPPING = 'shipping', 'Shipping'
        DELIVERED = 'delivered', 'Delivered'
        COMPLETED = 'completed', 'Completed'
    def __str__(self):
        return f"Order {self.order_number}"
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        PARTIALLY_REFUNDED = 'partially_refunded', 'Partially refunded'
        REFUNDED = 'refunded', 'Refunded'

    order_number = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2)
    extra_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Product.Currency.choices)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    # Delivery address snapshot, copied at checkout so later edits never change old orders.
    ship_name = models.CharField(max_length=150)
    ship_phone = models.CharField(max_length=20)
    ship_country = models.CharField(max_length=100)
    ship_province = models.CharField(max_length=100)
    ship_city = models.CharField(max_length=100)
    ship_street_address = models.CharField(max_length=255)
    ship_postal_code = models.CharField(max_length=20)
    tracking_number = models.CharField(max_length=100, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.order_number + self.user
    
class StockReservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        CONSUMED = 'consumed', 'Consumed (payment confirmed)'
        RELEASED = 'released', 'Released (payment failed)'
        EXPIRED = 'expired', 'Expired'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_reservations')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    order_header = models.ForeignKey(OrderHeader, null=True, blank=True, on_delete=models.SET_NULL, related_name='stock_reservations')
    def __str__(self):
        return f"Reservation {self.pk}: {self.quantity} x {self.product.name}"
    
class OrderDetail(models.Model):
    order_header = models.ForeignKey(OrderHeader, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=255)  # snapshot
    sku = models.CharField(max_length=64)            # snapshot
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.product_name

class OrderStatusHistory(models.Model):
    order_header = models.ForeignKey(OrderHeader, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.SET_NULL, related_name='+')
    changed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.new_status

class OrderIssue(models.Model):
    class IssueType(models.TextChoices):
        CANCELLATION = 'cancellation', 'Cancellation request'
        DELIVERY = 'delivery_issue', 'Delivery issue'
        REFUND = 'refund', 'Refund request'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In progress'
        RESOLVED = 'resolved', 'Resolved'
        REJECTED = 'rejected', 'Rejected'

    order_header = models.ForeignKey(OrderHeader, on_delete=models.CASCADE, related_name='issues')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='order_issues')
    issue_type = models.CharField(max_length=20, choices=IssueType.choices)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return self.issue_type

class Payment(models.Model):
    class PaymentType(models.TextChoices):
        ORDER = 'order', 'Order'
        CONSULTATION = 'consultation', 'Consultation'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCEEDED = 'succeeded', 'Succeeded'
        FAILED = 'failed', 'Failed'
        CANCELLED = 'cancelled', 'Cancelled'

    payment_type = models.CharField(max_length=20, choices=PaymentType.choices)
    order_header = models.ForeignKey(OrderHeader, null=True, blank=True, on_delete=models.PROTECT, related_name='payments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payments')
    provider = models.CharField(max_length=30, default='stripe')
    provider_transaction_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    idempotency_key = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Product.Currency.choices)
    exchange_rate = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    failure_reason = models.CharField(max_length=255, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    consultation = models.ForeignKey('Consultation', null=True, blank=True, on_delete=models.PROTECT, related_name='payments')

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(payment_type='order', order_header__isnull=False, consultation__isnull=True) |
                           Q(payment_type='consultation', consultation__isnull=False, order_header__isnull=True)), name='payment_has_exactly_one_target'),
        ]
    def __str__(self):
        return f"Payment {self.pk} ({self.status})"
    
class PaymentEvent(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='events')
    provider_event_id = models.CharField(max_length=255, unique=True)  # blocks duplicate callbacks
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    received_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.event_type

class Refund(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        APPROVED = 'approved', 'Approved'
        PROCESSED = 'processed', 'Processed'
        REJECTED = 'rejected', 'Rejected'
        FAILED = 'failed', 'Failed'

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='refunds')
    order_issue = models.ForeignKey(OrderIssue, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Product.Currency.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    provider_refund_id = models.CharField(max_length=255, null=True, blank=True, unique=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='refunds_requested')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='refunds_approved')
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    dispute = models.ForeignKey('Dispute', null=True, blank=True, on_delete=models.SET_NULL, related_name='refunds')
    def __str__(self):
        return f"Refund {self.pk} ({self.status})"
#--------------------------

class Review(models.Model):
    class Status(models.TextChoices):
        VISIBLE = 'visible', 'Visible'
        FLAGGED = 'flagged', 'Flagged'
        HIDDEN = 'hidden', 'Hidden'
        REMOVED = 'removed', 'Removed'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.VISIBLE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['product', 'user'], name='one_review_per_user_per_product'),
        ]
    def __str__(self):
        return f"{self.rating}/5 on {self.product.name}"

class SupportTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='support_tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    on_delete=models.SET_NULL, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.subject

class AccountDeletionRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='deletion_requests')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_deletions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=Q(status='pending'), name='one_pending_deletion_request_per_user'),
        ]
    def __str__(self):
        return f"Deletion request by {self.user} ({self.status})"


class Notification(models.Model):
    class Severity(models.TextChoices):
        URGENT = 'urgent', 'Urgent'
        ROUTINE = 'routine', 'Routine'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50)   # e.g. 'new_application', 'low_stock'
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.ROUTINE)
    message = models.CharField(max_length=255)
    related_type = models.CharField(max_length=50, blank=True)   # e.g. 'OrderHeader'
    related_id = models.PositiveBigIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return self.message

class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='audit_entries')
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50)
    target_id = models.PositiveBigIntegerField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    # Append-only: entries can be created but never edited or deleted through the model.
    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise PermissionError('Audit log entries cannot be modified.')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise PermissionError('Audit log entries cannot be deleted.')
    def __str__(self):
        return f"{self.action} on {self.target_type} {self.target_id}"

class SystemSetting(models.Model):
    setting_key = models.CharField(max_length=100, unique=True)
    setting_value = models.CharField(max_length=255)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.setting_key
#-----------------

class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class DesignStyle(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class DesignerApplication(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending_review', 'Pending Review'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='designer_applications')
    professional_info = models.TextField()
    years_experience = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    rejection_reason = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_applications')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], condition=Q(status='pending_review'), name='one_pending_application_per_user'),
        ]

    def clean(self):
        if self.status == self.Status.REJECTED and not self.rejection_reason.strip():
            raise ValidationError('A rejection reason is required.')
    def __str__(self):
        return f"Application by {self.user} ({self.status})"

class ApplicationDocument(models.Model):
    class DocumentType(models.TextChoices):
        IDENTITY = 'identity', 'Identity document'
        QUALIFICATION = 'qualification', 'Qualification / certificate'
        OTHER = 'other', 'Other'

    application = models.ForeignKey(DesignerApplication, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    file = models.FileField(upload_to='private/applications/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.document_type} for application {self.application_id}"

class DesignerAvailability(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='availability_slots')
    day_of_week = models.PositiveSmallIntegerField(validators=[MaxValueValidator(6)])  
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(start_time__lt=F('end_time')), name='availability_start_before_end'),
        ]
    def __str__(self):
        return f"{self.user} day {self.day_of_week} {self.start_time}-{self.end_time}"


class PortfolioItem(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        REMOVED = 'removed', 'Removed by admin'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio_items')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class PortfolioMedia(models.Model):
    class FileType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'

    portfolio_item = models.ForeignKey(PortfolioItem, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='portfolio/')
    file_type = models.CharField(max_length=10, choices=FileType.choices, default=FileType.IMAGE)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
    def __str__(self):
        return f"Media {self.pk} of {self.portfolio_item.title}"

class DesignerStatusHistory(models.Model):
    class Action(models.TextChoices):
        APPROVED = 'approved', 'Approved'
        SUSPENDED = 'suspended', 'Suspended'
        REINSTATED = 'reinstated', 'Reinstated'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='designer_status_history')
    action = models.CharField(max_length=20, choices=Action.choices)
    reason = models.TextField(blank=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='designer_actions')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.action == self.Action.SUSPENDED and not self.reason.strip():
            raise ValidationError('A reason is required to suspend a designer.')
    def __str__(self):
        return f"{self.user}: {self.action}"
    
#---------------

class Question(models.Model):
    class QuestionType(models.TextChoices):
        SINGLE = 'single_choice', 'Single choice'
        MULTIPLE = 'multiple_choice', 'Multiple choice'
        TEXT = 'text', 'Free text'

    text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=20, choices=QuestionType.choices)
    is_required = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    # Optional follow-up logic: only show this question if that option was chosen.
    shown_if_option = models.ForeignKey('AnswerOption', null=True, blank=True, on_delete=models.SET_NULL, related_name='follow_up_questions')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.text
    
class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']
    def __str__(self):
        return self.text

class Consultation(models.Model):
    class Status(models.TextChoices):
        NOT_CONFIRMED = 'not_confirmed', 'Not confirmed'
        CONFIRMED = 'confirmed', 'Confirmed'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    class PaymentStatus(models.TextChoices):
        UNPAID = 'unpaid', 'Unpaid'
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='consultations_as_customer')
    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='consultations_as_designer')
    project_info = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NOT_CONFIRMED)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~Q(customer=F('designer')), name='consultation_customer_not_designer'),
        ]
    def __str__(self):
        return f"Consultation {self.pk}: {self.customer} with {self.designer}"

class ConsultationAnswer(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    answer_option = models.ForeignKey(AnswerOption, null=True, blank=True, on_delete=models.PROTECT)
    answer_text = models.TextField(blank=True)
    question_text_snapshot = models.CharField(max_length=255)   # keeps old consultations readable
    def __str__(self):
        return self.question_text_snapshot

class ConsultationStatusHistory(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, blank=True)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    changed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.old_status} -> {self.new_status}"

class ConsultationTerms(models.Model):
    class Status(models.TextChoices):
        PROPOSED = 'proposed', 'Proposed'
        ACCEPTED = 'accepted', 'Accepted by both'
        SUPERSEDED = 'superseded', 'Superseded by a newer version'

    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='terms')
    version_number = models.PositiveIntegerField()
    proposed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Product.Currency.choices, default=Product.Currency.USD)
    scope = models.TextField()
    duration = models.CharField(max_length=100)
    deliverables = models.TextField()
    scheduling_details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROPOSED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['consultation', 'version_number'], name='unique_terms_version_per_consultation'),
        ]
    def __str__(self):
        return f"Terms v{self.version_number} for consultation {self.consultation_id}"

class TermsAcceptance(models.Model):
    terms = models.ForeignKey(ConsultationTerms, on_delete=models.CASCADE, related_name='acceptances')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    accepted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['terms', 'user'], name='one_acceptance_per_user_per_version'),
        ]
    def __str__(self):
        return f"{self.user} accepted terms {self.terms_id}"

class ConsultationMessage(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
    def __str__(self):
        return f"Message {self.pk} in consultation {self.consultation_id}"

class ConsultationFile(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='files')
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    file = models.FileField(upload_to='private/consultations/')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.file_name

class CancellationRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'requested', 'Requested'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='cancellation_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"Cancellation request for consultation {self.consultation_id} ({self.status})"

class Dispute(models.Model):
    class DisputeType(models.TextChoices):
        REFUND = 'refund_request', 'Refund request'
        DISPUTE = 'dispute', 'Dispute'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In progress'
        RESOLVED = 'resolved', 'Resolved'

    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='disputes')
    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    dispute_type = models.CharField(max_length=20, choices=DisputeType.choices)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    decision = models.TextField(blank=True)
    decision_rationale = models.TextField(blank=True)
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    decided_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.decision and not self.decision_rationale.strip():
            raise ValidationError('A decision needs a written rationale.')
    def __str__(self):
            return f"Dispute {self.pk} ({self.status})"
#---------------------------

class Report(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'

    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,related_name='reports_made')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name='reports_received')
    consultation = models.ForeignKey(Consultation, null=True, blank=True, on_delete=models.SET_NULL, related_name='reports')
    message = models.ForeignKey(ConsultationMessage, null=True, blank=True, on_delete=models.SET_NULL, related_name='reports')
    reason = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Report {self.pk} ({self.status})"

class ContactSharingFlag(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'

    message = models.ForeignKey(ConsultationMessage, on_delete=models.CASCADE, related_name='contact_flags')
    rule_matched = models.CharField(max_length=100)   # e.g. 'phone_number', 'email', 'external_link'
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Flag {self.pk}: {self.rule_matched}"

class ModerationAction(models.Model):
    class ActionType(models.TextChoices):
        WARNING = 'warning', 'Warning'
        MESSAGING_RESTRICTION = 'messaging_restriction', 'Messaging restriction'
        TEMPORARY_SUSPENSION = 'temporary_suspension', 'Temporary suspension'
        DISMISSED = 'dismissed', 'Dismissed (no action)'

    report = models.ForeignKey(Report, null=True, blank=True, on_delete=models.SET_NULL, related_name='actions')
    flag = models.ForeignKey(ContactSharingFlag, null=True, blank=True, on_delete=models.SET_NULL, related_name='actions')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='moderation_actions_received')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='moderation_actions_taken')
    action_type = models.CharField(max_length=30, choices=ActionType.choices)
    justification = models.TextField()
    expires_at = models.DateTimeField(null=True, blank=True)   # restrictions and suspensions are temporary
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.action_type} for {self.target_user}"

class AdminNote(models.Model):
    target_type = models.CharField(max_length=50)   # e.g. 'Dispute', 'DesignerApplication'
    target_id = models.PositiveBigIntegerField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='+')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Note on {self.target_type} {self.target_id}"
    
class DesignerEarning(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        AVAILABLE = 'available', 'Available for payout'
        PAID_OUT = 'paid_out', 'Paid out'
        REVERSED = 'reversed', 'Reversed (refunded)'

    consultation = models.OneToOneField(Consultation, on_delete=models.PROTECT, related_name='earning')
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT, related_name='earning')
    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='earnings')
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Product.Currency.choices, default=Product.Currency.USD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(gross_amount=F('commission_amount') + F('net_amount')), name='earning_gross_equals_commission_plus_net'),
        ]
    def __str__(self):
        return f"Earning {self.pk}: {self.net_amount} {self.currency}"

class EarningAdjustment(models.Model):
    earning = models.ForeignKey(DesignerEarning, on_delete=models.PROTECT, related_name='adjustments')
    refund = models.ForeignKey(Refund, null=True, blank=True, on_delete=models.SET_NULL, related_name='earning_adjustments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)   # negative for deductions
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Adjustment {self.pk}: {self.amount}"

class PayoutMethod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payout_methods')
    method_type = models.CharField(max_length=30)   # e.g. 'bank_transfer', 'stripe_connect'
    details_encrypted = models.TextField()
    is_default = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.method_type} for {self.user}"

class Payout(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        PAID = 'paid', 'Paid'
        FAILED = 'failed', 'Failed'

    designer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='payouts')
    payout_method = models.ForeignKey(PayoutMethod, on_delete=models.PROTECT, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=Product.Currency.choices, default=Product.Currency.USD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    transaction_reference = models.CharField(max_length=255, blank=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payout {self.pk}: {self.amount} {self.currency} ({self.status})"
    
class PayoutItem(models.Model):
    payout = models.ForeignKey(Payout, on_delete=models.CASCADE, related_name='items')
    earning = models.OneToOneField(DesignerEarning, on_delete=models.PROTECT, related_name='payout_item')
    def __str__(self):
        return f"Payout {self.payout_id} item {self.earning_id}"