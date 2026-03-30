# Masking Mode Feature - Quick Start Guide

## 30-Second Overview

**What:** Admin-controlled data masking modes for user email/phone  
**How It Works:** Admin sets mode via PATCH → User views masked data via GET  
**Status:** ✅ Complete & Ready to Deploy  

---

## Quick Setup (5 minutes)

### Step 1: Run Database Migration
```bash
# Windows
mysql -u root -p123456 csat_bmpt < migrations/add_masking_mode.sql

# Mac/Linux
mysql -u root -p csat_bmpt < migrations/add_masking_mode.sql
```

### Step 2: Restart FastAPI Server
```bash
# In your existing server terminal: Ctrl+C
# Then restart:
python main.py
```

### Step 3: Verify It Works
```bash
# Test migration succeeded
mysql -u root -p123456 -e "DESC user_db.users" | grep masking_mode
# Expected output: masking_mode | varchar(20) | ...
```

**Done!** Feature is now active.

---

## API Quick Reference

### Admin Sets Masking Mode
```bash
PATCH /users/{user_id}/masking-mode
Authorization: Bearer <admin_token>
Body: { "masking_mode": "shuffle" }
```

**Valid modes:** `mask` | `shuffle` | `fake` | `noise`

### User Views Data (Auto-Masked)
```bash
GET /users/{user_id}
Authorization: Bearer <user_token>
# Response includes email/phone masked per masking_mode
```

### Override Mode (Test)
```bash
GET /users/{user_id}?mask_mode=fake
# Temporarily use 'fake' mode instead of stored mode
```

---

## Test It (1 minute)

```bash
python test_masking_modes.py
```

This script will:
- ✅ Login as admin & user
- ✅ Admin sets masking mode
- ✅ User views masked data
- ✅ Test all 4 modes
- ✅ Verify admin sees decrypted data

---

## Mode Examples

| Mode | Input | Output | Use Case |
|------|-------|--------|----------|
| **mask** | john@gmail.com | j***@gmail.com | Keep identifiable pattern |
| **shuffle** | john@gmail.com | mliaoag@m.c | Unrecognizable shuffle |
| **fake** | john@gmail.com | user5234@example.com | Realistic fake data |
| **noise** | john@gmail.com | j#o@h!n*@#$g%m^a&i*l(.c)o%m | Maximum obfuscation |

---

## Workflow Example

### Scenario: Admin wants to shuffle user data

```bash
# 1. Admin login
curl -X POST http://localhost:8000/auth/login \
  -d '{"username":"admin","password":"admin123"}'
# Get access_token from response

# 2. Admin sets mode to 'shuffle' for user 3
curl -X PATCH http://localhost:8000/users/3/masking-mode \
  -H "Authorization: Bearer <token>" \
  -d '{"masking_mode":"shuffle"}'
# Response: User 3's masking_mode = "shuffle"

# 3. User 3 logs in and views own profile
curl -X POST http://localhost:8000/auth/login \
  -d '{"username":"User","password":"User@123"}'
# Get access_token

# 4. User 3 views profile
curl -X GET http://localhost:8000/users/3 \
  -H "Authorization: Bearer <token>"
# Response: email = "mliaoag@m.c" (shuffled, per admin's choice)
```

---

## File Locations

| File | Purpose |
|------|---------|
| [app/models.py](app/models.py) | User.masking_mode column |
| [app/security.py](app/security.py) | Masking functions |
| [app/schemas.py](app/schemas.py) | MaskingModeRequest schema |
| [app/routers/user.py](app/routers/user.py) | PATCH endpoint |
| [migrations/add_masking_mode.sql](migrations/add_masking_mode.sql) | DB migration |
| [test_masking_modes.py](test_masking_modes.py) | Test script |
| [MASKING_MODE_GUIDE.md](MASKING_MODE_GUIDE.md) | Full documentation |

---

## Key Restrictions

- ✅ **Admin only:** Can set masking mode via PATCH
- ✅ **User cannot escape:** Cannot change own masking mode
- ✅ **Admin always sees full:** Admin views always show decrypted data
- ✅ **Deterministic:** Same input = same masked output (reproducible)

---

## FAQ

**Q: How do I change masking mode for a user?**  
A: `PATCH /users/{id}/masking-mode` with `{"masking_mode": "fake"}`

**Q: Can user see real email if masking_mode is not set?**  
A: No, defaults to "mask" mode (first/last visible, middle masked)

**Q: Does query param override mode change stored mode?**  
A: No, stored mode unchanged. Override is temporary (just for that request)

**Q: What if encryption fails?**  
A: Fallback to masked pattern "***@***" (user cannot decrypt)

**Q: Is it backward compatible?**  
A: Yes, all existing users default to "mask" mode

---

## Troubleshooting

### "Unknown column 'masking_mode'"
→ Run migration: `mysql -u root -p123456 csat_bmpt < migrations/add_masking_mode.sql`

### "403 Forbidden on PATCH endpoint"
→ Use admin token, not user token

### "User still sees real email"
→ Check encryption is working (should be encrypted in DB, then masked)

### "Different output each time for 'shuffle'"
→ This shouldn't happen (uses seed). Check apply_masking function.

---

## Next Steps

### To Use This Feature
1. ✅ Run migration SQL
2. ✅ Restart server
3. ✅ Add UI to admin panel to set masking mode per user
4. ✅ Test with test_masking_modes.py

### To Extend This Feature
- [ ] Bulk set mode for multiple users
- [ ] Admin dashboard showing all users' modes
- [ ] Audit log of mode changes
- [ ] Preset mode templates (e.g., "strict privacy", "relaxed")

---

## Status

✅ **Implementation:** Complete  
✅ **Database Migration:** Ready  
✅ **Testing:** Test script included  
✅ **Documentation:** Comprehensive guides  
🔄 **Deployment:** Run migration, restart server  

---

## Files to Review

1. **Code changes:** See file diff for app/models.py, app/security.py, app/routers/user.py
2. **Full detail:** Read [MASKING_MODE_IMPLEMENTATION.md](MASKING_MODE_IMPLEMENTATION.md)
3. **Admin guide:** See [MASKING_MODE_GUIDE.md](MASKING_MODE_GUIDE.md)
4. **Deployment:** Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

**Created:** 2026-03-29  
**Feature Status:** Ready for Production  
**Estimated Time to Deploy:** 15 minutes
