from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import transaction


class Command(BaseCommand):
    help = 'Populate the entire database with sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        clear_flag = ['--clear'] if options['clear'] else []
        
        self.stdout.write('Starting database population...')
        
        with transaction.atomic():
            # Step 1: Populate products, categories, materials, gemstones, and basic users
            self.stdout.write('Step 1: Populating products and basic data...')
            call_command('populate_db', *clear_flag)
            
            # Step 2: Populate user profiles and addresses
            self.stdout.write('Step 2: Populating user profiles and addresses...')
            call_command('populate_users', *clear_flag)
            
            # Step 3: Populate orders, payments, and coupons
            self.stdout.write('Step 3: Populating orders, payments, and coupons...')
            call_command('populate_orders', *clear_flag)

        self.stdout.write(
            self.style.SUCCESS('Successfully populated entire database with sample data!')
        )
        
        self.stdout.write('\nSample data created:')
        self.stdout.write('• Categories: Rings, Necklaces, Earrings, Bracelets, etc.')
        self.stdout.write('• Materials: Gold, Silver, Platinum, Rose Gold, etc.')
        self.stdout.write('• Gemstones: Diamond, Ruby, Sapphire, Emerald, etc.')
        self.stdout.write('• Products: 8 sample jewelry items with images and details')
        self.stdout.write('• Users: 5 sample users with profiles and addresses')
        self.stdout.write('• Reviews: Product reviews from users')
        self.stdout.write('• Orders: Sample orders with different statuses')
        self.stdout.write('• Payments: Payment records for orders')
        self.stdout.write('• Coupons: Various discount coupons')
        self.stdout.write('• Carts & Wishlists: Sample shopping data')
        self.stdout.write('• Recommendations: Product recommendations')
