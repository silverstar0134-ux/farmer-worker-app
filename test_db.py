import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fish.settings')
django.setup()

from members.models import Userregister

# Create a test farmer
farmer = Userregister.objects.create(
    username='test_farmer',
    email='farmer@test.com',
    phonenumber='9876543210',
    current_password='securepass123',
    role='farmer',
    location='Mumbai'
)

print(f"✓ Created farmer: {farmer.username}")
print(f"  Email: {farmer.email}")
print(f"  Role: {farmer.get_role_display()}")
print(f"  Created at: {farmer.created_at}")

# Create a test worker
worker = Userregister.objects.create(
    username='test_worker',
    email='worker@test.com',
    phonenumber='9876543211',
    current_password='securepass123',
    role='worker',
    work_time='morning',
    location='Pune'
)

print(f"\n✓ Created worker: {worker.username}")
print(f"  Email: {worker.email}")
print(f"  Role: {worker.get_role_display()}")
print(f"  Work time: {worker.work_time}")

print("\n✓ Database is working correctly!")
