#!/bin/bash

# 🧪 Test Runner Script for Login Flow Testing
# Usage: ./run_tests.sh [option]
# Examples:
#   ./run_tests.sh all              # Run all tests
#   ./run_tests.sh ldap             # Run LDAP tests
#   ./run_tests.sh auth             # Run auth backend tests
#   ./run_tests.sh login            # Run login view tests
#   ./run_tests.sh dashboard        # Run dashboard tests
#   ./run_tests.sh integration      # Run integration tests
#   ./run_tests.sh coverage         # Run with coverage report
#   ./run_tests.sh verbose          # Run with verbose output

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
print_header() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║          🧪 Active Directory Login Flow Test Suite 🧪           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Print section
print_section() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Print success
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Print error
print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Run all tests
run_all_tests() {
    print_section "Running ALL Tests"
    python manage.py test --verbosity=2
    if [ $? -eq 0 ]; then
        print_success "All tests completed successfully!"
    else
        print_error "Some tests failed!"
        exit 1
    fi
}

# Run LDAP service tests
run_ldap_tests() {
    print_section "Running LDAP Service Tests"
    python manage.py test authentication.tests.LDAPServiceTests --verbosity=2
}

# Run authentication backend tests
run_auth_tests() {
    print_section "Running Authentication Backend Tests"
    python manage.py test authentication.tests.LDAPAuthenticationBackendTests --verbosity=2
}

# Run login view tests
run_login_tests() {
    print_section "Running Login View Tests"
    python manage.py test authentication.tests.LoginViewTests --verbosity=2
}

# Run dashboard view tests
run_dashboard_tests() {
    print_section "Running Dashboard View Tests"
    python manage.py test authentication.tests.DashboardViewTests --verbosity=2
}

# Run integration tests
run_integration_tests() {
    print_section "Running Integration Tests (Complete Login Flow)"
    python manage.py test authentication.tests.IntegrationTests --verbosity=2
}

# Run employee model tests
run_employee_tests() {
    print_section "Running Employee Model Tests"
    python manage.py test authentication.tests.EmployeeModelTests --verbosity=2
}

# Run form tests
run_form_tests() {
    print_section "Running Form Validation Tests"
    python manage.py test authentication.tests.LoginFormTests --verbosity=2
}

# Run with coverage
run_coverage() {
    print_section "Running Tests with Coverage Report"
    if command -v coverage &> /dev/null; then
        coverage run --source='.' manage.py test
        echo -e "${YELLOW}Coverage Report:${NC}"
        coverage report --omit='*/venv/*,*/migrations/*'
        echo -e "${YELLOW}Generating HTML coverage report...${NC}"
        coverage html --omit='*/venv/*,*/migrations/*'
        print_success "Coverage report generated in htmlcov/index.html"
    else
        print_error "coverage package not installed. Run: pip install coverage"
    fi
}

# Run with verbose output
run_verbose() {
    print_section "Running Tests with Maximum Verbosity"
    python manage.py test --verbosity=3
}

# Show help
show_help() {
    print_header
    echo "Available Test Options:"
    echo ""
    echo -e "${GREEN}  ./run_tests.sh all${NC}            - Run all tests"
    echo -e "${GREEN}  ./run_tests.sh ldap${NC}           - Run LDAP service tests"
    echo -e "${GREEN}  ./run_tests.sh auth${NC}           - Run authentication backend tests"
    echo -e "${GREEN}  ./run_tests.sh employee${NC}       - Run employee model tests"
    echo -e "${GREEN}  ./run_tests.sh login${NC}          - Run login view tests"
    echo -e "${GREEN}  ./run_tests.sh form${NC}           - Run form validation tests"
    echo -e "${GREEN}  ./run_tests.sh dashboard${NC}      - Run dashboard view tests"
    echo -e "${GREEN}  ./run_tests.sh integration${NC}    - Run complete login flow integration tests"
    echo -e "${GREEN}  ./run_tests.sh coverage${NC}       - Run tests with coverage report"
    echo -e "${GREEN}  ./run_tests.sh verbose${NC}        - Run with maximum verbosity"
    echo -e "${GREEN}  ./run_tests.sh help${NC}           - Show this help message"
    echo ""
    echo "Examples:"
    echo "  # Run all tests"
    echo "  ./run_tests.sh all"
    echo ""
    echo "  # Run specific test suite"
    echo "  ./run_tests.sh login"
    echo ""
    echo "  # Run with coverage"
    echo "  ./run_tests.sh coverage"
    echo ""
}

# Main logic
print_header

case "${1:-all}" in
    all)
        run_all_tests
        ;;
    ldap)
        run_ldap_tests
        ;;
    auth)
        run_auth_tests
        ;;
    employee)
        run_employee_tests
        ;;
    login)
        run_login_tests
        ;;
    form)
        run_form_tests
        ;;
    dashboard)
        run_dashboard_tests
        ;;
    integration)
        run_integration_tests
        ;;
    coverage)
        run_coverage
        ;;
    verbose)
        run_verbose
        ;;
    help)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac

echo ""
print_success "Test run completed!"
