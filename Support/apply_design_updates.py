#!/usr/bin/env python3
import re

# Read the file
with open('.kiro/specs/govt-scheme-rag/design.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Update 1: Replace old category values with new ones in dropdown descriptions
content = content.replace(
    'Agriculture / Healthcare / Education / Housing / Employment',
    'Solar Subsidy / Housing Aid / Education Loan / Startup Support / Jal Jeevan Scheme'
)

# Update 2: Update the note about category field values (both occurrences)
content = content.replace(
    'agriculture, healthcare, education, housing, employment',
    'solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme'
)

# Update 3: Add category field to request format JSON where missing
# Pattern to find request format without category
pattern1 = r'(\{[\s\n]*"name": "string",[\s\n]*"age": 25,[\s\n]*"city": "Mumbai",[\s\n]*"gender": "Male",[\s\n]*"income_range": "3-5L",[\s\n]*)"language":'
replacement1 = r'\1"category": "solar_subsidy",\n  "language":'
content = re.sub(pattern1, replacement1, content)

# Update 4: Update metadata structure to include category (if not already there)
# This pattern looks for the metadata structure and adds category if missing
if '"scheme_name": "PM-KISAN",' in content and '"category":' not in content.split('"scheme_name": "PM-KISAN",')[0].split('{')[-1]:
    pattern_meta = r'("scheme_name": "PM-KISAN",)\n(\s*"chunk_text":)'
    replacement_meta = r'\1\n    "category": "agriculture",\n\2'
    content = re.sub(pattern_meta, replacement_meta, content)

# Update 5: Add download/ folder to S3 storage if not present
if 'download/' not in content:
    content = content.replace(
        '  - `processed/` - Successfully processed PDFs',
        '  - `processed/` - Successfully processed PDFs\n  - `download/` - Generated PDF exports (Future Scope)'
    )

# Update 6: Update RAGOrchestratorFunction responsibilities
old_resp = '''**Responsibilities**:
1. Validate input (required fields, data types)
2. Generate query embedding using Bedrock Titan Embeddings
3. Call FAISS API (POST /search) for k-NN search (k=5)
4. Construct structured reasoning prompt with retrieved chunks
5. Call Bedrock Titan Text Express for LLM generation
6. Parse LLM response into structured JSON
7. Return schemes with eligibility, benefits, citations, confidence
8. Log query and response to CloudWatch'''

new_resp = '''**Responsibilities**:
1. Validate input (required fields, data types)
2. Generate query embedding using Bedrock Titan Embeddings
3. Call FAISS API (POST /search) for k-NN search (k=5)
4. Filter vector search results by category metadata
5. Include category context in LLM prompt
6. Construct structured reasoning prompt with retrieved chunks
7. Call Bedrock Titan Text Express for LLM generation
8. Parse LLM response into structured JSON
9. Return schemes with eligibility, benefits, citations, confidence
10. Log query and response to CloudWatch'''

if old_resp in content:
    content = content.replace(old_resp, new_resp)

# Update 7: Update Vector Store Usage example
old_usage = 'results = vector_store.search(query_embedding, top_k=5)'
new_usage = 'results = vector_store.search(query_embedding, top_k=5, category_filter=user_category)'
content = content.replace(old_usage, new_usage)

# Update 8: Update FAISS FastAPI Endpoints description
old_endpoint = '- `POST /search` - k-NN similarity search (k=5, cosine similarity)'
new_endpoint = '- `POST /search` - k-NN similarity search (k=5, cosine similarity) with optional category metadata filtering'
content = content.replace(old_endpoint, new_endpoint)

# Update 9: Fix CloudWatch monitoring note (remove extra blank lines)
content = re.sub(
    r'#### 7\. Observability Layer \(CloudWatch\)\n\n\n\n\*\*Note on CloudWatch Monitoring\*\*:',
    '#### 7. Observability Layer (CloudWatch)\n\n**Note on CloudWatch Monitoring**:',
    content
)

# Update 10: Update Technology Stack Frontend entry
content = content.replace(
    '- **Static Frontend**: S3 + CloudFront',
    '- **Static Frontend**: Static HTML/JS (3-page flow: Language Selection → User Input Form → Results Display) hosted on S3 + CloudFront'
)

# Write the updated content
with open('.kiro/specs/govt-scheme-rag/design.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully updated design.md")
print("\nChanges applied:")
print("1. Updated category dropdown values")
print("2. Updated category field API values")
print("3. Added category field to request formats")
print("4. Updated metadata structure")
print("5. Added download/ folder to S3")
print("6. Updated RAGOrchestratorFunction responsibilities")
print("7. Updated Vector Store Usage example")
print("8. Updated FAISS endpoints description")
print("9. Fixed CloudWatch monitoring note")
print("10. Updated Technology Stack Frontend entry")
