from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer, RegisterSerializer, UserSerializer, AccountDeletionRequestSerializer, AddressSerializer, ProfileSerializer
from django.db import transaction
from rest_framework import generics, viewsets
from .models import AccountDeletionRequest, Address

from django.db.models import Avg, BooleanField, Case, Count, Exists, OuterRef, Prefetch, Q, Value, When
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from .filters import ProductFilter
from .models import Category, Color, Material, Product, ProductVariant, Review, Shape
from .serializers import CategorySerializer, ColorSerializer, ProductDetailSerializer, ProductListSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({'user': UserSerializer(user).data,
                         'access': str(refresh.access_token),
                         'refresh': str(refresh)}, status=201)


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'head', 'options']   # partial updates only

    def get_object(self):
        return self.request.user


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        # Only the caller's own addresses; anyone else's id returns 404 (FR-CUS-50).
        return Address.objects.filter(user=self.request.user).order_by('-is_default', 'id')

    def _save(self, serializer):
        with transaction.atomic():
            address = serializer.save(user=self.request.user)
            if address.is_default:   # keep a single default address
                (Address.objects.filter(user=self.request.user)
                 .exclude(pk=address.pk).update(is_default=False))

    def perform_create(self, serializer):
        self._save(serializer)

    def perform_update(self, serializer):
        self._save(serializer)


class AccountDeletionRequestView(generics.ListCreateAPIView):
    serializer_class = AccountDeletionRequestSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return AccountDeletionRequest.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

def catalog_queryset():
    """Only products customers may see, with availability, price and rating computed."""
    variant_in_stock = ProductVariant.objects.filter(
        product=OuterRef('pk'), is_active=True, stock_quantity__gt=0)
    visible_reviews = Q(reviews__status=Review.Status.VISIBLE)

    return (
        Product.objects
        .filter(status=Product.Status.PUBLISHED, category__is_active=True)   # FR-CUS-03
        .annotate(
            in_stock=Case(
                When(is_discontinued=True, then=Value(False)),
                When(has_variants=False, stock_quantity__gt=0, then=Value(True)),
                When(Q(has_variants=True) & Exists(variant_in_stock), then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            current_price=Coalesce('sale_price', 'price'),
            avg_rating=Avg('reviews__rating', filter=visible_reviews),
            review_count=Count('reviews', filter=visible_reviews),
        )
        .select_related('category', 'color', 'material', 'shape')
        .order_by('-created_at', '-id')
    )


class ProductPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 48


class ProductListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = ProductListSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_queryset(self):
        return catalog_queryset().prefetch_related('images')


class ProductDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        return catalog_queryset().prefetch_related(
            'images',
            Prefetch('variants', queryset=ProductVariant.objects
                     .filter(is_active=True).select_related('color', 'material')),
            Prefetch('reviews', queryset=Review.objects
                     .filter(status=Review.Status.VISIBLE).select_related('user')
                     .order_by('-created_at')),
        )


class CategoryListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = CategorySerializer
    pagination_class = None
    queryset = Category.objects.filter(is_active=True)


class FilterOptionsView(APIView):
    """Values for the filter dropdowns."""
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        return Response({
            'colors': ColorSerializer(Color.objects.all(), many=True).data,
            'materials': list(Material.objects.values('id', 'name')),
            'shapes': list(Shape.objects.values('id', 'name')),
        })