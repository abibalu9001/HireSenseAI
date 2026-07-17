from django import forms
from .models import JobDescription


class JobDescriptionForm(forms.ModelForm):
    class Meta:
        model = JobDescription
        fields = ['title', 'description', 'experience_years', 'education_level', 'jd_file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g., Senior Python Developer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 10,
                'placeholder': 'Paste the full job description here...'
            }),
            'experience_years': forms.Select(attrs={'class': 'form-select'}),
            'education_level': forms.Select(attrs={'class': 'form-select'}),
            'jd_file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.docx,.txt'}),
        }
