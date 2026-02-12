# Deployment Checklist - Windows Server

Use this checklist to ensure your deployment is complete and correct before going live.

## Pre-Deployment (Before Moving to Server)

- [ ] **Code Review**
  - [ ] All changes committed to version control
  - [ ] No debug code left behind
  - [ ] All required dependencies in `requirements.txt`
  - [ ] `.gitignore` properly configured

- [ ] **Configuration Files**
  - [ ] `.env` file exists with all configuration values
  - [ ] `web.config` in project root
  - [ ] `DEPLOYMENT_WINDOWS_SERVER.md` reviewed
- [ ] `.env` file copied to Windows Server

- [ ] **Database**
  - [ ] SQL Server backup created
  - [ ] Database migration scripts prepared
  - [ ] Test migrations run successfully in dev

- [ ] **Static Files**
  - [ ] All CSS/JS files are in `static/` folder
  - [ ] Images optimized
  - [ ] `collectstatic` command tested locally

---

## Server Environment Setup

### Windows Server Prerequisites

- [ ] **Operating System**
  - [ ] Windows Server 2019 or 2022
  - [ ] Latest Windows Updates installed
  - [ ] System rebooted after updates

- [ ] **Required Software**
  - [ ] Python 3.9+ installed (Add to PATH ✓)
  - [ ] SQL Server 2016+ installed and running
  - [ ] ODBC Driver 17 for SQL Server installed
  - [ ] IIS installed with URL Rewrite module
  - [ ] PowerShell 5.1 or newer

- [ ] **Network & Firewall**
  - [ ] Port 80 (HTTP) open
  - [ ] Port 443 (HTTPS) open (if using SSL)
  - [ ] Port 1433 (SQL Server) accessible
  - [ ] Connection to AD server verified (port 389)
  - [ ] DNS configured for domain names

---

## Application Deployment

### Step 1: Copy Project

- [ ] Project folder copied to `C:\WebApps\AD-Task`
- [ ] File permissions allow IIS App Pool access
- [ ] Logs folder created and writable
- [ ] Media folder created and writable

### Step 2: Python Environment

- [ ] Virtual environment created: `venv\`
- [ ] Virtual environment activated
- [ ] pip upgraded to latest
- [ ] All requirements installed successfully
  ```powershell
  pip install -r requirements.txt
  ```
- [ ] No installation errors or warnings

### Step 3: Environment Variables

- [ ] `.env` file copied to Windows Server in project root
- [ ] Verify all required variables are present:
  - [ ] SECRET_KEY (new, unique value)
  - [ ] DEBUG=False
  - [ ] ALLOWED_HOSTS configured
  - [ ] DB_HOST points to SQL Server
  - [ ] DB_USER and DB_PASSWORD correct
  - [ ] AD_SERVER configured
  - [ ] AD_BASE_DN configured
  - [ ] AD_BIND_USER and password set

### Step 4: Database Migration

- [ ] Database created in SQL Server
- [ ] Migrations run successfully:
  ```powershell
  python manage.py migrate
  ```
- [ ] Superuser created:
  ```powershell
  python manage.py createsuperuser
  ```
- [ ] Test data loaded (if applicable)
- [ ] Database backup created

### Step 5: Static Files

- [ ] Static files collected:
  ```powershell
  python manage.py collectstatic --noinput
  ```
- [ ] staticfiles folder created with all assets
- [ ] CSS/JS files accessible

### Step 6: Application Testing

- [ ] Development server starts successfully:
  ```powershell
  python manage.py runserver
  ```
- [ ] Admin interface loads: `/admin`
- [ ] Login page loads: `/authentication/login`
- [ ] Dashboard loads (if authenticated): `/dashboard`
- [ ] No error messages in console

### Step 7: Gunicorn Testing

- [ ] Gunicorn installed: `pip install gunicorn`
- [ ] Gunicorn starts successfully:
  ```powershell
  gunicorn --bind 127.0.0.1:8000 core.wsgi:application
  ```
- [ ] Application accessible at `http://127.0.0.1:8000`
- [ ] All pages load correctly
- [ ] Static files display properly

---

## IIS Configuration

### Step 8: IIS Setup

- [ ] IIS Manager opened
- [ ] New Application Pool created: `AD-Task`
  - [ ] .NET CLR version: `No Managed Code`
  - [ ] Identity: `ApplicationPoolIdentity`
  - [ ] loadUserProfile: `True`

- [ ] New Website created
  - [ ] Physical path: `C:\WebApps\AD-Task`
  - [ ] Site name: `Active Directory Admin`
  - [ ] Application pool: `AD-Task`
  - [ ] Host name: Your domain/IP
  - [ ] Port: 80 (or 443 for HTTPS)

- [ ] File permissions set
  ```powershell
  icacls "C:\WebApps\AD-Task" /grant:r "IIS AppPool\AD-Task:(OI)(CI)F"
  icacls "C:\WebApps\AD-Task\logs" /grant:r "IIS AppPool\AD-Task:(OI)(CI)F"
  icacls "C:\WebApps\AD-Task\media" /grant:r "IIS AppPool\AD-Task:(OI)(CI)F"
  ```

