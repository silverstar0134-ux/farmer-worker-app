# Farmer-Worker Management System

A comprehensive Django-based web application for managing agricultural work, connecting farmers with workers, and automating payment processing with commission calculation.

## Features

### For Farmers
- ✅ Registration and secure login
- ✅ Post new work opportunities
- ✅ View posted work and manage applications
- ✅ Assign work to specific workers
- ✅ Track work status (Pending, In Progress, Completed)
- ✅ View payment summary and history
- ✅ Worker ratings and performance tracking

### For Workers
- ✅ Registration and secure login  
- ✅ Browse available work opportunities
- ✅ Apply for work
- ✅ Accept assigned work
- ✅ Track applications and assigned works
- ✅ View earnings and payment details
- ✅ Build reputation through completed works

### For Admin
- ✅ Comprehensive dashboard
- ✅ Manage all users (farmers and workers)
- ✅ Block/unblock users
- ✅ View all work postings
- ✅ Monitor all payments and transactions
- ✅ Automatic 5% commission calculation
- ✅ Track total commission earned

## Database Schema

### Core Models
- **Userregister**: Custom user model with role-based authentication
- **FarmerProfile**: Extended fields for farmers (land size, ratings, etc.)
- **WorkerProfile**: Extended fields for workers (skills, experience, earnings, etc.)
- **Work**: Job postings with status tracking
- **WorkApplication**: Applications submitted by workers
- **Payment**: Payment records for completed works
- **Commission**: Admin commission tracking

## Commission Logic
- When work is marked as **Completed**:
  - Total amount is split automatically
  - **Worker receives 95%** of the wage amount
  - **Admin receives 5%** commission
  - Payment and commission records are created automatically

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 6.0+
- MySQL 5.7+
- pip

### Step 1: Install Dependencies
```bash
pip install django mysqlclient django-mysql
```

### Step 2: Database Configuration
Update `fish/settings.py` with your MySQL credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'farmer',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```

### Step 3: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create Admin User
```bash
python manage.py createsuperuser
```

### Step 5: Run Development Server
```bash
python manage.py runserver
```

Access the application at: `http://localhost:8000`

## URL Routes

### Authentication
- `/login/` - Login page
- `/register/farmer/` - Farmer registration
- `/register/worker/` - Worker registration
- `/logout/` - Logout
- `/profile/` - User profile

### Farmer Routes
- `/farmer/dashboard/` - Farmer dashboard
- `/farmer/post-work/` - Post new work
- `/farmer/work/<id>/` - View work details
- `/farmer/work/<id>/assign/` - Assign work to worker
- `/farmer/work/<id>/update-status/` - Update work status
- `/farmer/payments/` - View payment summary

### Worker Routes
- `/worker/dashboard/` - Worker dashboard
- `/worker/available-works/` - Browse available works
- `/worker/apply/<id>/` - Apply for work
- `/worker/applications/` - View applications
- `/worker/assigned-works/` - View assigned works
- `/worker/payments/` - View earnings

### Admin Routes
- `/admin/login/` - Admin login
- `/admin/dashboard/` - Admin dashboard
- `/admin/users/` - User management
- `/admin/works/` - View all works
- `/admin/payments/` - View payments and commissions

## Default Admin Credentials
- **Username**: admin
- **Password**: admin

## Project Structure
```
farmer/
├── fish/               # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── members/            # Main app
│   ├── models.py       # Database models
│   ├── views.py        # Business logic
│   ├── forms.py        # Form validation
│   ├── urls.py         # URL routing
│   ├── admin.py        # Admin configuration
│   └── templates/      # HTML templates
├── manage.py
└── db.sqlite3
```

## File Descriptions

### models.py
Complete database models with relationships:
- User authentication with roles
- Profile extensions for farmers and workers
- Work posting and tracking
- Application management
- Payment processing
- Commission calculation

### views.py
Comprehensive view functions:
- Authentication views (register, login, logout)
- Farmer dashboard and work management
- Worker dashboard and job application
- Admin dashboard and user management
- Payment and commission tracking

### forms.py
Form validation and data handling:
- Registration forms (farmer/worker)
- Login form
- Work posting form
- Profile forms

### urls.py
Complete URL routing for all features

### templates/
- `base.html` - Base template with navigation and styling
- `index.html` - Home page
- `farmer_register.html` - Farmer registration
- `worker_register.html` - Worker registration
- `login.html` - Login page
- `farmer_dashboard.html` - Farmer dashboard
- `post_work.html` - Post work form
- `work_details.html` - Work details view
- `assign_work.html` - Assign work interface
- `update_work_status.html` - Status update form
- `farmer_payments.html` - Farmer payment summary
- `worker_dashboard.html` - Worker dashboard
- `available_works.html` - Browse works
- `worker_applications.html` - View applications
- `worker_assigned_works.html` - View assigned works
- `worker_payments.html` - Worker earnings
- `user_profile.html` - User profile
- `admin_login.html` - Admin login
- `admin_dashboard.html` - Admin dashboard
- `admin_user_management.html` - User management
- `admin_all_works.html` - All works
- `admin_all_payments.html` - Payments and commissions

## Features Details

### Authentication System
- Session-based authentication
- Separate login for Farmer, Worker, and Admin
- Password hashing using Django's make_password
- Role-based access control

### Work Management
- Create, read, update, delete operations
- Status tracking (Pending → In Progress → Completed)
- Worker application system
- Automatic assignment workflow

### Payment System
- Automatic payment calculation
- Commission tracking
- Payment status management
- Detailed payment history

### Admin Features
- User blocking/unblocking
- Complete system monitoring
- Commission earned tracking
- Statistical overview

## Security Features
- CSRF protection (CSRF tokens in forms)
- Password hashing
- Session management
- Role-based authorization
- Input validation through forms

## Responsive Design
- Bootstrap 5 CSS framework
- Mobile-friendly interface
- Adaptive layouts
- Professional styling

## Browser Compatibility
- Chrome (recommended)
- Firefox
- Safari
- Edge

## Troubleshooting

### Database Issues
```bash
# Reset database
python manage.py migrate --fake members zero
python manage.py migrate
```

### Missing Dependencies
```bash
pip install -r requirements.txt
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

## Future Enhancements
- Rating and review system
- Real-time notifications
- Payment gateway integration
- SMS/Email notifications
- Advanced analytics dashboard
- Mobile app

## Support & Documentation
For detailed documentation and support, refer to Django documentation at https://docs.djangoproject.com/

## License
MIT License - Feel free to use this project for educational and commercial purposes.

## Author
Developed as a comprehensive agricultural workforce management solution.

---

**Last Updated**: February 2024
**Version**: 1.0
