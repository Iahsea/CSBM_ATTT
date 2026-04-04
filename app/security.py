"""
Security Module: Encryption & Hashing
- Bcrypt (passlib) cho hash password
- AES-128 ECB tự cài đặt (không dùng thư viện ngoài) cho encrypt/decrypt
"""
from passlib.context import CryptContext
import os

# Bcrypt context cho password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# NOTE: Per-User Encryption Strategy
# ======================================
# Tất cả sensitive data (email, phone, password) được encrypt bằng per-user key
# Per-user key được sinh từ: username + password
# 
# Ưu điểm:
# - Mỗi user có key riêng => Admin cũng không thể xem email/phone của user khác
# - Tăng tính bảo mật cho từng user
#
# Hạn chế:
# - Khi user thay password, email/phone cần được re-encrypt với new key
# - Admin cũng không thể decrypt email/phone (trừ chính admin user của admin)
#
# KHÔNG còn dùng MASTER_KEY nữa (loại bỏ MASTER_KEY_SEED)


# =====================================================
# AES-128 (ECB) implementation - no external libraries
# =====================================================

SBOX = [
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
]

RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

INV_SBOX = [0] * 256
for i, v in enumerate(SBOX):
    INV_SBOX[v] = i


def _xtime(a: int) -> int:
    """GF(2^8) multiply by x."""
    return ((a << 1) ^ 0x1B) & 0xFF if a & 0x80 else (a << 1) & 0xFF


def _mul_gf(a: int, b: int) -> int:
    """GF(2^8) multiplication."""
    res = 0
    for _ in range(8):
        if b & 1:
            res ^= a
        a = _xtime(a)
        b >>= 1
    return res & 0xFF


def _key_expansion(key: bytes) -> list[bytes]:
    """Expand 16-byte key to 11 round keys (AES-128)."""
    w = bytearray(176)
    w[:16] = key
    for i in range(4, 44):
        temp = w[(i - 1) * 4 : i * 4]
        if i % 4 == 0:
            t0 = temp[0]
            temp = bytearray(
                [
                    SBOX[temp[1]] ^ RCON[i // 4],
                    SBOX[temp[2]],
                    SBOX[temp[3]],
                    SBOX[t0],
                ]
            )
        for j in range(4):
            w[i * 4 + j] = w[(i - 4) * 4 + j] ^ temp[j]
    return [bytes(w[i * 16 : (i + 1) * 16]) for i in range(11)]


def _decrypt_block(block: bytes, round_keys: list[bytes]) -> bytes:
    state = bytearray(block)
    _add_round_key(state, round_keys[10])
    for r in range(9, 0, -1):
        _inv_shift_rows(state)
        _inv_sub_bytes(state)
        _add_round_key(state, round_keys[r])
        _inv_mix_columns(state)
    _inv_shift_rows(state)
    _inv_sub_bytes(state)
    _add_round_key(state, round_keys[0])
    return bytes(state)

def _add_round_key(state: bytearray, rk: bytes) -> None:
    for i in range(16):
        state[i] ^= rk[i]

def _sub_bytes(state: bytearray) -> None:
    for i in range(16):
        state[i] = SBOX[state[i]]


def _inv_sub_bytes(state: bytearray) -> None:
    for i in range(16):
        state[i] = INV_SBOX[state[i]]


def _shift_rows(s: bytearray) -> None:
    s[1], s[5], s[9], s[13] = s[5], s[9], s[13], s[1]
    s[2], s[6], s[10], s[14] = s[10], s[14], s[2], s[6]
    s[3], s[7], s[11], s[15] = s[15], s[3], s[7], s[11]


def _inv_shift_rows(s: bytearray) -> None:
    s[1], s[5], s[9], s[13] = s[13], s[1], s[5], s[9]
    s[2], s[6], s[10], s[14] = s[10], s[14], s[2], s[6]
    s[3], s[7], s[11], s[15] = s[7], s[11], s[15], s[3]


def _inv_mix_columns(s: bytearray) -> None:
    for i in range(0, 16, 4):
        c0, c1, c2, c3 = s[i : i + 4]
        s[i] = _mul_gf(c0, 0x0E) ^ _mul_gf(c1, 0x0B) ^ _mul_gf(c2, 0x0D) ^ _mul_gf(c3, 0x09)
        s[i + 1] = _mul_gf(c0, 0x09) ^ _mul_gf(c1, 0x0E) ^ _mul_gf(c2, 0x0B) ^ _mul_gf(c3, 0x0D)
        s[i + 2] = _mul_gf(c0, 0x0D) ^ _mul_gf(c1, 0x09) ^ _mul_gf(c2, 0x0E) ^ _mul_gf(c3, 0x0B)
        s[i + 3] = _mul_gf(c0, 0x0B) ^ _mul_gf(c1, 0x0D) ^ _mul_gf(c2, 0x09) ^ _mul_gf(c3, 0x0E)


def _mix_columns(s: bytearray) -> None:
    for i in range(0, 16, 4):
        c0, c1, c2, c3 = s[i : i + 4]
        s[i] = _xtime(c0) ^ (_xtime(c1) ^ c1) ^ c2 ^ c3
        s[i + 1] = c0 ^ _xtime(c1) ^ (_xtime(c2) ^ c2) ^ c3
        s[i + 2] = c0 ^ c1 ^ _xtime(c2) ^ (_xtime(c3) ^ c3)
        s[i + 3] = (_xtime(c0) ^ c0) ^ c1 ^ c2 ^ _xtime(c3)




def _encrypt_block(block: bytes, round_keys: list[bytes]) -> bytes:
    state = bytearray(block)
    _add_round_key(state, round_keys[0])
    for r in range(1, 10):
        _sub_bytes(state)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, round_keys[r])
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[10])
    return bytes(state)





