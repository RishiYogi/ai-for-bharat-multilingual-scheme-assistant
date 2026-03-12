#!/usr/bin/env python3
"""Comprehensive update script for design.md"""

# Read entire file
with open('.kiro/specs/govt-scheme-rag/design.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track changes
changes_made = []

# Process line by line
for i in range(len(lines)):
    # Update 1: Category dropdown values
    if 'Agriculture / Healthcare / Education / Housing / Employment' in lines[i]:
        lines[i] = lines[i].replace(
            'Agriculture / Healthcare / Education / Housing / Employment',
            'Solar Subsidy / Housing Aid / Education Loan / Startup Support / Jal Jeevan Scheme'
        )
        changes_made.append(f"Line {i+1}: Updated category dropdown values")
    
    # Update 2: Category API values
    if 'agriculture, healthcare, education, housing, employment' in lines[i]:
        lines[i] = lines[i].replace(
            'agriculture, healthcare, education, housing, employment',
            'solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme'
        )
        changes_made.append(f"Line {i+1}: Updated category API values")
    
    # Update 3: FAISS endpoint description
    if '- `POST /search` - k-NN similarity search (k=5, cosine similarity)' in lines[i] and 'optional category' not in lines[i]:
        lines[i] = lines[i].replace(
            '- `POST /search` - k-NN similarity search (k=5, cosine similarity)',
            '- `POST /search` - k-NN similarity search (k=5, cosine similarity) with optional category metadata filtering'
        )
        changes_made.append(f"Line {i+1}: Updated FAISS endpoint description")
    
    # Update 4: Vector Store Usage
    if 'results = vector_store.search(query_embedding, top_k=5)' in lines[i] and 'category_filter' not in lines[i]:
        lines[i] = lines[i].replace(
            'results = vector_store.search(query_embedding, top_k=5)',
            'results = vector_store.search(query_embedding, top_k=5, category_filter=user_category)'
        )
        changes_made.append(f"Line {i+1}: Updated Vector Store Usage")
    
    # Update 5: Technology Stack Frontend
    if '- **Static Frontend**: S3 + CloudFront' in lines[i]:
        lines[i] = lines[i].replace(
            '- **Static Frontend**: S3 + CloudFront',
            '- **Static Frontend**: Static HTML/JS (3-page flow: Language Selection → User Input Form → Results Display) hosted on S3 + CloudFront'
        )
        changes_made.append(f"Line {i+1}: Updated Technology Stack Frontend")

# Write back
with open('.kiro/specs/govt-scheme-rag/design.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"✅ Successfully updated design.md")
print(f"\nTotal changes made: {len(changes_made)}")
for change in changes_made[:10]:  # Show first 10 changes
    print(f"  - {change}")
if len(changes_made) > 10:
    print(f"  ... and {len(changes_made) - 10} more changes")
