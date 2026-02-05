"""
Authentication Views
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm
from .ldap_service import ldap_service
from Employee.models import Employee


def home_view(request):
    """
    Home page - redirects to login or dashboard based on authentication
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('login')


def login_view(request):
    """
    Handle employee login using AD credentials
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Authenticate using LDAP backend
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password, or you are not registered in the system.')
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})


def logout_view(request):
    """
    Handle employee logout
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required(login_url='login')
def dashboard_view(request):
    """
    Employee dashboard showing database and AD information
    """
    try:
        # Get employee from database
        employee = Employee.objects.get(ad_username=request.user.username)
        
        # Get AD information
        ad_data = ldap_service.search_user(request.user.username)
        
        context = {
            'employee': employee,
            'ad_data': ad_data,
        }
        
        return render(request, 'authentication/dashboard.html', context)
        
    except Employee.DoesNotExist:
        messages.error(request, 'Employee record not found.')
        logout(request)
        return redirect('login')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('login')
