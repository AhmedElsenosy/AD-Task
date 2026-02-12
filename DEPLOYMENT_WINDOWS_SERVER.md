# Windows Server Deployment Guide

## Overview
This guide provides step-by-step instructions to deploy the Active Directory Integration System on Windows Server 2019/2022.

---

## Prerequisites

Before starting, ensure:
- ✅ Windows Server 2019 or 2022 installed
- ✅ Administrator access
- ✅ SQL Server installed (2016 or newer)
- ✅ Active Directory running on your network
- ✅ ODBC Driver 17 for SQL Server installed
- ✅ Python 3.9+ NOT installed (we'll install it)

---

## Phase 1: Python Environment Setup

### Step 1: Install Python

1. **Download Python 3.11** from [python.org](https://www.python.org/downloads/)
   - Choose: Windows installer (64-bit)
   
2. **Run the installer:**
   - ☑️ **IMPORTANT:** Check "Add Python to PATH"
   - ☑️ Check "Install pip"
   - Choose "Install Now" or customize installation
   
3. **Verify installation** in PowerShell:
   ```powershell
   python --version
   pip --version
   ```
   Expected output:
   ```
   Python 3.11.x
   pip 23.x.x
   ```

### Step 2: Install ODBC Driver for SQL Server

1. Download **ODBC Driver 17 for SQL Server 64-bit** from:
   https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

2. Run the installer and follow the prompts

3. Verify in PowerShell:
   ```powershell
   odbcconf /l
   ```
   You should see "ODBC Driver 17 for SQL Server" in the list

---

## Phase 2: Project Setup

### Step 3: Copy Project Folder

1. Copy your project folder to a production location:
   ```powershell
   # Example: C:\WebApps\AD-Task
   Copy-Item -Path "C:\Users\asome\Desktop\Logic Leap Project\AD-Task" -Destination "C:\WebApps\AD-Task" -Recurse
   ```

2. Navigate to project:
   ```powershell
   cd C:\WebApps\AD-Task
   ```

### Step 4: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Step 5: Install Python Dependencies

```powershell
# Make sure virtual environment is activated
pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt

# Verify installations
pip list | grep -E "Django|mssql|ldap3|gunicorn"
```

---

## Phase 3: Database & Environment Configuration

### Step 6: Configure Environment Variables

1. **Copy your existing .env file** to the Windows Server at `C:\WebApps\AD-Task\.env`
   
2. Verify all settings are correct for your Windows Server environment:
   ```ini
   SECRET_KEY=<generate-new-key>
   DEBUG=False
   ALLOWED_HOSTS=your-server-ip,your-domain.com
   
   # Database settings
   DB_HOST=your-sql-server-ip
   DB_USER=sa
   DB_PASSWORD=your-password
   
   # AD settings
   AD_SERVER=your-domain.com
   AD_BASE_DN=DC=your-domain,DC=com
   ```

3. **Generate a secure SECRET_KEY:**
   ```powershell
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Step 7: Initialize Database

```powershell
# Make sure virtual environment is activated and in project directory

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser
# Follow the prompts to create admin account

# Collect static files
python manage.py collectstatic --noinput
```

---

## Phase 4: Choose Your Web Server

### Option A: Using Gunicorn + IIS (Recommended)

#### Step 8a: Install Gunicorn

```powershell
pip install gunicorn

# Verify
gunicorn --version
```

#### Step 8b: Test with Gunicorn

```powershell
# Test locally (in project directory)
gunicorn --bind 127.0.0.1:8000 core.wsgi:application

# Should see:
# [INFO] Starting gunicorn
# [INFO] Listening at: http://127.0.0.1:8000
```

#### Step 8c: Configure IIS

1. **Open IIS Manager:**
   ```powershell
   inetmgr
   ```

2. **Add Application Pool:**
   - Right-click "Application Pools" → Add Application Pool
   - Name: `AD-Task`
   - .NET CLR version: `No Managed Code`
   - Identity: `ApplicationPoolIdentity`
   - Advanced Settings: Set `loadUserProfile` to `True`

3. **Create IIS Website:**
   - Right-click "Sites" → Add Website
   - Site name: `Active Directory Admin`
   - Physical path: `C:\WebApps\AD-Task`
   - Host name: Your server IP or domain
   - Port: 80 (or 443 for HTTPS)
   - Application pool: `AD-Task`

4. **Add URL Rewrite Rule** (IIS URL Rewrite module must be installed):
   See `web.config` in project root for details

#### Step 8d: Configure Windows Service (Optional but Recommended)

Create a Windows Service to run Gunicorn automatically:

1. Install `pywin32`:
   ```powershell
   pip install pywin32
   python Scripts/pywin32_postinstall.py -install
   ```

2. Create batch file `C:\WebApps\AD-Task\start-gunicorn.bat`:
   ```batch
   @echo off
   cd C:\WebApps\AD-Task
   C:\WebApps\AD-Task\venv\Scripts\gunicorn.exe --bind 127.0.0.1:8000 ^
       --workers 4 ^
       --timeout 300 ^
       --access-logfile logs/access.log ^
       --error-logfile logs/error.log ^
       core.wsgi:application
   ```

3. Create logs folder:
   ```powershell
   mkdir C:\WebApps\AD-Task\logs
   ```

---

### Option B: Using FastCGI with IIS (Advanced)

Requires additional Python FastCGI adapter - see IIS documentation.

---

## Phase 5: Security & Configuration

### Step 9: Disable Debug Mode

Ensure `.env` has:
```ini
DEBUG=False
```

### Step 10: Configure Firewall

```powershell
# Allow HTTP (port 80)
netsh advfirewall firewall add rule name="Allow HTTP" dir=in action=allow protocol=tcp localport=80

# Allow HTTPS (port 443)
netsh advfirewall firewall add rule name="Allow HTTPS" dir=in action=allow protocol=tcp localport=443

# Allow SQL Server (port 1433) - if on same server
netsh advfirewall firewall add rule name="Allow SQL Server" dir=in action=allow protocol=tcp localport=1433
```

### Step 11: Set File Permissions

```powershell
# Make sure project folder has proper permissions
icacls "C:\WebApps\AD-Task" /grant:r "IIS AppPool\AD-Task:(OI)(CI)F"
icacls "C:\WebApps\AD-Task\logs" /grant:r "IIS AppPool\AD-Task:(OI)(CI)F"
icacls "C:\WebApps\AD-Task\media" /grant:r "IIS AppPool\AD-Task:(OI)(CI)F"
```

---

## Phase 6: Testing & Verification

### Step 12: Test the Application

1. **Open your browser:**
   ```
   http://your-server-ip
   ```

2. **Expected pages:**
   - Admin interface: `http://your-server-ip/admin`
   - Login page: `http://your-server-ip/authentication/login`
   - Dashboard: `http://your-server-ip/dashboard`

3. **Test AD login:**
   - Username: `DOMAIN\username`
   - Password: Your AD password

### Step 13: Check Logs

```powershell
# Check web server logs
Get-Content C:\WebApps\AD-Task\logs\access.log -Tail 20

# Check error logs
Get-Content C:\WebApps\AD-Task\logs\error.log -Tail 20
```

---

## Phase 7: HTTPS Setup (Recommended)

### Step 14: Obtain SSL Certificate

1. **Option A: Self-signed (Testing only)**
   ```powershell
   $cert = New-SelfSignedCertificate -DnsName "your-domain" -CertStoreLocation "cert:\LocalMachine\My"
   ```

2. **Option B: Let's Encrypt (Free)**
   - Use Certbot with IIS plugin
   - https://certbot.eff.org/instructions?ws=iis&os=windows

3. **Option C: Commercial Certificate**
   - Purchase from trusted CA
   - Install in IIS

### Step 15: Configure HTTPS in IIS

1. Bind the certificate in IIS
2. Update `ALLOWED_HOSTS` in `.env`:
   ```ini
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   CSRF_TRUSTED_ORIGINS=https://your-domain.com
   ```

---

## Troubleshooting

### Python Not Found
- Ensure Python is in PATH: `python --version`
- Restart PowerShell after Python installation

### Database Connection Failed
- Verify SQL Server is running
- Check credentials in `.env`
- Test connection: `python manage.py dbshell`

### ODBC Driver Error
```
Error: ('HY000', '[HY000] [Microsoft][ODBC Driver 17 for SQL Server]...
```
- Install ODBC Driver 17 as described in Phase 1, Step 2
- Restart application after installation

### LDAP/AD Not Connecting
- Verify AD server is reachable: `Test-NetConnection -ComputerName your-domain.com -Port 389`
- Check AD credentials in `.env`
- Contact AD administrator for service account permissions

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput`
- Check IIS physical path is correct
- Verify file permissions on `staticfiles` folder

### Port Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr ":8000"

# Kill process if needed
taskkill /PID <process-id> /F
```

---

## Maintenance & Updates

### Regular Tasks

**Weekly:**
- Check error logs for issues
- Monitor disk space

**Monthly:**
- Review audit logs
- Check Python package updates:
  ```powershell
  pip list --outdated
  ```

**Quarterly:**
- Update Python packages (in test environment first)
- Backup database

---

## Backup & Restore

### Backup Database

```powershell
# Create backup script
sqlcmd -S your-sql-server -U sa -P password ^
  -Q "BACKUP DATABASE employee_ad_db TO DISK = 'C:\Backups\employee_ad_db_backup.bak'"
```

### Backup Application

```powershell
# Zip project folder regularly
$date = Get-Date -Format "yyyy-MM-dd"
Compress-Archive -Path "C:\WebApps\AD-Task" -DestinationPath "C:\Backups\AD-Task_$date.zip"
```

---

## Support & Documentation

- Django Documentation: https://docs.djangoproject.com/
- LDAP3 Documentation: https://ldap3.readthedocs.io/
- SQL Server: https://learn.microsoft.com/en-us/sql/
- IIS: https://learn.microsoft.com/en-us/iis/

---

## Quick Reference Commands

```powershell
# Activate virtual environment
cd C:\WebApps\AD-Task
.\venv\Scripts\Activate.ps1

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Test with development server (local only)
python manage.py runserver

# Run with production Gunicorn
gunicorn --bind 127.0.0.1:8000 --workers 4 core.wsgi:application

# Check Python version
python --version

# Check pip packages
pip list

# Deactivate virtual environment
deactivate
```

---

**Last Updated:** February 2026
**Version:** 1.0
**Status:** Production Ready
