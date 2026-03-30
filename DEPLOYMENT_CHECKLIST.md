# Masking Mode Feature - Post-Implementation Checklist

## ✅ Code Implementation Status

### Backend Code Changes
- [x] **app/models.py** - Added `masking_mode` column to User model
  - Location: `User.masking_mode = sa.Column(sa.String(20), default="mask")`
  
- [x] **app/security.py** - Added 4 masking methods
  - Completed functions:
    - `shuffle_text(text, seed)` - Deterministic shuffle
    - `add_noise(text, seed)` - Noise injection (40% probability)
    - `fake_email(seed)` - Fake email generator
    - `fake_phone(seed)` - Fake phone generator
  - Extended: `apply_masking(user_data, mask, mode)` with mode routing

- [x] **app/schemas.py** - Added MaskingModeRequest
  - Schema: `MaskingModeRequest(masking_mode: str)`

- [x] **app/routers/user.py** - Added PATCH endpoint & updated GET endpoints
  - New: `PATCH /users/{user_id}/masking-mode` (admin only)
  - Updated: `GET /users` with `mask_mode` query param
  - Updated: `GET /users/{user_id}` with `mask_mode` query param
  - Helper: `_user_response_with_masking(user, mask_mode)`

### Database Migration
- [x] **migrations/add_masking_mode.sql** - Created migration SQL
  - Command: `ALTER TABLE users ADD COLUMN masking_mode VARCHAR(20) DEFAULT 'mask'`
  - Index: Created `idx_masking_mode` for performance

---

## 📋 Pre-Deployment Steps

### 1. Database Migration
- [ ] Connect to production MySQL database
- [ ] Run migration SQL:
  ```bash
  mysql -u root -p<password> csat_bmpt < migrations/add_masking_mode.sql
  ```
- [ ] Verify column exists:
  ```sql
  DESCRIBE users;  -- Check for 'masking_mode' column
  SHOW INDEX FROM users;  -- Check for 'idx_masking_mode'
  ```

### 2. Environment Variables
- [ ] Ensure `MASTER_KEY_SEED` is set in production
  - Default: `csat_bmpt_master_key_2026`
  - Should be changed in production for security

### 3. Code Deployment
- [ ] Deploy updated files:
  - [ ] app/models.py
  - [ ] app/security.py
  - [ ] app/schemas.py
  - [ ] app/routers/user.py

### 4. Server Restart
- [ ] Stop FastAPI server
- [ ] Pull latest code
- [ ] Run migration SQL
- [ ] Restart FastAPI server
- [ ] Verify health check: `curl http://localhost:8000/health`

---

## 🧪 Post-Deployment Validation

### 1. Database Check
```bash
# Connect to MySQL
mysql -u root -p<password> csat_bmpt

# Verify column
DESC users;
SELECT user_id, masking_mode FROM users LIMIT 5;
```

### 2. API Endpoint Tests
```bash
# Admin login
curl -X POST http://localhost:8000/auth/login \
  -d '{"username":"admin","password":"admin123"}'
ADMIN_TOKEN=$(previous_response.access_token)

# Set masking mode
curl -X PATCH http://localhost:8000/users/3/masking-mode \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -d '{"masking_mode":"shuffle"}'

# Regular user login
curl -X POST http://localhost:8000/auth/login \
  -d '{"username":"User","password":"User@123"}'
USER_TOKEN=$(previous_response.access_token)

# User views with masking
curl -X GET http://localhost:8000/users/3 \
  -H "Authorization: Bearer $USER_TOKEN"
# Expected: Email/phone displayed with shuffle mode
```

### 3. Run Test Suite
```bash
# Make sure server is running
python test_masking_modes.py
```

### 4. Manual Verification Checklist
- [ ] Admin can set masking mode via PATCH endpoint
- [ ] User sees email masked (not decrypted)
- [ ] User sees phone masked (not decrypted)
- [ ] All 4 modes work: mask, shuffle, fake, noise
- [ ] Query param override works
- [ ] Admin always sees decrypted data
- [ ] Invalid mode values are rejected
- [ ] Non-admin users cannot call PATCH endpoint

---

## 📊 Mode Behavior Verification

### Test Each Mode

#### 1. Test mode='mask'
```bash
PATCH /users/3/masking-mode with {"masking_mode":"mask"}
GET /users/3 → email: "j***@gmail.com"  (first + last visible, middle masked)
```

#### 2. Test mode='shuffle'
```bash
PATCH /users/3/masking-mode with {"masking_mode":"shuffle"}
GET /users/3 → email: "mliaoag@m.c"  (characters shuffled)
```

#### 3. Test mode='fake'
```bash
PATCH /users/3/masking-mode with {"masking_mode":"fake"}
GET /users/3 → email: "user5234@example.com"  (fake data)
```

