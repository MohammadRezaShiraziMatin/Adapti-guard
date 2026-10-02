# Preregistration Audit Status Report (2026-10-01)

## Classification: C (LOCAL PREREGISTRATION ONLY)

**Status:** Preregistration protocol drafted locally but **NOT yet externally registered**.

---

## Summary

| Item | Status | Evidence |
|------|--------|----------|
| **Local draft exists** | ✅ YES | `PREREGISTRATION_OSF_DRAFT.md` (12 sections, complete) |
| **External registration** | ❌ NO | No OSF/AsPredicted URLs found in repository |
| **Registry URL in manuscript** | ❌ TODO | Line 202: `[TODO owner: insert registry URL and timestamp]` |
| **Experiment executed** | ✅ YES | InjecAgent live run (2026-10-01) |
| **Pre-execution registration** | ❌ NO | No evidence of external registration before run |

---

## Critical Finding

**The manuscript claims the experiment "was registered before this run" (line 148) but contains a TODO placeholder for the actual registry URL (line 202).** This indicates external preregistration has not yet occurred.

---

## Evidence Details

### ✅ What EXISTS Locally

```
docs/paper/negative_result/PREREGISTRATION_OSF_DRAFT.md
├── Section 1-12 complete
├── Protocol, hypotheses, analysis plan documented
├── Ready for external submission
└── Explicitly labeled "draft for external submission"
```

Status in draft: *"Submission is an external, timestamped action that only the owner can take (account required)"*

### ❌ What DOES NOT Exist Externally

- No `osf.io` URLs in repository
- No `aspredicted.org` references found
- No registration timestamps or confirmation numbers
- No evidence of external submission before 2026-10-01

### 🔴 Manuscript Discrepancy

| Line | Text | Status |
|------|------|--------|
| 148 | "The protocol, hypotheses and analysis plan are registered before the run (registry URL to be inserted) and frozen with a SHA-256." | ❌ TODO |
| 202 | "The owner reports that the protocol was registered before this run `[TODO owner: insert registry URL and timestamp]`." | ❌ TODO |

---

## Implications

### For Submission
- **Option A (Recommended):** Register externally on OSF or AsPredicted, get URL/timestamp, insert into line 202
- **Option B (Honesty fix):** Reword manuscript to say "preregistration planned" or "will register before submission"
- **Option C (Not viable):** Submit with TODO placeholder (journals will reject)

### For Registered Report
- If targeting a **Registered Report** venue: external preregistration MUST occur first
- If submitting to **regular venue with preregistration disclosure**: external registration must occur before submission

---

## Next Steps (IMMEDIATE)

1. **Decide:** Will study be externally preregistered?
   - YES → Proceed to step 2
   - NO → Reword manuscript honesty statement

2. **If YES:**
   - Go to osf.io or aspredicted.org
   - Create account (if needed)
   - Copy content from `PREREGISTRATION_OSF_DRAFT.md`
   - Submit as new registration
   - Record timestamp and URL

3. **Insert into manuscript:**
   - Line 202: Replace TODO with actual URL and timestamp
   - Line 148: Update phrasing if needed to match venue requirements

4. **Venue customization:**
   - Confirm target journal/venue (for Amendment 10 disclosure requirements)
   - Customize disclosure statements per venue policy (line 270)

---

## Related TODOs Still Pending

From `FINAL_AUDIT_20261001.md`:

| TODO | Location | Blocking |
|------|----------|----------|
| OSF registry URL | Section 6.6, line 202 | ✅ CRITICAL |
| Cui et al. paper | References (line 328) | ✅ CRITICAL |
| Amendment 10 approval | Section 10 (lines 270, 299, 300) | ⚠️ Important |
| Venue selection | General | ⚠️ Important |

---

**Classification assigned:** 2026-10-01  
**Last updated:** 2026-10-01

---

*This audit confirms: external preregistration is a separate action from local draft preparation. The draft is ready; the external action is pending owner decision and execution.*
