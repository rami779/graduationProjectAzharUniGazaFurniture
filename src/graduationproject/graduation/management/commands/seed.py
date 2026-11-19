from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from graduation.models import (
    AnswerOption, Category, Color, DesignStyle, Material, Product,
    ProductVariant, Question, Shape, ShippingZone, ShippingZoneDestination,
    Specialization, SystemSetting, WeightBracket,
)

User = get_user_model()

DEV_PASSWORD = 'Passw0rd!dev'   # development only, never use this anywhere real


class Command(BaseCommand):
    help = 'Fill the database with sample data for development (safe to run more than once).'

    @transaction.atomic
    def handle(self, *args, **options):
        self.seed_users()
        self.seed_catalog()
        self.seed_shipping()
        self.seed_designer_lookups()
        self.seed_questions()
        self.seed_settings()
        self.stdout.write(self.style.SUCCESS('Seed data created.'))

    # ---------- users ----------
    def make_user(self, username, **extra):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@example.com', **extra},
        )
        if created:
            user.set_password(DEV_PASSWORD)   # hashes the password
            user.save()
        return user

    def seed_users(self):
        self.make_user('superadmin1', first_name='Super', last_name='One', role=User.Role.SUPER_ADMIN, is_staff=True, is_superuser=True)
        self.make_user('superadmin2', first_name='Super', last_name='Two', role=User.Role.SUPER_ADMIN, is_staff=True, is_superuser=True)
        self.make_user('admin1', first_name='Ordinary', last_name='Admin', role=User.Role.ADMIN, is_staff=True)
        self.make_user('customer1', first_name='Sara', last_name='Customer')
        self.make_user('customer2', first_name='Omar', last_name='Customer')

        self.designer = self.make_user(
            'designer1', first_name='Lina', last_name='Designer',
            designer_status=User.DesignerStatus.APPROVED,
            is_profile_published=True, is_verified=True,
            designer_intro='Interior designer focused on small apartments.',
            designer_services='Space planning, color and furniture advice.',
        )

    # ---------- catalog ----------
    def seed_catalog(self):
        living, _ = Category.objects.get_or_create(name='Living Room', parent=None)
        bedroom, _ = Category.objects.get_or_create(name='Bedroom', parent=None)
        sofas, _ = Category.objects.get_or_create(name='Sofas', parent=living)
        tables, _ = Category.objects.get_or_create(name='Coffee Tables', parent=living)
        beds, _ = Category.objects.get_or_create(name='Beds', parent=bedroom)

        colors = {}
        for name, hexa in [('Grey', '#808080'), ('Beige', '#F5F5DC'), ('Green', '#2E8B57'), ('Walnut', '#5C4033')]:
            colors[name], _ = Color.objects.get_or_create(name=name, defaults={'color_hexa': hexa})

        fabric, _ = Material.objects.get_or_create(name='Fabric')
        wood, _ = Material.objects.get_or_create(name='Wood')
        rect, _ = Shape.objects.get_or_create(name='Rectangular')
        round_, _ = Shape.objects.get_or_create(name='Round')

        sofa, _ = Product.objects.get_or_create(
            sku='SOF-001',
            defaults=dict(name='Oslo 3-Seater Sofa', description='Comfortable three-seater sofa.',
                          category=sofas, price=Decimal('899.00'), weight=Decimal('42.00'),
                          length=Decimal('210'), width=Decimal('90'), height=Decimal('85'),
                          material=fabric, shape=rect, has_variants=True,
                          status=Product.Status.PUBLISHED),
        )
        for sku, color, stock in [('SOF-001-GRY', 'Grey', 5), ('SOF-001-BGE', 'Beige', 3), ('SOF-001-GRN', 'Green', 0)]:
            ProductVariant.objects.get_or_create(
                sku=sku,
                defaults=dict(product=sofa, price=Decimal('899.00'), stock_quantity=stock, color=colors[color], material=fabric),
            )

        Product.objects.get_or_create(
            sku='TAB-001',
            defaults=dict(name='Nordic Coffee Table', description='Solid wood coffee table.',
                          category=tables, price=Decimal('199.00'), sale_price=Decimal('169.00'),
                          weight=Decimal('12.50'), color=colors['Walnut'], material=wood,
                          shape=round_, stock_quantity=10, status=Product.Status.PUBLISHED),
        )
        Product.objects.get_or_create(
            sku='BED-001',
            defaults=dict(name='Atlas Queen Bed', description='Queen bed frame.',
                          category=beds, price=Decimal('649.00'), weight=Decimal('55.00'),
                          color=colors['Grey'], material=wood, shape=rect,
                          stock_quantity=4, status=Product.Status.PUBLISHED),
        )
        Product.objects.get_or_create(      # unpublished: must not appear in the catalog
            sku='DRAFT-001',
            defaults=dict(name='Draft Chair', category=living, price=Decimal('99.00'), weight=Decimal('6.00'), stock_quantity=2, status=Product.Status.DRAFT),
        )

    # ---------- shipping ----------
    def seed_shipping(self):
        zone, _ = ShippingZone.objects.get_or_create(name='Domestic')
        ShippingZoneDestination.objects.get_or_create(zone=zone, country='Egypt', province='')
        for lo, hi, fee in [(0, 5, 5), (5, 20, 12), (20, 60, 30)]:
            WeightBracket.objects.get_or_create(
                zone=zone, min_weight=Decimal(lo), max_weight=Decimal(hi),
                defaults={'fee': Decimal(fee)},
            )

    # ---------- designer lookups ----------
    def seed_designer_lookups(self):
        specs = [Specialization.objects.get_or_create(name=n)[0]
                 for n in ['Residential', 'Commercial', 'Small spaces']]
        styles = [DesignStyle.objects.get_or_create(name=n)[0]
                  for n in ['Modern', 'Minimalist', 'Classic']]
        self.designer.specializations.add(specs[0], specs[2])
        self.designer.styles.add(styles[0], styles[1])

    # ---------- intake questions ----------
    def seed_questions(self):
        def question(order, text, qtype, options=()):
            q, created = Question.objects.get_or_create(
                text=text, defaults={'question_type': qtype, 'sort_order': order})
            if created:
                for i, opt in enumerate(options):
                    AnswerOption.objects.create(question=q, text=opt, sort_order=i)

        question(1, 'What type of project is this?', Question.QuestionType.SINGLE,
                 ['New build', 'Renovation', 'Single room refresh'])
        question(2, 'Which space is it for?', Question.QuestionType.SINGLE,
                 ['Living room', 'Bedroom', 'Kitchen', 'Office'])
        question(3, 'What is your budget range?', Question.QuestionType.SINGLE,
                 ['Under $500', '$500 - $2,000', 'Over $2,000'])
        question(4, 'Anything else the designer should know?', Question.QuestionType.TEXT)

    # ---------- settings ----------
    def seed_settings(self):
        for key, value in [('low_stock_threshold', '5'),
                           ('reservation_minutes', '15'),
                           ('commission_rate', '0.00'),   
                           ('minimum_payout', '50.00')]:
            SystemSetting.objects.get_or_create(setting_key=key, defaults={'setting_value': value})