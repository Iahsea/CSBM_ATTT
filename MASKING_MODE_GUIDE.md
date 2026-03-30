# Data Masking Modes - Admin Control

## Overview

Admin (trang admin) có thể chọn phương thức che dấu dữ liệu cho từng user. Khi user xem, dữ liệu sẽ tự động được che dấu theo preference mà admin đã set.

## Các Masking Mode

### 1. **mask** (Mặc định - Che ký tự)
Giữ ký tự đầu/cuối, che phần giữa bằng `*`
```
Email: john@gmail.com  → j***@gmail.com
Phone: 0987654321      → 09****21
```

### 2. **shuffle** (Xáo trộn vị trí)
Xáo trộn vị trí ký tự (không khôi phục được)
```
Email: john@gmail.com  → mliaoag@m.c  (random nhưng deterministic)
Phone: 0987654321      → 1840299765  (random)
```

### 3. **fake** (Thay bằng dữ liệu giả)
Thay bằng dữ liệu giả cùng cấu trúc
```
Email: john@gmail.com  → user5234@example.com
Phone: 0987654321      → 9876543210
```

### 4. **noise** (Thêm nhiễu)
Thêm ký tự nhiễu ngẫu nhiên (không khôi phục được)
```
Email: john@gmail.com  → j#o@h!n*@#$g%m^a&i*l(.c)o%m
Phone: 0987654321      → 0#9@8!7*6#5@4$3%2&1
```

---

## API Endpoints

### 1. Admin Set Masking Mode

**Endpoint:** `PATCH /users/{user_id}/masking-mode`

**Authorization:** Admin only

**Request Body:**
```json
{
  "masking_mode": "shuffle"
}
```

**Valid modes:** `mask | shuffle | fake | noise`

**Response:**
```json
{
  "id": 1,
  "username": "john",
  "email": "***@***",
  "phone": "****",
  "role": "user",
  "created_at": "2026-03-29T10:30:45",
  "updated_at": "2026-03-29T14:25:30"
}
```

**Example cURL:**
```bash
curl -X PATCH http://localhost:8000/users/1/masking-mode \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"masking_mode": "fake"}'
```

---

### 2. User Get List (Áp dụng Stored Mode)

**Endpoint:** `GET /users?skip=0&limit=10`

**Authorization:** Required (User or Admin)

User sẽ thấy dữ liệu được che giấu theo `masking_mode` đã được admin set.
Admin vẫn thấy dữ liệu rõ (decrypted).

**Optional:** Có thể override mode bằng query param
```bash
GET /users?skip=0&limit=10&mask_mode=shuffle
```

**Response (for User role):**
```json
{
  "total": 2,
  "skip": 0,
  "limit": 10,
  "items": [
    {
      "id": 3,
      "username": "User",
      "email": "mliaoag@m.c",      // Áp dụng masking_mode của user này
      "phone": "1840299765",
      "role": "user"
    }
  ]
}
```

---

### 3. User Get Profile (Áp dụng Stored Mode)

**Endpoint:** `GET /users/{user_id}`

**Authorization:** User xem chính mình hoặc Admin

```bash
GET /users/1
  -H "Authorization: Bearer <token>"
```

User sẽ thấy dữ liệu theo `masking_mode` đã set.

---

## Workflow Example

### Bước 1: Admin Set Masking Mode

Admin vào admin panel, chọn user, chọn mode (vd: `shuffle`), nhấn Save:
```bash
PATCH /users/1/masking-mode
Body: { "masking_mode": "shuffle" }
```

### Bước 2: User Xem Profile

User login, xem profile, dữ liệu tự động hiển thị theo mode (shuffle):
```bash
GET /users/1
→ Email hiển thị: mliaoag@m.c (xáo trộn)
→ Phone hiển thị: 1840299765 (xáo trộn)
```

### Bước 3: Admin Thay Đổi Mode

Admin muốn che giấu hơn, chọn mode khác (vd: `fake`):
```bash
PATCH /users/1/masking-mode
Body: { "masking_mode": "fake" }
```

### Bước 4: User Xem Lại

User xem lại, dữ liệu đã thay đổi theo mode mới:
```bash
GET /users/1
→ Email hiển thị: user5234@example.com (giả)
→ Phone hiển thị: 9876543210 (giả)
```

---

## Database Update

Chạy migration để thêm column `masking_mode`:

```sql
ALTER TABLE users ADD COLUMN masking_mode VARCHAR(20) DEFAULT 'mask';
```

---

## Important Notes

- **Mặc định:** Tất cả user đều dùng mode `mask`
- **Chỉ admin có quyền:** Set masking mode cho user
- **User không thể thay:** Masking mode của chính mình (do admin control)
- **Admin vẫn thấy rõ:** Admin luôn xem email/phone decrypted, không bị mask
- **Override qua query param:** Có thể test mode khác với `?mask_mode=shuffle` (nếu user)
- **Deterministic:** Shuffle/fake/noise dùng seed từ data, nên kết quả ổn định (không random mỗi lần)
