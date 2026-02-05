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
