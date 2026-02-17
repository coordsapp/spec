"""
Backend API Testing for Coords Spatial OS
Tests all API endpoints including auth, protocol, docks, carriers, and analytics
"""
import requests
import sys
from datetime import datetime
import json

class CoordsAPITester:
    def __init__(self, base_url="https://github-connect-64.preview.emergentagent.com"):
        self.base_url = base_url
        self.session_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if headers:
            test_headers.update(headers)
        
        if self.session_token:
            test_headers['Authorization'] = f'Bearer {self.session_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {method} {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=test_headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.headers.get('content-type', '').startswith('application/json'):
                    return success, response.json()
                return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append(f"{name}: Expected {expected_status}, got {response.status_code}")

            return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append(f"{name}: Error - {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test basic health endpoints"""
        print("\n=== HEALTH CHECK TESTS ===")
        self.run_test("Health Check", "GET", "/api/health", 200)
        self.run_test("Root Endpoint", "GET", "/api/", 200)

    def test_protocol_lab(self):
        """Test Protocol Lab functionality"""
        print("\n=== PROTOCOL LAB TESTS ===")
        
        # Test L1 generation - specific test case from requirements
        test_data = {"lat": 37.7749, "lng": -122.4194, "alt": 15.25}
        success, response = self.run_test(
            "L1 Generation (Test Case)", 
            "POST", 
            "/api/v1/protocol/generate", 
            200, 
            test_data
        )
        if success and response:
            expected_checksum = "1c86401e"
            actual_checksum = response.get("checksum")
            if actual_checksum == expected_checksum:
                print(f"✅ Checksum validation passed: {actual_checksum}")
            else:
                print(f"❌ Checksum mismatch: expected {expected_checksum}, got {actual_checksum}")
                self.failed_tests.append(f"L1 Checksum: Expected {expected_checksum}, got {actual_checksum}")
        
        # Test L1 validation
        test_l1 = "coords:l1:v1:37.774900,-122.419400,15.25*1c86401e"
        success, response = self.run_test(
            "L1 Validation", 
            "POST", 
            "/api/v1/protocol/validate", 
            200, 
            {"l1_string": test_l1}
        )
        
        # Test vectors
        self.run_test("Test Vectors", "GET", "/api/v1/protocol/test-vectors", 200)

    def test_authentication(self):
        """Test authentication endpoints"""
        print("\n=== AUTHENTICATION TESTS ===")
        
        # Test user registration
        test_email = f"test_{datetime.now().strftime('%H%M%S')}@coords.app"
        reg_data = {
            "email": test_email,
            "password": "TestPass123!",
            "name": "Test User"
        }
        
        success, response = self.run_test(
            "User Registration", 
            "POST", 
            "/api/auth/register", 
            200, 
            reg_data
        )
        
        if success and response:
            self.session_token = response.get("token")
            print(f"   Got session token: {self.session_token[:20]}...")
        
        # Test login with created user
        login_data = {
            "email": test_email,
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Login", 
            "POST", 
            "/api/auth/login", 
            200, 
            login_data
        )
        
        if success and response and not self.session_token:
            self.session_token = response.get("token")
        
        # Test get current user (authenticated endpoint)
        if self.session_token:
            self.run_test("Get Current User", "GET", "/api/auth/me", 200)
        else:
            print("⚠️ Skipping authenticated tests - no token available")

    def test_dock_management(self):
        """Test dock management APIs"""
        print("\n=== DOCK MANAGEMENT TESTS ===")
        
        if not self.session_token:
            print("⚠️ Skipping dock tests - authentication required")
            return
        
        # Get docks list
        success, docks_response = self.run_test("Get Docks List", "GET", "/api/coordination/docks", 200)
        
        dock_id = None
        if success and docks_response and isinstance(docks_response, list) and len(docks_response) > 0:
            dock_id = docks_response[0].get("dock_id")
            print(f"   Found {len(docks_response)} docks, testing with dock: {dock_id}")
        
        # Get specific dock
        if dock_id:
            self.run_test("Get Specific Dock", "GET", f"/api/coordination/docks/{dock_id}", 200)
        
        # Create new dock
        new_dock_data = {
            "name": "Test Dock API",
            "lat": 38.9072,
            "lng": -77.0369,
            "capacity": 1,
            "l2_handle": "@test/api-dock"
        }
        success, create_response = self.run_test("Create Dock", "POST", "/api/coordination/docks", 200, new_dock_data)

    def test_carriers(self):
        """Test carrier management APIs"""
        print("\n=== CARRIER MANAGEMENT TESTS ===")
        
        if not self.session_token:
            print("⚠️ Skipping carrier tests - authentication required")
            return
        
        # Get carriers list
        success, carriers_response = self.run_test("Get Carriers List", "GET", "/api/carriers", 200)
        
        carrier_id = None
        if success and carriers_response and isinstance(carriers_response, list) and len(carriers_response) > 0:
            carrier_id = carriers_response[0].get("carrier_id")
            print(f"   Found {len(carriers_response)} carriers, testing with carrier: {carrier_id}")
        
        # Get specific carrier
        if carrier_id:
            self.run_test("Get Specific Carrier", "GET", f"/api/carriers/{carrier_id}", 200)
        
        # Create new carrier
        new_carrier_data = {
            "name": "Test Carrier API",
            "code": "TEST-001",
            "driver_name": "Test Driver",
            "driver_phone": "+1-555-0199"
        }
        self.run_test("Create Carrier", "POST", "/api/carriers", 200, new_carrier_data)

    def test_analytics(self):
        """Test analytics and dashboard APIs"""
        print("\n=== ANALYTICS TESTS ===")
        
        if not self.session_token:
            print("⚠️ Skipping analytics tests - authentication required")
            return
        
        # Dashboard stats
        self.run_test("Dashboard Stats", "GET", "/api/v1/analytics/dashboard", 200)
        
        # SLA compliance
        self.run_test("SLA Compliance", "GET", "/api/v1/analytics/sla-compliance", 200)

    def test_locations(self):
        """Test locations APIs"""
        print("\n=== LOCATIONS TESTS ===")
        
        if not self.session_token:
            print("⚠️ Skipping locations tests - authentication required")
            return
        
        # Get locations
        self.run_test("Get Locations", "GET", "/api/locations", 200)
        
        # Create location
        new_location_data = {
            "name": "Test Location",
            "lat": 38.9072,
            "lng": -77.0369,
            "type": "test",
            "l2_handle": "@test/api-location"
        }
        self.run_test("Create Location", "POST", "/api/locations", 200, new_location_data)

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Coords API Tests")
        print(f"Base URL: {self.base_url}")
        
        # Run test suites
        self.test_health_check()
        self.test_protocol_lab()
        self.test_authentication()
        self.test_dock_management()
        self.test_carriers()
        self.test_analytics()
        self.test_locations()
        
        # Print results
        print(f"\n{'='*50}")
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for failure in self.failed_tests:
                print(f"   • {failure}")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test runner"""
    tester = CoordsAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())