from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
import random
from datetime import datetime, timedelta

from product.models import (
    Category, Product, ProductImage, Review, Material, Gemstone, 
    ProductGemstone, Cart, CartItem, Wishlist, WishlistItem, RecommendedProduct
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with sample jewelry data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Creating sample data...')
        
        with transaction.atomic():
            # Create categories
            categories = self.create_categories()
            
            # Create materials
            materials = self.create_materials()
            
            # Create gemstones
            gemstones = self.create_gemstones()
            
            # Create users
            users = self.create_users()
            
            # Create products
            products = self.create_products(categories, materials, gemstones)
            
            # Create product images
            self.create_product_images(products)
            
            # Create product-gemstone relationships
            self.create_product_gemstones(products, gemstones)
            
            # Create reviews
            self.create_reviews(products, users)
            
            # Create recommendations
            self.create_recommendations(products)
            
            # Create carts and wishlists
            self.create_carts_and_wishlists(users, products)

        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )

    def clear_data(self):
        """Clear existing data"""
        RecommendedProduct.objects.all().delete()
        Review.objects.all().delete()
        ProductGemstone.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        WishlistItem.objects.all().delete()
        Wishlist.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        Gemstone.objects.all().delete()
        Material.objects.all().delete()
        Category.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_categories(self):
        """Create jewelry categories"""
        categories_data = [
            {
                'name': 'Rings',
                'description': 'Beautiful rings for every occasion',
                'parent': None
            },
            {
                'name': 'Necklaces',
                'description': 'Elegant necklaces and chains',
                'parent': None
            },
            {
                'name': 'Earrings',
                'description': 'Stunning earrings to complete your look',
                'parent': None
            },
            {
                'name': 'Bracelets',
                'description': 'Charming bracelets and bangles',
                'parent': None
            },
            {
                'name': 'Engagement Rings',
                'description': 'Special engagement rings',
                'parent': 'Rings'
            },
            {
                'name': 'Wedding Rings',
                'description': 'Classic wedding bands',
                'parent': 'Rings'
            },
            {
                'name': 'Pendants',
                'description': 'Beautiful pendants and charms',
                'parent': 'Necklaces'
            },
            {
                'name': 'Stud Earrings',
                'description': 'Classic stud earrings',
                'parent': 'Earrings'
            },
            {
                'name': 'Drop Earrings',
                'description': 'Elegant drop earrings',
                'parent': 'Earrings'
            }
        ]

        categories = {}
        for cat_data in categories_data:
            parent = None
            if cat_data['parent']:
                parent = categories[cat_data['parent']]
            
            category = Category.objects.create(
                name=cat_data['name'],
                description=cat_data['description'],
                parent=parent
            )
            categories[cat_data['name']] = category

        self.stdout.write(f'Created {len(categories)} categories')
        return categories

    def create_materials(self):
        """Create jewelry materials"""
        materials_data = [
            {'name': 'Gold', 'description': 'Classic gold material', 'is_precious': True},
            {'name': 'Silver', 'description': 'Elegant silver material', 'is_precious': True},
            {'name': 'Platinum', 'description': 'Premium platinum material', 'is_precious': True},
            {'name': 'Rose Gold', 'description': 'Romantic rose gold material', 'is_precious': True},
            {'name': 'White Gold', 'description': 'Modern white gold material', 'is_precious': True},
            {'name': 'Sterling Silver', 'description': 'High-quality sterling silver', 'is_precious': True},
            {'name': 'Brass', 'description': 'Durable brass material', 'is_precious': False},
            {'name': 'Copper', 'description': 'Warm copper material', 'is_precious': False},
        ]

        materials = {}
        for mat_data in materials_data:
            material = Material.objects.create(**mat_data)
            materials[mat_data['name']] = material

        self.stdout.write(f'Created {len(materials)} materials')
        return materials

    def create_gemstones(self):
        """Create gemstones"""
        gemstones_data = [
            {'name': 'Diamond', 'color': 'White', 'hardness': Decimal('10.0'), 'description': 'The hardest gemstone'},
            {'name': 'Ruby', 'color': 'Red', 'hardness': Decimal('9.0'), 'description': 'Beautiful red gemstone'},
            {'name': 'Sapphire', 'color': 'Blue', 'hardness': Decimal('9.0'), 'description': 'Stunning blue gemstone'},
            {'name': 'Emerald', 'color': 'Green', 'hardness': Decimal('7.5'), 'description': 'Vibrant green gemstone'},
            {'name': 'Amethyst', 'color': 'Purple', 'hardness': Decimal('7.0'), 'description': 'Royal purple gemstone'},
            {'name': 'Topaz', 'color': 'Blue', 'hardness': Decimal('8.0'), 'description': 'Clear blue gemstone'},
            {'name': 'Citrine', 'color': 'Yellow', 'hardness': Decimal('7.0'), 'description': 'Warm yellow gemstone'},
            {'name': 'Garnet', 'color': 'Red', 'hardness': Decimal('7.5'), 'description': 'Deep red gemstone'},
            {'name': 'Pearl', 'color': 'White', 'hardness': Decimal('2.5'), 'description': 'Classic pearl'},
            {'name': 'Opal', 'color': 'Multi', 'hardness': Decimal('5.5'), 'description': 'Iridescent opal'},
        ]

        gemstones = {}
        for gem_data in gemstones_data:
            gemstone = Gemstone.objects.create(**gem_data)
            gemstones[gem_data['name']] = gemstone

        self.stdout.write(f'Created {len(gemstones)} gemstones')
        return gemstones

    def create_users(self):
        """Create sample users"""
        users_data = [
            {
                'loginname': 'john_doe',
                'email': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'status': 1
            },
            {
                'loginname': 'jane_smith',
                'email': 'jane@example.com',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'status': 1
            },
            {
                'loginname': 'mike_wilson',
                'email': 'mike@example.com',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'status': 1
            },
            {
                'loginname': 'sarah_jones',
                'email': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Jones',
                'status': 1
            },
            {
                'loginname': 'david_brown',
                'email': 'david@example.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'status': 1
            }
        ]

        users = []
        for user_data in users_data:
            # Create user with loginname as the username field
            user = User.objects.create_user(
                loginname=user_data['loginname'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password='password123',
                status=user_data['status']
            )
            users.append(user)

        self.stdout.write(f'Created {len(users)} users')
        return users

    def create_products(self, categories, materials, gemstones):
        """Create sample products"""
        products_data = [
            {
                'title': 'Classic Gold Wedding Ring',
                'description': 'A timeless gold wedding ring perfect for your special day.',
                'studio_notes': 'Handcrafted with attention to detail.',
                'category': 'Wedding Rings',
                'jewelry_type': 'ring',
                'price': Decimal('299.99'),
                'cost_price': Decimal('150.00'),
                'markup_percentage': Decimal('100.00'),
                'stock_quantity': 25,
                'weight': Decimal('3.5'),
                'dimensions': '6mm x 2mm',
                'primary_material': 'Gold',
                'secondary_materials': ['Rose Gold'],
                'is_featured': True,
                'is_customizable': True,
                'care_instructions': 'Clean with soft cloth and store separately.'
            },
            {
                'title': 'Diamond Engagement Ring',
                'description': 'Stunning diamond engagement ring with brilliant cut center stone.',
                'studio_notes': 'Premium quality diamond with excellent cut.',
                'category': 'Engagement Rings',
                'jewelry_type': 'ring',
                'price': Decimal('1299.99'),
                'cost_price': Decimal('800.00'),
                'markup_percentage': Decimal('62.50'),
                'stock_quantity': 10,
                'weight': Decimal('2.8'),
                'dimensions': '8mm x 6mm',
                'primary_material': 'White Gold',
                'secondary_materials': ['Gold'],
                'is_featured': True,
                'is_customizable': True,
                'care_instructions': 'Professional cleaning recommended.'
            },
            {
                'title': 'Pearl Drop Earrings',
                'description': 'Elegant pearl drop earrings perfect for formal occasions.',
                'studio_notes': 'Freshwater pearls with sterling silver findings.',
                'category': 'Drop Earrings',
                'jewelry_type': 'earring',
                'price': Decimal('89.99'),
                'cost_price': Decimal('45.00'),
                'markup_percentage': Decimal('100.00'),
                'stock_quantity': 30,
                'weight': Decimal('4.2'),
                'dimensions': '15mm x 8mm',
                'primary_material': 'Sterling Silver',
                'secondary_materials': [],
                'is_featured': False,
                'is_customizable': False,
                'care_instructions': 'Avoid contact with perfumes and lotions.'
            },
            {
                'title': 'Ruby Heart Pendant',
                'description': 'Beautiful ruby heart pendant on a delicate chain.',
                'studio_notes': 'Natural ruby with excellent color and clarity.',
                'category': 'Pendants',
                'jewelry_type': 'pendant',
                'price': Decimal('199.99'),
                'cost_price': Decimal('120.00'),
                'markup_percentage': Decimal('66.67'),
                'stock_quantity': 15,
                'weight': Decimal('2.1'),
                'dimensions': '12mm x 10mm',
                'primary_material': 'Gold',
                'secondary_materials': ['Rose Gold'],
                'is_featured': True,
                'is_customizable': True,
                'care_instructions': 'Store in soft pouch to prevent scratching.'
            },
            {
                'title': 'Sapphire Tennis Bracelet',
                'description': 'Stunning sapphire tennis bracelet with matching stones.',
                'studio_notes': 'Consistent sapphire quality throughout the bracelet.',
                'category': 'Bracelets',
                'jewelry_type': 'bracelet',
                'price': Decimal('899.99'),
                'cost_price': Decimal('500.00'),
                'markup_percentage': Decimal('80.00'),
                'stock_quantity': 8,
                'weight': Decimal('12.5'),
                'dimensions': '18cm length',
                'primary_material': 'Platinum',
                'secondary_materials': ['White Gold'],
                'is_featured': True,
                'is_customizable': False,
                'care_instructions': 'Professional cleaning and inspection recommended.'
            },
            {
                'title': 'Emerald Stud Earrings',
                'description': 'Classic emerald stud earrings in elegant settings.',
                'studio_notes': 'Natural emeralds with excellent color saturation.',
                'category': 'Stud Earrings',
                'jewelry_type': 'earring',
                'price': Decimal('149.99'),
                'cost_price': Decimal('90.00'),
                'markup_percentage': Decimal('66.67'),
                'stock_quantity': 20,
                'weight': Decimal('1.8'),
                'dimensions': '6mm diameter',
                'primary_material': 'Gold',
                'secondary_materials': [],
                'is_featured': False,
                'is_customizable': True,
                'care_instructions': 'Handle with care, emeralds can be fragile.'
            },
            {
                'title': 'Opal Statement Necklace',
                'description': 'Bold opal statement necklace with multiple stones.',
                'studio_notes': 'Australian opals with unique play of color.',
                'category': 'Necklaces',
                'jewelry_type': 'necklace',
                'price': Decimal('399.99'),
                'cost_price': Decimal('250.00'),
                'markup_percentage': Decimal('60.00'),
                'stock_quantity': 5,
                'weight': Decimal('18.3'),
                'dimensions': '45cm length',
                'primary_material': 'Silver',
                'secondary_materials': ['Sterling Silver'],
                'is_featured': True,
                'is_customizable': False,
                'care_instructions': 'Avoid extreme temperatures and store carefully.'
            },
            {
                'title': 'Garnet Cocktail Ring',
                'description': 'Eye-catching garnet cocktail ring for special occasions.',
                'studio_notes': 'Deep red garnet with excellent clarity.',
                'category': 'Rings',
                'jewelry_type': 'ring',
                'price': Decimal('179.99'),
                'cost_price': Decimal('110.00'),
                'markup_percentage': Decimal('63.64'),
                'stock_quantity': 12,
                'weight': Decimal('4.7'),
                'dimensions': '10mm x 8mm',
                'primary_material': 'Rose Gold',
                'secondary_materials': ['Gold'],
                'is_featured': False,
                'is_customizable': True,
                'care_instructions': 'Clean with warm soapy water and soft brush.'
            }
        ]

        products = []
        for prod_data in products_data:
            secondary_materials = []
            if prod_data['secondary_materials']:
                secondary_materials = [materials[name] for name in prod_data['secondary_materials']]

            product = Product.objects.create(
                title=prod_data['title'],
                description=prod_data['description'],
                studio_notes=prod_data['studio_notes'],
                category=categories[prod_data['category']],
                jewelry_type=prod_data['jewelry_type'],
                price=prod_data['price'],
                cost_price=prod_data['cost_price'],
                markup_percentage=prod_data['markup_percentage'],
                stock_quantity=prod_data['stock_quantity'],
                weight=prod_data['weight'],
                dimensions=prod_data['dimensions'],
                primary_material=materials[prod_data['primary_material']],
                is_featured=prod_data['is_featured'],
                is_customizable=prod_data['is_customizable'],
                care_instructions=prod_data['care_instructions']
            )
            
            # Add secondary materials
            if secondary_materials:
                product.secondary_materials.set(secondary_materials)
            
            products.append(product)

        self.stdout.write(f'Created {len(products)} products')
        return products

    def create_product_images(self, products):
        """Create placeholder product images"""
        for product in products:
            # Create main image
            ProductImage.objects.create(
                product=product,
                image='products/placeholder.jpg',  # You'll need to add actual images
                alt_text=f'{product.title} - Main Image',
                is_main=True,
                order=1
            )
            
            # Create additional images
            for i in range(2, 4):
                ProductImage.objects.create(
                    product=product,
                    image=f'products/placeholder_{i}.jpg',
                    alt_text=f'{product.title} - Image {i}',
                    is_main=False,
                    order=i
                )

        self.stdout.write(f'Created product images for {len(products)} products')

    def create_product_gemstones(self, products, gemstones):
        """Create product-gemstone relationships"""
        gemstone_assignments = [
            ('Diamond Engagement Ring', 'Diamond', Decimal('0.5'), 'Brilliant', 'VS1', 'D'),
            ('Ruby Heart Pendant', 'Ruby', Decimal('0.3'), 'Oval', 'VS2', 'Red'),
            ('Sapphire Tennis Bracelet', 'Sapphire', Decimal('0.2'), 'Round', 'VS1', 'Blue'),
            ('Emerald Stud Earrings', 'Emerald', Decimal('0.15'), 'Round', 'VS2', 'Green'),
            ('Pearl Drop Earrings', 'Pearl', Decimal('0.0'), 'Round', 'AAA', 'White'),
            ('Opal Statement Necklace', 'Opal', Decimal('0.8'), 'Cabochon', 'AAA', 'Multi'),
            ('Garnet Cocktail Ring', 'Garnet', Decimal('0.4'), 'Oval', 'VS1', 'Red'),
        ]

        for product_title, gemstone_name, carat_weight, cut, clarity, color_grade in gemstone_assignments:
            product = next((p for p in products if p.title == product_title), None)
            gemstone = gemstones.get(gemstone_name)
            
            if product and gemstone:
                ProductGemstone.objects.create(
                    product=product,
                    gemstone=gemstone,
                    carat_weight=carat_weight,
                    cut=cut,
                    clarity=clarity,
                    color_grade=color_grade,
                    quantity=1
                )

        self.stdout.write('Created product-gemstone relationships')

    def create_reviews(self, products, users):
        """Create sample reviews"""
        review_data = [
            ('Classic Gold Wedding Ring', 'john_doe', 5, 'Perfect ring for our wedding!'),
            ('Diamond Engagement Ring', 'jane_smith', 5, 'She said yes! Beautiful ring.'),
            ('Pearl Drop Earrings', 'mike_wilson', 4, 'Great quality pearls, very elegant.'),
            ('Ruby Heart Pendant', 'sarah_jones', 5, 'Love this pendant, gets lots of compliments.'),
            ('Sapphire Tennis Bracelet', 'david_brown', 5, 'Stunning bracelet, excellent craftsmanship.'),
            ('Emerald Stud Earrings', 'john_doe', 4, 'Beautiful emeralds, perfect for everyday wear.'),
            ('Opal Statement Necklace', 'jane_smith', 5, 'Unique piece, the opals are mesmerizing.'),
            ('Garnet Cocktail Ring', 'mike_wilson', 4, 'Great statement piece for special occasions.'),
        ]

        for product_title, username, rating, comment in review_data:
            product = next((p for p in products if p.title == product_title), None)
            user = next((u for u in users if u.loginname == username), None)
            
            if product and user:
                Review.objects.create(
                    product=product,
                    user=user,
                    rating=rating,
                    comment=comment,
                    status=1  # Approved
                )

        self.stdout.write('Created product reviews')

    def create_recommendations(self, products):
        """Create product recommendations"""
        recommendations = [
            ('Classic Gold Wedding Ring', 'Diamond Engagement Ring', 'Perfect pair for couples'),
            ('Diamond Engagement Ring', 'Classic Gold Wedding Ring', 'Complete the set'),
            ('Pearl Drop Earrings', 'Ruby Heart Pendant', 'Elegant combination'),
            ('Sapphire Tennis Bracelet', 'Emerald Stud Earrings', 'Blue and green harmony'),
            ('Opal Statement Necklace', 'Garnet Cocktail Ring', 'Bold statement pieces'),
        ]

        for product_title, recommended_title, reason in recommendations:
            product = next((p for p in products if p.title == product_title), None)
            recommended = next((p for p in products if p.title == recommended_title), None)
            
            if product and recommended:
                RecommendedProduct.objects.create(
                    product=product,
                    recommended=recommended,
                    reason=reason
                )

        self.stdout.write('Created product recommendations')

    def create_carts_and_wishlists(self, users, products):
        """Create sample carts and wishlists"""
        for user in users:
            # Create cart
            cart, created = Cart.objects.get_or_create(user=user)
            
            # Add random items to cart
            cart_products = random.sample(products, random.randint(1, 3))
            for product in cart_products:
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=random.randint(1, 2)
                )
            
            # Create wishlist
            wishlist, created = Wishlist.objects.get_or_create(user=user)
            
            # Add random items to wishlist
            wishlist_products = random.sample(products, random.randint(1, 4))
            for product in wishlist_products:
                WishlistItem.objects.create(
                    wishlist=wishlist,
                    product=product
                )

        self.stdout.write('Created carts and wishlists')