def _pkcs7_pad(data: bytes) -> bytes:
    pad_len = 16 - (len(data) % 16)
    return data + bytes([pad_len]) * pad_len


def _pkcs7_unpad(data: bytes) -> bytes:
    if not data:
        return data
    pad_len = data[-1]
    if 0 < pad_len <= 16 and data.endswith(bytes([pad_len]) * pad_len):
        return data[:-pad_len]
    return data


def _normalize_key(secret_key: str | bytes) -> bytes:
    """Force key to 16 bytes (pad with zeros or truncate)."""
    if isinstance(secret_key, (bytes, bytearray)):
        kb = bytes(secret_key)
    else:
        kb = str(secret_key).encode("utf-8")
    if len(kb) < 16:
        kb = kb + bytes(16 - len(kb))
    else:
        kb = kb[:16]
    return kb


def aes_encrypt_bytes(raw: str, secret_key: str | bytes) -> bytes:
    """AES-128 ECB encrypt, return cipher bytes."""
    key = _normalize_key(secret_key)
    round_keys = _key_expansion(key)
    data = _pkcs7_pad(raw.encode("utf-8"))
    out = bytearray()
    for i in range(0, len(data), 16):
        out += _encrypt_block(data[i : i + 16], round_keys)
    return bytes(out)


def aes_decrypt_bytes(cipher: bytes, secret_key: str | bytes) -> str:
    """AES-128 ECB decrypt cipher bytes, return UTF-8 string."""
    # Gracefully handle non-16-multiple or empty input
    if not cipher or len(cipher) % 16 != 0:
        try:
            return cipher.decode("utf-8")  # type: ignore[arg-type]
        except Exception:
            return str(cipher)

    key = _normalize_key(secret_key)
    round_keys = _key_expansion(key)
    out = bytearray()
    for i in range(0, len(cipher), 16):
        out += _decrypt_block(cipher[i : i + 16], round_keys)
    out = _pkcs7_unpad(bytes(out))
    try:
        return out.decode("utf-8")
    except UnicodeDecodeError:
        return out.decode("latin1")


def hash_password(password: str) -> str:
    """
    Hash password bằng bcrypt.
    
    Args:
        password: Password plain text
    
    Returns:
        Hashed password
    
    Example:
        >>> hash_password("SecurePass123")
        "$2b$12$..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Xác thực password với bcrypt.
    
    Args:
        plain_password: Password plain text (từ request)
        hashed_password: Hashed password (từ DB)
    
    Returns:
        True nếu khớp, False nếu không
    
    Example:
        >>> verify_password("SecurePass123", "$2b$12$...")
        True
    """
    return pwd_context.verify(plain_password, hashed_password)


def simple_hash(data: str) -> int:
    """
    Sinh hash từ chuỗi input.
    
    Công thức:
        result = (result * 31 + ord(char)) % 256
    
    Args:
        data: Chuỗi input (username + password)
    
    Returns:
        Số nguyên từ 0-255 (1 byte)
    
    Example:
        >>> simple_hash("john_doeSecurePass123")
        215
    """
    result = 0
    for i in range(len(data)):
        result = (result * 31 + ord(data[i])) % 256
    return result


def encrypt(data: str, key: str | bytes | int) -> bytes:
    """Mã hóa AES-128 (ECB, PKCS7) trả về bytes để lưu DB."""
    return aes_encrypt_bytes(data, key)


def decrypt(encrypted_data: bytes, key: str | bytes | int) -> str:
    """Giải mã AES-128 (ECB, PKCS7) từ bytes DB về string."""
    return aes_decrypt_bytes(encrypted_data, key)


