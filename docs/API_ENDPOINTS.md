# API Endpoints
## Tai lieu API day du cho Frontend (cap nhat theo code hien tai)

---

## Muc luc

1. [Tong quan](#tong-quan)
2. [Luu y quan trong ve URL thuc te](#luu-y-quan-trong-ve-url-thuc-te)
3. [Auth](#auth)
4. [System](#system)
5. [Users](#users)
6. [Masking mode](#masking-mode)
7. [Ma tran phan quyen](#ma-tran-phan-quyen)
8. [Response codes](#response-codes)
9. [Mau tich hop frontend](#mau-tich-hop-frontend)

---

## Tong quan

### Server URL

```text
http://localhost:8000
```

### API Docs

```text
http://localhost:8000/docs
```

### OpenAPI JSON

```text
http://localhost:8000/openapi.json
```

### Authentication

- API su dung JWT Bearer token.
- Header:

```http
Authorization: Bearer <access_token>
```

---

## Luu y quan trong ve URL thuc te

Do router dang co `prefix` o ca `include_router(...)` va ben trong tung router, endpoint thuc te hien tai la:

- Auth base: `/api/auth/auth`
- Users base: `/api/users/users`

Frontend can goi theo cac URL thuc te ben duoi cho den khi backend chuan hoa lai prefix.

---

## Auth

### 1) Login

- Method: `POST`
- URL (thuc te): `/api/auth/auth/login`
- Auth: khong can token

Request body:

```json
{
  "username": "admin",
  "password": "123456"
}
```

Response `200`:

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer",
  "user_id": 1,
  "username": "admin",
  "role": "admin"
}
```

Loi thuong gap:

- `401`: `Invalid username or password`
- `500`: `Internal server error: ...`

---

## System

### 1) Root

- Method: `GET`
- URL: `/`
- Auth: khong can token

Response `200`:

```json
{
  "message": "Data Masking + Encryption Backend",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### 2) Health check

- Method: `GET`
- URL: `/health`
- Auth: khong can token

Response `200`:

```json
{
  "status": "healthy",
  "message": "Server is running"
}
```

---

## Users

Base URL thuc te: `/api/users/users`

### 1) Tao user

- Method: `POST`
- URL: `/api/users/users`
- Auth: khong can token

Request body:

```json
{
  "username": "john_doe",
  "email": "john@gmail.com",
  "phone": "0987654321",
  "password": "SecurePass123",
  "role": "user"
}
```

Ghi chu:

- `role` khong bat buoc, mac dinh la `user`.
- Du lieu nhay cam duoc ma hoa truoc khi luu.

Response `201`:

```json
{
  "id": 3,
  "username": "john_doe",
  "email": "j***@gmail.com",
  "phone": "09****21",
  "password": "***",
  "message": "User created successfully",
  "created_at": "2026-03-31T10:30:45"
}
```

### 2) Lay danh sach users

- Method: `GET`
- URL: `/api/users/users`
- Auth: can Bearer token

Query params:

- `skip` (int, default `0`, min `0`)
- `limit` (int, default `10`, min `1`, max `100`)

Ghi chu:

- User role: du lieu tra ve bi masking theo mode global cua role caller.
- Admin role: xem email/phone da decrypt (password van masked).

Response `200`:

```json
{
  "total": 2,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 3,
      "username": "john_doe",
      "email": "j***@gmail.com",
      "phone": "09****21",
      "password": "***",
      "role": "user",
      "created_at": "2026-03-31T10:30:45",
      "updated_at": "2026-03-31T10:30:45"
    }
  ]
}
```

### 3) Lay user theo ID

- Method: `GET`
- URL: `/api/users/users/{user_id}`
- Auth: can Bearer token

Ghi chu:

- Admin: xem duoc moi user.
- User: chi xem duoc chinh minh (`current_user.user_id == user_id`).

Response `200`:

```json
{
  "id": 3,
  "username": "john_doe",
  "email": "j***@gmail.com",
  "phone": "09****21",
  "password": "***",
  "role": "user",
  "created_at": "2026-03-31T10:30:45",
  "updated_at": "2026-03-31T10:30:45"
}
```

Loi thuong gap:

- `403`: `You can only view your own information`
- `404`: `User with ID {id} not found`

### 4) Xem thong tin decrypted day du

- Method: `POST`
- URL: `/api/users/users/{user_id}/decrypt-info`
- Auth: can Bearer token

Request body:

```json
{
  "password": "password_cua_user_do"
}
```

Ghi chu:

- Admin hoac chinh user moi duoc goi.
- API tra ve email/phone/password da decrypt, khong masking.

Response `200`:

```json
{
  "id": 3,
  "username": "john_doe",
  "email": "john@gmail.com",
  "phone": "0987654321",
  "password": "SecurePass123",
  "role": "user",
  "created_at": "2026-03-31T10:30:45",
  "updated_at": "2026-03-31T10:30:45"
}
```

### 5) Reset password user (admin only)

- Method: `POST`
- URL: `/api/users/users/{user_id}/reset-password`
- Auth: can Bearer token (admin)

Request body:

```json
{
  "new_password": "NewPassword123"
}
```

Response `200`:

```json
{
  "id": 3,
  "username": "john_doe",
  "email": "john@gmail.com",
  "phone": "0987654321",
  "password": "***",
  "role": "user",
  "created_at": "2026-03-31T10:30:45",
  "updated_at": "2026-03-31T11:00:00"
}
```

Loi thuong gap:

- `403`: `Only admin can reset password`

### 6) Cap nhat user

- Method: `PUT`
- URL: `/api/users/users/{user_id}`
- Auth: can Bearer token

Request body (tat ca optional):

```json
{
  "email": "john.new@gmail.com",
  "phone": "0912345678",
  "password": "NewPassword123",
  "old_password": "OldPassword123"
}
```

Ghi chu:

- User chi cap nhat duoc chinh minh.
- Admin cap nhat duoc moi user.
- Neu doi `password` thi can `old_password`.

Response `200`:

```json
{
  "id": 3,
  "username": "john_doe",
  "email": "j***@gmail.com",
  "phone": "09****78",
  "message": "User updated successfully",
  "updated_at": "2026-03-31T11:10:00"
}
```

### 7) Xoa user (admin only)

- Method: `DELETE`
- URL: `/api/users/users/{user_id}`
- Auth: can Bearer token (admin)

Response `200`:

```json
{
  "id": 3,
  "username": "john_doe",
  "message": "User deleted successfully"
}
```

Loi thuong gap:

- `403`: `Admin access required`
- `404`: `User with ID {id} not found`

---

## Masking mode

### 1) Set global masking mode theo role (admin only)

- Method: `PATCH`
- URL: `/api/users/users/masking-mode`
- Auth: can Bearer token (admin)

Request body:

```json
{
  "role": "user",
  "masking_mode": "shuffle"
}
```

Gia tri hop le cua `masking_mode`:

- `mask`
- `shuffle`
- `fake`
- `noise`

Response `200`:

```json
{
  "role": "user",
  "masking_mode": "shuffle",
  "updated_at": "2026-03-31T11:20:00"
}
```

Loi thuong gap:

- `400`: `Invalid masking mode. Valid options: mask, shuffle, fake, noise`
- `403`: `Only admin can set masking mode`

---

## Ma tran phan quyen

| Endpoint | User | Admin | Khong login |
|---|---|---|---|
| POST `/api/auth/auth/login` | ✅ | ✅ | ✅ |
| GET `/` | ✅ | ✅ | ✅ |
| GET `/health` | ✅ | ✅ | ✅ |
| POST `/api/users/users` | ✅ | ✅ | ✅ |
| GET `/api/users/users` | ✅ | ✅ | ❌ |
| GET `/api/users/users/{id}` | Chi chinh minh | ✅ | ❌ |
| POST `/api/users/users/{id}/decrypt-info` | Chi chinh minh | ✅ | ❌ |
| PUT `/api/users/users/{id}` | Chi chinh minh | ✅ | ❌ |
| DELETE `/api/users/users/{id}` | ❌ | ✅ | ❌ |
| POST `/api/users/users/{id}/reset-password` | ❌ | ✅ | ❌ |
| PATCH `/api/users/users/masking-mode` | ❌ | ✅ | ❌ |

---

## Response codes

| Status | Y nghia |
|---|---|
| `200` | OK |
| `201` | Created |
| `400` | Bad Request |
| `401` | Unauthorized (token sai/thieu) |
| `403` | Forbidden (khong du quyen) |
| `404` | Not Found |
| `422` | Validation Error (FastAPI/Pydantic) |
| `500` | Internal Server Error |

---

## Mau tich hop frontend

### 1) Dang nhap va luu token

```javascript
const loginRes = await fetch("http://localhost:8000/api/auth/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ username, password })
});

const loginData = await loginRes.json();
localStorage.setItem("access_token", loginData.access_token);
```

### 2) Goi API can auth

```javascript
const token = localStorage.getItem("access_token");

const res = await fetch("http://localhost:8000/api/users/users?skip=0&limit=10", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
});

const data = await res.json();
```

### 3) Set masking mode (admin)

```javascript
await fetch("http://localhost:8000/api/users/users/masking-mode", {
  method: "PATCH",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`
  },
  body: JSON.stringify({ role: "user", masking_mode: "fake" })
});
```

---

**Version**: 2.0  
**Updated**: 31/03/2026  
**Source of truth**: Swagger (`/docs`) + router code (`app/routers/*.py`)
