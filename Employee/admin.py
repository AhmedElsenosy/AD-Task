from django.contrib import admin
from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin interface for Employee management
    """
    
    # List display
    list_display = [
        'employee_id',
        'ad_username',
        'get_full_name_en',
        'get_full_name_ar',
        'job_title',
        'department',
        'hire_date',
        'is_active',
        'created_at'
    ]
    
    # Filters
    list_filter = [
        'department',
        'is_active',
        'hire_date',
        'created_at'
    ]
    
    # Search
    search_fields = [
        'ad_username',
        'first_name_en',
        'last_name_en',
        'first_name_ar',
        'last_name_ar',
        'national_id',
        'job_title'
    ]
    
    # Readonly fields
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    
    # Fieldsets for better organization
    fieldsets = (
        ('Active Directory Information', {
            'fields': ('ad_username',)
        }),
        ('Personal Information (English)', {
            'fields': ('first_name_en', 'last_name_en')
        }),
        ('Personal Information (Arabic)', {
            'fields': ('first_name_ar', 'last_name_ar')
        }),
        ('Employment Information', {
            'fields': ('job_title', 'department', 'hire_date')
        }),
        ('Identification', {
            'fields': ('national_id',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('employee_id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Ordering
    ordering = ['-created_at']
    
    # Number of items per page
    list_per_page = 25
    
    # Enable date hierarchy
    date_hierarchy = 'hire_date'
    
    # Actions
    actions = ['activate_employees', 'deactivate_employees']
    
    def activate_employees(self, request, queryset):
        """Activate selected employees"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} employee(s) activated successfully.')
    activate_employees.short_description = "Activate selected employees"
    
    def deactivate_employees(self, request, queryset):
        """Deactivate selected employees"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} employee(s) deactivated successfully.')
    deactivate_employees.short_description = "Deactivate selected employees"
    
    # Custom methods for list display
    def get_full_name_en(self, obj):
        return obj.get_full_name_en()
    get_full_name_en.short_description = 'Full Name (EN)'
    
    def get_full_name_ar(self, obj):
        return obj.get_full_name_ar()
    get_full_name_ar.short_description = 'Full Name (AR)'
