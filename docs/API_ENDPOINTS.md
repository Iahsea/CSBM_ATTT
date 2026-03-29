# 🌐 API Endpoints
## Tài liệu các endpoint RESTful của hệ thống

---

## 📋 Mục lục

1. [Tổng quan](#tổng-quan)
2. [Tạo User - POST /users](#tạo-user---post-users)
3. [Lấy danh sách Users - GET /users](#lấy-danh-sách-users---get-users)
4. [Lấy User theo ID - GET /users/{id}](#lấy-user-theo-id---get-usersid)
5. [Cập nhật User - PUT /users/{id}](#cập-nhật-user---put-usersid)
6. [Xóa User - DELETE /users/{id}](#xóa-user---delete-usersid)
7. [Response Codes](#response-codes)
8. [Ví dụ cURL](#ví-dụ-curl)
9. [Ví dụ Python](#ví-dụ-python)

---

## 📊 Tổng quan

### Base URL
```
http://localhost:8000/api
```

### Content-Type
```
application/json
```

### Authentication
- Hiện tại: **Không yêu cầu** (Basic)
- Tương lai: JWT Token (Authorization: Bearer {token})

### Endpoints Summary

| Phương thức | Endpoint | Mục đích |
|-----------|----------|---------|
| POST | `/users` | Tạo user mới |
| GET | `/users` | Lấy danh sách users |
| GET | `/users/{id}` | Lấy user theo ID |
| PUT | `/users/{id}` | Cập nhật user |
| DELETE | `/users/{id}` | Xóa user |

---

## 🆕 Tạo User - POST /users

### Endpoint
```
POST /api/users
```

### Request Headers
```
Content-Type: application/json
```

### Request Body (JSON Schema)

```json
{
  "username": "string (required, 3-50 chars, unique)",
  "email": "string (required, valid email format)",
  "phone": "string (required, 10-15 digits)",
  "password": "string (required, min 6 chars)"
}
```

### Request Parameters

| Tham số | Type | Bắt buộc | Mô tả | Ví dụ |
|--------|------|---------|-------|-------|
| `username` | string | YES | Tên đăng nhập, duy nhất | `john_doe` |
| `email` | string | YES | Email hợp lệ | `john@gmail.com` |
| `phone` | string | YES | Số điện thoại | `0987654321` |
| `password` | string | YES | Mật khẩu tối thiểu 6 ký tự | `SecurePass123` |

### Response Success (201 Created)

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "j***@gmail.com",
  "phone": "09****21",
  "message": "User created successfully",
  "created_at": "2026-03-28T10:30:45"
}
```

### Response Error - Duplicate Username (400 Bad Request)

```json
{
  "error": "Username already exists",
  "detail": "Username 'john_doe' is already taken"
}
```

### Response Error - Invalid Email (400 Bad Request)

```json
{
  "error": "Invalid email format",
  "detail": "Email must be a valid email address"
}
```

### Response Error - Phone Format (400 Bad Request)

```json
{
  "error": "Invalid phone format",
  "detail": "Phone must contain 10-15 digits"
}
```

### Response Error - Weak Password (400 Bad Request)

```json
{
  "error": "Weak password",
  "detail": "Password must be at least 6 characters"
}
```

### Validation Logic

```python
# Validation
├─ Username
│  ├─ Length: 3-50 characters
│  ├─ Pattern: alphanumeric + underscore
│  ├─ Unique: Check database
│  └─ Error: 400 Bad Request
│
├─ Email
│  ├─ Format: RFC 5322
│  ├─ Example: user@domain.com
│  └─ Error: 400 Bad Request
│
├─ Phone
│  ├─ Length: 10-15 digits
│  ├─ Pattern: digits only (0-9) or +country code
│  └─ Error: 400 Bad Request
│
└─ Password
   ├─ Length: minimum 6 characters
   ├─ Note: No complexity requirement
   └─ Error: 400 Bad Request
```

---

## 📖 Lấy danh sách Users - GET /users

### Endpoint
```
GET /api/users?mask=true&skip=0&limit=10
```

### Query Parameters

| Tham số | Type | Mặc định | Mô tả |
|--------|------|---------|-------|
| `mask` | boolean | `true` | Áp dụng masking hay không |
| `skip` | integer | `0` | Số record bỏ qua (pagination) |
| `limit` | integer | `10` | Số record trả về (max 100) |

### Request Headers
```
Accept: application/json
```

### Response Success (200 OK) - với mask=true

```json
{
  "total": 3,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "j***@gmail.com",
      "phone": "09****21",
      "password": "***",
      "created_at": "2026-03-28T10:30:45"
    },
    {
      "id": 2,
      "username": "alice_smith",
      "email": "a***@yahoo.com",
      "phone": "08****45",
      "password": "***",
      "created_at": "2026-03-28T11:00:00"
    },
    {
      "id": 3,
      "username": "bob_wilson",
      "email": "b***@outlook.com",
      "phone": "07****78",
      "password": "***",
      "created_at": "2026-03-28T11:15:30"
    }
  ]
}
```

### Response Success (200 OK) - với mask=false

```json
{
  "total": 3,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@gmail.com",
      "phone": "0987654321",
      "password": "SecurePass123",
      "created_at": "2026-03-28T10:30:45"
    },
    {
      "id": 2,
      "username": "alice_smith",
      "email": "alice@yahoo.com",
      "phone": "0823456745",
      "password": "AlicePass456",
      "created_at": "2026-03-28T11:00:00"
    },
    {
      "id": 3,
      "username": "bob_wilson",
      "email": "bob@outlook.com",
      "phone": "0734567878",
      "password": "BobPass789",
      "created_at": "2026-03-28T11:15:30"
    }
  ]
}
```

### Response Error - Not Found (404)

```json
{
  "error": "No users found",
  "detail": "Database is empty"
}
```

---

## 🔍 Lấy User theo ID - GET /users/{id}

### Endpoint
```
GET /api/users/{id}?mask=true
```

### Path Parameters

| Tham số | Type | Mô tả |
|--------|------|-------|
| `id` | integer | User ID (required) |

### Query Parameters

| Tham số | Type | Mặc định | Mô tả |
|--------|------|---------|-------|
| `mask` | boolean | `true` | Áp dụng masking hay không |

### Example Requests
```
GET /api/users/1?mask=true
GET /api/users/2?mask=false
```

### Response Success (200 OK) - với mask=true

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "j***@gmail.com",
  "phone": "09****21",
  "password": "***",
  "created_at": "2026-03-28T10:30:45",
  "updated_at": "2026-03-28T10:30:45"
}
```

### Response Success (200 OK) - với mask=false

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@gmail.com",
  "phone": "0987654321",
  "password": "SecurePass123",
  "created_at": "2026-03-28T10:30:45",
  "updated_at": "2026-03-28T10:30:45"
}
```

### Response Error - User Not Found (404)

```json
{
  "error": "User not found",
  "detail": "User with ID 999 does not exist"
}
```

### Response Error - Invalid ID (400)

```json
{
  "error": "Invalid ID format",
  "detail": "ID must be an integer"
}
```

---

## ✏️ Cập nhật User - PUT /users/{id}

### Endpoint
```
PUT /api/users/{id}
```

### Path Parameters

| Tham số | Type | Mô tả |
|--------|------|-------|
| `id` | integer | User ID (required) |

### Request Body (JSON Schema)

```json
{
  "email": "string (optional, valid email)",
  "phone": "string (optional, 10-15 digits)",
  "password": "string (optional, min 6 chars)"
}
```

**Lưu ý**: 
- `username` không được phép thay đổi
- Chỉ cần cập nhật fields cần thiết

### Request Example

```json
{
  "email": "john.new@gmail.com",
  "phone": "0912345678"
}
```

### Response Success (200 OK)

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "j***@gmail.com",
  "phone": "09****78",
  "message": "User updated successfully",
  "updated_at": "2026-03-28T14:30:45"
}
```

### Response Error - User Not Found (404)

```json
{
  "error": "User not found",
  "detail": "User with ID 999 does not exist"
}
```

### Response Error - Invalid Email (400)

```json
{
  "error": "Invalid email format",
  "detail": "Email must be a valid email address"
}
```

---

## 🗑️ Xóa User - DELETE /users/{id}

### Endpoint
```
DELETE /api/users/{id}
```

### Path Parameters

| Tham số | Type | Mô tả |
|--------|------|-------|
| `id` | integer | User ID (required) |

### Response Success (200 OK)

```json
{
  "id": 1,
  "username": "john_doe",
  "message": "User deleted successfully"
}
```

### Response Error - User Not Found (404)

```json
{
  "error": "User not found",
  "detail": "User with ID 999 does not exist"
}
```

---

## 📈 Response Codes

| Status Code | HTTP Status | Mô tả |
|------------|------------|-------|
| 200 | OK | Request thành công |
| 201 | Created | Tạo resource thành công |
| 400 | Bad Request | Input không hợp lệ |
| 404 | Not Found | Resource không tồn tại |
| 500 | Internal Server Error | Lỗi server |

---

## 🐚 Ví dụ cURL

### Tạo User
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@gmail.com",
    "phone": "0987654321",
    "password": "SecurePass123"
  }'
```

### Lấy danh sách Users (có masking)
```bash
curl -X GET "http://localhost:8000/api/users?mask=true&limit=10"
```

### Lấy danh sách Users (không masking)
```bash
curl -X GET "http://localhost:8000/api/users?mask=false&limit=10"
```

### Lấy User theo ID
```bash
curl -X GET "http://localhost:8000/api/users/1?mask=true"
```

### Cập nhật User
```bash
curl -X PUT http://localhost:8000/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.new@gmail.com",
    "phone": "0912345678"
  }'
```

### Xóa User
```bash
curl -X DELETE http://localhost:8000/api/users/1
```

---

## 🐍 Ví dụ Python

### Cài đặt requests library
```bash
pip install requests
```

### Tạo User
```python
import requests

url = "http://localhost:8000/api/users"
data = {
    "username": "john_doe",
    "email": "john@gmail.com",
    "phone": "0987654321",
    "password": "SecurePass123"
}

response = requests.post(url, json=data)
print(response.status_code)  # 201
print(response.json())
```

### Lấy danh sách Users
```python
import requests

url = "http://localhost:8000/api/users"
params = {"mask": True, "limit": 10}

response = requests.get(url, params=params)
users = response.json()
for user in users["items"]:
    print(f"{user['id']}: {user['username']} - {user['email']}")
```

### Lấy User theo ID
```python
import requests

user_id = 1
url = f"http://localhost:8000/api/users/{user_id}"
params = {"mask": True}

response = requests.get(url, params=params)
user = response.json()
print(user)
```

### Cập nhật User
```python
import requests

user_id = 1
url = f"http://localhost:8000/api/users/{user_id}"
data = {
    "email": "john.new@gmail.com",
    "phone": "0912345678"
}

response = requests.put(url, json=data)
print(response.json())
```

### Xóa User
```python
import requests

user_id = 1
url = f"http://localhost:8000/api/users/{user_id}"

response = requests.delete(url)
print(response.json())
```

---

##  Luồng Masking trong API

```
Client Request: GET /users?mask=true

Server Processing:
  1. Fetch data từ DB (encrypted)
  2. Decrypt data (XOR)
  3. Check mask=true?
     ├─ YES: Apply masking rules
     │  ├─ email: a***@domain.com
     │  ├─ phone: 09****21
     │  └─ password: ***
     └─ NO: Return plain decrypted data

Response:
  {
    "email": "j***@gmail.com",      ← Masked
    "phone": "09****21",            ← Masked
    "password": "***"               ← Masked
  }
```

---

**Phiên bản**: 1.0  
**Ngày cập nhật**: 28/03/2026  
**Liên quan**: [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md), [DATA_MASKING.md](./DATA_MASKING.md)
