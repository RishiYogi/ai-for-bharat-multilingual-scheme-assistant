#!/usr/bin/env python3
"""
Script to update the design.md file with architectural changes
"""

import re

def update_design_document():
    # Read the file
    with open('.kiro/specs/govt-scheme-rag/design.md', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update 1: Frontend Layer - Replace all occurrences
    old_frontend = r'''#### 2\. Frontend Layer \(Static HTML/JS\)

\*\*Single Page Application\*\*:
- \*\*Technology\*\*: Static HTML \+ Vanilla JavaScript
- \*\*Hosting\*\*: Amazon S3 \+ CloudFront distribution
- \*\*File Structure\*\*: 
  - `index\.html` - Single page with form
  - `app\.js` - JavaScript with fetch\(\) API calls
  - `styles\.css` - Minimal styling

\*\*User Input Form\*\*:
- \*\*Name\*\* \(text input, required\)
- \*\*Age\*\* \(number input, required, min=1, max=120\)
- \*\*City\*\* \(text input, required\)
- \*\*Gender\*\* \(dropdown, optional\): Male / Female / Other / Prefer not to say
- \*\*Income Range\*\* \(dropdown, optional\): <1L / 1-3L / 3-5L / 5-10L / >10L
- \*\*Language\*\* \(dropdown, required\): (?:Hindi, English, Tamil|English, Hindi, Tamil|Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi)
- \*\*Query\*\* \(textarea, required\): Free-text query about schemes
- \*\*Submit Button\*\*: Triggers POST /query to API Gateway
- \*\*Reset Button\*\*: Clears form

\*\*Data Privacy\*\*:
- NO collection of: Aadhaar, Bank details, DOB, Sensitive IDs
- All data sent via HTTPS
- No client-side storage of sensitive information

\*\*Response Display\*\*:
- Scheme cards with name, eligibility, benefits, application steps
- Source citations with document links
- Confidence scores \(High/Medium/Low\)
- Error messages for failed requests'''
    
    new_frontend = '''#### 2. Frontend Layer (Static HTML/JS)

**Three-Page Application Architecture**:
- **Technology**: Static HTML + Vanilla JavaScript
- **Hosting**: Amazon S3 + CloudFront distribution
- **File Structure**: 
  - `index.html` - Language selection page (Page 1)
  - `form.html` - User input form (Page 2)
  - `results.html` - Results display (Page 3)
  - `app.js` - JavaScript with fetch() API calls
  - `translations.js` - Multilingual UI translations
  - `styles.css` - Minimal styling

**Page 1: Language Selection (index.html)**:
- Display 10 language tiles in a grid layout
- Languages: Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, Punjabi
- Each tile is clickable and navigates to form.html with selected language
- Language selection stored in session storage
- All UI text on this page in English (default) with language names in native script

**Page 2: User Input Form (form.html)**:
- **Name** (text input, required)
- **Age** (number input, required, min=1, max=120)
- **City** (text input, required)
- **Gender** (dropdown, optional): Male / Female / Other / Prefer not to say
- **Income Range** (dropdown, optional): <1L / 1-3L / 3-5L / 5-10L / >10L
- **Category** (dropdown, required): Agriculture / Healthcare / Education / Housing / Employment
- **Query** (textarea, required): Free-text query about schemes
- **Submit Button**: Triggers POST /query to API Gateway, navigates to results.html
- **Reset Button**: Clears form
- **All UI elements** (labels, buttons, placeholders, error messages) displayed in selected language

**Page 3: Results Display (results.html)**:
- Scheme cards with name, eligibility, benefits, application steps
- Source citations with document links
- Confidence scores (High/Medium/Low)
- **PDF Download Button**: Generates and downloads PDF of results (Future Scope)
- **Back Button**: Returns to form.html for new search
- **All UI elements** displayed in selected language
- Error messages for failed requests in selected language

**Multilingual UI Support**:
- All labels, buttons, error messages, placeholders translated to selected language
- Translation files: `translations.js` with key-value pairs for each language
- Dynamic text replacement based on language selection
- Not just responses, but entire UI in user's preferred language

**Data Privacy**:
- NO collection of: Aadhaar, Bank details, DOB, Sensitive IDs
- All data sent via HTTPS
- No client-side storage of sensitive information'''
    
    # Replace all occurrences
    content = re.sub(old_frontend, new_frontend, content, flags=re.MULTILINE | re.DOTALL)
    
    # Update 2: Request Format - add category field
    old_request = r'''\*\*Request Format\*\*:
```json
\{
  "name": "string",
  "age": 25,
  "city": "Mumbai",
  "gender": "Male",
  "income_range": "3-5L",
  "language": "Hindi",
  "query": "मुझे कृषि योजनाओं के बारे में बताएं"
\}
```'''
    
    new_request = '''**Request Format**:
```json
{
  "name": "string",
  "age": 25,
  "city": "Mumbai",
  "gender": "Male",
  "income_range": "3-5L",
  "category": "agriculture",
  "language": "Hindi",
  "query": "मुझे कृषि योजनाओं के बारे में बताएं"
}
```

**Note**: The `category` field is required and must be one of: agriculture, healthcare, education, housing, employment'''
    
    content = re.sub(old_request, new_request, content, flags=re.MULTILINE | re.DOTALL)
    
    # Update 3: Add category to FAISS metadata structure
    old_metadata = r'''\*\*Metadata Structure\*\*:
```json
\{
  "doc_id_0": \{
    "scheme_id": "pm-kisan-2024",
    "scheme_name": "PM-KISAN",
    "chunk_text": "\.\.\.",
    "chunk_index": 0,
    "department": "Agriculture",
    "state": "All India",
    "city": "All",
    "source_url": "https://pmkisan\.gov\.in/\.\.\.",
    "last_updated": "2024-03-15"
  \}
\}
```'''
    
    new_metadata = '''**Metadata Structure**:
```json
{
  "doc_id_0": {
    "scheme_id": "pm-kisan-2024",
    "scheme_name": "PM-KISAN",
    "category": "agriculture",
    "chunk_text": "...",
    "chunk_index": 0,
    "department": "Agriculture",
    "state": "All India",
    "city": "All",
    "source_url": "https://pmkisan.gov.in/...",
    "last_updated": "2024-03-15"
  }
}
```'''
    
    content = re.sub(old_metadata, new_metadata, content, flags=re.MULTILINE | re.DOTALL)
    
    # Update 4: Update S3 Storage section to add download/ folder
    old_s3 = r'''\*\*S3 Storage\*\*:
- \*\*Bucket\*\*: aicloud-bharat-schemes
- \*\*Region\*\*: ap-south-1
- \*\*Folders\*\*: 
  - `raw/` - Uploaded PDFs \(triggers Lambda\)
  - `processed/` - Successfully processed PDFs'''
    
    new_s3 = '''**S3 Storage**:
- **Bucket**: aicloud-bharat-schemes
- **Region**: ap-south-1
- **Folders**: 
  - `raw/` - Uploaded PDFs (triggers Lambda)
  - `processed/` - Successfully processed PDFs
  - `download/` - Generated PDF exports (Future Scope)'''
    
    content = re.sub(old_s3, new_s3, content, flags=re.MULTILINE | re.DOTALL)
    
    # Update 5: Add PDF Export Service section before Error Handling
    pdf_export_section = '''

## PDF Export Service (Future Scope)

**Overview**: The PDF export feature allows users to download scheme recommendations as a PDF document for offline reference. This feature is marked as Future Scope and will be implemented in the final stage after core RAG functionality is validated.

**Architecture**:
- **Client-Side Generation**: Use jsPDF library in the browser to generate PDFs
- **Content**: Include user query, timestamp, all scheme recommendations with eligibility, benefits, and application steps
- **Multilingual Support**: Generate PDFs in the user's selected language
- **Storage**: Store generated PDFs in S3 download/ folder for audit and retrieval
- **Delivery**: Provide immediate download link to user

**Implementation Approach**:
```javascript
// Client-side PDF generation with jsPDF
function generatePDF(results, language) {
  const doc = new jsPDF();
  
  // Add header
  doc.setFontSize(16);
  doc.text(translations[language].pdfTitle, 10, 10);
  
  // Add timestamp
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 10, 20);
  
  // Add user query
  doc.setFontSize(12);
  doc.text(`Query: ${userQuery}`, 10, 30);
  
  // Add scheme recommendations
  let yPos = 40;
  results.schemes.forEach((scheme, index) => {
    doc.setFontSize(14);
    doc.text(`${index + 1}. ${scheme.scheme_name}`, 10, yPos);
    yPos += 10;
    
    doc.setFontSize(10);
    doc.text(`Eligibility: ${scheme.eligibility}`, 15, yPos);
    yPos += 10;
    doc.text(`Benefits: ${scheme.benefits}`, 15, yPos);
    yPos += 10;
    doc.text(`Application: ${scheme.application_steps}`, 15, yPos);
    yPos += 10;
    doc.text(`Source: ${scheme.source}`, 15, yPos);
    yPos += 15;
  });
  
  // Save PDF
  doc.save(`scheme-recommendations-${Date.now()}.pdf`);
  
  // Optional: Upload to S3 download/ folder for audit
  uploadToS3(doc.output('blob'), `download/scheme-${Date.now()}.pdf`);
}
```

**S3 Upload (Optional)**:
- Use AWS SDK for JavaScript to upload generated PDFs to S3
- Requires temporary credentials via Cognito Identity Pool or API Gateway
- PDFs stored with timestamp and session ID for audit trail
- Lifecycle policy: Delete PDFs older than 30 days

**Alternative: Server-Side Generation**:
- Create a new Lambda function for PDF generation
- Use Python libraries: ReportLab or WeasyPrint
- API endpoint: POST /api/generate-pdf
- Advantages: Better formatting control, server-side storage
- Disadvantages: Additional Lambda costs, slower response time

**Future Enhancements**:
- Add QR codes linking to official scheme portals
- Include scheme logos and government branding
- Support for multiple schemes in single PDF
- Email delivery option for users without download capability

'''
    
    # Insert before Error Handling section
    content = re.sub(
        r'(## Error Handling)',
        pdf_export_section + r'\1',
        content,
        count=1
    )
    
    # Update 6: Update Technology Stack section
    old_tech_stack = r'''\*\*Frontend\*\*: Static HTML \+ CloudFront for frontend distribution'''
    new_tech_stack = '''**Frontend**: Static HTML + CloudFront (3-page flow with multilingual UI support)'''
    content = re.sub(old_tech_stack, new_tech_stack, content)
    
    # Update 7: Add CloudWatch monitoring clarification
    cloudwatch_note = '''

**Note on CloudWatch Monitoring**: CloudWatch monitors backend services only (Lambda functions, API Gateway, EC2 FAISS service). Frontend errors and client-side issues are handled in the browser console and not logged to CloudWatch. User-facing error messages are displayed in the selected language on the frontend.

'''
    
    # Insert after CloudWatch section
    content = re.sub(
        r'(#### 7\. Observability Layer \(CloudWatch\).*?\n\n)(\*\*Lambda Monitoring\*\*:)',
        r'\1' + cloudwatch_note + r'\2',
        content,
        flags=re.DOTALL
    )
    
    # Write the updated content
    with open('.kiro/specs/govt-scheme-rag/design.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Design document updated successfully!")
    print("Changes applied:")
    print("1. Frontend Layer updated to 3-page architecture")
    print("2. Request Format updated with category field")
    print("3. FAISS Metadata Structure updated with category field")
    print("4. S3 Storage updated with download/ folder")
    print("5. PDF Export Service section added (Future Scope)")
    print("6. Technology Stack updated")
    print("7. CloudWatch monitoring clarification added")

if __name__ == "__main__":
    update_design_document()
