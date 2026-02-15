from django.contrib import admin
from .models import (
    Userregister, FarmerProfile, WorkerProfile, Work,
    WorkApplication, Payment, Commission
)


@admin.register(Userregister)
class UserregisterAdmin(admin.ModelAdmin):
    list_display = ('username', 'phonenumber', 'role', 'is_active', 'is_blocked', 'created_at')
    list_filter = ('role', 'is_active', 'is_blocked', 'created_at')
    search_fields = ('username', 'phonenumber', 'email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'email', 'phonenumber', 'location')
        }),
        ('Role & Status', {
            'fields': ('role', 'is_active', 'is_blocked')
        }),
        ('Work Preferences', {
            'fields': ('work_time',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'land_size', 'total_works_posted', 'rating')
    list_filter = ('created_at', 'rating')
    search_fields = ('user__username', 'user__phonenumber')
    readonly_fields = ('created_at',)


@admin.register(WorkerProfile)
class WorkerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'total_works_completed', 'total_earnings', 'rating')
    list_filter = ('experience_years', 'created_at', 'rating')
    search_fields = ('user__username', 'user__phonenumber', 'skills')
    readonly_fields = ('created_at',)


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'farmer', 'location', 'wage_amount', 'status', 'assigned_worker', 'created_at')
    list_filter = ('status', 'wage_type', 'created_at', 'location')
    search_fields = ('title', 'description', 'farmer__username', 'location')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'farmer', 'location')
        }),
        ('Work Details', {
            'fields': ('required_workers', 'wage_amount', 'wage_type', 'contact_phone')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Assignment', {
            'fields': ('status', 'assigned_worker')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkApplication)
class WorkApplicationAdmin(admin.ModelAdmin):
    list_display = ('worker', 'work', 'status', 'applied_at', 'accepted_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('worker__username', 'work__title')
    readonly_fields = ('applied_at', 'accepted_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('work', 'worker', 'farmer', 'total_amount', 'worker_share', 'admin_commission', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('work__title', 'worker__username', 'farmer__username')
    readonly_fields = ('created_at', 'completed_at', 'paid_at')
    
    fieldsets = (
        ('Work & Users', {
            'fields': ('work', 'worker', 'farmer')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'worker_share', 'admin_commission')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('amount', 'work', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('work__title', 'payment__worker__username')
    readonly_fields = ('created_at', 'received_date')
    
    fieldsets = (
        ('Commission Details', {
            'fields': ('payment', 'work', 'amount', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'received_date'),
            'classes': ('collapse',)
        }),
    )
