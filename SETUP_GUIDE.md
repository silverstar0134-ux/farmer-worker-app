# Farmer-Worker Management System - Setup & Testing Guide

## Quick Start Guide

### Step 1: Environment Setup

1. **Navigate to project directory:**
```bash
cd c:\Users\silve\Desktop\my\farmer
```

2. **Activate virtual environment:**
```bash
# Windows
env\Scripts\activate

# macOS/Linux
source env/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Database Setup

1. **Create MySQL Database:**
```sql
CREATE DATABASE farmer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. **Update Database Credentials in `fish/settings.py`:**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'farmer',
        'USER': 'root',          # Your MySQL username
        'PASSWORD': 'root',      # Your MySQL password
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```

### Step 4: Run Migrations

```bash
python manage.py makemigrations members
python manage.py migrate
```

### Step 5: Create Superuser (Optional - for Django Admin)

```bash
python manage.py createsuperuser
```

### Step 6: Run Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000`

---

## Testing the System

### Test Scenario 1: Farmer Registration & Dashboard

1. **Visit:** http://localhost:8000/
2. **Click:** "Register as Farmer"
3. **Fill Details:**
   - Full Name: John Farmer
   - Email: john@example.com
   - Phone: 9876543210
   - Location: Punjab
   - Land Size: 50
   - Password: Test@123

4. **Actions:**
   - Click "Post New Work"
   - Fill in work details
   - View dashboard

### Test Scenario 2: Worker Registration & Job Application

1. **Logout and return home**
2. **Click:** "Register as Worker"
3. **Fill Details:**
   - Full Name: Ram Singh
   - Email: ram@example.com
   - Phone: 9876543211
   - Location: Punjab
   - Work Time: Morning
   - Skills: Plowing, Irrigation
   - Experience: 5 years

4. **Actions:**
   - View available works
   - Apply for work posted by farmer
   - Track applications

### Test Scenario 3: Farmer Assigning Work

1. **Login as Farmer**
2. **Go to:** Dashboard → Work Details
3. **Click:** "Assign Worker"
4. **Select:** Worker who applied
5. **Verify:** Work status changes to "In Progress"

### Test Scenario 4: Complete Work & Test Commission

1. **Farmer Dashboard → Work Details**
2. **Click:** "Update Status"
3. **Select:** "Completed"
4. **Verify:**
   - Payment record created
   - Commission calculated (5% of wage)
   - Worker record updated

### Test Scenario 5: Admin Dashboard

1. **Visit:** http://localhost:8000/admin/login/
2. **Login with:** admin / admin
3. **View:**
   - Total farmers, workers, works
   - Commission earned (5% total)
   - Payment history
   - User management options

---

## API Endpoints Summary

### Authentication Endpoints
| Method | URL | Purpose |
|--------|-----|---------|
| GET/POST | `/login/` | User login |
| GET/POST | `/register/farmer/` | Farmer registration |
| GET/POST | `/register/worker/` | Worker registration |
| GET | `/logout/` | Logout user |

### Farmer Endpoints
| Method | URL | Purpose |
|--------|-----|---------|
| GET | `/farmer/dashboard/` | View farmer dashboard |
| GET/POST | `/farmer/post-work/` | Create new work |
| GET | `/farmer/work/<id>/` | View work details |
| GET/POST | `/farmer/work/<id>/assign/` | Assign work to worker |
| GET/POST | `/farmer/work/<id>/update-status/` | Update work status |
| GET | `/farmer/payments/` | View payment history |

### Worker Endpoints
| Method | URL | Purpose |
|--------|-----|---------|
| GET | `/worker/dashboard/` | View worker dashboard |
| GET | `/worker/available-works/` | Browse available work |
| POST | `/worker/apply/<id>/` | Apply for work |
| GET | `/worker/applications/` | View applications |
| GET | `/worker/assigned-works/` | View assigned works |
| GET/POST | `/worker/work/<id>/accept/` | Accept assigned work |
| GET | `/worker/payments/` | View earnings |

### Admin Endpoints
| Method | URL | Purpose |
|--------|-----|---------|
| GET/POST | `/admin/login/` | Admin login |
| GET | `/admin/dashboard/` | View admin dashboard |
| GET/POST | `/admin/users/` | Manage users |
| GET | `/admin/works/` | View all works |
| GET | `/admin/payments/` | View payments & commission |

---

## Commission Calculation Test

### Expected Behavior:

**Example Work Payment:**
- Work Wage: ₹1000
- Worker Share (95%): ₹950
- Admin Commission (5%): ₹50

**Verification Steps:**
1. Create work with wage ₹1000
2. Worker applies and farmer assigns
3. Farmer marks work as completed
4. Check payment record:
   - Total: ₹1000
   - Worker gets: ₹950
   - Admin receives: ₹50
5. Admin dashboard shows commission earned

---

## Troubleshooting

### Issue: "No module named 'mysql'"
**Solution:**
```bash
pip install mysqlclient
```

