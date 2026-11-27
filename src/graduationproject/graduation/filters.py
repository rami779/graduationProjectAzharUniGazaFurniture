import django_filters as df
from django.db.models import Exists, F, OuterRef, Q

from .models import Category, Color, Material, ProductVariant, Shape


class ProductFilter(df.FilterSet):
    search = df.CharFilter(method='filter_search')
    category = df.NumberFilter(method='filter_category')
    color = df.ModelMultipleChoiceFilter(queryset=Color.objects.all(), method='filter_color')
    material = df.ModelMultipleChoiceFilter(queryset=Material.objects.all(), method='filter_material')
    shape = df.ModelMultipleChoiceFilter(field_name='shape', queryset=Shape.objects.all())
    min_price = df.NumberFilter(field_name='current_price', lookup_expr='gte')
    max_price = df.NumberFilter(field_name='current_price', lookup_expr='lte')
    in_stock = df.BooleanFilter(field_name='in_stock')
    on_sale = df.BooleanFilter(method='filter_on_sale')
    ordering = df.OrderingFilter(fields=(('current_price', 'price'), ('created_at', 'created_at')))

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))

    def filter_category(self, queryset, name, value):
        # Includes direct subcategories (one level of nesting).
        ids = Category.objects.filter(Q(pk=value) | Q(parent_id=value)).values_list('pk', flat=True)
        return queryset.filter(category_id__in=ids)

    def filter_color(self, queryset, name, value):
        if not value:
            return queryset
        variants = ProductVariant.objects.filter(product=OuterRef('pk'), color__in=value)
        return queryset.filter(Q(color__in=value) | Exists(variants))

    def filter_material(self, queryset, name, value):
        if not value:
            return queryset
        variants = ProductVariant.objects.filter(product=OuterRef('pk'), material__in=value)
        return queryset.filter(Q(material__in=value) | Exists(variants))

    def filter_on_sale(self, queryset, name, value):
        on_sale = Q(sale_price__isnull=False, sale_price__lt=F('price'))
        return queryset.filter(on_sale) if value else queryset.exclude(on_sale)