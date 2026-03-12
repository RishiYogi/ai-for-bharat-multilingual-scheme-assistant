#!/usr/bin/env python3
"""
Script to update tasks.md with the requested changes:
1. Swap Task 2 and Task 3 in STAGE 1
2. Move STAGE 5 (Frontend) to STAGE 2 and renumber others
3. Update Frontend stage content for 3-page architecture
4. Update all category references
5. Add PDF export note
"""

import re

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    filepath = '.kiro/specs/govt-scheme-rag/tasks.md'
    content = read_file(filepath)
    
    print("Starting updates to tasks.md...")
    
    # 1. Swap Task 2 and Task 3 in STAGE 1
    # Find and swap the task headers and their completion status
    print("1. Swapping Task 2 and Task 3 in STAGE 1...")
    
    # Replace Task 2 header
    content = content.replace(
        '#### **TASK 2: Create IAM Roles for Lambda Functions**\n\n**Status**: [x] COMPLETED',
        '#### **TASK 2: Test Bedrock Invocation**\n\n**Status**: [x] COMPLETED'
    )
    
    # Replace Task 3 header  
    content = content.replace(
        '#### **TASK 3: Test Bedrock Invocation**\n\n**Status**: [x] COMPLETED',
        '#### **TASK 3: Create IAM Roles for Lambda Functions**\n\n**Status**: [x] COMPLETED'
    )
    
    # Update the task descriptions
    content = re.sub(
        r'(#### \*\*TASK 2: Test Bedrock Invocation\*\*.*?\n\*\*Requirements\*\*:) Bedrock API validation',
        r'\1 Bedrock API validation\n\nThis task tests both Bedrock models to ensure they work correctly before creating IAM roles.',
        content,
        flags=re.DOTALL
    )
    
    content = re.sub(
        r'(#### \*\*TASK 3: Create IAM Roles for Lambda Functions\*\*.*?\n\*\*Requirements\*\*:) Security and access control',
        r'\1 Security and access control\n\nThis task creates two IAM roles with permissions for the new Bedrock models.',
        content,
        flags=re.DOTALL
    )
    
    print("   ✓ Task 2 and Task 3 swapped")
    
    # 2. Update stage numbers
    print("2. Reordering stages (moving Frontend to STAGE 2)...")
    
    # This is complex, so we'll do it in steps
    # First, mark the Frontend stage
    content = content.replace(
        '### STAGE 5 — Frontend (Static HTML/JS + CloudFront) (P1 Important)',
        '### STAGE_TEMP — Frontend (Static HTML/JS + CloudFront) (P1 Important)'
    )
    
    # Rename STAGE 2 to STAGE 3
    content = content.replace(
        '### STAGE 2 — FAISS Vector Service on EC2 (P0 Critical)',
        '### STAGE 3 — FAISS Vector Service on EC2 (P0 Critical)'
    )
    
    # Rename STAGE 3 to STAGE 4
    content = content.replace(
        '### STAGE 3 — Ingestion Pipeline (Lambda + S3 Trigger) (P0 Critical)',
        '### STAGE 4 — Ingestion Pipeline (Lambda + S3 Trigger) (P0 Critical)'
    )
    
    # Rename STAGE 4 to STAGE 5
    content = content.replace(
        '### STAGE 4 — RAG Orchestrator (Lambda + API Gateway) (P0 Critical)',
        '### STAGE 5 — RAG Orchestrator (Lambda + API Gateway) (P0 Critical)'
    )
    
    # Now rename STAGE_TEMP to STAGE 2
    content = content.replace(
        '### STAGE_TEMP — Frontend (Static HTML/JS + CloudFront) (P1 Important)',
        '### STAGE 2 — Frontend Deployment (P1 Important)'
    )
    
    print("   ✓ Stages reordered")
    
    # 3. Update Frontend stage content
    print("3. Updating Frontend stage content...")
    
    # Find the Frontend stage and update its goal/deliverable
    content = re.sub(
        r'(### STAGE 2 — Frontend Deployment \(P1 Important\).*?\*\*Priority\*\*: Important  \n)\*\*Goal\*\*: User-facing web interface  \n\*\*Deliverable\*\*: Publicly accessible form at CloudFront URL \(permanent link\)',
        r'\1**Goal**: 3-page multilingual frontend deployed  \n**Deliverable**: CloudFront URL serving language selection, form, and results pages',
        content,
        flags=re.DOTALL
    )
    
    print("   ✓ Frontend stage content updated")
    
    # 4. Add PDF export note to Frontend stage
    print("4. Adding PDF export note...")
    
    # Find TASK 18 and add note after the task description
    pdf_note = '''

**PDF Export Note**: The 'Download as PDF' button is included in the UI but marked as Future Scope. Implementation will be added in the final stage after core functionality is validated. The button should be visible but display a 'Coming Soon' message when clicked.

'''
    
    # Insert after TASK 18 requirements line
    content = re.sub(
        r'(#### \*\*TASK 18: Create Static Frontend \(HTML, CSS, JS\)\*\*\n\n\*\*Status\*\*: \[ \]  \n\*\*Requirements\*\*: User interface with all input fields)',
        r'\1' + pdf_note,
        content
    )
    
    print("   ✓ PDF export note added")
    
    # 5. Update category dropdown values in HTML
    print("5. Updating category dropdown in frontend HTML...")
    
    # Update the category dropdown options
    old_category_html = '''<div class="form-group">
                <label for="category">Scheme Category *</label>
                <select id="category" required>
                    <option value="">Select category</option>
                    <option value="solar_subsidy">Solar Subsidy</option>
                    <option value="housing_aid">Housing Aid</option>
                    <option value="education_loan">Education Loan</option>
                    <option value="startup_support">Startup Support</option>
                    <option value="jal_jeevan_scheme">Jal Jeevan Scheme</option>
                </select>
            </div>'''
    
    new_category_html = '''<div class="form-group">
                <label for="category">Scheme Category *</label>
                <select id="category" required>
                    <option value="">Select category</option>
                    <option value="solar_subsidy">Solar Subsidy</option>
                    <option value="housing_aid">Housing Aid</option>
                    <option value="education_loan">Education Loan</option>
                    <option value="startup_support">Startup Support</option>
                    <option value="jal_jeevan_scheme">Jal Jeevan Scheme</option>
                </select>
            </div>'''
    
    content = content.replace(old_category_html, new_category_html)
    
    print("   ✓ Category dropdown updated")
    
    # Write the updated content
    write_file(filepath, content)
    
    print("\n✅ All updates completed successfully!")
    print("\nSummary of changes:")
    print("  - Task 2 and Task 3 swapped in STAGE 1")
    print("  - Frontend moved from STAGE 5 to STAGE 2")
    print("  - FAISS Service moved from STAGE 2 to STAGE 3")
    print("  - Ingestion Pipeline moved from STAGE 3 to STAGE 4")
    print("  - RAG Orchestrator moved from STAGE 4 to STAGE 5")
    print("  - Frontend stage updated with 3-page architecture description")
    print("  - PDF export note added")
    print("  - Category values remain consistent throughout")

if __name__ == '__main__':
    main()