### Issue: "MySQL connection refused"
**Solution:**
```bash
# Start MySQL service (Windows)
net start MySQL80

# Or check MySQL is running
mysql -u root -p
```

### Issue: Migrations error
**Solution:**
```bash
python manage.py makemigrations members
python manage.py migrate --run-syncdb
```

### Issue: Static files not loading
**Solution:**
```bash
python manage.py collectstatic
```

### Issue: CSRF validation failed
**Solution:**
- Ensure `{% csrf_token %}` is in all POST forms
- Check CSRF middleware is enabled in settings

---

## Demo Data Creation Script

Create file: `generate_demo_data.py`

```python
from members.models import Userregister, FarmerProfile, WorkerProfile, Work
from django.contrib.auth.hashers import make_password
from datetime import date, timedelta

# Create demo farmers
farmer1 = Userregister.objects.create(
    username="Demo Farmer 1",
    phonenumber="9999000001",
    current_password=make_password("test123"),
    role="farmer",
    location="Punjab"
)
FarmerProfile.objects.create(user=farmer1, land_size=50)

# Create demo workers
worker1 = Userregister.objects.create(
    username="Demo Worker 1",
    phonenumber="9999000002",
    current_password=make_password("test123"),
    role="worker",
    location="Punjab",
    work_time="morning"
)
WorkerProfile.objects.create(
    user=worker1,
    skills="Plowing, Irrigation",
    experience_years=5
)

# Create demo work
Work.objects.create(
    farmer=farmer1,
    title="Wheat Field Plowing",
    description="Need help plowing 2 acres",
    location="Punjab",
    required_workers=2,
    wage_amount=500,
    wage_type="per_day",
    start_date=date.today(),
    end_date=date.today() + timedelta(days=5),
    contact_phone="9999000001"
)

print("Demo data created successfully!")
```

**Run:**
```bash
python manage.py shell < generate_demo_data.py
```

---

## Security Checklist

- [ ] Change DEFAULT admin credentials in production
- [ ] Update SECRET_KEY in settings.py
- [ ] Set DEBUG = False in production
- [ ] Configure ALLOWED_HOSTS
- [ ] Use environment variables for sensitive data
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Regular database backups
- [ ] Input validation on all forms
- [ ] SQL injection prevention (Django ORM handles this)
- [ ] XSS protection (Django templates handle this)
- [ ] Password strength requirements

---

## Performance Optimization Tips

1. **Database Indexing:**
   - Indexes on phonenumber, role, status fields
   - Foreign key indexes are automatic

2. **Query Optimization:**
   - Use `select_related()` for ForeignKey
   - Use `prefetch_related()` for reverse relations

3. **Caching:**
   - Cache dashboard statistics
   - Cache user profile data

4. **Static Files:**
   - Serve via CDN in production
   - Minify CSS/JS

---

## Deployment Checklist

- [ ] Run full test suite
- [ ] Update requirements.txt
- [ ] Set environment variables
- [ ] Configure database backups
- [ ] Setup logging
- [ ] Configure email settings
- [ ] Test payment workflow
- [ ] Complete user documentation
- [ ] Create admin documentation
- [ ] Setup monitoring

---

## File Structure Reference

```
farmer/
├── manage.py
├── requirements.txt
├── README.md
├── SETUP_GUIDE.md
├── db.sqlite3
│
├── fish/                          # Main project
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── members/                       # Main app
│   ├── migrations/
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── farmer_register.html
│   │   ├── worker_register.html
│   │   ├── login.html
│   │   ├── farmer_dashboard.html
│   │   ├── post_work.html
│   │   ├── work_details.html
│   │   ├── assign_work.html
│   │   ├── update_work_status.html
│   │   ├── farmer_payments.html
│   │   ├── worker_dashboard.html
│   │   ├── available_works.html
│   │   ├── worker_applications.html
│   │   ├── worker_assigned_works.html
│   │   ├── worker_payments.html
│   │   ├── user_profile.html
│   │   ├── admin_login.html
│   │   ├── admin_dashboard.html
│   │   ├── admin_user_management.html
│   │   ├── admin_all_works.html
│   │   └── admin_all_payments.html
│   │
│   ├── __init__.py
│   ├── admin.py                  # Admin configuration
│   ├── apps.py
│   ├── models.py                 # Database models
│   ├── views.py                  # Business logic
│   ├── forms.py                  # Form validation
│   ├── urls.py                   # URL routing
│   └── tests.py
│
└── env/                           # Virtual environment
    ├── Scripts/
    ├── Lib/
    └── Include/
```

---

## Contact & Support

For questions or issues, refer to:
- Django Documentation: https://docs.djangoproject.com/
- Django Rest Framework: https://www.django-rest-framework.org/
- MySQL Documentation: https://dev.mysql.com/doc/

---

**Last Updated:** February 2024
**Version:** 1.0
**Status:** Production Ready
