"""
LDAP Service for Active Directory Integration
Provides utilities for connecting, binding, and searching AD
"""

from ldap3 import Server, Connection, ALL, SUBTREE, MODIFY_REPLACE
from ldap3.core.exceptions import LDAPException, LDAPBindError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class LDAPService:
    """
    LDAP Service for Active Directory operations
    """
    
    def __init__(self):
        self.server_address = settings.AD_SERVER
        self.server_port = settings.AD_PORT
        self.base_dn = settings.AD_BASE_DN
        self.use_ssl = settings.AD_USE_SSL
        self.server = None
        self.connection = None
    
    def get_server(self):
        """Get LDAP server instance"""
        if not self.server:
            self.server = Server(
                self.server_address,
                port=self.server_port,
                use_ssl=self.use_ssl,
                get_info=ALL
            )
        return self.server
    
    def bind_with_credentials(self, username, password):
        """
        Bind to LDAP server with user credentials
        
        Args:
            username: AD username (sAMAccountName)
            password: User password
            
        Returns:
            tuple: (success: bool, connection: Connection or None, error_message: str or None)
        """
        try:
            # Format username for AD binding
            # Try different formats: DOMAIN\username or username@domain
            user_dn = f"EISSA\\{username}"
            
            server = self.get_server()
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                auto_bind=True
            )
            
            if conn.bind():
                logger.info(f"Successfully authenticated user: {username}")
                return True, conn, None
            else:
                logger.warning(f"Failed to authenticate user: {username}")
                return False, None, "Invalid credentials"
                
        except LDAPBindError as e:
            logger.error(f"LDAP bind error for user {username}: {str(e)}")
            return False, None, "Invalid username or password"
        except LDAPException as e:
            logger.error(f"LDAP exception for user {username}: {str(e)}")
            return False, None, f"LDAP error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during bind for user {username}: {str(e)}")
            return False, None, f"Authentication error: {str(e)}"
    
    def search_user(self, username, connection=None):
        """
        Search for user in Active Directory
        
        Args:
            username: AD username (sAMAccountName)
            connection: Existing LDAP connection (optional)
            
        Returns:
            dict: User attributes or None if not found
        """
        try:
            # Use provided connection or create admin connection
            conn = connection
            close_after = False
            
            if not conn:
                # Use admin bind credentials if available
                admin_user = settings.AD_BIND_USER
                admin_password = settings.AD_BIND_PASSWORD
                
                if admin_user and admin_password:
                    _, conn, _ = self.bind_with_credentials(admin_user, admin_password)
                    close_after = True
                else:
                    logger.error("No connection provided and no admin credentials configured")
                    return None
            
            if not conn:
                return None
            
            # Search for user
            search_filter = f'(sAMAccountName={username})'
            attributes = [
                'cn', 'sAMAccountName', 'mail', 'telephoneNumber',
                'displayName', 'givenName', 'sn', 'distinguishedName',
                'memberOf', 'userPrincipalName', 'department', 'title'
            ]
            
            conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes
            )
            
            if conn.entries:
                entry = conn.entries[0]
                user_data = {
                    'username': str(entry.sAMAccountName) if hasattr(entry, 'sAMAccountName') else username,
                    'email': str(entry.mail) if hasattr(entry, 'mail') else '',
                    'phone': str(entry.telephoneNumber) if hasattr(entry, 'telephoneNumber') else '',
                    'display_name': str(entry.displayName) if hasattr(entry, 'displayName') else '',
                    'first_name': str(entry.givenName) if hasattr(entry, 'givenName') else '',
                    'last_name': str(entry.sn) if hasattr(entry, 'sn') else '',
                    'dn': str(entry.distinguishedName) if hasattr(entry, 'distinguishedName') else '',
                    'upn': str(entry.userPrincipalName) if hasattr(entry, 'userPrincipalName') else '',
                    'department': str(entry.department) if hasattr(entry, 'department') else '',
                    'title': str(entry.title) if hasattr(entry, 'title') else '',
                }
                
                # Extract OU from DN
                if user_data['dn']:
                    user_data['ou'] = self.extract_ou_from_dn(user_data['dn'])
                else:
                    user_data['ou'] = ''
                
                logger.info(f"Found user in AD: {username}")
                
                if close_after:
                    conn.unbind()
                
                return user_data
            else:
                logger.warning(f"User not found in AD: {username}")
                if close_after and conn:
                    conn.unbind()
                return None
                
        except LDAPException as e:
            logger.error(f"LDAP error during user search for {username}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during user search for {username}: {str(e)}")
            return None
    
    def extract_ou_from_dn(self, dn):
        """
        Extract Organizational Unit from Distinguished Name
        
        Args:
            dn: Distinguished Name (e.g., CN=mohamed khaled,OU=projects,OU=New,DC=eissa,DC=local)
            
        Returns:
            str: OU path (e.g., projects/New)
        """
        try:
            parts = dn.split(',')
            ou_parts = [part.split('=')[1] for part in parts if part.strip().startswith('OU=')]
            return '/'.join(ou_parts) if ou_parts else ''
        except Exception as e:
            logger.error(f"Error extracting OU from DN {dn}: {str(e)}")
            return ''
    
    def move_user_to_ou(self, username, new_ou, connection=None):
        """
        Move user to a different Organizational Unit (Phase 2)
        
        Args:
            username: AD username
            new_ou: New OU DN (e.g., OU=IT,OU=New,DC=eissa,DC=local)
            connection: Existing LDAP connection (optional)
            
        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        try:
            # Get current user DN
            user_data = self.search_user(username, connection)
            if not user_data or not user_data.get('dn'):
                return False, "User not found in AD"
            
            old_dn = user_data['dn']
            
            # Extract CN from old DN
            cn = old_dn.split(',')[0]
            
            # Use provided connection or create admin connection
            conn = connection
            close_after = False
            
            if not conn:
                admin_user = settings.AD_BIND_USER
                admin_password = settings.AD_BIND_PASSWORD
                
                if admin_user and admin_password:
                    _, conn, _ = self.bind_with_credentials(admin_user, admin_password)
                    close_after = True
                else:
                    return False, "No admin credentials configured"
            
            if not conn:
                return False, "Could not establish LDAP connection"
            
            # Move user
            success = conn.modify_dn(old_dn, cn, new_superior=new_ou)
            
            if close_after:
                conn.unbind()
            
            if success:
                logger.info(f"Successfully moved user {username} from {old_dn} to {new_ou}")
                return True, None
            else:
                logger.error(f"Failed to move user {username}: {conn.result}")
                return False, f"Move failed: {conn.result}"
                
        except LDAPException as e:
            logger.error(f"LDAP error during user move for {username}: {str(e)}")
            return False, f"LDAP error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during user move for {username}: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def test_connection(self):
        """
        Test LDAP connection to AD server
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            server = self.get_server()
            # Try anonymous bind just to test connection
            conn = Connection(server, auto_bind=True)
            conn.unbind()
            return True, f"Successfully connected to {self.server_address}:{self.server_port}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"


# Singleton instance
ldap_service = LDAPService()
