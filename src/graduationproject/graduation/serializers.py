from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import AccountDeletionRequest, Address, Category, Color, Product, ProductImage,ProductVariant, Review
from datetime import timedelta
from django.db.models import F
from django.utils import timezone

User = get_user_model()
MAX_FAILED_LOGINS = 5
LOCKOUT_MINUTES = 15

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'designer_status')
        read_only_fields = fields   # role and status must never be writable by the client


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value

    def validate_password(self, value):
        validate_password(value)   # uses the validators in settings.py
        return value

    def create(self, validated_data):
        first, _, last = validated_data['name'].strip().partition(' ')
        email = validated_data['email']
        return User.objects.create_user(
            username=email, email=email, password=validated_data['password'],
            first_name=first, last_name=last,
        )


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(self.username_field, None)
        self.fields['email'] = serializers.EmailField()

    def _register_failure(self, account):
        # F() makes the increment atomic, so parallel guesses can't skip the counter.
        User.objects.filter(pk=account.pk).update(failed_login_count=F('failed_login_count') + 1)
        account.refresh_from_db(fields=['failed_login_count'])
        if account.failed_login_count >= MAX_FAILED_LOGINS:
            User.objects.filter(pk=account.pk).update(
                failed_login_count=0,
                locked_until=timezone.now() + timedelta(minutes=LOCKOUT_MINUTES),
            )

    def validate(self, attrs):
        account = User.objects.filter(email__iexact=attrs['email']).first()

        if account and account.locked_until and account.locked_until > timezone.now():
            raise AuthenticationFailed('Too many failed attempts. Please try again later.')

        user = None
        if account:
            user = authenticate(self.context.get('request'), username=account.username, password=attrs['password'])

        if user is None:
            if account:
                self._register_failure(account)
            raise AuthenticationFailed('Invalid email or password.')
        if user.status == User.Status.SUSPENDED:
            raise AuthenticationFailed('This account is suspended. Please contact support.')

        if user.failed_login_count or user.locked_until:
            User.objects.filter(pk=user.pk).update(failed_login_count=0, locked_until=None)

        refresh = self.get_token(user)
        return {'access': str(refresh.access_token), 'refresh': str(refresh),
                'user': UserSerializer(user).data}
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'designer_status')
        read_only_fields = ('id', 'email', 'role', 'designer_status')   # only name and phone are editable


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'label', 'country', 'province', 'city', 'street_address', 'postal_code', 'is_default')


class AccountDeletionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountDeletionRequest
        fields = ('id', 'status', 'reason', 'created_at', 'reviewed_at')
        read_only_fields = ('id', 'status', 'created_at', 'reviewed_at')

    def validate(self, attrs):
        user = self.context['request'].user
        if AccountDeletionRequest.objects.filter(
                user=user, status=AccountDeletionRequest.Status.PENDING).exists():
            raise serializers.ValidationError('You already have a pending deletion request.')
        return attrs

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'parent')


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ('id', 'name', 'color_hexa')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'sort_order')


class ProductVariantSerializer(serializers.ModelSerializer):
    color = ColorSerializer(read_only=True)
    material = serializers.StringRelatedField()
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ('id', 'sku', 'price', 'size', 'color', 'material', 'in_stock')

    def get_in_stock(self, obj):
        return obj.stock_quantity > 0   


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'author', 'rating', 'comment', 'created_at')   # no email or username


class ProductListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    color = ColorSerializer(read_only=True)
    main_image = serializers.SerializerMethodField()
    in_stock = serializers.BooleanField(read_only=True)     # computed in the view
    availability = serializers.SerializerMethodField()
    avg_rating = serializers.FloatField(read_only=True)     # computed in the view

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'sale_price', 'currency', 'category', 'color',
                  'main_image', 'in_stock', 'availability', 'avg_rating')

    def get_main_image(self, obj):
        images = list(obj.images.all())          
        if not images:
            return None
        url = images[0].image.url
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

    def get_availability(self, obj):
        return 'In Stock' if obj.in_stock else 'Out of Stock'


class ProductDetailSerializer(ProductListSerializer):
    material = serializers.StringRelatedField()
    shape = serializers.StringRelatedField()
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + (
            'description', 'sku', 'weight', 'length', 'width', 'height', 'material', 'shape',
            'has_variants', 'is_discontinued', 'images', 'variants', 'reviews', 'review_count')