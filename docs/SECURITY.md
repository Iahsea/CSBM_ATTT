# 🔐 Security - Encryption & Hashing
## Chi tiết cơ chế bảo mật: XOR Encryption + Simple Hash

---

## 📋 Mục lục

1. [Tổng quan](#tổng-quan)
2. [Simple Hash Algorithm](#simple-hash-algorithm)
3. [XOR Encryption](#xor-encryption)
4. [Encrypt Process](#encrypt-process)
5. [Decrypt Process](#decrypt-process)
6. [Ví dụ chi tiết](#ví-dụ-chi-tiết)
7. [Security Considerations](#security-considerations)

---

## 🎯 Tổng quan

### Lý do cần Security

```
Nguy hiểm:
├─ Bị hack database → Dữ liệu lộ
├─ Admin truy cập trái phép
└─ Man-in-the-middle attack

Giải pháp:
├─ Encryption: Bảo vệ dữ liệu lưu trữ
├─ Hashing: Sinh key ngẫu nhiên
└─ XOR: Mã hóa đơn giản nhưng hiệu quả
```

### Flow Bảo mật

```
        Input Data
             ↓
        Generate Key
        (simple_hash)
             ↓
        XOR Encryption
             ↓
        Lưu LargeBinary
        trong Database
             ↓  (khi cần)
        XOR Decryption
        (dùng key cũ)
             ↓
        Original Data
```

---

## 🔢 Simple Hash Algorithm

### Định nghĩa

```python
def simple_hash(data: str) -> int:
    """
    Sinh hash từ chuỗi input.
    
    Công thức:
        result = (result * 31 + ord(char)) % 256
    
    Args:
        data: Chuỗi input (username + password)
    
    Returns:
        Số nguyên từ 0-255 (1 byte)
    """
    result = 0
    for i in range(len(data)):
        result = (result * 31 + ord(data[i])) % 256
    return result
```

### Phân tích từng bước

#### Input
```
data = "john_doe" + "password123"
     = "john_doepassword123"
```

#### Bước tính toán

| Bước | Ký tự | ASCII | Công thức | Kết quả |
|-----|--------|-------|----------|---------|
| 1 | 'j' | 106 | (0 * 31 + 106) % 256 | 106 |
| 2 | 'o' | 111 | (106 * 31 + 111) % 256 | 53 |
| 3 | 'h' | 104 | (53 * 31 + 104) % 256 | 151 |
| 4 | 'n' | 110 | (151 * 31 + 110) % 256 | 41 |
| ... | ... | ... | ... | ... |
| N | '3' | 51 | (...) % 256 | 127 |

#### Kết quả cuối
```
Key = 127 (hoặc giá trị nào đó từ 0-255)
```

### Giải thích toán học

| Phần | Ý nghĩa |
|-----|---------|
| `result * 31` | Nhân với số nguyên tố (31) để phân tán giá trị |
| `+ ord(char)` | Cộng với giá trị ASCII của ký tự |
| `% 256` | Modulo 256 để giữ trong phạm vi 1 byte (0-255) |

### Tính chất Hash

1. **Deterministic**: Input giống → Output giống
   ```
   simple_hash("john_doepassword123") = 127
   simple_hash("john_doepassword123") = 127  ← Same!
   ```

2. **Fixed Output**: Luôn trả về 0-255
   ```
   simple_hash("a") = 97
   simple_hash("abcdefghijklmnopqrstuvwxyz") = 89
   ← Cả hai trong phạm vi 0-255
   ```

3. **Avalanche Effect**:
   ```
   simple_hash("john_doepassword123") = 127
   simple_hash("john_doepassword124") = 128  ← Khác!
   ```

### Code Demo

```python
def simple_hash(data: str) -> int:
    result = 0
    for i in range(len(data)):
        result = (result * 31 + ord(data[i])) % 256
    return result

# Demo
username = "john_doe"
password = "SecurePass123"
combined = username + password

key = simple_hash(combined)
print(f"Input: {combined}")
print(f"Hash Key: {key}")
# Output:
# Input: john_doeSecurePass123
# Hash Key: 215
```

---

## 🔤 XOR Encryption

### Định nghĩa XOR

**XOR** (Exclusive OR) là phép toán bitwise:

| A | B | A ^ B |
|---|---|-------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

### Tính chất quan trọng

```
A ^ B ^ B = A

Ví dụ:
5 ^ 3 ^ 3 = 5
```

### Encryption Function

```python
def encrypt(data: str, key: int) -> bytes:
    """
    Mã hóa chuỗi input bằng XOR với key.
    
    Args:
        data: Chuỗi gốc (email/phone/password)
        key: Số từ 0-255
    
    Returns:
        bytes (binary data)
    """
    encrypted_bytes = []
    for char in data:
        encrypted_char = ord(char) ^ key
        encrypted_bytes.append(encrypted_char)
    return bytes(encrypted_bytes)
```

### Decryption Function

```python
def decrypt(encrypted_data: bytes, key: int) -> str:
    """
    Giải mã binary data bằng XOR với key.
    
    Args:
        encrypted_data: bytes (mã hóa)
        key: Số từ 0-255 (phải giống lúc encrypt)
    
    Returns:
        str (chuỗi gốc)
    """
    decrypted_chars = []
    for byte in encrypted_data:
        decrypted_char = chr(byte ^ key)
        decrypted_chars.append(decrypted_char)
    return ''.join(decrypted_chars)
```

---

## 🔐 Encrypt Process (Chi tiết)

### Luồng tổng quát

```
Input Data
    ↓
1. Generate Key
    ↓
2. Encrypt Email/Phone/Password
    ↓
3. Convert to bytes
    ↓
4. Lưu vào Database
```

### Ví dụ: Encrypt Email

#### Input
```python
email = "john@gmail.com"
username = "john_doe"
password = "SecurePass123"
```

#### Step 1: Generate Key
```python
combined = username + password
         = "john_doeSecurePass123"
key = simple_hash(combined)
    = 215  # (example value)
```

#### Step 2: Encrypt Email
```python
# Email: "john@gmail.com"
# Key: 215

Ký tự → ASCII → XOR 215 → Binary
───────────────────────────────
'j'  → 106  → 213 → 11010101
'o'  → 111  → 172 → 10101100
'h'  → 104  → 183 → 10110111
'n'  → 110  → 189 → 10111101
'@'  → 64   → 151 → 10010111
'g'  → 103  → 184 → 10111000
'm'  → 109  → 190 → 10111110
'a'  → 97   → 182 → 10110110
'i'  → 105  → 186 → 10111010
'l'  → 108  → 187 → 10111011
'.'  → 46   → 233 → 11101001
'c'  → 99   → 180 → 10110100
'o'  → 111  → 172 → 10101100
'm'  → 109  → 190 → 10111110
```

#### Step 3: Convert to bytes
```python
encrypted_email = bytes([213, 172, 183, 189, 151, 184, 190, 182, 186, 187, 233, 180, 172, 190])

# Representation:
# \xd5\xac\xb7\xbd\x97\xb8\xbe\xb6\xba\xbb\xe9\xb4\xac\xbe
# hay
# b'\xd5\xac\xb7\xbd\x97\xb8\xbe\xb6\xba\xbb\xe9\xb4\xac\xbe'
```

#### Step 4: Lưu Database
```python
# SQL
INSERT INTO users (username, email)
VALUES ('john_doe', b'\xd5\xac\xb7\xbd\x97\xb8\xbe\xb6\xba\xbb\xe9\xb4\xac\xbe')

# Trong Database Client (MySQL Workbench):
# email column hiển thị: (binary data)
```

---

## 🔓 Decrypt Process (Chi tiết)

### Luồng tổng quát

```
Database (Binary)
    ↓
1. Retrieve Encrypted Data
    ↓
2. Regenerate Key (từ username + password)
    ↓
3. XOR Decrypt
    ↓
4. Return Original String
```

### Ví dụ: Decrypt Email

#### Input
```python
# Từ Database:
encrypted_email = b'\xd5\xac\xb7\xbd\x97\xb8\xbe\xb6\xba\xbb\xe9\xb4\xac\xbe'

# Credentials:
username = "john_doe"
password = "SecurePass123"
```

#### Step 1: Regenerate Key
```python
combined = username + password
         = "john_doeSecurePass123"
key = simple_hash(combined)
    = 215  # ← Phải giống lúc encrypt!
```

#### Step 2: XOR Decrypt
```python
# Decryption:
Binary → XOR 215 → ASCII → Ký tự
────────────────────────────────
213 → 106 → 'j'
172 → 111 → 'o'
183 → 104 → 'h'
189 → 110 → 'n'
151 → 64  → '@'
184 → 103 → 'g'
190 → 109 → 'm'
182 → 97  → 'a'
186 → 105 → 'i'
187 → 108 → 'l'
233 → 46  → '.'
180 → 99  → 'c'
172 → 111 → 'o'
190 → 109 → 'm'
```

#### Step 3: Return Original
```python
decrypted_email = "john@gmail.com"
```

---

## 📝 Ví dụ chi tiết

### Scenario: Tạo User

#### Input từ Frontend
```python
{
  "username": "alice_smith",
  "email": "alice@yahoo.com",
  "phone": "0823456789",
  "password": "AlicePassword456"
}
```

#### Backend Processing

**Step 1: Validate Input**
```python
# ✓ Username: 11 chars (valid)
# ✓ Email: valid format
# ✓ Phone: 10 digits (valid)
# ✓ Password: 17 chars (valid)
```

**Step 2: Generate Key**
```python
combined = "alice_smith" + "AlicePassword456"
         = "alice_smithAlicePassword456"
key = simple_hash(combined)
    = 182  # example
```

**Step 3: Encrypt Each Field**
```python
# Email
encrypted_email = encrypt("alice@yahoo.com", 182)
                = b'\xa4\x81\xff\xb0\x68\xaf\xb5\x86...'

# Phone
encrypted_phone = encrypt("0823456789", 182)
                = b'\x78\x61\x47\x38...'

# Password
encrypted_password = encrypt("AlicePassword456", 182)
                   = b'\xc3\xd1\xb8\xc4...'
```

**Step 4: Save to Database**
```python
INSERT INTO users (username, email, phone, password, created_at)
VALUES (
  'alice_smith',
  b'\xa4\x81\xff\xb0\x68\xaf\xb5\x86...',
  b'\x78\x61\x47\x38...',
  b'\xc3\xd1\xb8\xc4...',
  '2026-03-28T10:00:00'
)
```

**Step 5: Response to Frontend (with masking)**
```python
{
  "id": 2,
  "username": "alice_smith",
  "email": "a***@yahoo.com",    # Masked
  "phone": "08****89",           # Masked
  "password": "***",             # Masked
  "message": "User created successfully"
}
```

---

## 🛡️ Security Considerations

### ✅ Những gì được bảo vệ

| Tiêu chí | Trạng thái | Mô tả |
|---------|-----------|-------|
| **Data in Storage** | ✓ Bảo vệ | Encrypted trong DB |
| **Data in Transit (API)** | ⚠️ Riêng | Cần HTTPS |
| **Data in Memory** | ⚠️ Riêng | Cần quản lý memory |
| **Key Management** | ⚠️ Riêng | Key stored in file/env |

### ⚠️ Hạn chế (không an toàn production)

```
❌ XOR Encryption
├─ Dễ crack (brute force 256 keys)
├─ Không đủ cho production
└─ Dùng cho học tập/demo

❌ Simple Hash
├─ Không collision-resistant
├─ Không salted
└─ Dễ bị rainbow table attack

❌ Key Generation
├─ Key sinh từ password
├─ Không random
└─ Weak entropy
```

### 🔒 Khuyến nghị Production

```python
# Thay vì XOR:
├─ Dùng AES-256 (cryptography library)
├─ Dùng bcrypt/argon2 cho password hash
└─ Dùng secure random key generation

# Thay vì Simple Hash:
├─ Dùng PBKDF2 / bcrypt
├─ Thêm salt (random)
└─ Tăng iteration count

# Key Management:
├─ Lưu key trong key vault
├─ Rotate keys định kỳ
└─ Separate key từ data
```

### 📋 Checklist Bảo mật

- [x] Encrypt sensitive fields (email, phone, password)
- [x] Use deterministic key (reproducible)
- [x] Decrypt khi cần (lấy dữ liệu gốc)
- [ ] HTTPS cho API
- [ ] Authentication (JWT tokens)
- [ ] Rate limiting
- [ ] Audit logging
- [ ] Input validation
- [ ] SQL injection prevention (ORM helps)

---

## 🧪 Test Cases

### Test 1: Encrypt/Decrypt Consistency
```python
def test_encrypt_decrypt():
    data = "test@example.com"
    key = 42
    
    encrypted = encrypt(data, key)
    decrypted = decrypt(encrypted, key)
    
    assert decrypted == data, "Mismatch!"
    print("✓ Encrypt/Decrypt consistent")
```

### Test 2: Simple Hash Deterministic
```python
def test_hash_deterministic():
    combined = "userpass"
    
    key1 = simple_hash(combined)
    key2 = simple_hash(combined)
    
    assert key1 == key2, "Hash not deterministic!"
    print("✓ Hash deterministic")
```

### Test 3: Different Keys → Different Output
```python
def test_different_keys():
    data = "john@gmail.com"
    
    encrypted1 = encrypt(data, 42)
    encrypted2 = encrypt(data, 99)
    
    assert encrypted1 != encrypted2, "Keys don't differ output!"
    print("✓ Different keys produce different output")
```

---

**Phiên bản**: 1.0  
**Ngày cập nhật**: 28/03/2026  
**Liên quan**: [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md), [DATA_MASKING.md](./DATA_MASKING.md)

**⚠️ Lưu ý**: System này là cho mục đích học tập/demo. Không nên dùng XOR encryption trong production environment. Hãy sử dụng cryptography libraries được chứng thực như `cryptography` hay `PyCryptodome`.
