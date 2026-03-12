# Language Handling Corrections Applied ✅

## Summary

Both requested corrections have been applied to the spec documents.

---

## Correction 1: LLM Prompt Language Instruction ✅

**Issue**: Prompt was designed to send ISO code directly to LLM ("Respond in hi")

**Solution**: Convert ISO code to full language name before constructing prompt

**Implementation**:

```python
# Convert ISO-639-1 code to full language name for LLM prompt
language_map = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil"
}
response_language = language_map.get(language, "English")

prompt = f"""
System: You are a helpful assistant explaining government schemes to rural Indian citizens.
Respond in {response_language}. Use simple vocabulary suitable for users with basic literacy.
...
"""
```

**Example Flow**:
- User request contains: `language: "hi"`
- Backend converts: `response_language = "Hindi"`
- Prompt instruction: `"Respond in Hindi."`

**Files Updated**:
- `design.md` - Prompt template section (added language_map conversion)
- `requirements.md` - Example prompt structure (added conversion note)

---

## Correction 2: Frontend Safety Fallback ✅

**Issue**: Code could send undefined value if selectedLanguage is missing

**Solution**: Add fallback to "en"

**Implementation**:

```javascript
const formData = {
    name: document.getElementById('name').value,
    age: parseInt(document.getElementById('age').value),
    gender: document.getElementById('gender').value,
    state: document.getElementById('state').value,
    category: document.getElementById('category').value,
    income: document.getElementById('income').value,
    language: languageCodes[selectedLanguage] || 'en',  // ← Fallback added
    query: document.getElementById('query').value
};
```

**Behavior**:
- If `selectedLanguage` is valid: Sends mapped ISO code ("en", "hi", "ta")
- If `selectedLanguage` is undefined/unrecognized: Defaults to "en"
- System never sends undefined or invalid language values

**Files Updated**:
- `tasks.md` - TASK 8 (app.js code)

---

## Complete Corrected Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Frontend (index.html)                                       │
│   User selects: "Hindi"                                     │
│   Stored in localStorage: "Hindi"                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend (app.js)                                           │
│   languageCodes["Hindi"] → "hi"                             │
│   Fallback: || 'en'                                         │
│   Sends to API: {"language": "hi", ...}                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ API Gateway (STAGE 5 - NOT IMPLEMENTED)                     │
│   Receives: {"language": "hi"}                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ RAG Orchestrator Lambda (STAGE 5 - NOT IMPLEMENTED)         │
│   Extracts: language = "hi"                                 │
│   Converts: response_language = language_map["hi"]          │
│   Result: response_language = "Hindi"                       │
│   Constructs prompt: "Respond in Hindi."                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Bedrock Nova 2 Lite                                         │
│   Receives prompt: "Respond in Hindi."                      │
│   Generates response in Hindi                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend (results.html)                                     │
│   Displays Hindi response                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Updated Code Snippets

### Frontend (tasks.md - TASK 8)

**app.js - Language code mapping**:
```javascript
// Language code mapping (ISO-639-1)
const languageCodes = {
    'English': 'en',
    'Hindi': 'hi',
    'Tamil': 'ta'
};
```

**app.js - Form submission with fallback**:
```javascript
function setupFormSubmission() {
    const form = document.getElementById('scheme-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            gender: document.getElementById('gender').value,
            state: document.getElementById('state').value,
            category: document.getElementById('category').value,
            income: document.getElementById('income').value,
            language: languageCodes[selectedLanguage] || 'en',  // ← Fallback to 'en'
            query: document.getElementById('query').value
        };
        
        localStorage.setItem('formData', JSON.stringify(formData));
        window.location.href = 'results.html';
    });
}
```

---

### Backend (design.md - STAGE 5 specification)

**RAG Orchestrator Lambda - Language conversion**:
```python
# Convert ISO-639-1 code to full language name for LLM prompt
language_map = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil"
}
response_language = language_map.get(language, "English")

prompt = f"""
System: You are a helpful assistant explaining government schemes to rural Indian citizens.
Respond in {response_language}. Use simple vocabulary suitable for users with basic literacy.

User Profile:
- Age: {age}
- Gender: {gender}
- State: {state}
- Income Range: {income_range}
- Category: {category}

Context: [Top 5 retrieved chunks from ChromaDB]

User Query: {query}

Instructions:
1. List relevant schemes with names and brief descriptions
2. Explain eligibility criteria considering the user's profile
3. Explain WHY the user may qualify based on their age, state, income, category
4. Describe key benefits in clear language
5. Provide application steps with official links
6. Cite source documents
7. Provide confidence score (High/Medium/Low)

Respond in {response_language}.
"""
```

---

## Files Modified

1. **tasks.md** (TASK 8 - app.js):
   - ✅ Added fallback: `|| 'en'`
   - ✅ Updated note to explain ISO code → full name conversion

2. **design.md** (Prompt template section):
   - ✅ Added `language_map` conversion logic
   - ✅ Changed prompt to use full language name
   - ✅ Updated system prompt description

3. **requirements.md** (Example prompt structure):
   - ✅ Added note about ISO code to full name conversion
   - ✅ Updated example to show "Respond in English"

---

## Verification Checklist

When STAGE 5 is implemented, verify:

- [ ] Frontend sends ISO code: "en", "hi", or "ta"
- [ ] Frontend never sends undefined (fallback to "en" works)
- [ ] Lambda receives ISO code from API Gateway
- [ ] Lambda converts ISO code to full language name
- [ ] LLM prompt includes: `Respond in English.` (or Hindi/Tamil)
- [ ] Bedrock Nova 2 Lite receives prompt with full language name
- [ ] Response is generated in correct language
- [ ] Test all 3 languages end-to-end

---

## Language Format Summary

| Location | Format | Example | Purpose |
|----------|--------|---------|---------|
| Frontend UI | Full names | "English", "Hindi", "Tamil" | User-friendly display |
| Frontend → API | ISO codes | "en", "hi", "ta" | Standardized transport |
| Ingestion metadata | ISO codes | "en", "hi", "ta" | Database storage |
| ChromaDB metadata | ISO codes | "en", "hi", "ta" | Filtering & retrieval |
| RAG Orchestrator | ISO codes | "en", "hi", "ta" | Internal processing |
| LLM Prompt | Full names | "English", "Hindi", "Tamil" | Natural language instruction |

---

## Key Design Decisions

1. **ISO codes for transport & storage**: Consistent, compact, international standard
2. **Full names for LLM prompts**: Better LLM comprehension and response quality
3. **Fallback to "en"**: Ensures system never breaks due to missing language
4. **Conversion at RAG layer**: Single point of conversion, clean separation of concerns

---

## Next Steps

1. Complete STAGE 4 (Ingestion Pipeline) - TASK 18-22
2. Populate STAGE 5 (RAG Orchestrator) with language conversion logic
3. Implement Lambda function following corrected design
4. Test end-to-end with all 3 languages

The language handling is now **CORRECTLY DESIGNED** with proper format conversions at each layer.
