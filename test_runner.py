#!/usr/bin/env python
"""
🧪 Interactive Test Runner for Login Flow
Provides an interactive menu to run different test suites
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.test.utils import get_runner
from django.conf import settings


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header():
    """Print header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║       🧪 Active Directory Login Flow Test Suite 🧪              ║")
    print("║           Interactive Test Runner v1.0                         ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}\n")


def print_menu():
    """Print test menu"""
    print(f"{Colors.CYAN}{Colors.BOLD}Available Test Suites:{Colors.ENDC}\n")
    print(f"{Colors.GREEN}  1.{Colors.ENDC} Run ALL Tests")
    print(f"{Colors.GREEN}  2.{Colors.ENDC} LDAP Service Tests")
    print(f"{Colors.GREEN}  3.{Colors.ENDC} Authentication Backend Tests")
    print(f"{Colors.GREEN}  4.{Colors.ENDC} Employee Model Tests")
    print(f"{Colors.GREEN}  5.{Colors.ENDC} Login View Tests")
    print(f"{Colors.GREEN}  6.{Colors.ENDC} Form Validation Tests")
    print(f"{Colors.GREEN}  7.{Colors.ENDC} Dashboard View Tests")
    print(f"{Colors.GREEN}  8.{Colors.ENDC} Complete Integration Tests")
    print(f"{Colors.GREEN}  9.{Colors.ENDC} Run with Coverage Report")
    print(f"{Colors.GREEN}  10.{Colors.ENDC} Run with Maximum Verbosity")
    print(f"{Colors.GREEN}  0.{Colors.ENDC} Exit")
    print()


def run_tests(test_name, verbosity=2):
    """Run specific tests"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}→ Running: {test_name}{Colors.ENDC}\n")
    try:
        if test_name == "all":
            call_command('test', verbosity=verbosity)
        elif test_name == "ldap":
            call_command('test', 'authentication.tests.LDAPServiceTests', verbosity=verbosity)
        elif test_name == "auth":
            call_command('test', 'authentication.tests.LDAPAuthenticationBackendTests', verbosity=verbosity)
        elif test_name == "employee":
            call_command('test', 'authentication.tests.EmployeeModelTests', verbosity=verbosity)
        elif test_name == "login":
            call_command('test', 'authentication.tests.LoginViewTests', verbosity=verbosity)
        elif test_name == "form":
            call_command('test', 'authentication.tests.LoginFormTests', verbosity=verbosity)
        elif test_name == "dashboard":
            call_command('test', 'authentication.tests.DashboardViewTests', verbosity=verbosity)
        elif test_name == "integration":
            call_command('test', 'authentication.tests.IntegrationTests', verbosity=verbosity)
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Tests completed successfully!{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Tests failed: {str(e)}{Colors.ENDC}\n")


def run_coverage():
    """Run tests with coverage"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}→ Running Tests with Coverage Report{Colors.ENDC}\n")
    try:
        # Run with coverage
        subprocess.run([
            sys.executable, '-m', 'coverage', 'run', 
            '--source=.', 'manage.py', 'test'
        ], check=True)
        
        # Print coverage report
        print(f"\n{Colors.CYAN}{Colors.BOLD}Coverage Report:{Colors.ENDC}\n")
        subprocess.run([
            sys.executable, '-m', 'coverage', 'report',
            '--omit=*/venv/*,*/migrations/*'
        ], check=True)
        
        # Generate HTML report
        print(f"\n{Colors.YELLOW}Generating HTML coverage report...{Colors.ENDC}\n")
        subprocess.run([
            sys.executable, '-m', 'coverage', 'html',
            '--omit=*/venv/*,*/migrations/*'
        ], check=True)
        
        print(f"{Colors.GREEN}{Colors.BOLD}✅ Coverage report generated in htmlcov/index.html{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ Coverage failed: {str(e)}{Colors.ENDC}\n")


def print_test_stats():
    """Print test statistics"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}📊 Test Statistics:{Colors.ENDC}\n")
    
    stats = {
        "LDAP Service Tests": 4,
        "Auth Backend Tests": 3,
        "Employee Model Tests": 5,
        "Login View Tests": 8,
        "Form Validation Tests": 3,
        "Dashboard View Tests": 3,
        "Integration Tests": 1,
    }
    
    total = 0
    for test_name, count in stats.items():
        print(f"  {Colors.GREEN}●{Colors.ENDC} {test_name}: {Colors.BOLD}{count}{Colors.ENDC} tests")
        total += count
    
    print(f"\n  {Colors.BOLD}Total: {total} tests{Colors.ENDC}\n")


def main():
    """Main interactive menu"""
    print_header()
    
    while True:
        print_test_stats()
        print_menu()
        
        choice = input(f"{Colors.BOLD}Enter your choice (0-10): {Colors.ENDC}").strip()
        
        if choice == "0":
            print(f"{Colors.YELLOW}Exiting...{Colors.ENDC}\n")
            break
        elif choice == "1":
            run_tests("all")
        elif choice == "2":
            run_tests("ldap")
        elif choice == "3":
            run_tests("auth")
        elif choice == "4":
            run_tests("employee")
        elif choice == "5":
            run_tests("login")
        elif choice == "6":
            run_tests("form")
        elif choice == "7":
            run_tests("dashboard")
        elif choice == "8":
            run_tests("integration")
        elif choice == "9":
            run_coverage()
        elif choice == "10":
            run_tests("all", verbosity=3)
        else:
            print(f"{Colors.RED}Invalid choice! Please try again.{Colors.ENDC}\n")
        
        input(f"{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
        print("\033[H\033[J")  # Clear screen
        print_header()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test runner interrupted.{Colors.ENDC}\n")
        sys.exit(0)
