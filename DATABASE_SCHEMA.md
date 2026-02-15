# Database Schema Reference Guide

## Complete Field Reference

### 1. Userregister Model (Custom User)
```
Field Name          | Type              | Properties
--------------------|------------------|---------------------------
id                  | AutoField         | Primary Key (auto)
username            | CharField(100)    | User's full name
email               | EmailField        | Unique, nullable
phonenumber         | CharField(15)     | Unique (login credential)
current_password    | CharField(100)    | Hashed password
role                | CharField(10)     | Choice: farmer, worker
work_time           | CharField(10)     | Choice: morning, evening
location            | CharField(100)    | City/District
is_active           | BooleanField      | Default: True
is_blocked          | BooleanField      | Default: False
created_at          | DateTimeField     | Auto-set on creation
updated_at          | DateTimeField     | Auto-update
```

### 2. FarmerProfile Model
```
Field Name              | Type              | Properties
------------------------|------------------|---------------------------
id                      | AutoField         | Primary Key
user                    | OneToOneField     | FK to Userregister
land_size               | DecimalField      | Acres (max 10,2)
total_works_posted      | PositiveInteger   | Counter (default 0)
total_workers_hired     | PositiveInteger   | Counter (default 0)
rating                  | DecimalField      | 0-5 stars (3,2)
created_at              | DateTimeField     | Auto-set
```

### 3. WorkerProfile Model
```
Field Name              | Type              | Properties
------------------------|------------------|---------------------------
id                      | AutoField         | Primary Key
user                    | OneToOneField     | FK to Userregister
skills                  | TextField         | Comma-separated
experience_years        | PositiveInteger   | Years worked
total_works_completed   | PositiveInteger   | Counter (default 0)
total_earnings          | DecimalField      | Total earned (12,2)
rating                  | DecimalField      | 0-5 stars (3,2)
created_at              | DateTimeField     | Auto-set
```

### 4. Work Model (Job Posting)
```
Field Name              | Type              | Properties
------------------------|------------------|---------------------------
id                      | AutoField         | Primary Key
farmer                  | ForeignKey        | References Userregister
title                   | CharField(200)    | Work title
description             | TextField         | Detailed description
location                | CharField(100)    | Work location
required_workers        | PositiveInteger   | Number needed
wage_amount             | DecimalField      | Amount (10,2)
wage_type               | CharField(20)     | Choice: per_day, total
start_date              | DateField         | Start date
end_date                | DateField         | End date (nullable)
status                  | CharField(20)     | pending/in_progress/completed/cancelled
assigned_worker         | ForeignKey        | References Userregister (nullable)
contact_phone           | CharField(15)     | Farmer contact
created_at              | DateTimeField     | Auto-set
updated_at              | DateTimeField     | Auto-update
```

### 5. WorkApplication Model
```
Field Name              | Type              | Properties
------------------------|------------------|---------------------------
id                      | AutoField         | Primary Key
work                    | ForeignKey        | References Work
worker                  | ForeignKey        | References Userregister
status                  | CharField(15)     | applied/accepted/rejected/completed
applied_at              | DateTimeField     | Auto-set
accepted_at             | DateTimeField     | Set when accepted, nullable
Unique Together         | (work, worker)    | Prevents duplicate applications
```

### 6. Payment Model
```
Field Name              | Type              | Properties
------------------------|------------------|---------------------------
id                      | AutoField         | Primary Key
work                    | OneToOneField     | References Work
worker                  | ForeignKey        | References Userregister (worker)
farmer                  | ForeignKey        | References Userregister (farmer)
total_amount            | DecimalField      | Total wage (12,2)
worker_share            | DecimalField      | 95% of total (12,2)
admin_commission        | DecimalField      | 5% of total (12,2)
status                  | CharField(15)     | pending/completed/paid
created_at              | DateTimeField     | Auto-set
completed_at            | DateTimeField     | Set when work completed
paid_at                 | DateTimeField     | Set when paid
```

### 7. Commission Model
```
Field Name              | Type              | Properties
------------------------|------------------|---------------------------
id                      | AutoField         | Primary Key
payment                 | OneToOneField     | References Payment
work                    | ForeignKey        | References Work
amount                  | DecimalField      | Commission amount (12,2)
status                  | CharField(15)     | earned/paid
created_at              | DateTimeField     | Auto-set
received_date           | DateTimeField     | When commission received
```

---

## Key Relationships

### User to Profile (1:1)
```
Userregister.role == 'farmer' → FarmerProfile (1:1)
Userregister.role == 'worker' → WorkerProfile (1:1)
```

### Farmer to Works (1:M)
```
Userregister (farmer) → Work (multiple posted works)
```

### Work to Applications (1:M)
```
Work → WorkApplication (multiple worker applications)
```

### Worker to Applications (1:M)
```
Userregister (worker) → WorkApplication (multiple applied works)
```

### Work to Payment (1:1)
```
Work → Payment (one payment record per completed work)
```

### Payment to Commission (1:1)
```
Payment → Commission (one commission record per payment)
```

