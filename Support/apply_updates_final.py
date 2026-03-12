#!/usr/bin/env python3
"""Apply all requested updates to design.md"""

# Read the file
with open('.kiro/specs/govt-scheme-rag/design.md', 'r', encoding='utf-8') as f:
    content = f.read()

print("Original file size:", len(content), "characters")

# Update 1: Replace old category dropdown values with new ones
old_count = content.count('Agriculture / Healthcare / Education / Housing / Employment')
content = content.replace(
    'Agriculture / Healthcare / Education / Housing / Employment',
    'Solar Subsidy / Housing Aid / Education Loan / Startup Support / Jal Jeevan Scheme'
)
print(f"✅ Update 1: Replaced {old_count} occurrences of category dropdown values")

# Update 2: Update category API values in notes
old_count = content.count('agriculture, healthcare, education, housing, employment')
content = content.replace(
    'agriculture, healthcare, education, housing, employment',
    'solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme'
)
print(f"✅ Update 2: Replaced {old_count} occurrences of category API values")

# Update 3: Update FAISS endpoint description
old_endpoint = '- `POST /search` - k-NN similarity search (k=5, cosine similarity)'
new_endpoint = '- `POST /search` - k-NN similarity search (k=5, cosine similarity) with optional category metadata filtering'
old_count = content.count(old_endpoint)
content = content.replace(old_endpoint, new_endpoint)
print(f"✅ Update 3: Updated {old_count} FAISS endpoint descriptions")

# Update 4: Update Vector Store Usage
old_usage = 'results = vector_store.search(query_embedding, top_k=5)'
new_usage = 'results = vector_store.search(query_embedding, top_k=5, category_filter=user_category)'
old_count = content.count(old_usage)
content = content.replace(old_usage, new_usage)
print(f"✅ Update 4: Updated {old_count} Vector Store Usage examples")

# Update 5: Update RAGOrchestratorFunction responsibilities (if old version exists)
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
    print("✅ Update 5: Updated RAGOrchestratorFunction responsibilities")
else:
    print("⚠️  Update 5: RAGOrchestratorFunction responsibilities already updated or not found")

# Update 6: Update Technology Stack Frontend entry
old_frontend = '- **Static Frontend**: S3 + CloudFront'
new_frontend = '- **Static Frontend**: Static HTML/JS (3-page flow: Language Selection → User Input Form → Results Display) hosted on S3 + CloudFront'
old_count = content.count(old_frontend)
content = content.replace(old_frontend, new_frontend)
print(f"✅ Update 6: Updated {old_count} Technology Stack Frontend entries")

# Write the updated content
with open('.kiro/specs/govt-scheme-rag/design.md', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ All updates applied successfully!")
print("Updated file size:", len(content), "characters")
