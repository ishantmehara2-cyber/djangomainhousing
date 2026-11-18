from django.core.management.base import BaseCommand
from apps.accounts.models import User, RoleChoices, UserStatusChoices

class Command(BaseCommand):
    help = 'Create or update default admin user account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin')
        parser.add_argument('--email', type=str, default='admin@thehomefirst.com')
        parser.add_argument('--password', type=str, default='Admin@12345')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'role': RoleChoices.ADMIN,
                'status': UserStatusChoices.ACTIVE,
                'is_staff': True,
                'is_superuser': True,
                'email_verified': True,
                'phone_verified': True,
            }
        )

        user.email = email
        user.role = RoleChoices.ADMIN
        user.status = UserStatusChoices.ACTIVE
        user.is_staff = True
        user.is_superuser = True
        user.email_verified = True
        user.phone_verified = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(
            f"✅ Successfully {action} Admin Account!\n"
            f"   Username: {username}\n"
            f"   Email: {email}\n"
            f"   Password: {password}\n"
            f"   Role: ADMIN (is_staff=True, is_superuser=True)\n"
            f"   URLs: /admin-panel/ (Custom Admin) | /admin/ (Django System Admin)"
        ))
