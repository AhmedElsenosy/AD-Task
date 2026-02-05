"""
Authentication Forms
"""

from django import forms


class LoginForm(forms.Form):
    """
    Login form for AD authentication
    """
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'AD Username (e.g., mohamed.khaled)',
            'autofocus': True
        }),
        label='Username'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        }),
        label='Password'
    )
