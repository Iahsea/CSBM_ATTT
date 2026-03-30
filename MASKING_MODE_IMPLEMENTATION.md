# Masking Mode Feature - Complete Implementation Guide

## Overview

This document summarizes the complete implementation of the **Data Masking Mode Control** feature that was added to the CSAT-BMPT backend.

---

## What Was Implemented

### Feature: Admin-Controlled Data Masking Modes

**Goal:** Allow administrators to choose how sensitive user data (email, phone) is masked when displayed to users or other admins.

**4 Masking Methods:**
1. **mask** - Keep first/last character, replace middle with `*`
   - Example: `john@gmail.com` → `j***@gmail.com`
2. **shuffle** - Deterministically shuffle character positions
   - Example: `john@gmail.com` → `mliaoag@m.c`
3. **fake** - Replace with realistic fake data
   - Example: `john@gmail.com` → `user5234@example.com`
4. **noise** - Add random special characters
   - Example: `john@gmail.com` → `j#o@h!n*@#$g%m^a&i*l(.c)o%m`

---

## Code Changes

### Core Files Modified

#### 1. `app/models.py`
- **Added:** `masking_mode` field to User model
- **Type:** String(20)
- **Default:** "mask"
- **Purpose:** Stores admin's chosen masking preference per user

```python
masking_mode = sa.Column(sa.String(20), default="mask", nullable=True)
```

#### 2. `app/security.py`
- **Added Functions:**
  - `shuffle_text(text, seed)` - Deterministic shuffle with seeded random
  - `add_noise(text, seed)` - Inject noise at 40% probability
  - `fake_email(seed)` - Generate `user{N}@example.com`
  - `fake_phone(seed)` - Generate random 10-digit phone
  - `fake_password(seed)` - Generate random password

- **Extended:** `apply_masking(user_data, mask, mode)`
  - Now accepts `mode` parameter: "mask"|"shuffle"|"fake"|"noise"
  - Routes to appropriate masking function

#### 3. `app/schemas.py`
- **Added:** `MaskingModeRequest` schema
  - Field: `masking_mode: str`
  - Validates in ["mask", "shuffle", "fake", "noise"]

#### 4. `app/routers/user.py`
- **New Endpoint:** `PATCH /users/{user_id}/masking-mode`
  - Admin-only access
  - Validates masking mode
  - Updates user.masking_mode in database
  - Returns admin view (decrypted data)

- **Updated:** `GET /users` and `GET /users/{user_id}`
  - Added `mask_mode` query parameter for override
  - Uses stored `user.masking_mode` if available
  - Falls back to "mask" if not set

- **New Helper:** `_user_response_with_masking(user, mask_mode)`
  - Applies stored or overridden masking mode
  - Returns masked pattern for non-admin users

#### 5. `migrations/add_masking_mode.sql`
- **Added:** SQL migration to add column to database
- **Creates:** Index on masking_mode for performance

```sql
ALTER TABLE users ADD COLUMN masking_mode VARCHAR(20) DEFAULT 'mask';
CREATE INDEX idx_masking_mode ON users(masking_mode);
```

---

## How It Works

### Admin Sets Masking Mode

```
Admin: PATCH /users/3/masking-mode
Body: { "masking_mode": "shuffle" }

Backend:
  1. Check user is admin ✓
  2. Validate mode in ["mask","shuffle","fake","noise"] ✓
  3. Update: users.masking_mode = "shuffle" WHERE id = 3
  4. Return user data (admin sees decrypted)
```

### User Views Data with Applied Masking

```
User: GET /users/3
Header: Authorization: Bearer <token>

Backend:
  1. Retrieve user record → masking_mode = "shuffle"
  2. Decrypt email with MASTER_KEY → "john@gmail.com"
  3. Apply shuffle masking → "mliaoag@m.c"
  4. Return to user → email: "mliaoag@m.c"
```

### Override with Query Parameter

```
User: GET /users/3?mask_mode=fake
Header: Authorization: Bearer <token>

Backend:
  1. User's stored mode = "shuffle"
  2. Query param override = "fake"
  3. Apply fake masking instead → user5234@example.com
  4. Stored mode unchanged (still "shuffle")
```

---

## API Endpoints

### 1. Set Masking Mode (Admin Only)
```
PATCH /users/{user_id}/masking-mode
Header: Authorization: Bearer <admin_token>
Body: { "masking_mode": "fake" }

Response:
{
  "id": 3,
  "username": "User",
  "email": "john.doe@gmail.com",     // Admin sees full
  "phone": "0987654321",              // Admin sees full
  "masking_mode": "fake"
}
```

