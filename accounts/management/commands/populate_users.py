from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import date

from accounts.models import UserProfile, Address

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate user profiles and addresses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing user data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing user data...')
            self.clear_data()

        self.stdout.write('Creating user profiles and addresses...')
        
        with transaction.atomic():
            # Get existing users
            users = User.objects.filter(is_superuser=False)
            
            if not users.exists():
                self.stdout.write('No users found. Please run populate_db first.')
                return
            
            # Create user profiles
            self.create_user_profiles(users)
            
            # Create addresses
            self.create_addresses(users)

        self.stdout.write(
            self.style.SUCCESS('Successfully populated user profiles and addresses!')
        )

    def clear_data(self):
        """Clear existing user data"""
        Address.objects.all().delete()
        UserProfile.objects.all().delete()

    def create_user_profiles(self, users):
        """Create user profiles for existing users"""
        profile_data = [
            {
                'phone': '+1-555-0101',
                'date_of_birth': date(1990, 5, 15),
                'gender': 'male',
                'bio': 'Love collecting vintage jewelry and unique pieces.',
                'newsletter_subscription': True,
                'sms_notifications': False,
                'email_notifications': True,
                'website': 'https://jewelrycollector.com',
                'instagram': '@jewelry_lover',
                'facebook': 'john.doe.jewelry'
            },
            {
                'phone': '+1-555-0102',
                'date_of_birth': date(1988, 8, 22),
                'gender': 'female',
                'bio': 'Fashion enthusiast with a passion for elegant jewelry.',
                'newsletter_subscription': True,
                'sms_notifications': True,
                'email_notifications': True,
                'website': '',
                'instagram': '@fashion_jane',
                'facebook': 'jane.smith.fashion'
            },
            {
                'phone': '+1-555-0103',
                'date_of_birth': date(1992, 3, 10),
                'gender': 'male',
                'bio': 'Professional who appreciates quality craftsmanship.',
                'newsletter_subscription': False,
                'sms_notifications': False,
                'email_notifications': True,
                'website': '',
                'instagram': '@mike_wilson',
                'facebook': 'mike.wilson.pro'
            },
            {
                'phone': '+1-555-0104',
                'date_of_birth': date(1985, 12, 5),
                'gender': 'female',
                'bio': 'Jewelry designer and collector of rare gemstones.',
                'newsletter_subscription': True,
                'sms_notifications': True,
                'email_notifications': True,
                'website': 'https://sarahjewelrydesign.com',
                'instagram': '@sarah_jewelry_design',
                'facebook': 'sarah.jones.designer'
            },
            {
                'phone': '+1-555-0105',
                'date_of_birth': date(1995, 7, 18),
                'gender': 'male',
                'bio': 'Young professional starting my jewelry collection.',
                'newsletter_subscription': True,
                'sms_notifications': False,
                'email_notifications': True,
                'website': '',
                'instagram': '@david_brown',
                'facebook': 'david.brown.young'
            }
        ]

        for i, user in enumerate(users):
            if i < len(profile_data):
                UserProfile.objects.create(
                    user=user,
                    **profile_data[i]
                )

        self.stdout.write(f'Created profiles for {len(users)} users')

    def create_addresses(self, users):
        """Create addresses for users"""
        address_data = [
            {
                'address_type': 'home',
                'first_name': 'John',
                'last_name': 'Doe',
                'company': '',
                'address_line_1': '123 Main Street',
                'address_line_2': 'Apt 4B',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'United States',
                'phone': '+1-555-0101',
                'is_default': True,
                'is_billing': True,
                'is_shipping': True
            },
            {
                'address_type': 'work',
                'first_name': 'John',
                'last_name': 'Doe',
                'company': 'Tech Corp',
                'address_line_1': '456 Business Ave',
                'address_line_2': 'Suite 200',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10002',
                'country': 'United States',
                'phone': '+1-555-0101',
                'is_default': False,
                'is_billing': False,
                'is_shipping': False
            },
            {
                'address_type': 'home',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'company': '',
                'address_line_1': '789 Oak Lane',
                'address_line_2': '',
                'city': 'Los Angeles',
                'state': 'CA',
                'postal_code': '90210',
                'country': 'United States',
                'phone': '+1-555-0102',
                'is_default': True,
                'is_billing': True,
                'is_shipping': True
            },
            {
                'address_type': 'home',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'company': '',
                'address_line_1': '321 Pine Street',
                'address_line_2': 'Unit 12',
                'city': 'Chicago',
                'state': 'IL',
                'postal_code': '60601',
                'country': 'United States',
                'phone': '+1-555-0103',
                'is_default': True,
                'is_billing': True,
                'is_shipping': True
            },
            {
                'address_type': 'home',
                'first_name': 'Sarah',
                'last_name': 'Jones',
                'company': '',
                'address_line_1': '654 Maple Drive',
                'address_line_2': '',
                'city': 'Miami',
                'state': 'FL',
                'postal_code': '33101',
                'country': 'United States',
                'phone': '+1-555-0104',
                'is_default': True,
                'is_billing': True,
                'is_shipping': True
            },
            {
                'address_type': 'home',
                'first_name': 'David',
                'last_name': 'Brown',
                'company': '',
                'address_line_1': '987 Cedar Court',
                'address_line_2': 'Apt 7C',
                'city': 'Seattle',
                'state': 'WA',
                'postal_code': '98101',
                'country': 'United States',
                'phone': '+1-555-0105',
                'is_default': True,
                'is_billing': True,
                'is_shipping': True
            }
        ]

        for i, user in enumerate(users):
            if i < len(address_data):
                Address.objects.create(
                    user=user,
                    **address_data[i]
                )

        self.stdout.write(f'Created addresses for {len(users)} users')
