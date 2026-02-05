# 🧪 Test Mode Guide - Login Flow Testing

## Overview
This guide explains how to run comprehensive tests for the authentication and login flow system.

---

## 📋 What Gets Tested

### 1. **LDAP Service Tests**
- ✅ LDAP bind with valid credentials
- ✅ LDAP bind with invalid credentials
- ✅ LDAP user search functionality
- ✅ LDAP server connection

### 2. **Authentication Backend Tests**
- ✅ Successful authentication against AD
- ✅ Failed authentication with invalid credentials
- ✅ Missing credentials handling

### 3. **Employee Model Tests**
- ✅ Employee creation with all fields
- ✅ Employee full name generation (Arabic & English)
- ✅ String representation
- ✅ Unique AD username validation
- ✅ Unique National ID validation

### 4. **Login View Tests**
- ✅ Login page loads successfully
- ✅ Login form displays all required fields
- ✅ Successful login with valid credentials
- ✅ Failed login with invalid credentials
- ✅ Login with empty fields
- ✅ Already authenticated user redirects to dashboard
- ✅ Logout functionality

### 5. **Dashboard View Tests**
- ✅ Dashboard requires authentication
- ✅ Dashboard loads for authenticated users
- ✅ Dashboard displays employee and AD data

### 6. **Login Form Tests**
- ✅ Form validation with valid data
- ✅ Form validation with missing username
- ✅ Form validation with missing password

### 7. **Integration Tests**
- ✅ Complete login flow (end-to-end):
  1. Load login page
  2. Submit credentials
  3. Get authenticated
  4. Access dashboard
  5. Logout successfully
  6. Verify access denied after logout

---

## 🚀 Running Tests

### Option 1: Run All Tests
```bash
python manage.py test
```

### Option 2: Run Specific Test Class
```bash
# LDAP Service Tests
python manage.py test authentication.tests.LDAPServiceTests

# Authentication Backend Tests
python manage.py test authentication.tests.LDAPAuthenticationBackendTests

# Employee Model Tests
python manage.py test authentication.tests.EmployeeModelTests

# Login View Tests
python manage.py test authentication.tests.LoginViewTests

# Dashboard View Tests
python manage.py test authentication.tests.DashboardViewTests

# Login Form Tests
python manage.py test authentication.tests.LoginFormTests

# Integration Tests
python manage.py test authentication.tests.IntegrationTests
```

### Option 3: Run Specific Test Method
```bash
# Test successful LDAP bind
python manage.py test authentication.tests.LDAPServiceTests.test_ldap_bind_success

# Test login page loads
python manage.py test authentication.tests.LoginViewTests.test_login_page_loads

# Test complete login flow
python manage.py test authentication.tests.IntegrationTests.test_complete_login_flow
```

### Option 4: Run Tests with Verbosity
```bash
# Level 0 - Minimal output
python manage.py test --verbosity=0

# Level 1 - Normal output (default)
python manage.py test --verbosity=1

# Level 2 - Verbose output
python manage.py test --verbosity=2

# Level 3 - Maximum verbosity
python manage.py test --verbosity=3
```

