from django.db import models
from django.utils import timezone
from decimal import Decimal


class Userregister(models.Model):
    """Custom User model with role-based authentication"""
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('worker', 'Worker'),
    )

    TIME_CHOICES = (
        ('morning', 'Morning'),
        ('evening', 'Evening'),
    )

    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    phonenumber = models.CharField(max_length=15, unique=True)
    current_password = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    work_time = models.CharField(max_length=10, choices=TIME_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "User Register"
        verbose_name_plural = "User Registers"


class FarmerProfile(models.Model):
    """Extended profile for Farmers"""
    user = models.OneToOneField(Userregister, on_delete=models.CASCADE, related_name='farmer_profile')
    land_size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Land size in acres", null=True, blank=True)
    total_works_posted = models.PositiveIntegerField(default=0)
    total_workers_hired = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="Average rating out of 5")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Farmer Profile - {self.user.username}"

    def get_total_spent(self):
        """Calculate total amount spent on completed works"""
        completed_works = self.user.jobs.filter(status='completed')
        total = sum([work.salary for work in completed_works])
        return total


class WorkerProfile(models.Model):
    """Extended profile for Workers"""
    user = models.OneToOneField(Userregister, on_delete=models.CASCADE, related_name='worker_profile')
    skills = models.TextField(help_text="Comma-separated list of skills", null=True, blank=True)
    experience_years = models.PositiveIntegerField(default=0, help_text="Years of experience")
    total_works_completed = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text="Average rating out of 5")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Worker Profile - {self.user.username}"


class Work(models.Model):
    """Work/Job posted by Farmers"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    farmer = models.ForeignKey(Userregister, on_delete=models.CASCADE, related_name='posted_works')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    required_workers = models.PositiveIntegerField(default=1)
    wage_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Wage per worker")
    wage_type = models.CharField(max_length=20, choices=(('per_day', 'Per Day'), ('total', 'Total')), default='per_day')
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_worker = models.ForeignKey(Userregister, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_works')
    
    contact_phone = models.CharField(max_length=15)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} - Posted by {self.farmer.username}"

    class Meta:
        ordering = ['-created_at']

    def mark_completed(self):
        """Mark work as completed and create payment/commission"""
        self.status = 'completed'
        self.save()
        
        # Create payment and commission when work is completed
        if self.assigned_worker:
            payment = Payment.objects.create(
                work=self,
                worker=self.assigned_worker,
                farmer=self.farmer,
                total_amount=self.wage_amount,
                worker_share=self.wage_amount * Decimal('0.95'),
                admin_commission=self.wage_amount * Decimal('0.05'),
                status='completed'
            )
            
            # Create commission record
            Commission.objects.create(
                payment=payment,
                amount=self.wage_amount * Decimal('0.05'),
                work=self
            )


class WorkApplication(models.Model):
    """Application submitted by Worker to apply for Work"""
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='applications')
    worker = models.ForeignKey(Userregister, on_delete=models.CASCADE, related_name='work_applications')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('work', 'worker')

    def __str__(self):
        return f"{self.worker.username} applied for {self.work.title} ({self.status})"

    def accept(self):
        """Accept the application and assign work to worker"""
        self.status = 'accepted'
        self.accepted_at = timezone.now()
        self.save()
        
        # Assign work to this worker
        self.work.assigned_worker = self.worker
        self.work.status = 'in_progress'
        self.work.save()


class Payment(models.Model):
    """Payment records for completed works"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('paid', 'Paid'),
    )

    work = models.OneToOneField(Work, on_delete=models.CASCADE, related_name='payment')
    worker = models.ForeignKey(Userregister, on_delete=models.CASCADE, related_name='payments_received')
    farmer = models.ForeignKey(Userregister, on_delete=models.CASCADE, related_name='payments_made')
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    worker_share = models.DecimalField(max_digits=12, decimal_places=2, help_text="95% of total amount")
    admin_commission = models.DecimalField(max_digits=12, decimal_places=2, help_text="5% of total amount")
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment for {self.work.title} - {self.worker.username}"

    class Meta:
        ordering = ['-created_at']

    def mark_as_paid(self):
        """Mark payment as paid"""
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()


class Commission(models.Model):
    """Admin commission records"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='commission')
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='commissions')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=(('earned', 'Earned'), ('paid', 'Paid')), default='earned')
    
    created_at = models.DateTimeField(default=timezone.now)
    received_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Commission - {self.amount} from {self.work.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Commissions"

    @staticmethod
    def get_total_commission():
        """Get total commission earned by admin"""
        return Commission.objects.filter(status='earned').aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
