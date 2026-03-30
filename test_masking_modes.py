#!/usr/bin/env python3
"""
Test Script: End-to-End Masking Mode Control
Demonstrates admin setting masking mode → user viewing masked data
"""

import asyncio
import httpx
import json
from typing import Optional

BASE_URL = "http://localhost:8000"
ADMIN_TOKEN = None
USER_TOKEN = None

class Colors:
    """Terminal colors for output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(title: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_info(msg: str):
    print(f"{Colors.CYAN}ℹ {msg}{Colors.ENDC}")

def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.ENDC}")

def print_response(title: str, data: dict):
    print(f"\n{Colors.BLUE}{title}:{Colors.ENDC}")
    print(json.dumps(data, indent=2, ensure_ascii=False))

async def login_admin() -> bool:
    """Login as admin to get token"""
    global ADMIN_TOKEN
    print_step("Step 1: Admin Login")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "admin123"}
            )
            if response.status_code == 200:
                data = response.json()
                ADMIN_TOKEN = data.get("access_token")
                print_success(f"Admin logged in, token: {ADMIN_TOKEN[:20]}...")
                return True
            else:
                print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Connection error: {str(e)}")
            return False

async def login_user() -> bool:
    """Login as regular user to get token"""
    global USER_TOKEN
    print_step("Step 2: User Login")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/auth/login",
                json={"username": "User", "password": "User@123"}
            )
            if response.status_code == 200:
                data = response.json()
                USER_TOKEN = data.get("access_token")
                print_success(f"User logged in, token: {USER_TOKEN[:20]}...")
                return True
            else:
                print_error(f"Login failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Connection error: {str(e)}")
            return False

async def test_set_masking_mode(user_id: int, mode: str) -> bool:
    """Admin sets masking mode for a user"""
    print_step(f"Step 3a: Admin Sets Masking Mode to '{mode}' for User {user_id}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.patch(
                f"{BASE_URL}/users/{user_id}/masking-mode",
                json={"masking_mode": mode},
                headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"Masking mode set to '{mode}'")
                print_response("Response", data)
                return True
            else:
                print_error(f"Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Connection error: {str(e)}")
            return False

async def test_user_view_data(user_id: int, token: str, role: str = "user") -> bool:
    """User/Admin views data (applies stored masking mode)"""
    role_name = "Admin" if role == "admin" else "User"
    print_step(f"Step 3b: {role_name} Views User {user_id} Profile")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/users/{user_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"{role_name} can view profile")
                print_response(f"{role_name} View", data)
                return True
            else:
                print_error(f"Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Connection error: {str(e)}")
            return False

async def test_list_users(token: str, mask_mode: Optional[str] = None) -> bool:
    """List users with optional mask_mode override"""
    params = {}
    if mask_mode:
        params["mask_mode"] = mask_mode
    
    mode_str = f"with override '{mask_mode}'" if mask_mode else "with stored mode"
    print_step(f"Step 4: User Lists All Users {mode_str}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{BASE_URL}/users",
                params=params,
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"Users list retrieved")
                print_response("User List Response", {
                    "total": data.get("total"),
                    "count": len(data.get("items", [])),
                    "first_item": data.get("items", [{}])[0] if data.get("items") else None
                })
                return True
            else:
                print_error(f"Failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Connection error: {str(e)}")
            return False

async def demonstrate_mode_changes(user_id: int):
    """Demonstrate changing modes and seeing different masked data"""
    print_step("Step 5: Demonstrate Mode Changes")
    
    modes = ["mask", "shuffle", "fake", "noise"]
    
    for mode in modes:
        print_info(f"Testing mode: {mode}")
        
        # Admin sets mode
        success = await test_set_masking_mode(user_id, mode)
        if not success:
            print_error(f"Failed to set mode '{mode}'")
            continue
        
        # User views data
        print_info(f"User viewing with mode '{mode}'...")
        success = await test_user_view_data(user_id, USER_TOKEN)
        if not success:
            print_error(f"Failed to view with mode '{mode}'")
            continue
        
        print(f"\n{Colors.YELLOW}Mode '{mode}' test completed{Colors.ENDC}\n")
        await asyncio.sleep(0.5)  # Small delay between requests

async def main():
    """Main test execution"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}╔════════════════════════════════════════════════════════════╗{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}║      Data Masking Mode Control - End-to-End Test            ║{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}╚════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    # Step 1: Login
    if not await login_admin():
        print_error("Admin login failed, aborting test")
        return
    
    if not await login_user():
        print_error("User login failed, aborting test")
        return
    
    # Use user ID 3 (the "User" user)
    user_id = 3
    
    # Step 2: Test mode changes
    await demonstrate_mode_changes(user_id)
    
    # Step 3: Test list endpoint
    print_info("Testing user list endpoint with stored masking mode...")
    await test_list_users(USER_TOKEN)
    
    # Step 4: Test with override
    print_info("Testing list endpoint with mask_mode override...")
    await test_list_users(USER_TOKEN, mask_mode="noise")
    
    # Step 5: Admin always sees decrypted
    print_step("Step 6: Admin Always Sees Decrypted Data")
    print_info("Regardless of masking_mode, admin sees full email/phone")
    await test_user_view_data(user_id, ADMIN_TOKEN, role="admin")
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}Test completed!{Colors.ENDC}\n")

if __name__ == "__main__":
    # Note: Make sure the FastAPI server is running on localhost:8000
    print_info("Make sure FastAPI server is running on http://localhost:8000")
    print_info("Default test users: admin/admin123, User/User@123")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_error("\nTest interrupted by user")
    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")
