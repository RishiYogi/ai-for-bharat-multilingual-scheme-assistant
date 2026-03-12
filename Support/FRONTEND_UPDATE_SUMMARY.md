# Frontend Update Summary - Employment Field Separation

## Changes Made

### Objective
Separated "Employment Status" from "Income Range" to fix the incorrect inclusion of "Unemployed" as an income category.

### Updated Files

The following 3 files have been updated and need to be replaced in your S3 bucket:

1. **form.html**
   - Added new "Employment" dropdown field after "Gender" field
   - Moved "Employment" field before "Income Range" for logical grouping
   - Removed "Unemployed" option from Income Range dropdown
   - Updated Income Range options to: <1L, 1-3L, 3-5L, 5-10L, >10L

2. **translations.js**
   - Added `labelEmployment` translation key for all 3 languages
   - Added `employmentPlaceholder` translation key for all 3 languages
   - Added `employmentOptions` object with 4 options:
     - student (छात्र / மாணவர்)
     - unemployed (बेरोजगार / வேலையில்லாதவர்)
     - employed (नियोजित / வேலையில் உள்ளவர்)
     - self_employed (स्व-नियोजित / சுயதொழில்)
   - Removed "Unemployed" (0) from `incomeOptions` in all 3 languages

3. **app.js**
   - Added employment field handling in `applyTranslations()` function
   - Added employment dropdown population with translations
   - Updated form submission to include `employment` field in API payload
   - Changed income field name from `income` to `income_range` in API payload for consistency

### API Payload Changes

**Before:**
```json
{
  "name": "Ravi",
  "age": 32,
  "gender": "Male",
  "state": "Tamil Nadu",
  "category": "agriculture",
  "income": "0",
  "language": "en",
  "query": "Am I eligible for farmer schemes?"
}
```

**After:**
```json
{
  "name": "Ravi",
  "age": 32,
  "gender": "Male",
  "employment": "self_employed",
  "income_range": "1-3L",
  "state": "Tamil Nadu",
  "category": "agriculture",
  "language": "en",
  "query": "Am I eligible for farmer schemes?"
}
```

### Field Specifications

**Employment Field:**
- Label: "Employment" (रोजगार / வேலைவாய்ப்பு)
- Type: Dropdown (select)
- Required: No (optional)
- Options: student, unemployed, employed, self_employed
- Position: After Gender, before Income Range

**Income Range Field:**
- Label: "Income Range" (आय सीमा / வருமான வரம்பு)
- Type: Dropdown (select)
- Required: No (optional)
- Options: <1L, 1-3L, 3-5L, 5-10L, >10L
- Position: After Employment, before State

### Validation Rules
- Both Employment and Income Range are optional fields
- No validation dependency between them
- User can select one, both, or neither

### Backward Compatibility
- The `income_range` field replaces the old `income` field in the API payload
- Backend should handle both field names during transition period
- No breaking changes to existing API structure

## Deployment Instructions

### Step 1: Upload Updated Files to S3

Navigate to your frontend directory and upload the 3 updated files:

```bash
cd frontend

# Upload form.html
aws s3 cp form.html s3://aicloud-bharat-schemes/frontend/form.html --content-type "text/html"

# Upload translations.js
aws s3 cp translations.js s3://aicloud-bharat-schemes/frontend/translations.js --content-type "application/javascript"

# Upload app.js
aws s3 cp app.js s3://aicloud-bharat-schemes/frontend/app.js --content-type "application/javascript"
```

### Step 2: Invalidate CloudFront Cache (if using CloudFront)

After uploading, invalidate the CloudFront cache to ensure users get the updated files:

```bash
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/frontend/form.html" "/frontend/translations.js" "/frontend/app.js"
```

Replace `YOUR_DISTRIBUTION_ID` with your actual CloudFront distribution ID.

### Step 3: Verify Changes

1. Open your frontend URL in a browser
2. Select a language (English, Hindi, or Tamil)
3. Verify the form shows:
   - Gender dropdown
   - **Employment dropdown** (new field)
   - Income Range dropdown (without "Unemployed" option)
4. Fill out the form and submit
5. Check browser console (F12) to verify the API payload includes `employment` and `income_range` fields

## Files Location

All updated files are in the `frontend/` directory:
- `frontend/form.html`
- `frontend/translations.js`
- `frontend/app.js`

## Testing Checklist

- [ ] Employment dropdown appears after Gender field
- [ ] Employment dropdown has 4 options: Student, Unemployed, Employed, Self Employed
- [ ] Income Range dropdown does NOT have "Unemployed" option
- [ ] Income Range dropdown has 5 options: <1L, 1-3L, 3-5L, 5-10L, >10L
- [ ] Both fields are optional (can be left blank)
- [ ] Translations work correctly in Hindi and Tamil
- [ ] Form submission includes `employment` field in payload
- [ ] Form submission includes `income_range` field in payload (not `income`)

## Backend Impact

**Note:** The backend (RAG Orchestrator Lambda) may need to be updated to:
1. Accept the new `employment` field in the request payload
2. Handle both `income` and `income_range` field names during transition
3. Update filtering logic to use employment status separately from income range

This frontend update is backward compatible - the backend can continue to work with the old field names while you update it to support the new structure.
