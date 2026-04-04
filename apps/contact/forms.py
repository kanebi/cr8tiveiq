from django import forms
from .models import ContactInquiry, NewsletterSubscriber


class ContactForm(forms.ModelForm):
    """Contact form."""
    class Meta:
        model = ContactInquiry
        fields = ['name', 'email', 'phone', 'company', 'project_description', 'service_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Company'}),
            'project_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Project Description', 'rows': 5}),
            'service_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Service Type'}),
        }


class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form."""
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
        }
