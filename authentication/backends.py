"""
Custom Django Authentication Backend for Active Directory (LDAP)
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from Employee.models import Employee
from .ldap_service import ldap_service
import logging

logger = logging.getLogger(__name__)


class LDAPAuthenticationBackend(BaseBackend):
    """
    Authenticate against Active Directory using LDAP
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user against Active Directory
        
        Args:
            request: HTTP request
            username: AD username (sAMAccountName)
            password: User password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if not username or not password:
            return None
        
        try:
            # Step 1: Authenticate against Active Directory
            success, connection, error = ldap_service.bind_with_credentials(username, password)
            
            if not success:
                logger.warning(f"AD authentication failed for user: {username}")
                return None
            
            # Step 2: Search for user in AD to get additional information
            ad_user_data = ldap_service.search_user(username, connection)
            
            if connection:
                connection.unbind()
            
            if not ad_user_data:
                logger.warning(f"User found in AD but could not retrieve data: {username}")
                return None
            
            # Step 3: Check if employee exists in database
            try:
                employee = Employee.objects.get(ad_username=username)
            except Employee.DoesNotExist:
                logger.warning(f"User {username} authenticated in AD but not found in Employee database")
                return None
            
            # Step 4: Get or create Django User for session management
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': ad_user_data.get('email', ''),
                    'first_name': ad_user_data.get('first_name', ''),
                    'last_name': ad_user_data.get('last_name', ''),
                    'is_staff': False,
                    'is_superuser': False,
                }
            )
            
            # Update user information from AD
            if not created:
                user.email = ad_user_data.get('email', '')
                user.first_name = ad_user_data.get('first_name', '')
                user.last_name = ad_user_data.get('last_name', '')
                user.save()
            
            # Attach employee and AD data to user object for use in views
            user.employee = employee
            user.ad_data = ad_user_data
            
            logger.info(f"Successfully authenticated user: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error during authentication for user {username}: {str(e)}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID for session management
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
