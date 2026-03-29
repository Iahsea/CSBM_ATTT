# 🎭 Data Masking
## Luật che giấu dữ liệu an toàn khi hiển thị

---

## 📋 Mục lục

1. [Tổng quan](#tổng-quan)
2. [Email Masking](#email-masking)
3. [Phone Masking](#phone-masking)
4. [Password Masking](#password-masking)
5. [Implementation](#implementation)
6. [Luồng Masking trong API](#luồng-masking-trong-api)
7. [Test Cases](#test-cases)

---

## 🎯 Tổng quan

### Định nghĩa Data Masking

**Data Masking** là kỹ thuật che giấu một phần dữ liệu nhạy cảm khi hiển thị, trong khi vẫn giữ lại thông tin để nhận diện.

### Tại sao cần Data Masking?

```
Vấn đề:
├─ Frontend hiển thị email/phone đầy đủ
├─ Dễ bị nhìn trộm (xem qua vai, screenshot)
└─ Không an toàn cho user

Giải pháp:
├─ Che giấu phần nhạy cảm
├─ Giữ lại ký tự đầu/cuối để nhận diện
└─ Frontend vẫn có thể xác nhận user

Ví dụ:
  john@gmail.com → j***@gmail.com ✓
  0987654321     → 09****21       ✓
  SecurePass123  → ***            ✓
```

### So sánh: Encryption vs Masking

| Tiêu chí | Encryption | Data Masking |
|---------|-----------|-------------|
| **Mục đích** | Bảo vệ lưu trữ | Bảo vệ hiển thị |
| **Có khôi phục được không** | CÓ (với key) | KHÔNG (mất thông tin) |
| **Lúc áp dụng** | Khi save DB | Khi trả API |
| **Cần key** | CÓ | KHÔNG |
| **Query được không** | Không (binary) | N/A (output format) |
| **Ví dụ** | `encrypted_bytes` | `a***@gmail.com` |

### Khi nào áp dụng Masking?

```python
# Trong API response, có parameter: mask=true/false

# mask=true (default)
GET /users?mask=true
Response:
{
  "email": "j***@gmail.com",    ← Masked
  "phone": "09****21",           ← Masked
  "password": "***"              ← Masked
}

# mask=false (admin only?)
GET /users?mask=false
Response:
{
  "email": "john@gmail.com",    ← Plain (decrypted)
  "phone": "0987654321",         ← Plain (decrypted)
  "password": "SecurePass123"    ← Plain (decrypted)
}
```

---

## 📧 Email Masking

### Luật Masking Email

```
Quy tắc:
├─ Giữ ký tự đầu tiên
├─ Ẩn toàn bộ phần trước @ (trừ ký tự đầu)
└─ Giữ nguyên domain (@domain)
```

### Ví dụ

| Original | Masked | Giải thích |
|----------|--------|------------|
| `john@gmail.com` | `j***@gmail.com` | j + *** + @gmail.com |
| `alice_smith@yahoo.com` | `a***@yahoo.com` | a + *** + @yahoo.com |
| `b@test.co.uk` | `b***@test.co.uk` | b + *** + @test.co.uk |
| `a@a.com` | `a***@a.com` | a + *** + @a.com |
| `contact.me@company.org` | `c***@company.org` | c + *** + @company.org |

### Implementation

```python
def mask_email(email: str) -> str:
    """
    Mask email: giữ ký tự đầu + domain, ẩn phần giữa.
    
    Args:
        email: Email gốc (đã decrypt)
        
    Returns:
        str: Email đã mask
        
    Example:
        >>> mask_email("john@gmail.com")
        "j***@gmail.com"
    """
    if '@' not in email:
        return "***@***"
    
    # Split email
    local_part, domain = email.split('@')
    
    if len(local_part) == 0:
        return "***@" + domain
    
    # Mask local part: keep first char + ***
    masked_local = local_part[0] + "***"
    
    # Combine
    return masked_local + "@" + domain
```

### Test Cases

```python
def test_mask_email():
    assert mask_email("john@gmail.com") == "j***@gmail.com"
    assert mask_email("alice_smith@yahoo.com") == "a***@yahoo.com"
    assert mask_email("b@test.co.uk") == "b***@test.co.uk"
    assert mask_email("a@a.com") == "a***@a.com"
    print("✓ Email masking tests passed")
```

---

## 📱 Phone Masking

### Luật Masking Phone

```
Quy tắc:
├─ Giữ 2 số đầu (country code / area code)
├─ Ẩn số giữa (**** - 4 dấu sao)
├─ Giữ 2 số cuối (last digits)
└─ Total: xx****yy
```

### Ví dụ

| Original | Masked | Giải thích |
|----------|--------|------------|
| `0987654321` | `09****21` | 09 + **** + 21 |
| `0856123456` | `08****56` | 08 + **** + 56 |
| `01228899001` | `01****01` | 01 + **** + 01 |
| `+84987654321` | `+8****21` | +8 + **** + 21 |
| `0123456789` | `01****89` | 01 + **** + 89 |

### Implementation

```python
def mask_phone(phone: str) -> str:
    """
    Mask phone: giữ 2 số đầu + 2 số cuối, ẩn phần giữa.
    
    Args:
        phone: Số điện thoại gốc (đã decrypt)
        
    Returns:
        str: Số điện thoại đã mask
        
    Example:
        >>> mask_phone("0987654321")
        "09****21"
    """
    # Remove non-digit characters (keep only digits and +)
    digits_only = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    if len(digits_only) < 4:
        return "****"
    
    # Handle + prefix
    prefix = ""
    if digits_only.startswith('+'):
        prefix = digits_only[0]  # Keep +
        digits_only = digits_only[1:]  # Remove +
    
    # Get first 2 and last 2 digits
    first_two = digits_only[:2]
    last_two = digits_only[-2:]
    
    # Mask: xx****yy
    masked = prefix + first_two + "****" + last_two
    
    return masked
```

### Test Cases

```python
def test_mask_phone():
    assert mask_phone("0987654321") == "09****21"
    assert mask_phone("0856123456") == "08****56"
    assert mask_phone("01228899001") == "01****01"
    assert mask_phone("+84987654321") == "+8****21"
    assert mask_phone("0123456789") == "01****89"
    print("✓ Phone masking tests passed")
```

---

## 🔐 Password Masking

### Luật Masking Password

```
Quy tắc:
├─ Ẩn 100% mật khẩu
├─ Không hiển thị thông tin nào
└─ Cố định 6 dấu sao (hoặc = độ dài)
```

### Ví dụ

| Original | Masked |
|----------|--------|
| `SecurePass123` | `***` |
| `123456` | `***` |
| `VeryLongPassword12345` | `***` |
| `a` | `***` |
| (bất kỳ) | `***` |

### Implementation

```python
def mask_password(password: str) -> str:
    """
    Mask password: ẩn hoàn toàn, trả về dấu sao.
    
    Args:
        password: Mật khẩu gốc (đã decrypt)
        
    Returns:
        str: Dấu sao (không lộ thông tin)
        
    Example:
        >>> mask_password("SecurePass123")
        "***"
    """
    # Option 1: Cố định 3 dấu sao (recommended)
    return "***"
    
    # Option 2: Cố định 6 dấu sao (hoặc length(password))
    # return "*" * 6
    
    # Option 3: Dùng độ dài mật khẩu (ví dụ 8 ký tự)
    # return "*" * min(len(password), 8)
```

### Test Cases

```python
def test_mask_password():
    assert mask_password("SecurePass123") == "***"
    assert mask_password("123456") == "***"
    assert mask_password("VeryLongPassword") == "***"
    assert mask_password("a") == "***"
    print("✓ Password masking tests passed")
```

---

## 💻 Implementation (Masking Module)

### File: `security.py` hoặc `masking.py`

```python
"""
Data Masking Functions
Che giấu dữ liệu sensitive khi trả API
"""

def mask_email(email: str) -> str:
    """Email masking: j***@gmail.com"""
    if '@' not in email:
        return "***@***"
    
    local_part, domain = email.split('@')
    if len(local_part) == 0:
        return "***@" + domain
    
    masked_local = local_part[0] + "***"
    return masked_local + "@" + domain


def mask_phone(phone: str) -> str:
    """Phone masking: 09****21"""
    digits_only = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    if len(digits_only) < 4:
        return "****"
    
    prefix = ""
    if digits_only.startswith('+'):
        prefix = digits_only[0]
        digits_only = digits_only[1:]
    
    first_two = digits_only[:2]
    last_two = digits_only[-2:]
    
    return prefix + first_two + "****" + last_two


def mask_password(password: str) -> str:
    """Password masking: ***"""
    return "***"


def apply_masking(user_data: dict, mask: bool = True) -> dict:
    """
    Áp dụng masking cho user data nếu mask=true.
    
    Args:
        user_data: Dict chứa user info (decrypted)
        mask: Boolean flag
        
    Returns:
        Dict với dữ liệu đã mask (nếu mask=true)
    """
    if not mask:
        # Return dữ liệu gốc (decrypted)
        return user_data
    
    # Áp dụng masking
    masked_data = user_data.copy()
    
    if 'email' in masked_data:
        masked_data['email'] = mask_email(masked_data['email'])
    
    if 'phone' in masked_data:
        masked_data['phone'] = mask_phone(masked_data['phone'])
    
    if 'password' in masked_data:
        masked_data['password'] = mask_password(masked_data['password'])
    
    return masked_data
```

---

## 🔄 Luồng Masking trong API

### Scenario: GET /users?mask=true

```
┌─────────────────────────────────────────────────────├─
│ client request                                       │
│ GET /users?mask=true                                 │
└─────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────┐
│ Backend: Fetch from Database                        │
│ SELECT * FROM users                                 │
│ Result: (encrypted binary data)                     │
└─────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────┐
│ Decryption Layer                                    │
│ - Retrieve key: simple_hash(username + password)   │
│ - XOR decrypt: email, phone, password              │
│ Result: (decrypted plain text)                     │
│                                                     │
│ Example:                                            │
│   {                                                 │
│     "id": 1,                                        │
│     "username": "john_doe",                         │
│     "email": "john@gmail.com",                      │
│     "phone": "0987654321",                          │
│     "password": "SecurePass123"                     │
│   }                                                 │
└─────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────┐
│ Check Query Parameter: mask=?                       │
│                                                     │
│ if mask == true:  Apply masking ✓                  │
│ else:             Return plain data                │
└─────────────────────────────────────────────────────┘
                         │
                         ↓ (since mask=true)
┌─────────────────────────────────────────────────────┐
│ Apply Masking                                       │
│ - mask_email("john@gmail.com")     → "j***@gmail.com"  │
│ - mask_phone("0987654321")         → "09****21"    │
│ - mask_password("SecurePass123")   → "***"         │
│                                                     │
│ Result:                                             │
│   {                                                 │
│     "id": 1,                                        │
│     "username": "john_doe",                         │
│     "email": "j***@gmail.com",                      │
│     "phone": "09****21",                            │
│     "password": "***"                               │
│   }                                                 │
└─────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────┐
│ Return Response (200 OK)                            │
└─────────────────────────────────────────────────────┘
                         │
                         ↓
                   client receives
                   masked data ✓
```

### Pseudocode - API Handler

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int, mask: bool = True):
    # 1. Fetch from DB
    user_encrypted = db.query(User).filter(User.id == user_id).first()
    
    if not user_encrypted:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 2. Decrypt
    key = simple_hash(user_encrypted.username + password)
    user_decrypted = {
        "id": user_encrypted.id,
        "username": user_encrypted.username,
        "email": decrypt(user_encrypted.email, key),
        "phone": decrypt(user_encrypted.phone, key),
        "password": decrypt(user_encrypted.password, key),
    }
    
    # 3. Apply masking if needed
    user_response = apply_masking(user_decrypted, mask=mask)
    
    # 4. Return response
    return user_response
```

---

## 🧪 Test Cases

### Test Suite

```python
def test_masking_suite():
    """Run all masking tests"""
    
    # Email Masking
    assert mask_email("john@gmail.com") == "j***@gmail.com"
    assert mask_email("alice@test.co.uk") == "a***@test.co.uk"
    
    # Phone Masking
    assert mask_phone("0987654321") == "09****21"
    assert mask_phone("+84987654321") == "+8****21"
    
    # Password Masking
    assert mask_password("anything") == "***"
    assert mask_password("12345678") == "***"
    
    # Apply Masking to dict
    user = {
        "id": 1,
        "username": "john_doe",
        "email": "john@gmail.com",
        "phone": "0987654321",
        "password": "SecurePass123"
    }
    
    masked = apply_masking(user, mask=True)
    assert masked["email"] == "j***@gmail.com"
    assert masked["phone"] == "09****21"
    assert masked["password"] == "***"
    
    # No masking
    unmasked = apply_masking(user, mask=False)
    assert unmasked["email"] == "john@gmail.com"
    assert unmasked["phone"] == "0987654321"
    assert unmasked["password"] == "SecurePass123"
    
    print("✓ All masking tests passed!")

# Run
if __name__ == "__main__":
    test_masking_suite()
```

### Integration Test

```python
def test_api_masking():
    """Test API endpoint masking"""
    
    # Create user
    response = client.post("/api/users", json={
        "username": "test_user",
        "email": "test@gmail.com",
        "phone": "0912345678",
        "password": "Pass123"
    })
    assert response.status_code == 201
    user_id = response.json()["id"]
    
    # Get with masking
    response = client.get(f"/api/users/{user_id}?mask=true")
    assert response.status_code == 200
    user = response.json()
    
    # Verify masking applied
    assert user["email"] == "t***@gmail.com"
    assert user["phone"] == "09****78"
    assert user["password"] == "***"
    
    # Get without masking
    response = client.get(f"/api/users/{user_id}?mask=false")
    assert response.status_code == 200
    user = response.json()
    
    # Verify no masking
    assert user["email"] == "test@gmail.com"
    assert user["phone"] == "0912345678"
    assert user["password"] == "Pass123"
    
    print("✓ API masking integration test passed!")
```

---

## 🔒 Security Notes

### Khi nào sử dụng mask=false?

```
⚠️ Chỉ cho:
├─ Admin/staff (internal use)
├─ User xem dữ liệu của chính họ
└─ Các API endpoint require authentication

❌ Không cho:
├─ Public API
├─ User xem dữ liệu của người khác
└─ Unauthenticated requests
```

### Recommend Authentication

```python
# Add JWT/Authorization check:

@app.get("/users/{user_id}")
async def get_user(
    user_id: int, 
    mask: bool = True,
    current_user = Depends(get_current_user)  # ← Auth required
):
    # If viewing other user's data
    if user_id != current_user.id:
        # Always mask
        mask = True
    
    # ... rest of logic
```

---

**Phiên bản**: 1.0  
**Ngày cập nhật**: 28/03/2026  
**Liên quan**: [API_ENDPOINTS.md](./API_ENDPOINTS.md), [SECURITY.md](./SECURITY.md), [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
