from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Sum, Count
from datetime import date, datetime
from decimal import Decimal

from .models import (
    Userregister, Work, WorkApplication, FarmerProfile, 
    WorkerProfile, Payment, Commission
)
from .forms import (
    FarmerRegistrationForm, WorkerRegistrationForm, LoginForm,
    WorkForm, UpdateWorkStatusForm, FarmerProfileForm, WorkerProfileForm
)


# ============= Authentication Views =============

def index(request):
    """Home page"""
    context = {
        'total_farmers': Userregister.objects.filter(role='farmer', is_active=True).count(),
        'total_workers': Userregister.objects.filter(role='worker', is_active=True).count(),
        'total_works': Work.objects.count(),
    }
    return render(request, 'index.html', context)


def farmer_register(request):
    """Farmer registration"""
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            if Userregister.objects.filter(phonenumber=form.cleaned_data['phonenumber']).exists():
                messages.error(request, 'Phone number already registered')
                return render(request, 'farmer_register.html', {'form': form})

            user = Userregister.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phonenumber=form.cleaned_data['phonenumber'],
                current_password=make_password(form.cleaned_data['password']),
                role='farmer',
                location=form.cleaned_data['location']
            )

            # Create farmer profile
            FarmerProfile.objects.create(
                user=user,
                land_size=form.cleaned_data.get('land_size')
            )

            # Auto-login
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['role'] = user.role
            messages.success(request, 'Farmer registration successful!')
            return redirect('farmer_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = FarmerRegistrationForm()

    return render(request, 'farmer_register.html', {'form': form})


def worker_register(request):
    """Worker registration"""
    if request.method == 'POST':
        form = WorkerRegistrationForm(request.POST)
        if form.is_valid():
            if Userregister.objects.filter(phonenumber=form.cleaned_data['phonenumber']).exists():
                messages.error(request, 'Phone number already registered')
                return render(request, 'worker_register.html', {'form': form})

            user = Userregister.objects.create(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                phonenumber=form.cleaned_data['phonenumber'],
                current_password=make_password(form.cleaned_data['password']),
                role='worker',
                location=form.cleaned_data['location'],
                work_time=form.cleaned_data['work_time']
            )

            # Create worker profile
            WorkerProfile.objects.create(
                user=user,
                skills=form.cleaned_data.get('skills', ''),
                experience_years=form.cleaned_data.get('experience_years', 0)
            )

            # Auto-login
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['role'] = user.role
            messages.success(request, 'Worker registration successful!')
            return redirect('worker_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = WorkerRegistrationForm()

    return render(request, 'worker_register.html', {'form': form})


def login_view(request):
    """Login for farmers and workers"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            phonenumber = form.cleaned_data['phonenumber']
            password = form.cleaned_data['password']

            try:
                user = Userregister.objects.get(phonenumber=phonenumber)
            except Userregister.DoesNotExist:
                messages.error(request, 'Invalid phone number or password')
                return render(request, 'login.html', {'form': form})

            if user.is_blocked:
                messages.error(request, 'Your account has been blocked by admin')
                return render(request, 'login.html', {'form': form})

            if check_password(password, user.current_password):
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                request.session['role'] = user.role
                messages.success(request, f'Welcome {user.username}!')

                if user.role == 'farmer':
                    return redirect('farmer_dashboard')
                else:
                    return redirect('worker_dashboard')
            else:
                messages.error(request, 'Invalid phone number or password')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Logout"""
    request.session.flush()
    messages.info(request, 'You have been logged out')
    return redirect('index')


# ============= Decorator for Authentication =============

def login_required_with_role(required_role=None):
    """Decorator to check login and role"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user_id = request.session.get('user_id')
            if not user_id:
                messages.error(request, 'Please login first')
                return redirect('login')

            user = get_object_or_404(Userregister, id=user_id)

            if required_role and user.role != required_role:
                return HttpResponse('Unauthorized - You do not have access to this resource', status=403)

            request.current_user = user
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ============= Farmer Dashboard & Work Management =============

@login_required_with_role('farmer')
def farmer_dashboard(request):
    """Farmer dashboard - view posted works"""
    user = request.current_user
    
    try:
        farmer_profile = user.farmer_profile
    except FarmerProfile.DoesNotExist:
        farmer_profile = FarmerProfile.objects.create(user=user)

    works = Work.objects.filter(farmer=user).order_by('-created_at')
    
    # Get statistics
    stats = {
        'total_works': works.count(),
        'pending_works': works.filter(status='pending').count(),
        'in_progress_works': works.filter(status='in_progress').count(),
        'completed_works': works.filter(status='completed').count(),
        'total_spent': Payment.objects.filter(farmer=user).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00'),
    }

    context = {
        'farmer_profile': farmer_profile,
        'works': works,
        'stats': stats,
    }
    return render(request, 'farmer_dashboard.html', context)


@login_required_with_role('farmer')
def post_work(request):
    """Post new work"""
    user = request.current_user

    if request.method == 'POST':
        form = WorkForm(request.POST)
        if form.is_valid():
            work = form.save(commit=False)
            work.farmer = user
            work.save()
            messages.success(request, 'Work posted successfully!')
            return redirect('farmer_dashboard')
    else:
        form = WorkForm()

    return render(request, 'post_work.html', {'form': form})


@login_required_with_role('farmer')
def work_details(request, work_id):
    """View work details and manage applications"""
    user = request.current_user
    work = get_object_or_404(Work, id=work_id, farmer=user)
    applications = work.applications.all().select_related('worker')

    context = {
        'work': work,
        'applications': applications,
    }
    return render(request, 'work_details.html', context)


@login_required_with_role('farmer')
def assign_work(request, work_id):
    """Assign work to a worker"""
    user = request.current_user
    work = get_object_or_404(Work, id=work_id, farmer=user)

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        application = get_object_or_404(WorkApplication, id=app_id, work=work)

        # Accept the application
        application.accept()
        messages.success(request, f'Work assigned to {application.worker.username}')
        return redirect('work_details', work_id=work.id)

    applications = work.applications.filter(status='applied')
    context = {
        'work': work,
        'applications': applications,
    }
    return render(request, 'assign_work.html', context)


@login_required_with_role('farmer')
def update_work_status(request, work_id):
    """Update work status"""
    user = request.current_user
    work = get_object_or_404(Work, id=work_id, farmer=user)

    if request.method == 'POST':
        form = UpdateWorkStatusForm(request.POST)
        if form.is_valid():
            status = form.cleaned_data['status']
            work.status = status

            if status == 'completed':
                work.mark_completed()
                messages.success(request, 'Work marked as completed and payment processed!')
            else:
                work.save()
                messages.success(request, f'Work status updated to {status}')

            return redirect('work_details', work_id=work.id)
    else:
        form = UpdateWorkStatusForm()

    context = {
        'work': work,
        'form': form,
    }
    return render(request, 'update_work_status.html', context)


@login_required_with_role('farmer')
def farmer_payments(request):
    """View payment summary for farmer"""
    user = request.current_user
    payments = Payment.objects.filter(farmer=user).order_by('-created_at')

    stats = {
        'total_amount': payments.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
        'total_paid': payments.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
        'pending_amount': payments.filter(status='pending').aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
    }

    context = {
        'payments': payments,
        'stats': stats,
    }
    return render(request, 'farmer_payments.html', context)


# ============= Worker Dashboard & Work Application =============

@login_required_with_role('worker')
def worker_dashboard(request):
    """Worker dashboard - view available works"""
    user = request.current_user

    try:
        worker_profile = user.worker_profile
    except WorkerProfile.DoesNotExist:
        worker_profile = WorkerProfile.objects.create(user=user)

    # Get available works
    available_works = Work.objects.filter(
        status__in=['pending', 'in_progress'],
        farmer__is_blocked=False
    ).exclude(
        applications__worker=user,
        applications__status__in=['accepted']
    ).order_by('-created_at')

    # Get worker's applied works
    applied_works = Work.objects.filter(
        applications__worker=user
    ).order_by('-created_at')

    # Get statistics
    stats = {
        'available_works': available_works.count(),
        'applied_works': applied_works.count(),
        'assigned_works': Work.objects.filter(assigned_worker=user, status='in_progress').count(),
        'completed_works': Work.objects.filter(assigned_worker=user, status='completed').count(),
        'total_earnings': Payment.objects.filter(worker=user, status='completed').aggregate(
            total=Sum('worker_share')
        )['total'] or Decimal('0.00'),
    }

    context = {
        'worker_profile': worker_profile,
        'available_works': available_works[:10],
        'applied_works': applied_works,
        'stats': stats,
    }
    return render(request, 'worker_dashboard.html', context)


@login_required_with_role('worker')
def view_available_works(request):
    """View all available works with filters"""
    user = request.current_user

    works = Work.objects.filter(
        status__in=['pending', 'in_progress'],
        farmer__is_blocked=False
    ).exclude(
        applications__worker=user,
        applications__status__in=['accepted']
    ).order_by('-created_at')

    # Filters
    location = request.GET.get('location')
    wage_min = request.GET.get('wage_min')
    wage_max = request.GET.get('wage_max')

    if location:
        works = works.filter(location__icontains=location)
    if wage_min:
        works = works.filter(wage_amount__gte=wage_min)
    if wage_max:
        works = works.filter(wage_amount__lte=wage_max)

    context = {
        'works': works,
        'location': location,
        'wage_min': wage_min,
        'wage_max': wage_max,
    }
    return render(request, 'available_works.html', context)


@login_required_with_role('worker')
def apply_for_work(request, work_id):
    """Apply for a work"""
    user = request.current_user
    work = get_object_or_404(Work, id=work_id)

    # Check if already applied
    if work.applications.filter(worker=user).exists():
        messages.error(request, 'You have already applied for this work')
        return redirect('view_available_works')

    # Create application
    WorkApplication.objects.create(work=work, worker=user)
    messages.success(request, f'Successfully applied for {work.title}!')
    return redirect('view_available_works')


@login_required_with_role('worker')
def worker_applications(request):
    """View worker's applications"""
    user = request.current_user
    applications = user.work_applications.all().select_related('work', 'work__farmer').order_by('-applied_at')

    context = {
        'applications': applications,
    }
    return render(request, 'worker_applications.html', context)


@login_required_with_role('worker')
def accept_assigned_work(request, work_id):
    """Accept assigned work (when farmer assigns)"""
    user = request.current_user
    work = get_object_or_404(Work, id=work_id, assigned_worker=user)

    if request.method == 'POST':
        work.status = 'in_progress'
        work.save()
        messages.success(request, 'You have accepted the work!')
        return redirect('worker_assigned_works')

    context = {
        'work': work,
    }
    return render(request, 'accept_work.html', context)


@login_required_with_role('worker')
def worker_assigned_works(request):
    """View works assigned to worker"""
    user = request.current_user
    assigned_works = Work.objects.filter(assigned_worker=user).order_by('-created_at')

    context = {
        'assigned_works': assigned_works,
    }
    return render(request, 'worker_assigned_works.html', context)


@login_required_with_role('worker')
def worker_payments(request):
    """View payment details for worker"""
    user = request.current_user
    payments = Payment.objects.filter(worker=user).order_by('-created_at')

    stats = {
        'total_earned': payments.aggregate(Sum('worker_share'))['worker_share__sum'] or Decimal('0.00'),
        'total_completed': payments.filter(status='completed').count(),
        'pending_payments': payments.filter(status__in=['pending', 'completed']).count(),
    }

    context = {
        'payments': payments,
        'stats': stats,
    }
    return render(request, 'worker_payments.html', context)


# ============= Admin Dashboard =============

def admin_dashboard(request):
    """Admin dashboard statistics"""
    # Note: In production, use proper authentication instead of session
    if not request.session.get('is_admin'):
        return redirect('admin_login')

    farmers = Userregister.objects.filter(role='farmer')
    workers = Userregister.objects.filter(role='worker')
    works = Work.objects.all()
    payments = Payment.objects.all()
    commissions = Commission.objects.all()

    context = {
        'total_farmers': farmers.count(),
        'total_workers': workers.count(),
        'total_works': works.count(),
        'total_payments': payments.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
        'total_commission': Commission.get_total_commission(),
        'completed_works': works.filter(status='completed').count(),
        'blocked_users': Userregister.objects.filter(is_blocked=True).count(),
    }

    return render(request, 'admin_dashboard.html', context)


def admin_login(request):
    """Admin login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's built-in admin credentials check
        # This is simplified - use proper authentication in production
        if username == 'admin' and password == 'admin':
            request.session['is_admin'] = True
            messages.success(request, 'Admin login successful')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials')

    return render(request, 'admin_login.html')


def admin_logout(request):
    """Admin logout"""
    request.session.flush()
    messages.info(request, 'Logged out')
    return redirect('index')


def admin_user_management(request):
    """Manage users - view all farmers and workers"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')

    role = request.GET.get('role', 'all')

    if role == 'farmer':
        users = Userregister.objects.filter(role='farmer')
    elif role == 'worker':
        users = Userregister.objects.filter(role='worker')
    else:
        users = Userregister.objects.all()

    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        user = get_object_or_404(Userregister, id=user_id)

        if action == 'block':
            user.is_blocked = True
            user.save()
            messages.success(request, f'{user.username} has been blocked')
        elif action == 'unblock':
            user.is_blocked = False
            user.save()
            messages.success(request, f'{user.username} has been unblocked')

        return redirect('admin_user_management')

    context = {
        'users': users,
        'role': role,
    }
    return render(request, 'admin_user_management.html', context)


def admin_all_works(request):
    """View all works"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')

    status = request.GET.get('status', 'all')

    if status != 'all':
        works = Work.objects.filter(status=status)
    else:
        works = Work.objects.all()

    works = works.order_by('-created_at')

    context = {
        'works': works,
        'status': status,
    }
    return render(request, 'admin_all_works.html', context)


def admin_all_payments(request):
    """View all payments and commissions"""
    if not request.session.get('is_admin'):
        return redirect('admin_login')

    payments = Payment.objects.all().order_by('-created_at')
    commissions = Commission.objects.all().order_by('-created_at')

    stats = {
        'total_payments': payments.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
        'total_commission': Commission.get_total_commission(),
        'total_paid': payments.filter(status='paid').aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0.00'),
    }

    context = {
        'payments': payments,
        'commissions': commissions,
        'stats': stats,
    }
    return render(request, 'admin_all_payments.html', context)


@login_required_with_role()
def user_profile(request):
    """View and edit user profile"""
    user = request.current_user

    if request.method == 'POST':
        if user.role == 'farmer':
            form = FarmerProfileForm(request.POST, instance=user.farmer_profile)
        else:
            form = WorkerProfileForm(request.POST, instance=user.worker_profile)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
    else:
        if user.role == 'farmer':
            form = FarmerProfileForm(instance=user.farmer_profile)
        else:
            form = WorkerProfileForm(instance=user.worker_profile)

    context = {
        'user': user,
        'form': form,
    }
    return render(request, 'user_profile.html', context)