### Step 9: URL Rewrite

- [ ] IIS URL Rewrite module installed
- [ ] `web.config` in project root
- [ ] URL Rewrite rules configured:
  - [ ] HTTP to HTTPS redirect (if using SSL)
  - [ ] Proxy to Gunicorn on port 8000
  - [ ] Static files bypass (optional)

---

## Security Verification

- [ ] **Django Security**
  - [ ] DEBUG = False
  - [ ] SECRET_KEY is unique and strong
  - [ ] SECURE_SSL_REDIRECT = True (if HTTPS)
  - [ ] SESSION_COOKIE_SECURE = True
  - [ ] CSRF_COOKIE_SECURE = True
  - [ ] ALLOWED_HOSTS configured correctly
  - [ ] CSRF_TRUSTED_ORIGINS set correctly

- [ ] **Server Security**
  - [ ] Firewall rules applied
  - [ ] Unnecessary ports closed
  - [ ] Directory listing disabled
  - [ ] Dangerous file extensions blocked (`.exe`, `.bat`, etc.)

- [ ] **Database Security**
  - [ ] SQL Server set to authenticate users (not sa account)
  - [ ] Database backups configured
  - [ ] Connection strings use encrypted passwords

- [ ] **Email/Logging** (Optional)
  - [ ] Email configured for admin alerts
  - [ ] Log file rotation configured
  - [ ] Sensitive data not logged

---

## SSL/HTTPS Setup (Recommended)

- [ ] SSL Certificate obtained
  - [ ] [ ] Self-signed (testing only)
  - [ ] [ ] Let's Encrypt (free)
  - [ ] [ ] Commercial CA

- [ ] Certificate installed in IIS
- [ ] HTTPS binding created on port 443
- [ ] HTTP redirects to HTTPS (in web.config)
- [ ] Certificate renewal process scheduled

---

## Testing & Validation

### Functional Testing

- [ ] **Login/Authentication**
  - [ ] Admin login works with superuser credentials
  - [ ] AD login works with domain credentials
  - [ ] Invalid credentials rejected
  - [ ] Session timeout works

- [ ] **Pages Load Correctly**
  - [ ] Home page: `/`
  - [ ] Login page: `/authentication/login`
  - [ ] Admin interface: `/admin`
  - [ ] Dashboard: `/dashboard`
  - [ ] Employee list: (check in admin)

- [ ] **Database Operations**
  - [ ] Can view employee records
  - [ ] Can create new records
  - [ ] Can edit existing records
  - [ ] Can search/filter records

- [ ] **Active Directory**
  - [ ] Can authenticate with AD credentials
  - [ ] AD employee data loads correctly
  - [ ] AD sync works as expected

- [ ] **Static Files**
  - [ ] CSS stylesheets load
  - [ ] JavaScript files load
  - [ ] Images display correctly
  - [ ] Admin interface looks good

- [ ] **Error Handling**
  - [ ] 404 pages display correctly
  - [ ] 500 errors logged properly
  - [ ] No sensitive data in error messages

### Performance Testing

- [ ] Application loads in < 2 seconds
- [ ] No obvious lag in page navigation
- [ ] Database queries complete quickly
- [ ] Memory usage is reasonable

### Browser Compatibility

- [ ] Chrome works
- [ ] Firefox works
- [ ] Edge works
- [ ] Safari works (if applicable)

---

## Monitoring & Logging

- [ ] **Logs Configured**
  - [ ] Application logs: `logs/error.log`
  - [ ] Access logs: `logs/access.log`
  - [ ] Gunicorn logs configured
  - [ ] IIS logs accessible

- [ ] **Log Rotation**
  - [ ] Log files don't grow infinitely
  - [ ] Old logs archived/deleted
  - [ ] Disk space monitored

- [ ] **Error Monitoring**
  - [ ] Error log checked for issues
  - [ ] Admin email alerts configured (optional)
  - [ ] Error dashboard set up (optional)

---

## Post-Deployment

- [ ] Users notified of go-live
- [ ] Support team trained on application
- [ ] Documentation shared with team
- [ ] Backup schedule created
- [ ] Monitoring in place for 24/7
- [ ] Incident response plan established

---

## Rollback Plan

In case of critical issues on day 1:

- [ ] Previous version backed up
- [ ] Rollback procedure tested
- [ ] Rollback team identified
- [ ] Rollback communication plan ready

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| **Developer** | | | |
| **System Admin** | | | |
| **Project Manager** | | | |
| **IT Manager** | | | |

---

## Notes & Issues Found

```
[Use this section to document any issues found during deployment
and how they were resolved]




```

---

**Deployment Date:** ________________
**Deployed To:** ____________________
**By:** ____________________________
**Status:** ✅ COMPLETE / ❌ INCOMPLETE