### Option 5: Run Tests with Coverage Report
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # Generates HTML report in htmlcov/
```

---

## 📊 Test Statistics

Total Tests: **30+**

| Test Category | Count | Status |
|--------------|-------|--------|
| LDAP Service | 4 | ✅ |
| Auth Backend | 3 | ✅ |
| Employee Model | 5 | ✅ |
| Login Views | 8 | ✅ |
| Dashboard Views | 3 | ✅ |
| Form Validation | 3 | ✅ |
| Integration | 1 | ✅ |
| **Total** | **30** | ✅ |

---

## 🔍 Understanding Test Output

### Successful Test Output
```
test_ldap_bind_success (__main__.LDAPServiceTests) ... ok
test_login_page_loads (__main__.LoginViewTests) ... ok
✅ Login page loads test passed
```

### Failed Test Output
```
FAIL: test_login_fails_with_wrong_password
AssertionError: 302 != 200
```

### Error Output
```
ERROR: test_ldap_connection
DatabaseError: Connection refused
```

---

## 🛠️ Test Mocking Strategy

All LDAP and AD calls are **mocked** to avoid needing:
- Active Directory server running
- Network connectivity
- Real AD credentials

### Mocked Components:
1. **LDAP Server** - `@patch('authentication.ldap_service.Server')`
2. **LDAP Connection** - `@patch('authentication.ldap_service.Connection')`
3. **Authentication** - `@patch('authentication.views.authenticate')`
4. **LDAP Service** - `@patch('authentication.views.ldap_service')`

---

## 📝 Test Database

Tests use an **in-memory SQLite database** that:
- Creates test data automatically
- Runs in isolation
- Cleans up after each test
- Does NOT affect production data

---

## 🐛 Debugging Failed Tests

### 1. Get More Details
```bash
python manage.py test --verbosity=3
```

### 2. Run Single Test
```bash
python manage.py test authentication.tests.LoginViewTests.test_login_page_loads -v 3
```

### 3. Add Print Statements
Edit the test file and add `print()` statements, then run:
```bash
python manage.py test --verbosity=3 -k  # Keep print statements visible
```

### 4. Use Python Debugger
```python
import pdb; pdb.set_trace()  # Add in test method
```

---

## 📦 Quick Test Script

Create a file `run_tests.sh`:
```bash
#!/bin/bash

echo "🧪 Running All Tests..."
python manage.py test --verbosity=2

echo ""
echo "📊 Running Coverage..."
coverage run --source='.' manage.py test
coverage report --omit='*/venv/*'

echo ""
echo "✅ Tests Complete!"
```

Make it executable:
```bash
chmod +x run_tests.sh
./run_tests.sh
```

---

## 🔑 Key Test Features

### 1. **Isolation**
Each test class has its own `setUp()` and `tearDown()`:
```python
def setUp(self):
    # Create test data
    self.user = User.objects.create_user(...)

def tearDown(self):
    # Automatic cleanup by Django
```

### 2. **Mocking**
```python
@patch('authentication.ldap_service.Connection')
def test_example(self, mock_connection):
    mock_connection.return_value.bind.return_value = True
```

### 3. **Assertions**
```python
self.assertEqual(result, expected)
self.assertTrue(condition)
self.assertIn(value, list)
self.assertIsNone(value)
```

---

## ✅ Expected Test Results

When all tests pass, you should see:
```
Ran 30 tests in 2.345s

OK ✅
```

With logging output:
```
✅ LDAP bind success test passed
✅ Login page loads test passed
✅ Authentication success test passed
✅ Employee creation test passed
✅ Successful login test passed
✅ Complete login flow integration test PASSED
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "No database"
```
DatabaseError: no such table: auth_user
```
**Solution:** Run migrations first
```bash
python manage.py migrate
```

### Issue 2: "ImportError"
```
ImportError: No module named 'ldap3'
```
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue 3: "Test database doesn't support transactions"
**Solution:** Add to settings.py
```python
DATABASES = {
    'default': {
        # ... other settings ...
        'TEST': {
            'NAME': ':memory:',
        }
    }
}
```

---

## 📚 Test Files Location

```
/venv/src/
├── authentication/
│   └── tests.py              # ← Main test file
├── Employee/
│   └── tests.py              # ← Employee model tests
└── TEST_MODE_GUIDE.md        # ← This file
```

---

## 🎯 Next Steps

1. **Run all tests:**
   ```bash
   python manage.py test
   ```

2. **Review test coverage:**
   ```bash
   coverage report
   ```

3. **Fix any failures:**
   - Check error messages
   - Debug with verbosity level 3
   - Review test documentation

4. **Add more tests as needed:**
   - For new features
   - For bug fixes
   - For edge cases

---

## 📞 Support

For test-related questions:
- Check this guide first
- Review test file comments
- Use `--verbosity=3` for more details
- Add your own print statements for debugging

---

**Happy Testing! 🚀**
