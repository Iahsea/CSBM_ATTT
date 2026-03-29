"""
Test Script: Basic API Testing
Script để test các endpoints cơ bản của API
"""
import asyncio
import httpx
import json
from typing import Optional

BASE_URL = "http://localhost:8000"
API_PREFIX = f"{BASE_URL}/api"

# Test data
TEST_USER = {
    "username": "test_user_001",
    "email": "test@example.com",
    "phone": "0987654321",
    "password": "TestPassword123"
}


async def print_response(response: httpx.Response, title: str = ""):
    """Pretty print API response"""
    title_str = f" {title} " if title else ""
    print(f"\n{'='*60}")
    print(f"  {response.status_code}{title_str}")
    print(f"{'='*60}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print()


async def test_api():
    """Run API tests"""
    
    print("\n" + "="*60)
    print("  🧪 API Testing Suite")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health Check
        print("\n[1/6] Health Check...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            await print_response(response, "Health Check")
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        
        # Test 2: Root Endpoint
        print("[2/6] Root Endpoint...")
        response = await client.get(f"{BASE_URL}/")
        await print_response(response, "Root")
        
        
        # Test 3: Create User
        print("[3/6] Create User...")
        response = await client.post(
            f"{API_PREFIX}/users",
            json=TEST_USER
        )
        await print_response(response, "Create User")
        
        if response.status_code != 201:
            print("❌ Failed to create user, skipping remaining tests")
            return
        
        user_id = response.json().get("id")
        print(f"✅ Created user with ID: {user_id}")
        
        
        # Test 4: Get User by ID (with masking)
        print(f"\n[4/6] Get User {user_id} (masked)...")
        response = await client.get(
            f"{API_PREFIX}/users/{user_id}",
            params={"mask": True}
        )
        await print_response(response, "Get User (Masked)")
        
        
        # Test 5: Get All Users (with masking)
        print("[5/6] Get All Users (masked)...")
        response = await client.get(
            f"{API_PREFIX}/users",
            params={"mask": True, "limit": 10}
        )
        await print_response(response, "Get All Users (Masked)")
        
        
        # Test 6: Update User
        print(f"[6/6] Update User {user_id}...")
        update_data = {
            "email": "newemail@example.com",
            "phone": "0912345678"
        }
        response = await client.put(
            f"{API_PREFIX}/users/{user_id}",
            json=update_data
        )
        await print_response(response, "Update User")
        
        
        # Bonus: Delete User (Optional)
        print("🗑️  Delete User (Optional)...")
        response = await client.delete(f"{API_PREFIX}/users/{user_id}")
        await print_response(response, "Delete User")
        
        
        print("\n" + "="*60)
        print("  ✅ Testing Complete!")
        print("="*60)


async def test_error_cases():
    """Test error handling"""
    
    print("\n" + "="*60)
    print("  ❌ Error Handling Tests")
    print("="*60)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Invalid Email
        print("\n[1/3] Invalid Email...")
        response = await client.post(
            f"{API_PREFIX}/users",
            json={
                "username": "test_invalid",
                "email": "not-an-email",
                "phone": "0987654321",
                "password": "test123"
            }
        )
        await print_response(response, "Invalid Email (Expected Error)")
        
        
        # Test 2: Duplicate Username
        print("[2/3] Duplicate Username...")
        await client.post(
            f"{API_PREFIX}/users",
            json={
                "username": "duplicate_test",
                "email": "dup1@example.com",
                "phone": "0987654321",
                "password": "test123"
            }
        )
        response = await client.post(
            f"{API_PREFIX}/users",
            json={
                "username": "duplicate_test",
                "email": "dup2@example.com",
                "phone": "0987654321",
                "password": "test123"
            }
        )
        await print_response(response, "Duplicate Username (Expected Error)")
        
        
        # Test 3: User Not Found
        print("[3/3] User Not Found...")
        response = await client.get(f"{API_PREFIX}/users/99999")
        await print_response(response, "User Not Found (Expected Error)")
        
        
        print("\n" + "="*60)
        print("  ✅ Error Tests Complete!")
        print("="*60)


def main():
    """Main entry point"""
    import sys
    
    print("\n🚀 Backend API Test Runner")
    print("\nTests:")
    print("1. Basic API Tests")
    print("2. Error Handling Tests")
    print("3. Both")
    
    choice = input("\nSelect test suite (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(test_api())
    elif choice == "2":
        asyncio.run(test_error_cases())
    elif choice == "3":
        asyncio.run(test_api())
        asyncio.run(test_error_cases())
    else:
        print("❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()