def generate_key(username: str, password: str) -> bytes:
    """
    Sinh secret key 16 byte từ username + password.
    
    Key này được dùng để encrypt/decrypt tất cả sensitive data (email, phone, password).
    Mỗi user có key riêng => Admin không thể xem email/phone của user khác.
    
    Args:
        username: Username của user
        password: Password plain text của user
    
    Returns:
        bytes: 16-byte key (padded or truncated từ username + password)
    
    Note:
        - Khi user thay password, email/phone cần re-encrypt với new key
        - Không sử dụng MASTER_KEY nữa
    """
    return _normalize_key(username + password)

# Masking Functions
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
    
    local_part, domain = email.split('@', 1)
    
    if len(local_part) == 0:
        return "***@" + domain
    
    masked_local = local_part[0] + "***"
    return masked_local + "@" + domain


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
    digits_only = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    if len(digits_only) < 4:
        return "****"
    
    prefix = ""
    if digits_only.startswith('+'):
        prefix = digits_only[0]
        digits_only = digits_only[1:]
    
    first_two = digits_only[:2]
    last_two = digits_only[-2:]
    
    masked = prefix + first_two + "****" + last_two
    return masked


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
    return "***"


def _prng_next(state: list) -> int:
    """Pseudorandom generator (LCG) without stdlib random."""
    # next = (a * prev + c) mod m, using glibc-like constants
    state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
    return state[0]


def _seeded_shuffle(text: str, seed: int) -> str:
    """Deterministic shuffle (Fisher-Yates) using LCG."""
    if not text:
        return text
    chars = list(text)
    state = [seed]
    for i in range(len(chars) - 1, 0, -1):
        j = _prng_next(state) % (i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def _seeded_noise(text: str, seed: int, noise_charset: str = "#@!$%^&*+-") -> str:
    """Insert deterministic noise characters using LCG (no stdlib random)."""
    if not text:
        return text
    state = [seed]
    out = []
    for ch in text:
        out.append(ch)
        rand_norm = (_prng_next(state) & 0xFFFF) / 65536.0
        if rand_norm < 0.4:  # 40% chance to inject noise
            idx = _prng_next(state) % len(noise_charset)
            out.append(noise_charset[idx])
    return "".join(out)


def shuffle_text(text: str) -> str:
    """Mask bằng xáo trộn vị trí ký tự (không khôi phục được)."""
    return _seeded_shuffle(text, simple_hash(text)) if text else text


def add_noise(text: str) -> str:
    """Mask bằng thêm nhiễu (không khôi phục được)."""
    return _seeded_noise(text, simple_hash(text)) if text else text


def fake_email(email: str) -> str:
    """Thay thế email bằng giá trị giả nhưng cùng cấu trúc cơ bản (LCG)."""
    seed = simple_hash(email)
    state = [seed]
    rand_num = (_prng_next(state) % 9000) + 1000  # 1000-9999
    user_part = f"user{rand_num}"
    domain = "example.com"
    return f"{user_part}@{domain}"


def fake_phone(phone: str) -> str:
    """Thay thế phone bằng dãy số giả cùng độ dài (LCG)."""
    digits = ''.join(c for c in phone if c.isdigit()) or "000000"
    seed = simple_hash(digits)
    state = [seed]
    return ''.join(str(_prng_next(state) % 10) for _ in range(len(digits)))


def fake_password(password: str) -> str:
    """Password giả; luôn ẩn hoàn toàn."""
    return "***fake***" if password else "***"


def apply_masking(user_data: dict, mask: bool = True, mode: str = "mask") -> dict:
    """
    Áp dụng che giấu dữ liệu với nhiều phương pháp.
    mode: "mask" (che ký tự), "shuffle" (xáo trộn),
          "fake" (thay bằng dữ liệu giả), "noise" (thêm nhiễu).
    """
    if not mask:
        return user_data

    mode = (mode or "mask").lower()
    masked_data = user_data.copy()

    def _mask_email(val: str) -> str:
        if mode == "mask":
            return mask_email(val)
        if mode == "shuffle":
            return shuffle_text(val)
        if mode == "fake":
            return fake_email(val)
        if mode == "noise":
            return add_noise(val)
        return mask_email(val)

    def _mask_phone(val: str) -> str:
        if mode == "mask":
            return mask_phone(val)
        if mode == "shuffle":
            return shuffle_text(val)
        if mode == "fake":
            return fake_phone(val)
        if mode == "noise":
            return add_noise(val)
        return mask_phone(val)

    def _mask_password(val: str) -> str:
        if mode == "mask":
            return mask_password(val)
        if mode == "shuffle":
            return shuffle_text(val)
        if mode == "fake":
            return fake_password(val)
        if mode == "noise":
            return add_noise(val)
        return mask_password(val)

    if "email" in masked_data and masked_data["email"]:
        masked_data["email"] = _mask_email(masked_data["email"])

    if "phone" in masked_data and masked_data["phone"]:
        masked_data["phone"] = _mask_phone(masked_data["phone"])

    if "password" in masked_data and masked_data["password"]:
        masked_data["password"] = _mask_password(masked_data["password"])

    return masked_data
