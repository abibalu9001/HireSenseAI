from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=50, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    company = forms.CharField(max_length=200, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Company Name (optional)'}))
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email',
                  'company', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                company=self.cleaned_data.get('company', ''),
                role=self.cleaned_data.get('role', 'recruiter'),
            )
        return user


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Username', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'placeholder': 'Password', 'class': 'form-control'}))
