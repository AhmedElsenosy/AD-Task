from django.db import models
from django.core.validators import RegexValidator


class Employee(models.Model):
    """
    Employee model linked to Active Directory
    
    Note: Email, Phone, and Password are NOT stored here - they come from AD
    """
    
    # Primary Key
    employee_id = models.AutoField(primary_key=True, verbose_name="Employee ID")
    
    # AD Link - This is the username used in Active Directory
    ad_username = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="AD Username (sAMAccountName)",
        help_text="Active Directory username (e.g., mohamed.khaled)"
    )
    
    # Full Name in English
    first_name_en = models.CharField(max_length=100, verbose_name="First Name (English)")
    last_name_en = models.CharField(max_length=100, verbose_name="Last Name (English)")
    
    # Full Name in Arabic
    first_name_ar = models.CharField(max_length=100, verbose_name="First Name (Arabic)")
    last_name_ar = models.CharField(max_length=100, verbose_name="Last Name (Arabic)")
    
    # Job Information
    job_title = models.CharField(max_length=150, verbose_name="Job Title")
    department = models.CharField(
        max_length=100, 
        verbose_name="Department",
        choices=[
            ('IT', 'IT (تكنولوجيا المعلومات)'),
            ('HR', 'HR (الموارد البشرية)'),
            ('Accountant', 'Accountant (المحاسبة)'),
            ('Administrative Affairs', 'Administrative Affairs (الشؤون الإدارية)'),
            ('Camera', 'Camera (الكاميرات)'),
            ('Exhibit', 'Exhibit (المعارض)'),
            ('Audit', 'Audit (المراجعة)'),
            ('Out Work', 'Out Work (العمل الخارجي)'),
            ('Projects', 'Projects (المشاريع)'),
            ('Sales', 'Sales (المبيعات)'),
            ('Supplies', 'Supplies (المشتريات)'),
            ('Secretarial', 'Secretarial (السكرتارية)'),
        ]
    )
    
    # Employment Details
    hire_date = models.DateField(verbose_name="Hire Date")
    
    # National ID with validation (Egyptian National ID is 14 digits)
    national_id_validator = RegexValidator(
        regex=r'^\d{14}$',
        message="National ID must be exactly 14 digits"
    )
    national_id = models.CharField(
        max_length=14,
        unique=True,
        validators=[national_id_validator],
        verbose_name="National ID"
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ad_username']),
            models.Index(fields=['national_id']),
            models.Index(fields=['department']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name_en()} ({self.ad_username})"
    
    def get_full_name_en(self):
        """Return full name in English"""
        return f"{self.first_name_en} {self.last_name_en}"
    
    def get_full_name_ar(self):
        """Return full name in Arabic"""
        return f"{self.first_name_ar} {self.last_name_ar}"
    
    @property
    def full_name_en(self):
        return self.get_full_name_en()
    
    @property
    def full_name_ar(self):
        return self.get_full_name_ar()


class AuditLog(models.Model):
    """
    Audit Log for tracking OU changes
    
    Task 13: Move User Between OUs
    Logs all employee organizational unit changes for compliance and tracking
    """
    
    # Foreign Key to Employee
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='ou_changes',
        verbose_name="Employee"
    )
    
    # OU Information
    old_ou = models.CharField(
        max_length=255,
        verbose_name="Previous OU",
        help_text="Previous organizational unit (e.g., IT or IT/New)"
    )
    
    new_ou = models.CharField(
        max_length=255,
        verbose_name="New OU",
        help_text="New organizational unit (e.g., HR or HR/Management)"
    )
    
    # Change Details
    changed_by = models.CharField(
        max_length=100,
        verbose_name="Changed By",
        help_text="Username of admin who made the change"
    )
    
    changed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Changed At",
        help_text="Timestamp of the change"
    )
    
    # Status
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='success',
        verbose_name="Status",
        help_text="Status of the OU change operation"
    )
    
    # Error message (if failed)
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Error Message",
        help_text="Error message if the move failed"
    )
    
    # Old DN for reference
    old_dn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Old DN",
        help_text="Previous Distinguished Name"
    )
    
    # New DN for reference
    new_dn = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="New DN",
        help_text="New Distinguished Name"
    )
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['employee']),
            models.Index(fields=['changed_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.employee.ad_username}: {self.old_ou} → {self.new_ou} ({self.changed_at.strftime('%Y-%m-%d %H:%M')})"