---

## Sample Data Populations

### Creating a Farmer
```python
from members.models import Userregister, FarmerProfile
from django.contrib.auth.hashers import make_password

farmer = Userregister.objects.create(
    username="John Farmer",
    email="john@example.com",
    phonenumber="9876543210",
    current_password=make_password("SecurePass123"),
    role="farmer",
    location="Punjab",
    is_active=True,
    is_blocked=False
)

FarmerProfile.objects.create(
    user=farmer,
    land_size=50
)
```

### Creating a Worker
```python
worker = Userregister.objects.create(
    username="Ram Singh",
    email="ram@example.com",
    phonenumber="9876543211",
    current_password=make_password("SecurePass123"),
    role="worker",
    location="Punjab",
    work_time="morning",
    is_active=True,
    is_blocked=False
)

WorkerProfile.objects.create(
    user=worker,
    skills="Plowing, Irrigation, Planting",
    experience_years=5
)
```

### Creating a Work
```python
from datetime import date, timedelta

work = Work.objects.create(
    farmer=farmer,
    title="Wheat Field Plowing",
    description="Need to plow 2 acres for wheat season",
    location="Punjab",
    required_workers=2,
    wage_amount=1000,
    wage_type="per_day",
    start_date=date.today(),
    end_date=date.today() + timedelta(days=5),
    contact_phone="9876543210",
    status="pending"
)
```

### Creating Work Application
```python
app = WorkApplication.objects.create(
    work=work,
    worker=worker,
    status="applied"
)
```

### Assigning Work & Payment
```python
from datetime import datetime
from decimal import Decimal

# Assign work
work.assigned_worker = worker
work.status = "in_progress"
work.save()

# Accept application
app.status = "accepted"
app.accepted_at = datetime.now()
app.save()

# Mark as completed (generates payment & commission)
work.mark_completed()  # This handles everything automatically
```

---

## Query Examples

### Get all farms by a farmer
```python
farmer = Userregister.objects.get(id=1)
works = Work.objects.filter(farmer=farmer)
```

### Get all applications for a work
```python
work = Work.objects.get(id=1)
applications = work.applications.all()
```

### Get worker's total earnings
```python
worker = Userregister.objects.get(id=2)
total_earnings = Payment.objects.filter(
    worker=worker,
    status="completed"
).aggregate(Sum('worker_share'))['worker_share__sum']
```

### Get admin's total commission
```python
from django.db.models import Sum
total_commission = Commission.objects.filter(
    status="earned"
).aggregate(Sum('amount'))['amount__sum']
```

### Get completed works
```python
completed_works = Work.objects.filter(status="completed")
```

### Get available works in a location
```python
works = Work.objects.filter(
    location="Punjab",
    status__in=["pending", "in_progress"]
)
```

---

## Database Constraints & Rules

### Unique Constraints
- `Userregister.phonenumber` - Unique
- `Userregister.email` - Unique
- `WorkApplication` - Unique: (work, worker)

### Foreign Key Constraints
- `Work.farmer` - CASCADE delete
- `Work.assigned_worker` - SET NULL
- `WorkApplication.work` - CASCADE delete
- `WorkApplication.worker` - CASCADE delete
- `Payment.work` - CASCADE delete
- `Payment.worker` - CASCADE delete
- `Payment.farmer` - CASCADE delete
- `Commission.work` - CASCADE delete

### Default Values
- `is_active` = True
- `is_blocked` = False
- `status` = "pending" (for Work)
- `total_works_posted` = 0
- `total_works_completed` = 0
- `rating` = 0.00

---

## Indexed Fields

For better performance, consider indexing:
```python
# In models
class Meta:
    indexes = [
        models.Index(fields=['status']),
        models.Index(fields=['location']),
        models.Index(fields=['farmer']),
        models.Index(fields=['worker']),
        models.Index(fields=['created_at']),
    ]
```

---

## Payment Calculation Logic

```
Total Work Wage = 1000

When marked Complete:
  Worker Share (95%) = 1000 × 0.95 = 950
  Admin Commission (5%) = 1000 × 0.05 = 50
  
  Total = Worker Share + Admin Commission = 950 + 50 = 1000
```

---

## Database Migrations

```bash
# Create migrations
python manage.py makemigrations members

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations members

# Rollback migrations
python manage.py migrate members zero
```

---

## Data Export Query

```python
# Export farmer data
farmers = Userregister.objects.filter(role='farmer').values(
    'id', 'username', 'phonenumber', 'email', 'location',
    'farmer_profile__land_size'
)

# Export work data
works = Work.objects.values(
    'id', 'title', 'location', 'wage_amount', 'status',
    'farmer__username', 'assigned_worker__username'
)

# Export payment data
payments = Payment.objects.values(
    'id', 'work__title', 'worker__username', 'farmer__username',
    'total_amount', 'worker_share', 'admin_commission', 'status'
)
```

---

**Last Updated:** February 2024
**Database Type:** MySQL 5.7+
**ORM**: Django ORM
**Version**: 1.0
