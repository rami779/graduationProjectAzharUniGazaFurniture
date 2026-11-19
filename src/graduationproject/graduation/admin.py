from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    AccountDeletionRequest, Address, AdminNote, AnswerOption, ApplicationDocument,
    AuditLog, CancellationRequest, Cart, CartItem, Category, Color, ContactSharingFlag,
    Consultation, ConsultationAnswer, ConsultationFile, ConsultationMessage,
    ConsultationStatusHistory, ConsultationTerms, DesignStyle, DesignerApplication,
    DesignerAvailability, DesignerEarning, DesignerStatusHistory, Dispute, EarningAdjustment,
    Material, ModerationAction, Notification, OrderDetail, OrderHeader, OrderIssue,
    OrderStatusHistory, Payment, PaymentEvent, Payout, PayoutItem, PayoutMethod,
    PortfolioItem, PortfolioMedia, Product, ProductImage, ProductVariant, Question, Refund,
    Report, Review, Shape, ShippingZone, ShippingZoneDestination, Specialization,
    StockReservation, SupportTicket, SystemSetting, TermsAcceptance, User, WeightBracket,
)


# ---------- users ----------
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'status', 'designer_status', 'is_staff')
    list_filter = ('role', 'status', 'designer_status', 'is_verified', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Platform', {'fields': ('role', 'status', 'phone_number', 'google_id', 'failed_login_count', 'locked_until')}),
        ('Designer profile', {'fields': ('designer_status', 'designer_intro', 'designer_services', 'time_zone', 'is_profile_published', 'is_verified', 'specializations', 'styles')}),
    )
    # The "add user" page: required email plus the role.
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('email', 'role')}),
    )
    filter_horizontal = UserAdmin.filter_horizontal + ('specializations', 'styles')


# ---------- catalog ----------
class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'price', 'stock_quantity', 'status')
    list_filter = ('status', 'category', 'has_variants', 'is_discontinued')
    search_fields = ('name', 'sku')
    inlines = [ProductVariantInline, ProductImageInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')


# ---------- shipping ----------
class ShippingZoneDestinationInline(admin.TabularInline):
    model = ShippingZoneDestination
    extra = 0


@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    inlines = [ShippingZoneDestinationInline]


@admin.register(WeightBracket)
class WeightBracketAdmin(admin.ModelAdmin):
    list_display = ('zone', 'min_weight', 'max_weight', 'fee')


# ---------- orders and payments ----------
class OrderDetailInline(admin.TabularInline):
    model = OrderDetail
    extra = 0


@admin.register(OrderHeader)
class OrderHeaderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'status', 'payment_status', 'total_price', 'order_date')
    list_filter = ('status', 'payment_status')
    search_fields = ('order_number', 'user__username', 'user__email')
    inlines = [OrderDetailInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'payment_type', 'user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('payment_type', 'status')


# ---------- designers ----------
class ApplicationDocumentInline(admin.TabularInline):
    model = ApplicationDocument
    extra = 0


@admin.register(DesignerApplication)
class DesignerApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submitted_at', 'reviewed_by')
    list_filter = ('status',)
    inlines = [ApplicationDocumentInline]


class PortfolioMediaInline(admin.TabularInline):
    model = PortfolioMedia
    extra = 0


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status')
    list_filter = ('status',)
    inlines = [PortfolioMediaInline]


# ---------- intake questions ----------
class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 0
    fk_name = 'question'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'is_required', 'sort_order', 'is_active')
    inlines = [AnswerOptionInline]


# ---------- consultations ----------
@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'designer', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status')


# ---------- append-only records: view only ----------
class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AuditLog)
class AuditLogAdmin(ReadOnlyAdmin):
    list_display = ('created_at', 'actor', 'action', 'target_type', 'target_id')
    list_filter = ('action', 'target_type')


@admin.register(PaymentEvent)
class PaymentEventAdmin(ReadOnlyAdmin):
    list_display = ('received_at', 'payment', 'event_type', 'provider_event_id')


# ---------- everything else: default admin ----------
for model in (
    AccountDeletionRequest, Address, AdminNote, CancellationRequest, Cart, CartItem, Color,
    ContactSharingFlag, ConsultationAnswer, ConsultationFile, ConsultationMessage,
    ConsultationStatusHistory, ConsultationTerms, DesignStyle, DesignerAvailability,
    DesignerEarning, DesignerStatusHistory, Dispute, EarningAdjustment, Material,
    ModerationAction, Notification, OrderIssue, OrderStatusHistory, Payout, PayoutItem,
    PayoutMethod, Refund, Report, Review, Shape, Specialization, StockReservation,
    SupportTicket, SystemSetting, TermsAcceptance,
):
    admin.site.register(model)