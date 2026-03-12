#!/usr/bin/env python3
import sys

try:
    # Read the entire file
    with open('.kiro/specs/govt-scheme-rag/design.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_length = len(content)
    
    # Apply all updates
    updates = []
    
    # Update 1
    count = content.count('Agriculture / Healthcare / Education / Housing / Employment')
    content = content.replace(
        'Agriculture / Healthcare / Education / Housing / Employment',
        'Solar Subsidy / Housing Aid / Education Loan / Startup Support / Jal Jeevan Scheme'
    )
    updates.append(f"Category dropdown values: {count} replacements")
    
    # Update 2
    count = content.count('agriculture, healthcare, education, housing, employment')
    content = content.replace(
        'agriculture, healthcare, education, housing, employment',
        'solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme'
    )
    updates.append(f"Category API values: {count} replacements")
    
    # Update 3
    old_text = '- `POST /search` - k-NN similarity search (k=5, cosine similarity)'
    new_text = '- `POST /search` - k-NN similarity search (k=5, cosine similarity) with optional category metadata filtering'
    count = content.count(old_text)
    content = content.replace(old_text, new_text)
    updates.append(f"FAISS endpoint description: {count} replacements")
    
    # Update 4
    old_text = 'results = vector_store.search(query_embedding, top_k=5)'
    new_text = 'results = vector_store.search(query_embedding, top_k=5, category_filter=user_category)'
    count = content.count(old_text)
    content = content.replace(old_text, new_text)
    updates.append(f"Vector Store Usage: {count} replacements")
    
    # Update 5
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
        updates.append("RAGOrchestratorFunction responsibilities: 1 replacement")
    else:
        updates.append("RAGOrchestratorFunction responsibilities: already updated or not found")
    
    # Update 6
    old_text = '- **Static Frontend**: S3 + CloudFront'
    new_text = '- **Static Frontend**: Static HTML/JS (3-page flow: Language Selection → User Input Form → Results Display) hosted on S3 + CloudFront'
    count = content.count(old_text)
    content = content.replace(old_text, new_text)
    updates.append(f"Technology Stack Frontend: {count} replacements")
    
    # Write back
    with open('.kiro/specs/govt-scheme-rag/design.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_length = len(content)
    
    print("✅ Successfully updated design.md")
    print(f"\nFile size: {original_length} → {new_length} characters")
    print("\nUpdates applied:")
    for i, update in enumerate(updates, 1):
        print(f"  {i}. {update}")
    
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