### 2. User Views Profile (Uses Masking Mode)
```
GET /users/3
Header: Authorization: Bearer <user_token>

Response (with masking_mode="fake"):
{
  "id": 3,
  "username": "User",
  "email": "user5234@example.com",    // Masked as fake
  "phone": "9876543210",              // Masked as fake
  "masking_mode": "fake"
}
```

### 3. List Users (Uses Stored Masking Mode)
```
GET /users?skip=0&limit=10
Header: Authorization: Bearer <user_token>

Response: All users masked with their stored masking_mode
```

### 4. Override Masking Mode
```
GET /users/3?mask_mode=noise
Header: Authorization: Bearer <user_token>

Response: Data masked with 'noise' instead of stored 'fake'
```

---

## Database Migration

**Location:** `migrations/add_masking_mode.sql`

**To Run:**
```bash
# Option 1: MySQL CLI
mysql -u root -p csat_bmpt < migrations/add_masking_mode.sql

# Option 2: Python
import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root', database='csat_bmpt')
cursor = conn.cursor()
with open('migrations/add_masking_mode.sql') as f:
    for statement in f.read().split(';'):
        if statement.strip():
            cursor.execute(statement)
conn.commit()

# Option 3: Verify
DESCRIBE users;  # Should show 'masking_mode' column
```

---

## Testing

### Test Script
**Location:** `test_masking_modes.py`

**Features:**
- Login as admin and user
- Admin sets different masking modes
- User views data with applied masking
- Test all 4 modes
- Test query parameter override
- Verify admin always sees decrypted

**To Run:**
```bash
# Make sure FastAPI is running on localhost:8000
python test_masking_modes.py
```

---

## Important Technical Details

### Deterministic vs. Random

- **shuffle:** Uses `Random(seed)` with data as seed → same input always produces same output
- **fake:** Uses seed to generate same fake data → consistent across requests
- **noise:** Uses seed for randomness → same input = same noise pattern
- **All modes:** Reproducible (running twice on same data gives same masked result)

### Encryption Keys

- **Master Key:** Used to decrypt email/phone (`MASTER_KEY_SEED` env var)
- **Per-User Key:** Used to encrypt password (username+password)
- **Admin:** Always has access to master key → sees decrypted data
- **Regular User:** Cannot decrypt email/phone → sees masked pattern

### Fallback Behavior

- If user cannot decrypt data (no key): Shows masked pattern "***@***"
- If masking_mode not set: Uses default "mask" mode
- If masking_mode is invalid: Falls back to "mask" mode
- Admin always sees decrypted, regardless of masking_mode

---

## Verification Checklist

- [ ] Migration SQL executed successfully
- [ ] New `masking_mode` column exists in users table
- [ ] Production server restarted
- [ ] Admin can set masking mode via PATCH endpoint
- [ ] User sees data masked according to masking_mode
- [ ] Query parameter override works correctly
- [ ] All 4 masking modes produce valid output
- [ ] Admin always sees decrypted data
- [ ] Test script runs without errors

---

## Example Workflow

### Step 1: Admin Sets Mode
```bash
curl -X PATCH http://localhost:8000/users/3/masking-mode \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"masking_mode": "shuffle"}'
```

### Step 2: User Views Data
```bash
curl -X GET http://localhost:8000/users/3 \
  -H "Authorization: Bearer $USER_TOKEN"

# Output: Email is shuffled (e.g., "mliaoag@m.c")
```

### Step 3: Admin Changes Mode
```bash
curl -X PATCH http://localhost:8000/users/3/masking-mode \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"masking_mode": "fake"}'
```

### Step 4: User Sees Updated Masked Data
```bash
curl -X GET http://localhost:8000/users/3 \
  -H "Authorization: Bearer $USER_TOKEN"

# Output: Email is now fake (e.g., "user5234@example.com")
```

---

## Files Created/Modified

**Modified Files:**
1. `app/models.py` - Added masking_mode column
2. `app/security.py` - Added masking functions
3. `app/schemas.py` - Added MaskingModeRequest
4. `app/routers/user.py` - Added PATCH endpoint

**Created Files:**
1. `migrations/add_masking_mode.sql` - Database migration
2. `test_masking_modes.py` - End-to-end test script
3. `MASKING_MODE_GUIDE.md` - User guide
4. `MASKING_MODE_IMPLEMENTATION.md` - This file

---

## Summary

The data masking mode feature provides administrators with granular control over how sensitive user data is displayed throughout the application. Each user can have a different masking mode set by administrators, allowing for customized privacy levels based on organizational needs.

The implementation is:
- **Secure:** Uses encryption keys for data protection
- **Flexible:** 4 different masking methods to choose from
- **Deterministic:** Same input always produces same output
- **Backward Compatible:** Default mode is "mask" for existing users
- **Admin-Controlled:** Regular users cannot change their own masking mode

---

**Status:** ✅ Complete and Ready for Testing  
**Created:** 2026-03-29
