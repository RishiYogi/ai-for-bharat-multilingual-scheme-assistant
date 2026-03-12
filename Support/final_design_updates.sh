#!/bin/bash

# Backup the original file
cp .kiro/specs/govt-scheme-rag/design.md .kiro/specs/govt-scheme-rag/design.md.backup

# Update 1: Replace old category values with new ones
sed -i 's/Agriculture \/ Healthcare \/ Education \/ Housing \/ Employment/Solar Subsidy \/ Housing Aid \/ Education Loan \/ Startup Support \/ Jal Jeevan Scheme/g' .kiro/specs/govt-scheme-rag/design.md

# Update 2: Update category API values in the note
sed -i 's/agriculture, healthcare, education, housing, employment/solar_subsidy, housing_aid, education_loan, startup_support, jal_jeevan_scheme/g' .kiro/specs/govt-scheme-rag/design.md

# Update 3: Update FAISS endpoint description
sed -i 's/- `POST \/search` - k-NN similarity search (k=5, cosine similarity)/- `POST \/search` - k-NN similarity search (k=5, cosine similarity) with optional category metadata filtering/g' .kiro/specs/govt-scheme-rag/design.md

# Update 4: Update Vector Store Usage
sed -i 's/results = vector_store\.search(query_embedding, top_k=5)/results = vector_store.search(query_embedding, top_k=5, category_filter=user_category)/g' .kiro/specs/govt-scheme-rag/design.md

# Update 5: Update Technology Stack Frontend entry
sed -i 's/- \*\*Static Frontend\*\*: S3 + CloudFront/- **Static Frontend**: Static HTML\/JS (3-page flow: Language Selection → User Input Form → Results Display) hosted on S3 + CloudFront/g' .kiro/specs/govt-scheme-rag/design.md

echo "✅ Design.md updated successfully!"
echo "Backup saved to design.md.backup"