#### 4. Test mode='noise'
```bash
PATCH /users/3/masking-mode with {"masking_mode":"noise"}
GET /users/3 → email: "j#o@h!n*@#$g%m^a&i*l(.c)o%m"  (noisy)
```

---

## 🔍 Troubleshooting

### Issue: Migration Fails to Run
**Symptoms:** "1054: Unknown column 'masking_mode'"
**Solution:**
1. Check if migration was already run: `DESC users;`
2. If column exists, skip migration
3. If not, run migration manually with proper user/password

### Issue: Admin Cannot Set Masking Mode
**Symptoms:** PATCH endpoint returns 403 Forbidden
**Solution:**
1. Verify user has admin role: `SELECT role FROM users WHERE username='admin'`
2. Verify token is valid: Check Authorization header
3. Check user.py imports: Ensure `get_current_admin` is imported

### Issue: User Still Sees Decrypted Data
**Symptoms:** User can read email/phone in plain text
**Solution:**
1. Check encryption is working: Verify encrypted values in DB (should be unreadable)
2. Verify masking_mode is set: `SELECT masking_mode FROM users WHERE id=3`
3. Check _user_response_with_masking function is being called
4. Review apply_masking function logic

### Issue: Same Input Produces Different Masked Output
**Symptoms:** Running same masking mode twice gives different results
**Solution:**
1. Check if mode is 'shuffle' or 'noise' (should be deterministic with seed)
2. Verify seeding mechanism in shuffle_text/add_noise uses data as seed
3. Traces: Log mask operations to debug

### Issue: Query Param Override Not Working
**Symptoms:** `?mask_mode=fake` doesn't change output to fake mode
**Solution:**
1. Check query param is passed correctly
2. Verify GET endpoint processes mask_mode param
3. Verify _user_response_with_masking accepts override
4. Check if user has permission (non-admin cannot override others' data)

---

## 📈 Performance Considerations

### Database Index
- [ ] `idx_masking_mode` was created for query performance
- [ ] Verify index is present: `SHOW INDEX FROM users;`

### Encryption Performance
- [ ] AES-128 ECB is relatively fast (custom implementation)
- [ ] Masking operations are O(n) where n = data length
- [ ] Consider caching decrypted values for batch operations

### API Response Time
- [ ] Test PATCH endpoint response time (should be < 200ms)
- [ ] Test GET endpoint response time (should be < 500ms for bulk list)

---

## 🔐 Security Verification

### Encryption Keys
- [ ] Verify MASTER_KEY_SEED is set and different from default
- [ ] Verify per-user keys are generated correctly
- [ ] Confirm emails/phones are encrypted, not plaintext in DB

### Access Control
- [ ] Verify only admin can call PATCH endpoint
- [ ] Confirm user cannot change own masking_mode
- [ ] Check JWT tokens are validated correctly

### Data Privacy
- [ ] Regular user cannot decrypt email/phone
- [ ] User sees masked data, not plaintext
- [ ] Admin always sees decrypted data

---

## 📚 Documentation Files Created

- [x] **MASKING_MODE_GUIDE.md** - User-facing guide with examples
- [x] **MASKING_MODE_IMPLEMENTATION.md** - Technical implementation details
- [x] **test_masking_modes.py** - Automated test script
- [x] **README.md** - Updated with masking mode info
- [x] **migrations/add_masking_mode.sql** - Database migration

---

## 🎯 Final Deployment Sign-Off

### Pre-Deployment Checklist
- [ ] All code changes reviewed and tested
- [ ] Database migration script verified
- [ ] Test script runs successfully
- [ ] Documentation complete and clear
- [ ] Admin UI prepared (if applicable)

### Deployment Checklist
- [ ] Code deployed to production
- [ ] Database migration executed
- [ ] Server restarted and healthy
- [ ] Health check passes
- [ ] All API endpoints responding

### Post-Deployment Checklist
- [ ] Test suite passes on production
- [ ] Admin can set masking mode
- [ ] Users see masked data
- [ ] All 4 modes work correctly
- [ ] Performance acceptable
- [ ] No errors in logs

### Rollback Plan (If Needed)
```sql
-- Undo migration if necessary
ALTER TABLE users DROP COLUMN masking_mode;
DROP INDEX idx_masking_mode ON users;

-- Revert code to previous version
-- Restart FastAPI server
```

---

## 📞 Support & Escalation

### Known Limitations
1. Masking is applied at data retrieval time (stateless, not cached)
2. Per-user masking mode means all users see same masked pattern for same original data
3. Query param override only works for users viewing own data (permission check)

### Future Enhancements
- [ ] Batch API to set masking mode for multiple users
- [ ] Bulk export of users with masking mode
- [ ] Audit log of masking mode changes
- [ ] Admin dashboard showing all users' masking modes
- [ ] Caching layer for decrypted values

---

**Last Updated:** 2026-03-29  
**Status:** Ready for Deployment  
**Reviewed By:** [Your Name]  
**Approval:** [ ] Ready to Deploy
