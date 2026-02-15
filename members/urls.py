from django.urls import path
from . import views

urlpatterns = [
    # ========== Public Pages ==========
    path('', views.index, name='index'),
    
    # ========== Authentication ==========
    path('register/farmer/', views.farmer_register, name='farmer_register'),
    path('register/worker/', views.worker_register, name='worker_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ========== User Profile ==========
    path('profile/', views.user_profile, name='user_profile'),
    
    # ========== Farmer URLs ==========
    path('farmer/dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('farmer/post-work/', views.post_work, name='post_work'),
    path('farmer/work/<int:work_id>/', views.work_details, name='work_details'),
    path('farmer/work/<int:work_id>/assign/', views.assign_work, name='assign_work'),
    path('farmer/work/<int:work_id>/update-status/', views.update_work_status, name='update_work_status'),
    path('farmer/payments/', views.farmer_payments, name='farmer_payments'),
    
    # ========== Worker URLs ==========
    path('worker/dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('worker/available-works/', views.view_available_works, name='view_available_works'),
    path('worker/apply/<int:work_id>/', views.apply_for_work, name='apply_for_work'),
    path('worker/applications/', views.worker_applications, name='worker_applications'),
    path('worker/assigned-works/', views.worker_assigned_works, name='worker_assigned_works'),
    path('worker/work/<int:work_id>/accept/', views.accept_assigned_work, name='accept_assigned_work'),
    path('worker/payments/', views.worker_payments, name='worker_payments'),
    
    # ========== Admin URLs ==========
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_user_management, name='admin_user_management'),
    path('admin/works/', views.admin_all_works, name='admin_all_works'),
    path('admin/payments/', views.admin_all_payments, name='admin_all_payments'),
]