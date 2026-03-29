# 🧪 Test Plan: Auth + Role + Data Masking

## 📋 Test Overview

Hệ thống này có ba tính năng chính:
1. **JWT Authentication** - Đăng nhập & lấy token
2. **Role-Based Access Control** - Admin vs User roles
3. **Data Masking** - Sensitive data được ẩn cho user role

---

## ⚙️ Setup

### 1. Tạo Database
```bash
# Sử dụng setup.sql để tạo database
mysql -u root -p < setup.sql
```

### 2. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 3. Khởi Động Server
```bash
python main.py
# hoặc
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧬 Test Flow

### Phase 1: User Registration & Login

#### Test 1.1: Create Admin User (POST /api/users)
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@gmail.com",
    "phone": "0987654321",
    "password": "admin123",
    "role": "admin"
  }'
```

**Expected Response (201):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "a***@gmail.com",
  "phone": "09****21",
  "password": "***",
  "message": "User created successfully",
  "created_at": "2026-03-28T10:30:45"
}
```

✅ **Check:** Data đã được masked (email, phone, password)

---

#### Test 1.2: Create Regular User (POST /api/users)
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@gmail.com",
    "phone": "0912345678",
    "password": "SecurePass123",
    "role": "user"
  }'
```

**Expected Response (201):** User created with masked data

---

#### Test 1.3: Admin Login (POST /api/auth/login)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "admin",
  "role": "admin"
}
```

✅ **Check:** Token được tạo, role là "admin"

---

#### Test 1.4: User Login (POST /api/auth/login)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

**Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 2,
  "username": "john_doe",
  "role": "user"
}
```

✅ **Check:** Token được tạo, role là "user"

---

### Phase 2: Data Masking Test

#### Test 2.1: Get Users List as Admin (GET /api/users)
```bash
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

**Expected Response (200):**
```json
{
  "total": 2,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "username": "admin",
      "email": "***@***",
      "phone": "****",
      "password": "***",
      "role": "admin",
      "created_at": "2026-03-28T10:30:45"
    },
    {
      "id": 2,
      "username": "john_doe",
      "email": "***@***",
      "phone": "****",
      "password": "***",
      "role": "user",
      "created_at": "2026-03-28T10:30:46"
    }
  ]
}
```

**Note:** Dữ liệu được masked cho cả admin vì không decrypt được (không có password của other users)

✅ **Check:** Email, phone, password đều masked

---

#### Test 2.2: Get Users List as User (GET /api/users)
```bash
curl -X GET http://localhost:8000/api/users \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Expected Response (200):** Dữ liệu masked (như admin, vì không có password)

✅ **Check:** User role có thể access /api/users

---

#### Test 2.3: Get Specific User as Admin (GET /api/users/{id})
```bash
curl -X GET http://localhost:8000/api/users/2 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

**Expected Response (200):** Masked data (vì không decrypt được)

---

### Phase 3: User Update Test

#### Test 3.1: User tự update password (PUT /api/users/{id})
```bash
curl -X PUT http://localhost:8000/api/users/2 \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "NewPassword456",
    "old_password": "SecurePass123"
  }'
```

**Expected Response (200):**
```json
{
  "id": 2,
  "username": "john_doe",
  "email": "j***@gmail.com",
  "phone": "09****78",
  "password": "***",
  "message": "User updated successfully",
  "updated_at": "2026-03-28T10:35:50"
}
```

✅ **Check:** 
- Password được update
- Old password verification thành công
- Data re-encrypted với new key

---

#### Test 3.2: Update email (PUT /api/users/{id})
```bash
curl -X PUT http://localhost:8000/api/users/2 \
  -H "Authorization: Bearer <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.new@gmail.com",
    "old_password": "NewPassword456"
  }'
```

**Expected Response (200):** Email updated & masked

---

### Phase 4: Authorization Test

#### Test 4.1: Try Access Without Token (GET /api/users)
```bash
curl -X GET http://localhost:8000/api/users
```

**Expected Response (401):**
```json
{
  "detail": "Missing authorization header"
}
```

✅ **Check:** Unauthorized access rejected

---

#### Test 4.2: Try Delete User as User (DELETE /api/users/{id})
```bash
curl -X DELETE http://localhost:8000/api/users/1 \
  -H "Authorization: Bearer <USER_TOKEN>"
```

**Expected Response (403):**
```json
{
  "detail": "Admin access required"
}
```

✅ **Check:** Non-admin cannot delete

---

#### Test 4.3: Delete User as Admin (DELETE /api/users/{id})
```bash
curl -X DELETE http://localhost:8000/api/users/2 \
  -H "Authorization: Bearer <ADMIN_TOKEN>"
```

**Expected Response (200):**
```json
{
  "id": 2,
  "username": "john_doe",
  "message": "User deleted successfully"
}
```

✅ **Check:** Admin can delete user

---

### Phase 5: Invalid Input Test

#### Test 5.1: Invalid Password (POST /api/auth/login)
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "wrongpassword"
  }'
```

**Expected Response (401):**
```json
{
  "detail": "Invalid username or password"
}
```

✅ **Check:** Wrong password rejected

---

#### Test 5.2: Duplicate Username (POST /api/users)
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "another@gmail.com",
    "phone": "0999999999",
    "password": "pass123",
    "role": "user"
  }'
```

**Expected Response (400):**
```json
{
  "detail": "Username 'admin' already exists"
}
```

✅ **Check:** Duplicate username rejected

---

## 🤖 Automated Test Script

Chạy test suite hoàn toàn:
```bash
python test_complete_flow.py
```

**Kết quả:** Báo cáo chi tiết về tất cả test cases

---

## 📊 Summary Checklist

- [ ] ✅ Create User (registration)
- [ ] ✅ Login (get JWT token)
- [ ] ✅ Get Users List (with masking)
- [ ] ✅ Get User by ID (with masking)
- [ ] ✅ Update User (password, email, phone)
- [ ] ✅ Delete User (admin only)
- [ ] ✅ Unauthorized Access (rejected)
- [ ] ✅ Data Masking (email, phone, password)
- [ ] ✅ Role-Based Access (admin vs user)
- [ ] ✅ Token Verification (valid/invalid token)

---

## 🐛 Troubleshooting

### Issue: 401 Unauthorized
**Solution:** 
- Check token is valid and not expired
- Verify Authorization header format: `Bearer <token>`

### Issue: 403 Forbidden
**Solution:**
- Check user role (must be admin for certain endpoints)
- Verify token claims

### Issue: Database Connection Error
**Solution:**
- Check MySQL is running
- Verify database credentials in .env
- Run: `mysql -u root -p < setup.sql`

### Issue: Encryption/Decryption Failed
**Solution:**
- Check username & password are correct
- Verify password wasn't modified in database
- Check key generation logic

---

## 📝 Notes

1. **Data Masking Pattern:**
   - Email: `j***@gmail.com` (first letter + *** + domain)
   - Phone: `09****78` (first 2 + **** + last 2)
   - Password: `***` (always masked)

2. **Encryption Method:**
   - XOR encryption with key = hash(username + password)
   - Key is 0-255 integer
   - Both admin & user see masked data in list endpoints

3. **Token Expiration:**
   - Default: 60 minutes
   - Can be changed in .env: `JWT_EXPIRE_MINUTES=120`

4. **Database:**
   - All sensitive data (email, phone, password) stored as VARBINARY (encrypted)
   - Only username stored as plain text (used to generate encryption key)
