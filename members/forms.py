from django import forms
from django.contrib.auth.hashers import make_password
from .models import Userregister, Work, WorkApplication, FarmerProfile, WorkerProfile


class FarmerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    email = forms.EmailField(required=True)
    land_size = forms.DecimalField(required=False, label="Land Size (acres)")

    class Meta:
        model = Userregister
        fields = ['username', 'email', 'phonenumber', 'location']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phonenumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['confirm_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        self.fields['land_size'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Land Size (acres)'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")

        return cleaned_data


class WorkerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    email = forms.EmailField(required=True)
    skills = forms.CharField(required=False, widget=forms.Textarea, label="Skills (comma-separated)")
    experience_years = forms.IntegerField(required=False, label="Years of Experience")
    work_time = forms.ChoiceField(choices=Userregister.TIME_CHOICES)

    class Meta:
        model = Userregister
        fields = ['username', 'email', 'phonenumber', 'location', 'work_time']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'phonenumber': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'work_time': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['confirm_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        self.fields['skills'].widget.attrs.update({'class': 'form-control', 'placeholder': 'e.g., Plowing, Irrigation, Planting'})
        self.fields['experience_years'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")

        return cleaned_data


class LoginForm(forms.Form):
    phonenumber = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone Number'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class WorkForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['title', 'description', 'location', 'required_workers', 'wage_amount', 'wage_type', 'start_date', 'end_date', 'contact_phone']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Work Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the work'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'required_workers': forms.NumberInput(attrs={'class': 'form-control'}),
            'wage_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'wage_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Phone'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")

        return cleaned_data


class WorkApplicationForm(forms.ModelForm):
    class Meta:
        model = WorkApplication
        fields = []


class UpdateWorkStatusForm(forms.Form):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))


class FarmerProfileForm(forms.ModelForm):
    class Meta:
        model = FarmerProfile
        fields = ['land_size']
        widgets = {
            'land_size': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class WorkerProfileForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ['skills', 'experience_years']
        widgets = {
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
        }
