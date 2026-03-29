"""
Security Module: Encryption & Hashing
XOR Encryption + Simple Hash Algorithm + Bcrypt
"""
from passlib.context import CryptContext
import os

# Bcrypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Master Key cho decrypt email/phone (cho admin xem được)
# Sử dụng env var hoặc default value
MASTER_KEY_SEED = os.getenv("MASTER_KEY_SEED", "csat_bmpt_master_key_2026")


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


def encrypt(data: str, key: int) -> bytes:
    """
    Mã hóa chuỗi input bằng XOR với key.
    
    Args:
        data: Chuỗi gốc (email/phone/password)
        key: Số từ 0-255
    
    Returns:
        bytes (binary data)
    
    Example:
        >>> encrypt("john@gmail.com", 215)
        b'\\xd5\\xac\\xb7\\xbd\\x97\\xb8\\xbe\\xb6\\xba\\xbb\\xe9\\xb4\\xac\\xbe'
    """
    encrypted_bytes = []
    for char in data:
        encrypted_char = ord(char) ^ key
        encrypted_bytes.append(encrypted_char)
    return bytes(encrypted_bytes)


def decrypt(encrypted_data: bytes, key: int) -> str:
    """
    Giải mã binary data bằng XOR với key.
    
    Args:
        encrypted_data: bytes (mã hóa)
        key: Số từ 0-255 (phải giống lúc encrypt)
    
    Returns:
        str (chuỗi gốc)
    
    Example:
        >>> encrypted = encrypt("john@gmail.com", 215)
        >>> decrypt(encrypted, 215)
        'john@gmail.com'
    """
    decrypted_chars = []
    for byte in encrypted_data:
        decrypted_char = chr(byte ^ key)
        decrypted_chars.append(decrypted_char)
    return ''.join(decrypted_chars)


def generate_key(username: str, password: str) -> int:
    """
    Sinh key encryption từ username + password.
    
    Args:
        username: Tên đăng nhập
        password: Mật khẩu
    
    Returns:
        int: Key (0-255)
    """
    combined = username + password
    key = simple_hash(combined)
    return key

def get_master_key() -> int:
    """
    Get Master Key để decrypt email/phone (admin xem được).
    Master Key là fixed value từ env var, chỉ admin/server biết.
    
    Returns:
        int: Master key (0-255)
    """
    return simple_hash(MASTER_KEY_SEED)

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
        return user_data
    
    masked_data = user_data.copy()
    
    if 'email' in masked_data and masked_data['email']:
        masked_data['email'] = mask_email(masked_data['email'])
    
    if 'phone' in masked_data and masked_data['phone']:
        masked_data['phone'] = mask_phone(masked_data['phone'])
    
    if 'password' in masked_data and masked_data['password']:
        masked_data['password'] = mask_password(masked_data['password'])
    
    return masked_data
