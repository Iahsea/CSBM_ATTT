"""
Complete Flow Test: Auth + Role + Data Masking
Test tất cả features của hệ thống
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000/api"

# ==================== Test Data ====================

ADMIN_CREDS = {
    "username": "admin",
    "password": "admin123"
}

USER_CREDS = {
    "username": "john_doe",
    "password": "SecurePass123"
}

NEW_USER = {
    "username": "jane_smith",
    "email": "jane@gmail.com",
    "phone": "0912345678",
    "password": "JanePass123",
    "role": "user"
}

# ==================== Helper Functions ====================

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_response(response: requests.Response, label: str = ""):
    """Print response status & data"""
    status_icon = "✅" if response.status_code < 400 else "❌"
    print(f"{status_icon} [{response.status_code}] {label}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print()


# ==================== Test Cases ====================

def test_1_create_admin():
    """Test 1: Create admin user"""
    print_section("TEST 1: Create Admin User")
    
    response = requests.post(
        f"{BASE_URL}/users",
        json={
            "username": "admin",
            "email": "admin@gmail.com",
            "phone": "0987654321",
            "password": "admin123",
            "role": "admin"
        }
    )
    print_response(response, "Create Admin")
    return response.status_code == 201


def test_2_create_user():
    """Test 2: Create regular user"""
    print_section("TEST 2: Create User")
    
    response = requests.post(
        f"{BASE_URL}/users",
        json=USER_CREDS | {
            "email": "john@gmail.com",
            "phone": "0912345678",
            "role": "user"
        }
    )
    print_response(response, "Create User")
    return response.status_code == 201


def test_3_login_admin():
    """Test 3: Login as admin"""
    print_section("TEST 3: Login as Admin")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=ADMIN_CREDS
    )
    print_response(response, "Admin Login")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ Admin Token: {token[:50]}...\n")
        return token
    return None


def test_4_login_user():
    """Test 4: Login as regular user"""
    print_section("TEST 4: Login as User")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json=USER_CREDS
    )
    print_response(response, "User Login")
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✅ User Token: {token[:50]}...\n")
        return token
    return None


def test_5_get_users_list(token: str, label: str):
    """Test 5: Get users list"""
    print_section(f"TEST 5: Get Users List ({label})")
    
    response = requests.get(
        f"{BASE_URL}/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response, f"Get Users ({label})")
    
    if response.status_code == 200:
        users = response.json()["items"]
        print(f"✅ Got {len(users)} users\n")
    return response.status_code == 200


def test_6_get_user_by_id(token: str, user_id: int, label: str):
    """Test 6: Get user by ID"""
    print_section(f"TEST 6: Get User by ID ({label})")
    
    response = requests.get(
        f"{BASE_URL}/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response, f"Get User {user_id} ({label})")
    return response.status_code == 200


def test_7_create_another_user(token: str):
    """Test 7: Create another user (by admin)"""
    print_section("TEST 7: Create Another User (by Admin)")
    
    response = requests.post(
        f"{BASE_URL}/users",
        json=NEW_USER,
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response, "Create Jane Smith")
    
    if response.status_code == 201:
        user_id = response.json()["id"]
        print(f"✅ Created user ID: {user_id}\n")
        return user_id
    return None


def test_8_update_user_password(token: str, user_id: int):
    """Test 8: Update user password"""
    print_section("TEST 8: Update User Password")
    
    response = requests.put(
        f"{BASE_URL}/users/{user_id}",
        json={
            "password": "NewPassword456",
            "old_password": USER_CREDS["password"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response, "Update Password")
    return response.status_code == 200


def test_9_update_user_email(token: str, user_id: int):
    """Test 9: Update user email"""
    print_section("TEST 9: Update User Email")
    
    response = requests.put(
        f"{BASE_URL}/users/{user_id}",
        json={
            "email": "john.new@gmail.com",
            "old_password": USER_CREDS["password"]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response, "Update Email")
    return response.status_code == 200


def test_10_unauthorized_access():
    """Test 10: Test unauthorized access"""
    print_section("TEST 10: Test Unauthorized Access")
    
    # Try without token
    response = requests.get(f"{BASE_URL}/users")
    print_response(response, "Get Users without token")
    
    if response.status_code == 401:
        print("✅ Correctly rejected unauthorized access\n")
    return response.status_code == 401


def test_11_delete_user(token: str, user_id: int):
    """Test 11: Delete user (admin only)"""
    print_section("TEST 11: Delete User (Admin)")
    
    response = requests.delete(
        f"{BASE_URL}/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    print_response(response, "Delete User")
    return response.status_code in [200, 204]


def test_12_verify_masking(token: str):
    """Test 12: Verify data masking in response"""
    print_section("TEST 12: Verify Data Masking")
    
    response = requests.get(
        f"{BASE_URL}/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        users = response.json()["items"]
        if users:
            user = users[0]
            print(f"User: {user['username']}")
            print(f"Email: {user['email']} (should be masked like j***@gmail.com)")
            print(f"Phone: {user['phone']} (should be masked like 09****78)")
            print(f"Password: {user['password']} (should be ***)")
            
            # Check masking
            is_masked = (
                user['email'].count('*') > 0 or user['email'] == "***@***" or
                user['phone'].count('*') > 0 or
                user['password'] == "***"
            )
            if is_masked:
                print("\n✅ Data masking working correctly\n")
            else:
                print("\n⚠️  Data might not be properly masked\n")


# ==================== Main Test Suite ====================

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("  COMPLETE FLOW TEST: Auth + Role + Data Masking")
    print("="*60)
    
    results = {}
    
    # Test 1: Create users
    results["Create Admin"] = test_1_create_admin()
    results["Create User"] = test_2_create_user()
    
    # Test 3-4: Login
    admin_token = test_3_login_admin()
    user_token = test_4_login_user()
    
    if not admin_token or not user_token:
        print("❌ Login failed. Stopping tests.")
        return results
    
    # Test 5-6: Get users
    results["Get Users (Admin)"] = test_5_get_users_list(admin_token, "Admin")
    results["Get Users (User)"] = test_5_get_users_list(user_token, "User")
    results["Get User by ID (Admin)"] = test_6_get_user_by_id(admin_token, 1, "Admin")
    results["Get User by ID (User)"] = test_6_get_user_by_id(user_token, 1, "User")
    
    # Test 7: Create another user
    new_user_id = test_7_create_another_user(admin_token)
    
    # Test 8-9: Update user
    if new_user_id:
        results["Update Password"] = test_8_update_user_password(user_token, 2)
        results["Update Email"] = test_9_update_user_email(user_token, 2)
    
    # Test 10: Unauthorized
    results["Unauthorized Access"] = test_10_unauthorized_access()
    
    # Test 11: Delete user
    if new_user_id:
        results["Delete User"] = test_11_delete_user(admin_token, new_user_id)
    
    # Test 12: Verify masking
    test_12_verify_masking(admin_token)
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    for test_name, result in results.items():
        icon = "✅" if result else "❌"
        print(f"{icon} {test_name}")


if __name__ == "__main__":
    print("\n⚠️  Make sure the FastAPI server is running on http://localhost:8000")
    print("   Run: python main.py\n")
    
    try:
        run_all_tests()
    except Exception as e:
        print(f"\n❌ Test suite failed with error:")
        print(f"{type(e).__name__}: {e}")
