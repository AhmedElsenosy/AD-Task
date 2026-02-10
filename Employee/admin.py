from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from .models import Employee, AuditLog
from authentication.ldap_service import ldap_service


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Admin interface for Employee management
    
    Task 11: Fetch Current User OU
    - Displays current OU from Active Directory
    - Reads distinguishedName
    - Parses and shows OU path
    
    Task 13: Move User Between OUs
    - Move employees to different organizational units
    - Execute via LDAP modify_dn
    - Log all changes to AuditLog
    """
    
    # Custom template for change form (Task 13)
    change_form_template = 'admin/Employee/employee_change_form.html'
    
    # List display
    list_display = [
        'employee_id',
        'ad_username',
        'get_full_name_en',
        'get_full_name_ar',
        'job_title',
        'department',
        'get_current_ou',
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
    readonly_fields = ['employee_id', 'created_at', 'updated_at', 'get_current_ou_display', 'get_available_ous_display']
    
    # Fieldsets for better organization
    fieldsets = (
        ('Active Directory Information', {
            'fields': ('ad_username', 'get_current_ou_display')
        }),
        ('Organizational Unit Management (Task 12)', {
            'fields': ('get_available_ous_display',),
            'classes': ('wide',),
            'description': 'View and manage employee organizational unit assignment'
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
    
    def get_current_ou(self, obj):
        """
        Task 11: Display current OU in list view
        Fetches OU from Active Directory
        """
        try:
            ou_info = ldap_service.get_user_ou_info(obj.ad_username)
            if ou_info and ou_info.get('ou_path'):
                return ou_info['ou_path']
            return '—'
        except Exception as e:
            # Gracefully handle errors without breaking the list view
            return '⚠️  Error fetching OU'
    get_current_ou.short_description = 'Current OU'
    
    def get_current_ou_display(self, obj):
        """
        Task 11: Display detailed OU information in detail view
        Shows full DN and parsed OU path
        """
        try:
            ou_info = ldap_service.get_user_ou_info(obj.ad_username)
            if ou_info:
                html = '<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; font-family: monospace;">'
                html += f'<strong>Current OU:</strong> {ou_info.get("ou_name", "N/A")}<br>'
                html += f'<strong>OU Path:</strong> {ou_info.get("ou_path", "N/A")}<br>'
                html += f'<strong>Distinguished Name:</strong><br>'
                html += f'<code style="word-break: break-all;">{ou_info.get("dn", "N/A")}</code><br>'
                html += f'<strong>OU DN:</strong><br>'
                html += f'<code style="word-break: break-all;">{ou_info.get("ou_dn", "N/A")}</code>'
                html += '</div>'
                from django.utils.html import mark_safe
                return mark_safe(html)
            else:
                return '<span style="color: red;">Could not fetch OU information</span>'
        except Exception as e:
            from django.utils.html import mark_safe
            return mark_safe(f'<span style="color: red;">Error: {str(e)}</span>')
    get_current_ou_display.short_description = 'Organizational Unit Details'
    
    def get_available_ous(self, obj=None):
        """
        Task 12: List Available OUs
        Fetch all available OUs from Active Directory
        Returns list of tuples for dropdown: [(name, name), ...]
        """
        try:
            ous = ldap_service.get_all_ous()
            if ous:
                # Return list of tuples (value, display)
                return [(ou['name'], ou['path']) for ou in ous]
            return []
        except Exception as e:
            # Return empty list if error occurs
            return []
    
    def get_available_ous_display(self, obj=None):
        """
        Task 12: Display available OUs as formatted HTML list
        Shows all target OUs available for selection
        """
        try:
            ous = ldap_service.get_all_ous()
            if ous and len(ous) > 0:
                from django.utils.html import mark_safe
                html = '<div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #0066cc;">'
                html += '<strong style="color: #0066cc; font-size: 14px;">Available Organizational Units</strong><br>'
                html += '<select style="width: 100%; padding: 8px; margin-top: 10px; border: 1px solid #ccc; border-radius: 3px;" onchange="alert(\'OU Move functionality coming in Task 14\')">'
                html += '<option value="">-- Select OU to move employee --</option>'
                
                for ou in ous:
                    html += f'<option value="{ou["name"]}">{ou["path"]}</option>'
                
                html += '</select><br>'
                html += f'<small style="color: #666; margin-top: 8px; display: block;"><strong>Total OUs Available:</strong> {len(ous)}</small>'
                html += '</div>'
                return mark_safe(html)
            else:
                from django.utils.html import mark_safe
                return mark_safe('<div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; color: #856404;">No OUs available</div>')
        except Exception as e:
            from django.utils.html import mark_safe
            return mark_safe(f'<div style="background-color: #f8d7da; padding: 10px; border-radius: 5px; color: #721c24;">Error fetching OUs: {str(e)}</div>')
    get_available_ous_display.short_description = 'Organizational Unit Selection'
    
    def move_user_ou(self, request, queryset):
        """
        Task 13: Admin action to move users between OUs
        Move selected employees to a new organizational unit
        """
        # For now, we'll redirect to a change form where they can select OU
        # In the future, this could be a custom form action
        
        if queryset.count() == 1:
            # Get the single selected employee
            employee = queryset.first()
            # Redirect to employee detail page where they can see the move UI
            return HttpResponseRedirect(
                reverse('admin:Employee_employee_change', args=[employee.pk]) + 
                '#move-ou-section'
            )
        else:
            self.message_user(
                request,
                'Please select exactly one employee to move.',
                messages.WARNING
            )
    
    move_user_ou.short_description = "Move selected employee to different OU"
    
    def response_change(self, request, obj):
        """
        Handle OU move form submission
        Task 13: Execute actual OU move when form is submitted
        Task 15: Enhanced UI with formatted confirmation messages
        """
        if 'move_to_ou' in request.POST:
            new_ou_name = request.POST.get('move_to_ou', '').strip()
            
            if not new_ou_name:
                self.message_user(
                    request,
                    '<strong>⚠️ Selection Required</strong><br>Please select an organizational unit to move to.',
                    messages.WARNING
                )
                return super().response_change(request, obj)
            
            try:
                # Get current OU info
                old_ou_info = ldap_service.get_user_ou_info(obj.ad_username)
                old_ou_name = old_ou_info.get('ou_name', 'Unknown') if old_ou_info else 'Unknown'
                old_ou_path = old_ou_info.get('ou_path', 'Unknown') if old_ou_info else 'Unknown'
                old_dn = old_ou_info.get('dn', '') if old_ou_info else ''
                old_ou_dn = old_ou_info.get('ou_dn', '') if old_ou_info else ''
                
                # Get list of OUs to find the DN for the new OU
                all_ous = ldap_service.get_all_ous()
                new_ou_dn = None
                new_ou_path = None
                
                for ou in all_ous:
                    if ou['name'] == new_ou_name:
                        new_ou_dn = ou['dn']
                        new_ou_path = ou['path']
                        break
                
                if not new_ou_dn:
                    self.message_user(
                        request,
                        f'<strong>❌ OU Not Found</strong><br>The organizational unit "{new_ou_name}" could not be found in Active Directory.',
                        messages.ERROR
                    )
                    return super().response_change(request, obj)
                
                # Check if already in target OU
                if new_ou_dn == old_ou_dn:
                    self.message_user(
                        request,
                        f'<strong>ℹ️ Already in OU</strong><br>{obj.ad_username} is already assigned to <strong>{new_ou_name}</strong> organizational unit.',
                        messages.INFO
                    )
                    return super().response_change(request, obj)
                
                # Execute the move
                success, error_msg = ldap_service.move_user_to_ou(obj.ad_username, new_ou_dn)
                
                if success:
                    # Verify the move by checking the new OU
                    new_ou_info = ldap_service.get_user_ou_info(obj.ad_username)
                    new_dn = new_ou_info.get('dn', '') if new_ou_info else ''
                    
                    # Create audit log entry
                    AuditLog.objects.create(
                        employee=obj,
                        old_ou=old_ou_path,
                        new_ou=new_ou_path,
                        changed_by=request.user.username,
                        status='success',
                        old_dn=old_dn,
                        new_dn=new_dn
                    )
                    
                    # Enhanced success message with better formatting
                    success_message = (
                        f'<strong>✅ Move Successful!</strong><br><br>'
                        f'<strong>Employee:</strong> {obj.ad_username}<br>'
                        f'<strong>Previous OU:</strong> {old_ou_path}<br>'
                        f'<strong>New OU:</strong> {new_ou_path}<br>'
                        f'<strong>Changed by:</strong> {request.user.username}<br><br>'
                        f'<em>The change has been applied to Active Directory and will be reflected on the Domain Controller within seconds.</em>'
                    )
                    self.message_user(
                        request,
                        success_message,
                        messages.SUCCESS
                    )
                else:
                    # Create failed audit log entry
                    AuditLog.objects.create(
                        employee=obj,
                        old_ou=old_ou_path,
                        new_ou=new_ou_path,
                        changed_by=request.user.username,
                        status='failed',
                        error_message=error_msg,
                        old_dn=old_dn
                    )
                    
                    # Enhanced error message with better formatting
                    error_msg_display = error_msg if error_msg else 'Unknown error occurred'
                    error_message = (
                        f'<strong>❌ Move Failed</strong><br><br>'
                        f'<strong>Employee:</strong> {obj.ad_username}<br>'
                        f'<strong>Target OU:</strong> {new_ou_path}<br><br>'
                        f'<strong>Error Details:</strong><br>'
                        f'{error_msg_display}<br><br>'
                        f'<em>Please check the Audit Log for more information. Contact your AD administrator if the issue persists.</em>'
                    )
                    self.message_user(
                        request,
                        error_message,
                        messages.ERROR
                    )
                    
            except Exception as e:
                self.message_user(
                    request,
                    f'<strong>❌ Operation Error</strong><br>An error occurred during the move operation: {str(e)}<br><br>'
                    f'<em>Please check the Audit Log for more information.</em>',
                    messages.ERROR
                )
        
        return super().response_change(request, obj)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        Task 13: Add move OU form to change view
        Display OU move interface in the employee detail page
        """
        extra_context = extra_context or {}
        
        # Get the employee object
        from django.shortcuts import get_object_or_404
        obj = get_object_or_404(Employee, pk=object_id)
        
        # Get available OUs
        available_ous = ldap_service.get_all_ous()
        
        # Get current OU
        current_ou_info = ldap_service.get_user_ou_info(obj.ad_username)
        current_ou = current_ou_info.get('ou_name', 'Unknown') if current_ou_info else 'Unknown'
        
        extra_context['available_ous'] = available_ous
        extra_context['current_ou'] = current_ou
        extra_context['employee_obj'] = obj
        
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin interface for Audit Log viewing
    Task 13: Track all OU changes
    """
    
    list_display = [
        'employee',
        'old_ou',
        'new_ou',
        'status_badge',
        'changed_by',
        'changed_at'
    ]
    
    list_filter = [
        'status',
        'changed_at',
        ('employee', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'employee__ad_username',
        'employee__first_name_en',
        'employee__last_name_en',
        'changed_by'
    ]
    
    readonly_fields = [
        'employee',
        'old_ou',
        'new_ou',
        'old_dn',
        'new_dn',
        'changed_by',
        'changed_at',
        'status',
        'error_message',
        'formatted_change_details'
    ]
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('OU Change Details', {
            'fields': ('old_ou', 'new_ou', 'old_dn', 'new_dn')
        }),
        ('Operation Details', {
            'fields': ('status', 'error_message', 'changed_by', 'changed_at')
        }),
        ('Formatted Summary', {
            'fields': ('formatted_change_details',),
            'classes': ('wide',)
        }),
    )
    
    ordering = ['-changed_at']
    list_per_page = 50
    
    def status_badge(self, obj):
        """Display status with color coding"""
        from django.utils.html import mark_safe
        
        colors = {
            'success': '#28a745',
            'failed': '#dc3545',
            'pending': '#ffc107'
        }
        
        color = colors.get(obj.status, '#6c757d')
        text_color = 'white' if obj.status != 'pending' else 'black'
        
        html = f'<span style="background-color: {color}; color: {text_color}; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{obj.get_status_display()}</span>'
        return mark_safe(html)
    
    status_badge.short_description = 'Status'
    
    def formatted_change_details(self, obj):
        """Display formatted change details"""
        from django.utils.html import mark_safe
        
        html = '<div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #0066cc; font-family: monospace;">'
        html += f'<strong>Employee:</strong> {obj.employee.ad_username}<br>'
        html += f'<strong>Previous OU:</strong> {obj.old_ou}<br>'
        html += f'<strong>New OU:</strong> {obj.new_ou}<br>'
        html += f'<strong>Changed By:</strong> {obj.changed_by}<br>'
        html += f'<strong>Changed At:</strong> {obj.changed_at.strftime("%Y-%m-%d %H:%M:%S")}<br>'
        html += f'<strong>Status:</strong> {obj.get_status_display()}<br>'
        
        if obj.error_message:
            html += f'<strong style="color: red;">Error:</strong> {obj.error_message}<br>'
        
        if obj.old_dn:
            html += f'<strong>Previous DN:</strong><br><code style="word-break: break-all;">{obj.old_dn}</code><br>'
        
        if obj.new_dn:
            html += f'<strong>New DN:</strong><br><code style="word-break: break-all;">{obj.new_dn}</code>'
        
        html += '</div>'
        return mark_safe(html)
    
    formatted_change_details.short_description = 'Change Details'
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs"""
        return False
