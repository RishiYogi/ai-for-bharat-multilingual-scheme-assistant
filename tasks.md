# Implementation Plan: Multilingual Government Scheme Assistant (ChromaDB + Lambda)

## Overview

This implementation plan breaks down the hybrid serverless RAG-based government scheme assistant into 9 structured development stages. The system uses AWS Lambda, Amazon Bedrock (Titan models), ChromaDB vector database on EC2, and S3 + CloudFront for a cost-optimized, pluggable architecture.

The implementation follows a staged approach: **AWS Setup → Frontend → ChromaDB Service → Ingestion Pipeline → RAG Orchestrator → Gatekeeper → Response Persistence & PDF Export → Observability → Testing**. Each stage has clear deliverables optimized for prototype evaluation.

## Technology Stack

- **Compute**: AWS Lambda (Python 3.11) + EC2 t3.micro (ChromaDB service)
- **Frontend**: Static HTML/JS hosted on S3 + CloudFront
- **Vector Database**: ChromaDB on EC2 (pluggable)
- **Embeddings**: Amazon Bedrock - amazon.titan-embed-text-v2:0 (1024 dimensions)
- **LLM**: Amazon Bedrock - global.amazon.nova-2-lite-v1:0 (Nova 2 Lite-Inference Profile)
- **Storage**: Amazon S3 + EBS (8 GB)
- **API**: Amazon API Gateway (HTTP API)
- **Monitoring**: Amazon CloudWatch
- **Region**: ap-south-1 (Mumbai)

## Architecture Principle

**Pluggable Vector Database**:
```
VectorStore (interface)
    ├── ChromaVectorStore (EC2 default - prototype)
    └── OpenSearchVectorStore (future - production)
```

Lambda functions use `VectorStoreFactory.get_store()` - never directly call ChromaDB or OpenSearch.
Backend selected via `VECTOR_DB_TYPE` environment variable.

## User Input Fields

- **Name** (required, text)
- **Age** (required, numeric, 1-120)
- **Gender** (optional dropdown: Male / Female / Other / Prefer not to say)
- **State** (required dropdown): All 28 states and 8 union territories of India
- **Category** (required dropdown): Education & Skills / Solar Subsidy / Startup and Self Employment / Housing Aid / Water & Sanitation / Agriculture / Health Care / Other Schemes
- **Community** (required dropdown): General / OBC / PVTG / SC / ST / DNT
- **Physically Challenged** (required dropdown): Yes / No
- **Language** (required dropdown): English (default), Hindi, Tamil
- **Query** (required, free-text)

## Category Values (for API)

- `education_skill` - Education and skill development programs
- `solar_subsidy` - Solar panel installation subsidies
- `startup_selfemployment` - Startup and self-employment schemes
- `housing_aid` - Housing and shelter assistance schemes
- `water_sanitation` - Water supply and sanitation schemes
- `agriculture` - Agriculture and farming support schemes
- `healthcare` - Health care and medical assistance schemes
- `others` - Other government schemes


## Data Privacy

**NO collection of**:
- Aadhaar numbers
- Bank details
- Date of Birth
- Any sensitive government IDs

## Estimated Monthly Cost (Free Tier Optimized)

```
EC2 t3.micro (24/7):        $0 (free tier: 750 hours)
EBS 8 GB:                   $0 (free tier: 30 GB)
Lambda:                     $0 (free tier: 1M requests)
API Gateway:                $0 (free tier: 1M requests)
Bedrock (Embeddings + LLM):  $5-10 (pay per token)
S3:                         $0 (free tier: 5 GB)
CloudFront:                 $0 (free tier: 1 TB transfer)
CloudWatch Logs:            $1-2
----------------------------
Total:                      $6-12/month ✅
```

---

## Tasks

### STAGE 1 — AWS Infrastructure Setup (P0 Critical)

**Priority**: Highest  
**Goal**: AWS backbone ready  
**Deliverable**: S3, IAM roles, Bedrock access configured

---

#### **TASK 0: Verify Bedrock Model Access**

**Status**: [x] COMPLETED  
**Requirements**: LLM and embedding model access

As of 2026, Bedrock model access is automatic - no manual enabling required. This task verifies that your AWS account has access to the required models.

**STEP 1: Verify Bedrock is available in your region**

Run this command in your terminal:
```
aws bedrock list-foundation-models --region ap-south-1 --query "modelSummaries[?contains(modelId, 'titan') || contains(modelId, 'nova')].{Name:modelName,ID:modelId}" --output table
```

**Expected output**: You should see these models listed:
- `amazon.titan-embed-text-v2:0` (Titan Text Embeddings V2)
- `global.amazon.nova-lite-v1:0` (Nova 2 Lite)

**STEP 2: Confirm no manual action needed**

In 2026, you do NOT need to:
- Navigate to Bedrock console
- Click "Manage model access"
- Request access

Model access is granted automatically when Bedrock is enabled in your account.

---

#### **TASK 1: Region Lock and S3 Bucket Creation**

**Status**: [x] COMPLETED  
**Requirements**: Storage infrastructure

**STEP 1: Log into AWS Console**

Sub-step 1.1: Open your browser and navigate to https://console.aws.amazon.com  
Sub-step 1.2: Sign in with your AWS credentials

**STEP 2: Select the correct region**

Sub-step 2.1: Look at the top right corner of the AWS Console  
Sub-step 2.2: Click on the region dropdown  
Sub-step 2.3: Select **Asia Pacific (Mumbai) ap-south-1**

**STEP 3: Navigate to S3 service**

Sub-step 3.1: Click on "Services" in the top navigation bar  
Sub-step 3.2: Under "Storage", click on "S3"  
OR: Type "S3" in the search bar and click on the result

**STEP 4: Create the bucket**

Sub-step 4.1: Click the "Create bucket" button  
Sub-step 4.2: Enter bucket name: `aicloud-bharat-schemes`  
Sub-step 4.3: Verify region is set to: **ap-south-1**  
Sub-step 4.4: Under "Object Ownership", select: **ACLs disabled (recommended)**  
Sub-step 4.5: Under "Block Public Access settings", ensure all checkboxes are **checked** (enabled)  
Sub-step 4.6: Under "Bucket Versioning", select: **Disable**  
Sub-step 4.7: Under "Default encryption", select: **Server-side encryption with Amazon S3 managed keys (SSE-S3)**  
Sub-step 4.8: Click "Create bucket" at the bottom

**STEP 5: Create folders inside the bucket**

Sub-step 5.1: Click on the newly created bucket name `aicloud-bharat-schemes`  
Sub-step 5.2: Click "Create folder" button  
Sub-step 5.3: Enter folder name: `raw/` and click "Create folder"  
Sub-step 5.4: Click "Create folder" button again  
Sub-step 5.5: Enter folder name: `processed/` and click "Create folder"  
Sub-step 5.6: Click "Create folder" button again  
Sub-step 5.7: Enter folder name: `frontend/` and click "Create folder"

**Note**: The `raw/` folder stores uploaded PDFs, `processed/` stores processed PDFs, and `frontend/` will store the static website files (created in STAGE 2).

**STEP 6: Verify bucket creation via CLI (optional)**

Run this command in your terminal:
```
aws s3 ls
```

Expected output should include:
```
2026-03-01 19:02:55 aicloud-bharat-schemes
```

---

#### **TASK 2: Test Bedrock Invocation**

**Status**: [x] COMPLETED  
**Requirements**: Bedrock API validation

This task tests both Bedrock models to ensure they work correctly.

**STEP 1: Install required Python package**

Sub-step 1.1: Open your terminal

Sub-step 1.2: Run this command:
```
pip install boto3
```

Sub-step 1.3: Wait for installation to complete

**STEP 2: Create test script**

Sub-step 2.1: Create a new folder named `scripts` (if it doesn't exist)

Sub-step 2.2: Create a new file named `test_bedrock.py` inside the `scripts` folder

Sub-step 2.3: Put the following content inside the file:
```python
import boto3
import json

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1')

print("=" * 60)
print("Testing Amazon Bedrock Models in ap-south-1")
print("=" * 60)

# Test 1: Titan Embeddings V2
print("\n[TEST 1] Testing Titan Embeddings V2...")
try:
    embedding_response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v2:0',
        body=json.dumps({
            "inputText": "solar subsidy scheme"
        })
    )
    
    embedding_result = json.loads(embedding_response['body'].read())
    embedding_vector = embedding_result['embedding']
    
    print(f"✅ Embedding generated successfully")
    print(f"   Dimension: {len(embedding_vector)}")
    print(f"   First 5 values: {embedding_vector[:5]}")
    
    if len(embedding_vector) == 1024:
        print("   ✅ Dimension is 1024 (Titan V2 standard)")
    else:
        print(f"   ⚠️  Unexpected dimension: {len(embedding_vector)}")

except Exception as e:
    print(f"❌ Embedding test failed: {str(e)}")

# Test 2: Nova 2 Lite
print("\n[TEST 2] Testing Nova 2 Lite LLM...")
try:
    llm_response = bedrock.invoke_model(
        modelId='global.amazon.nova-lite-v1:0',
        body=json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": "What is a solar subsidy scheme? Answer in one sentence."}]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 100,
                "temperature": 0.7
            }
        })
    )
    
    llm_result = json.loads(llm_response['body'].read())
    response_text = llm_result['output']['message']['content'][0]['text']
    
    print(f"✅ LLM response generated successfully")
    print(f"   Response: {response_text}")
    print(f"   Response length: {len(response_text)} characters")

except Exception as e:
    print(f"❌ LLM test failed: {str(e)}")

print("\n" + "=" * 60)
print("Bedrock testing complete!")
print("=" * 60)
```

Sub-step 2.4: Save the file

**STEP 3: Run the test script**

Sub-step 3.1: Open your terminal

Sub-step 3.2: Navigate to your project directory

Sub-step 3.3: Run this command:
```
python scripts/test_bedrock.py
```

**STEP 4: Verify test results**

Sub-step 4.1: Check that TEST 1 (Embeddings) shows:
- ✅ Embedding generated successfully
- Dimension: 1024
- ✅ Dimension is 1024 (Titan V2 standard)

Sub-step 4.2: Check that TEST 2 (LLM) shows:
- ✅ LLM response generated successfully
- Response: (some text about solar subsidies)
- Response length: (some number) characters

Sub-step 4.3: Verify both tests completed in less than 2 seconds

**STEP 5: Troubleshoot if tests fail**

If TEST 1 fails:
- Verify IAM role has permission for `amazon.titan-embed-text-v2:0`
- Check AWS credentials: Run `aws sts get-caller-identity`
- Verify region is ap-south-1: Run `aws configure get region`

If TEST 2 fails:
- Verify IAM role has permission for `global.amazon.nova-lite-v1:0`
- Check model ID is correct (includes `global.` prefix)
- Verify API format uses `messages` array (not `inputText`)

**Note**: Titan Embed Text V2 produces 1024-dimensional embeddings (V1 was 1536)

---

#### **TASK 3: Create IAM Roles for Lambda Functions**

**Status**: [x] COMPLETED  
**Requirements**: Security and access control

This task creates two IAM roles with permissions for the new Bedrock models.

**STEP 1: Delete old IAM roles (if they exist)**

Sub-step 1.1: Open your terminal (Command Prompt or PowerShell on Windows)

Sub-step 1.2: Run these commands to delete SchemeIngestionLambdaRole:
```
aws iam detach-role-policy --role-name SchemeIngestionLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```
```
aws iam delete-role-policy --role-name SchemeIngestionLambdaRole --policy-name S3AccessPolicy
```
```
aws iam delete-role-policy --role-name SchemeIngestionLambdaRole --policy-name BedrockAccessPolicy
```
```
aws iam delete-role --role-name SchemeIngestionLambdaRole
```

Sub-step 1.3: Run these commands to delete RAGOrchestratorLambdaRole:
```
aws iam detach-role-policy --role-name RAGOrchestratorLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```
```
aws iam delete-role-policy --role-name RAGOrchestratorLambdaRole --policy-name BedrockAccessPolicy
```
```
aws iam delete-role --role-name RAGOrchestratorLambdaRole
```

**Note**: Errors are normal if roles don't exist yet. Continue to next step.

**STEP 2: Create trust policy file**

Sub-step 2.1: Create a new file named `lambda-trust-policy.json`

Sub-step 2.2: Put the following content inside the file:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Sub-step 2.3: Save the file

**STEP 3: Create SchemeIngestionLambdaRole**

Sub-step 3.1: Create the role by running this command in your terminal:
```
aws iam create-role --role-name SchemeIngestionLambdaRole --assume-role-policy-document file://lambda-trust-policy.json
```

Sub-step 3.2: Attach basic execution policy by running this command:
```
aws iam attach-role-policy --role-name SchemeIngestionLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

Sub-step 3.3: Create a new file named `ingestion-s3-policy.json`

Sub-step 3.4: Put the following content inside the file:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::aicloud-bharat-schemes/*"
    }
  ]
}
```

Sub-step 3.5: Save the file

Sub-step 3.6: Create a new file named `ingestion-bedrock-policy.json`

Sub-step 3.7: Put the following content inside the file:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v2:0"
    }
  ]
}
```

Sub-step 3.8: Save the file

Sub-step 3.9: Attach S3 policy by running this command:
```
aws iam put-role-policy --role-name SchemeIngestionLambdaRole --policy-name S3AccessPolicy --policy-document file://ingestion-s3-policy.json
```

Sub-step 3.10: Attach Bedrock policy by running this command:
```
aws iam put-role-policy --role-name SchemeIngestionLambdaRole --policy-name BedrockAccessPolicy --policy-document file://ingestion-bedrock-policy.json
```

**STEP 4: Create RAGOrchestratorLambdaRole**

Sub-step 4.1: Create the role by running this command in your terminal:
```
aws iam create-role --role-name RAGOrchestratorLambdaRole --assume-role-policy-document file://lambda-trust-policy.json
```

Sub-step 4.2: Attach basic execution policy by running this command:
```
aws iam attach-role-policy --role-name RAGOrchestratorLambdaRole --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

Sub-step 4.3: Create a new file named `orchestrator-bedrock-policy.json`

Sub-step 4.4: Put the following content inside the file:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": [
        "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v2:0",
        "arn:aws:bedrock:*::foundation-model/global.amazon.nova-lite-v1:0"
      ]
    }
  ]
}
```

Sub-step 4.5: Save the file

Sub-step 4.6: Attach Bedrock policy by running this command:
```
aws iam put-role-policy --role-name RAGOrchestratorLambdaRole --policy-name BedrockAccessPolicy --policy-document file://orchestrator-bedrock-policy.json
```

**STEP 5: Verify roles were created successfully**

Sub-step 5.1: Run this command in your terminal:
```
aws iam list-roles --query "Roles[?contains(RoleName, 'Lambda')].RoleName"
```

Sub-step 5.2: Verify the output shows both roles:
```json
[
    "RAGOrchestratorLambdaRole",
    "SchemeIngestionLambdaRole"
]
```

**ALTERNATIVE: Use automated script**

Instead of manual steps above, you can run the automated script:

For Windows: Run `scripts\setup_iam_roles.bat`  
For Linux/Mac: Run `scripts/setup_iam_roles.sh`

---

### STAGE 2 — Frontend Deployment (P1 Important)

**Priority**: Important  
**Goal**: 3-page multilingual frontend deployed  
**Deliverable**: CloudFront URL serving language selection, form, and results pages

---

#### **TASK 4: Create Language Selection Page (index.html)**

**Status**: [x] COMPLETED  
**Requirements**: Landing page with 3 language tiles

**STEP 1: Create frontend directory structure**

Sub-step 1.1: Create a new folder named `frontend`

Sub-step 1.2: Navigate to the frontend directory:
```
cd frontend
```

**STEP 2: Create index.html file**

Sub-step 2.1: Create a new file named `index.html`

Sub-step 2.2: Put the following content inside the file:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Government Scheme Assistant</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>Government Scheme Assistant</h1>
        <p class="subtitle">Select your preferred language</p>
        
        <div class="language-tiles">
            <div class="language-tile" onclick="selectLanguage('English')">
                <h2>English</h2>
                <p>Find government schemes</p>
            </div>
            
            <div class="language-tile" onclick="selectLanguage('Hindi')">
                <h2>हिंदी</h2>
                <p>सरकारी योजनाएं खोजें</p>
            </div>
            
            <div class="language-tile" onclick="selectLanguage('Tamil')">
                <h2>தமிழ்</h2>
                <p>அரசு திட்டங்களைக் கண்டறியவும்</p>
            </div>
        </div>
    </div>
    
    <script src="app.js"></script>
</body>
</html>
```

Sub-step 2.3: Save the file

---

#### **TASK 5: Create User Input Form (form.html)**

**Status**: [x] COMPLETED  
**Requirements**: Form with category dropdown and all required fields

**STEP 1: Create form.html file**

Sub-step 1.1: Create a new file named `form.html`

Sub-step 1.2: Put the following content inside the file:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Government Scheme Assistant - Form</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1 id="form-title">Government Scheme Assistant</h1>
        <p class="subtitle" id="form-subtitle">Tell us about yourself</p>
        
        <form id="scheme-form">
            <div class="form-group">
                <label for="name" id="label-name">Name *</label>
                <input type="text" id="name" required>
            </div>
            
            <div class="form-group">
                <label for="age" id="label-age">Age *</label>
                <input type="number" id="age" min="1" max="120" required>
            </div>

            <div class="form-group">
                <label for="gender" id="label-gender">Gender</label>
                <select id="gender">
                    <option value="">Prefer not to say</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                </select>
            </div>

            <div class="form-group">
                <label for="state" id="label-state">State *</label>
                <select id="state" required>
                    <option value="">Select your state</option>
                    <option value="andhra_pradesh">Andhra Pradesh</option>
                    <option value="arunachal_pradesh">Arunachal Pradesh</option>
                    <option value="assam">Assam</option>
                    <option value="bihar">Bihar</option>
                    <option value="chhattisgarh">Chhattisgarh</option>
                    <option value="goa">Goa</option>
                    <option value="gujarat">Gujarat</option>
                    <option value="haryana">Haryana</option>
                    <option value="himachal_pradesh">Himachal Pradesh</option>
                    <option value="jharkhand">Jharkhand</option>
                    <option value="karnataka">Karnataka</option>
                    <option value="kerala">Kerala</option>
                    <option value="madhya_pradesh">Madhya Pradesh</option>
                    <option value="maharashtra">Maharashtra</option>
                    <option value="manipur">Manipur</option>
                    <option value="meghalaya">Meghalaya</option>
                    <option value="mizoram">Mizoram</option>
                    <option value="nagaland">Nagaland</option>
                    <option value="odisha">Odisha</option>
                    <option value="punjab">Punjab</option>
                    <option value="rajasthan">Rajasthan</option>
                    <option value="sikkim">Sikkim</option>
                    <option value="tamil_nadu">Tamil Nadu</option>
                    <option value="telangana">Telangana</option>
                    <option value="tripura">Tripura</option>
                    <option value="uttar_pradesh">Uttar Pradesh</option>
                    <option value="uttarakhand">Uttarakhand</option>
                    <option value="west_bengal">West Bengal</option>
                    <option value="andaman_nicobar">Andaman and Nicobar Islands</option>
                    <option value="chandigarh">Chandigarh</option>
                    <option value="dadra_nagar_haveli_daman_diu">Dadra and Nagar Haveli and Daman and Diu</option>
                    <option value="delhi">Delhi</option>
                    <option value="jammu_kashmir">Jammu and Kashmir</option>
                    <option value="ladakh">Ladakh</option>
                    <option value="lakshadweep">Lakshadweep</option>
                    <option value="puducherry">Puducherry</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="category" id="label-category">Scheme Category *</label>
                <select id="category" required>
                    <option value="">Select category</option>
                    <option value="education_skill">Education & Skills</option>                    
                    <option value="startup_selfemployment">Startup & Self Employment</option>
                    <option value="agriculture">Agriculture</option>
                    <option value="healthcare">Health Care</option>
                    <option value="solar_subsidy">Solar Subsidy</option>
                    <option value="housing_aid">Housing Aid</option>
                    <option value="water_sanitation">Water & Sanitation</option>                    
                    <option value="others">Other Schemes</option>
                </select>
            </div>            
                      
            <div class="form-group">
                <label for="community" id="label-community">Community *</label>
                <select id="community" required>
                    <option value="">Select community</option>
                    <option value="general">General</option>
                    <option value="obc">OBC</option>
                    <option value="pvtg">PVTG</option>
                    <option value="sc">SC</option>
                    <option value="st">ST</option>
                    <option value="dnt">DNT</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="physically_challenged" id="label-physically-challenged">Physically Challenged *</label>
                <select id="physically_challenged" required>
                    <option value="">Select option</option>
                    <option value="yes">Yes</option>
                    <option value="no">No</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="query" id="label-query">Your Question *</label>
                <textarea id="query" rows="4" required></textarea>
            </div>
            
            <button type="submit" id="submit-btn">Find Schemes</button>
        </form>
        
        <button class="back-btn" onclick="goBack()">Back</button>
    </div>
    
    <script src="translations.js"></script>
    <script src="app.js"></script>
</body>
</html>
```

Sub-step 1.3: Save the file

---

#### **TASK 6: Create Results Display Page (results.html)**

**Status**: [x] COMPLETED  
**Requirements**: Results page with back button

**STEP 1: Create results.html file**

Sub-step 1.1: Create a new file named `results.html`

Sub-step 1.2: Put the following content inside the file:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Government Scheme Assistant - Results</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <h1 id="results-title">Your Scheme Recommendations</h1>
        
        <div id="loading" class="loading">
            <p>Finding relevant schemes for you...</p>
        </div>
        
        <div id="results-content" class="results-content" style="display: none;">
            <div id="response-text"></div>
            
            <div class="sources" id="sources-section" style="display: none;">
                <h3>Sources:</h3>
                <ul id="sources-list"></ul>
            </div>
        </div>
        
        <div id="error-message" class="error-message" style="display: none;"></div>
        
        <div class="button-group">
            <button class="back-btn" onclick="goToForm()">New Search</button>
            <button class="download-btn" onclick="downloadPDF()">Download as PDF</button>
        </div>
    </div>
    
    <script src="translations.js"></script>
    <script src="app.js"></script>
</body>
</html>
```

Sub-step 1.3: Save the file

**Note**: The "Download as PDF" button is included in the UI but marked as Future Scope. Implementation will be added in the final stage after core functionality is validated. The button should be visible but display a "Coming Soon" message when clicked.

---

#### **TASK 7: Create Multilingual Translations (translations.js)**

**Status**: [x] COMPLETED  
**Requirements**: Translations for 3 languages only

**STEP 1: Create translations.js file**

Sub-step 1.1: Create a new file named `translations.js`

Sub-step 1.2: Put the following content inside the file:
```javascript
const translations = {
    English: {
        formTitle: "Government Scheme Assistant",
        formSubtitle: "Tell us about yourself",
        labelName: "Name *",
        labelAge: "Age *",
        labelGender: "Gender",
        labelState: "State *",
        labelCategory: "Scheme Category *",
        labelCommunity: "Community *",
        labelPhysicallyChallenged: "Physically Challenged *",
        labelQuery: "Your Question *",
        submitBtn: "Find Schemes",
        backBtn: "Back",
        resultsTitle: "Your Scheme Recommendations",
        loading: "Finding relevant schemes for you...",
        newSearch: "New Search",
        downloadPDF: "Download as PDF",
        sources: "Sources:",
        statePlaceholder: "Select your state",
        categoryPlaceholder: "Select category",
        genderPlaceholder: "Prefer not to say",
        communityPlaceholder: "Select community",
        physicallyChallengedPlaceholder: "Select option",
        categories: {
            education_skill: "Education & Skills",
            solar_subsidy: "Solar Subsidy",
            startup_selfemployment: "Startup and Self Employment",
            housing_aid: "Housing Aid",
            water_sanitation: "Water & Sanitation",
            agriculture: "Agriculture",
            healthcare: "Health Care",
            others: "Other Schemes"
        },
        states: {
            andhra_pradesh: "Andhra Pradesh",
            arunachal_pradesh: "Arunachal Pradesh",
            assam: "Assam",
            bihar: "Bihar",
            chhattisgarh: "Chhattisgarh",
            goa: "Goa",
            gujarat: "Gujarat",
            haryana: "Haryana",
            himachal_pradesh: "Himachal Pradesh",
            jharkhand: "Jharkhand",
            karnataka: "Karnataka",
            kerala: "Kerala",
            madhya_pradesh: "Madhya Pradesh",
            maharashtra: "Maharashtra",
            manipur: "Manipur",
            meghalaya: "Meghalaya",
            mizoram: "Mizoram",
            nagaland: "Nagaland",
            odisha: "Odisha",
            punjab: "Punjab",
            rajasthan: "Rajasthan",
            sikkim: "Sikkim",
            tamil_nadu: "Tamil Nadu",
            telangana: "Telangana",
            tripura: "Tripura",
            uttar_pradesh: "Uttar Pradesh",
            uttarakhand: "Uttarakhand",
            west_bengal: "West Bengal",
            andaman_nicobar: "Andaman and Nicobar Islands",
            chandigarh: "Chandigarh",
            dadra_nagar_haveli_daman_diu: "Dadra and Nagar Haveli and Daman and Diu",
            delhi: "Delhi",
            jammu_kashmir: "Jammu and Kashmir",
            ladakh: "Ladakh",
            lakshadweep: "Lakshadweep",
            puducherry: "Puducherry"
        },
        genderOptions: {
            "": "Prefer not to say",
            male: "Male",
            female: "Female",
            other: "Other"
        },
        communityOptions: {
            "": "Select community",
            general: "General",
            obc: "OBC",
            pvtg: "PVTG",
            sc: "SC",
            st: "ST",
            dnt: "DNT"
        },
        physicallyChallengedOptions: {
            "": "Select option",
            yes: "Yes",
            no: "No"
        }
    },
    Hindi: {
        formTitle: "सरकारी योजना सहायक",
        formSubtitle: "अपने बारे में बताएं",
        labelName: "नाम *",
        labelAge: "आयु *",
        labelGender: "लिंग",
        labelState: "राज्य *",
        labelCategory: "योजना श्रेणी *",
        labelCommunity: "समुदाय *",
        labelPhysicallyChallenged: "शारीरिक रूप से विकलांग *",
        labelQuery: "आपका प्रश्न *",
        submitBtn: "योजनाएं खोजें",
        backBtn: "वापस",
        resultsTitle: "आपकी योजना सिफारिशें",
        loading: "आपके लिए प्रासंगिक योजनाएं खोज रहे हैं...",
        newSearch: "नई खोज",
        downloadPDF: "PDF डाउनलोड करें",
        sources: "स्रोत:",
        statePlaceholder: "अपना राज्य चुनें",
        categoryPlaceholder: "श्रेणी चुनें",
        genderPlaceholder: "नहीं बताना चाहते",
        communityPlaceholder: "समुदाय चुनें",
        physicallyChallengedPlaceholder: "विकल्प चुनें",
        categories: {
            education_skill: "शिक्षा और कौशल",
            solar_subsidy: "सौर सब्सिडी",
            startup_selfemployment: "स्टार्टअप और स्वरोजगार",
            housing_aid: "आवास सहायता",
            water_sanitation: "जल और स्वच्छता",
            agriculture: "कृषि",
            healthcare: "स्वास्थ्य देखभाल",
            others: "अन्य योजनाएं"
        },
        states: {
            andhra_pradesh: "आंध्र प्रदेश",
            arunachal_pradesh: "अरुणाचल प्रदेश",
            assam: "असम",
            bihar: "बिहार",
            chhattisgarh: "छत्तीसगढ़",
            goa: "गोवा",
            gujarat: "गुजरात",
            haryana: "हरियाणा",
            himachal_pradesh: "हिमाचल प्रदेश",
            jharkhand: "झारखंड",
            karnataka: "कर्नाटक",
            kerala: "केरल",
            madhya_pradesh: "मध्य प्रदेश",
            maharashtra: "महाराष्ट्र",
            manipur: "मणिपुर",
            meghalaya: "मेघालय",
            mizoram: "मिजोरम",
            nagaland: "नागालैंड",
            odisha: "ओडिशा",
            punjab: "पंजाब",
            rajasthan: "राजस्थान",
            sikkim: "सिक्किम",
            tamil_nadu: "तमिल नाडु",
            telangana: "तेलंगाना",
            tripura: "त्रिपुरा",
            uttar_pradesh: "उत्तर प्रदेश",
            uttarakhand: "उत्तराखंड",
            west_bengal: "पश्चिम बंगाल",
            andaman_nicobar: "अंडमान और निकोबार द्वीप समूह",
            chandigarh: "चंडीगढ़",
            dadra_nagar_haveli_daman_diu: "दादरा और नगर हवेली और दमन और दीव",
            delhi: "दिल्ली",
            jammu_kashmir: "जम्मू और कश्मीर",
            ladakh: "लद्दाख",
            lakshadweep: "लक्षद्वीप",
            puducherry: "पुडुचेरी"
        },
        genderOptions: {
            "": "नहीं बताना चाहते",
            male: "पुरुष",
            female: "महिला",
            other: "अन्य"
        },
        communityOptions: {
            "": "समुदाय चुनें",
            general: "सामान्य",
            obc: "ओबीसी",
            pvtg: "पीवीटीजी",
            sc: "अनुसूचित जाति",
            st: "अनुसूचित जनजाति",
            dnt: "डीएनटी"
        },
        physicallyChallengedOptions: {
            "": "विकल्प चुनें",
            yes: "हाँ",
            no: "नहीं"
        }
    },
    Tamil: {
        formTitle: "அரசு திட்ட உதவியாளர்",
        formSubtitle: "உங்களைப் பற்றி எங்களிடம் கூறுங்கள்",
        labelName: "பெயர் *",
        labelAge: "வயது *",
        labelGender: "பாலினம்",
        labelState: "மாநிலம் *",
        labelCategory: "திட்ட வகை *",
        labelCommunity: "சமூகம் *",
        labelPhysicallyChallenged: "உடல் ஊனமுற்றவர் *",
        labelQuery: "உங்கள் கேள்வி *",
        submitBtn: "திட்டங்களைக் கண்டறியவும்",
        backBtn: "பின்செல்",
        resultsTitle: "உங்கள் திட்ட பரிந்துரைகள்",
        loading: "உங்களுக்கான தொடர்புடைய திட்டங்களைக் கண்டறிகிறது...",
        newSearch: "புதிய தேடல்",
        downloadPDF: "PDF பதிவிறக்கம்",
        sources: "ஆதாரங்கள்:",
        statePlaceholder: "உங்கள் மாநிலத்தைத் தேர்ந்தெடுக்கவும்",
        categoryPlaceholder: "வகையைத் தேர்ந்தெடுக்கவும்",
        genderPlaceholder: "சொல்ல விரும்பவில்லை",
        communityPlaceholder: "சமூகத்தைத் தேர்ந்தெடுக்கவும்",
        physicallyChallengedPlaceholder: "விருப்பத்தைத் தேர்ந்தெடுக்கவும்",
        categories: {
            education_skill: "கல்வி மற்றும் திறன்கள்",
            solar_subsidy: "சூரிய மானியம்",
            startup_selfemployment: "தொடக்க மற்றும் சுயதொழில்",
            housing_aid: "வீட்டு உதவி",
            water_sanitation: "நீர் மற்றும் சுகாதாரம்",
            agriculture: "விவசாயம்",
            healthcare: "சுகாதார பராமரிப்பு",
            others: "பிற திட்டங்கள்"
        },
        states: {
            andhra_pradesh: "ஆந்திரப் பிரதேசம்",
            arunachal_pradesh: "அருணாச்சலப் பிரதேசம்",
            assam: "அசாம்",
            bihar: "பீகார்",
            chhattisgarh: "சத்தீஸ்கர்",
            goa: "கோவா",
            gujarat: "குஜராத்",
            haryana: "ஹரியானா",
            himachal_pradesh: "இமாச்சலப் பிரதேசம்",
            jharkhand: "ஜார்கண்ட்",
            karnataka: "கர்நாடகா",
            kerala: "கேரளா",
            madhya_pradesh: "மத்தியப் பிரதேசம்",
            maharashtra: "மகாராஷ்டிரா",
            manipur: "மணிப்பூர்",
            meghalaya: "மேகாலயா",
            mizoram: "மிசோரம்",
            nagaland: "நாகாலாந்து",
            odisha: "ஒடிசா",
            punjab: "பஞ்சாப்",
            rajasthan: "ராஜஸ்தான்",
            sikkim: "சிக்கிம்",
            tamil_nadu: "தமிழ்நாடு",
            telangana: "தெலங்கானா",
            tripura: "திரிபுரா",
            uttar_pradesh: "உத்தரப் பிரதேசம்",
            uttarakhand: "உத்தரகண்ட்",
            west_bengal: "மேற்கு வங்காளம்",
            andaman_nicobar: "அந்தமான் நிக்கோபார் தீவுகள்",
            chandigarh: "சண்டிகர்",
            dadra_nagar_haveli_daman_diu: "தாத்ரா நகர் ஹவேலி தமன் தீவு",
            delhi: "டெல்லி",
            jammu_kashmir: "ஜம்மு காஷ்மீர்",
            ladakh: "லடாக்",
            lakshadweep: "லட்சத்தீவு",
            puducherry: "புதுச்சேரி"
        },
        genderOptions: {
            "": "சொல்ல விரும்பவில்லை",
            male: "ஆண்",
            female: "பெண்",
            other: "மற்றவை"
        },
        communityOptions: {
            "": "சமூகத்தைத் தேர்ந்தெடுக்கவும்",
            general: "பொது",
            obc: "ஓபிசி",
            pvtg: "பிவிடிஜி",
            sc: "எஸ்சி",
            st: "எஸ்டி",
            dnt: "டிஎன்டி"
        },
        physicallyChallengedOptions: {
            "": "விருப்பத்தைத் தேர்ந்தெடுக்கவும்",
            yes: "ஆம்",
            no: "இல்லை"
        }
    }
};
```

Sub-step 1.3: Save the file

---

#### **TASK 8: Create Application Logic (app.js)**

**Status**: [x] COMPLETED  
**Requirements**: Navigation, API calls, language handling

**STEP 1: Create app.js file**

Sub-step 1.1: Create a new file named `app.js`

Sub-step 1.2: Put the following content inside the file:
```javascript
// API Configuration
const API_ENDPOINT = 'YOUR_API_GATEWAY_URL_HERE'; // Will be updated after API Gateway deployment

// Language selection
let selectedLanguage = 'English';

// Language code mapping (ISO-639-1)
const languageCodes = {
    'English': 'en',
    'Hindi': 'hi',
    'Tamil': 'ta'
};

function selectLanguage(language) {
    selectedLanguage = language;
    localStorage.setItem('selectedLanguage', language);
    window.location.href = 'form.html';
}

function goBack() {
    window.location.href = 'index.html';
}

function goToForm() {
    window.location.href = 'form.html';
}

// Load language on form page
window.addEventListener('DOMContentLoaded', () => {
    const currentPage = window.location.pathname.split('/').pop();
    
    if (currentPage === 'form.html') {
        selectedLanguage = localStorage.getItem('selectedLanguage') || 'English';
        applyTranslations();
        setupFormSubmission();
    } else if (currentPage === 'results.html') {
        selectedLanguage = localStorage.getItem('selectedLanguage') || 'English';
        applyTranslations();
        fetchResults();
    }
});

function applyTranslations() {
    const t = translations[selectedLanguage];
    
    // Form page translations - Labels
    const formTitle = document.getElementById('form-title');
    if (formTitle) formTitle.textContent = t.formTitle;
    
    const formSubtitle = document.getElementById('form-subtitle');
    if (formSubtitle) formSubtitle.textContent = t.formSubtitle;
    
    const labelName = document.getElementById('label-name');
    if (labelName) labelName.textContent = t.labelName;
    
    const labelAge = document.getElementById('label-age');
    if (labelAge) labelAge.textContent = t.labelAge;
    
    const labelGender = document.getElementById('label-gender');
    if (labelGender) labelGender.textContent = t.labelGender;
    
    const labelState = document.getElementById('label-state');
    if (labelState) labelState.textContent = t.labelState;
    
    const labelCategory = document.getElementById('label-category');
    if (labelCategory) labelCategory.textContent = t.labelCategory;
    
    const labelCommunity = document.getElementById('label-community');
    if (labelCommunity) labelCommunity.textContent = t.labelCommunity;
    
    const labelPhysicallyChallenged = document.getElementById('label-physically-challenged');
    if (labelPhysicallyChallenged) labelPhysicallyChallenged.textContent = t.labelPhysicallyChallenged;
    
    const labelQuery = document.getElementById('label-query');
    if (labelQuery) labelQuery.textContent = t.labelQuery;
    
    const submitBtn = document.getElementById('submit-btn');
    if (submitBtn) submitBtn.textContent = t.submitBtn;
    
    // Populate State dropdown with translations
    const stateSelect = document.getElementById('state');
    if (stateSelect && t.states) {
        const currentValue = stateSelect.value;
        stateSelect.innerHTML = `<option value="">${t.statePlaceholder}</option>`;
        for (const [key, value] of Object.entries(t.states)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            stateSelect.appendChild(option);
        }
        stateSelect.value = currentValue;
    }
    
    // Populate Category dropdown with translations
    const categorySelect = document.getElementById('category');
    if (categorySelect && t.categories) {
        const currentValue = categorySelect.value;
        categorySelect.innerHTML = `<option value="">${t.categoryPlaceholder}</option>`;
        for (const [key, value] of Object.entries(t.categories)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            categorySelect.appendChild(option);
        }
        categorySelect.value = currentValue;
    }
    
    // Populate Gender dropdown with translations
    const genderSelect = document.getElementById('gender');
    if (genderSelect && t.genderOptions) {
        const currentValue = genderSelect.value;
        genderSelect.innerHTML = '';
        for (const [key, value] of Object.entries(t.genderOptions)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            genderSelect.appendChild(option);
        }
        genderSelect.value = currentValue;
    }
    
    // Populate Community dropdown with translations
    const communitySelect = document.getElementById('community');
    if (communitySelect && t.communityOptions) {
        const currentValue = communitySelect.value;
        communitySelect.innerHTML = '';
        for (const [key, value] of Object.entries(t.communityOptions)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            communitySelect.appendChild(option);
        }
        communitySelect.value = currentValue;
    }
    
    // Populate Physically Challenged dropdown with translations
    const physicallyChallengedSelect = document.getElementById('physically_challenged');
    if (physicallyChallengedSelect && t.physicallyChallengedOptions) {
        const currentValue = physicallyChallengedSelect.value;
        physicallyChallengedSelect.innerHTML = '';
        for (const [key, value] of Object.entries(t.physicallyChallengedOptions)) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = value;
            physicallyChallengedSelect.appendChild(option);
        }
        physicallyChallengedSelect.value = currentValue;
    }
    
    // Results page translations
    const resultsTitle = document.getElementById('results-title');
    if (resultsTitle) resultsTitle.textContent = t.resultsTitle;
}

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
            community: document.getElementById('community').value,
            physically_challenged: document.getElementById('physically_challenged').value,
            language: languageCodes[selectedLanguage] || 'en',
            query: document.getElementById('query').value
        };
        
        // Store form data for results page
        localStorage.setItem('formData', JSON.stringify(formData));
        
        // Navigate to results page
        window.location.href = 'results.html';
    });
}

async function fetchResults() {
    const formData = JSON.parse(localStorage.getItem('formData'));
    
    if (!formData) {
        window.location.href = 'form.html';
        return;
    }
    
    try {
        const response = await fetch(`${API_ENDPOINT}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch results');
        }
        
        const data = await response.json();
        
        // Hide loading, show results
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results-content').style.display = 'block';
        
        // Display response
        document.getElementById('response-text').innerHTML = formatResponse(data.response);
        
        // Display sources
        if (data.sources && data.sources.length > 0) {
            document.getElementById('sources-section').style.display = 'block';
            const sourcesList = document.getElementById('sources-list');
            sourcesList.innerHTML = data.sources.map(s => 
                `<li>${s.source} (Chunk ${s.chunk_id})</li>`
            ).join('');
        }
        
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error-message').style.display = 'block';
        document.getElementById('error-message').textContent = 
            'Sorry, we encountered an error. Please try again.';
    }
}

function formatResponse(text) {
    // Simple formatting: convert newlines to <br> and preserve structure
    return text.replace(/\n/g, '<br>');
}

function downloadPDF() {
    alert('PDF export feature coming soon!');
}
```

Sub-step 1.3: Save the file

**Note**: The API_ENDPOINT will be updated in TASK 10 after API Gateway is deployed.

**Important - Language Code Format**: 
- The frontend sends ISO-639-1 language codes ("en", "hi", "ta") to the backend for consistency with the ingestion pipeline
- The `languageCodes` mapping converts the user's language selection to ISO codes
- Includes fallback to "en" if selectedLanguage is undefined or unrecognized
- The RAG Orchestrator (STAGE 5) will convert ISO codes back to full language names ("English", "Hindi", "Tamil") when constructing the LLM prompt, as LLMs respond better to natural language instructions like "Respond in Hindi" rather than "Respond in hi"

---

#### **TASK 9: Create Styles (styles.css)**

**Status**: [x] COMPLETED  
**Requirements**: Responsive design for all pages

**STEP 1: Create styles.css file**

Sub-step 1.1: Create a new file named `styles.css`

Sub-step 1.2: Put the following content inside the file:
```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
}

.container {
    background: white;
    border-radius: 20px;
    padding: 40px;
    max-width: 600px;
    width: 100%;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

h1 {
    color: #333;
    text-align: center;
    margin-bottom: 10px;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 30px;
}

.language-tiles {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
    margin-top: 30px;
}

.language-tile {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px 20px;
    border-radius: 15px;
    text-align: center;
    cursor: pointer;
    transition: transform 0.3s, box-shadow 0.3s;
}

.language-tile:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.language-tile h2 {
    font-size: 24px;
    margin-bottom: 10px;
}

.language-tile p {
    font-size: 14px;
    opacity: 0.9;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    color: #333;
    font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #667eea;
}

button[type="submit"],
.back-btn,
.download-btn {
    width: 100%;
    padding: 15px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.3s;
    margin-top: 10px;
}

button[type="submit"]:hover,
.back-btn:hover,
.download-btn:hover {
    transform: translateY(-2px);
}

.back-btn {
    background: #6c757d;
    margin-top: 20px;
}

.loading {
    text-align: center;
    padding: 40px;
    color: #666;
}

.results-content {
    padding: 20px;
    background: #f8f9fa;
    border-radius: 10px;
    margin-bottom: 20px;
}

#response-text {
    line-height: 1.8;
    color: #333;
}

.sources {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 2px solid #ddd;
}

.sources h3 {
    color: #333;
    margin-bottom: 10px;
}

.sources ul {
    list-style-position: inside;
    color: #666;
}

.sources li {
    margin-bottom: 5px;
}

.error-message {
    background: #f8d7da;
    color: #721c24;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}

.button-group {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

@media (max-width: 768px) {
    .language-tiles {
        grid-template-columns: 1fr;
    }
    
    .button-group {
        grid-template-columns: 1fr;
    }
    
    .container {
        padding: 20px;
    }
}
```

Sub-step 1.3: Save the file

---

#### **TASK 10: Deploy to S3 and Configure CloudFront**

**Status**: [x] COMPLETED  
**Requirements**: Static website hosting with CDN

**STEP 1: Create frontend folder in existing S3 bucket**

Sub-step 1.1: Go to S3 console  
Sub-step 1.2: Click on the existing bucket `aicloud-bharat-schemes`  
Sub-step 1.3: Click "Create folder" button  
Sub-step 1.4: Enter folder name: `frontend/` and click "Create folder"

**STEP 2: Create frontend files locally**

Sub-step 2.1: On your local machine, create a new folder named `frontend`  
Sub-step 2.2: Inside the `frontend` folder, create these 6 files:
- `index.html` (from TASK 4)
- `form.html` (from TASK 5)
- `results.html` (from TASK 6)
- `translations.js` (from TASK 7)
- `app.js` (from TASK 8)
- `styles.css` (from TASK 9)

Sub-step 2.3: Verify all files are saved correctly

**STEP 3: Upload frontend files to S3**

Sub-step 3.1: In S3 console, navigate to `aicloud-bharat-schemes/frontend/`  
Sub-step 3.2: Click "Upload"  
Sub-step 3.3: Click "Add files" and select all 6 files from your local `frontend` folder  
Sub-step 3.4: Click "Upload"  
Sub-step 3.5: Wait for upload to complete  
Sub-step 3.6: Verify all 6 files appear in the `frontend/` folder

**STEP 4: Update bucket permissions for public access**

Sub-step 4.1: Go back to bucket root (`aicloud-bharat-schemes`)  
Sub-step 4.2: Go to "Permissions" tab  
Sub-step 4.3: Scroll to "Block public access (bucket settings)"  
Sub-step 4.4: Click "Edit"  
Sub-step 4.5: Uncheck "Block all public access" (this will reveal 4 sub-options below)  
Sub-step 4.6: You will see 4 individual options - **uncheck all 4 of them**:
   - ☐ Block public access to buckets and objects granted through new access control lists (ACLs)
   - ☐ Block public access to buckets and objects granted through any access control lists (ACLs)
   - ☐ Block public access to buckets and objects granted through new public bucket or access point policies
   - ☐ Block public and cross-account access to buckets and objects through any public bucket or access point policies
Sub-step 4.7: Click "Save changes"  
Sub-step 4.8: A warning dialog will appear - check the acknowledgment box that says "I acknowledge that the current settings might result in this bucket and the objects within becoming public"
Sub-step 4.9: Type "confirm" in the text field when prompted
Sub-step 4.10: Click "Confirm"

**Note**: We're allowing public access at the bucket level, but in STEP 5 we'll add a bucket policy that restricts public access to ONLY the `frontend/` folder. The `raw/` and `processed/` folders will remain private.

**STEP 5: Add bucket policy for frontend folder**

Sub-step 5.1: Still in "Permissions" tab, scroll to "Bucket policy"  
Sub-step 5.2: Click "Edit"  
Sub-step 5.3: Add the following policy (this allows public read access to files inside /frontend folder only):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::aicloud-bharat-schemes/frontend/*"
        }
    ]
}
```

Sub-step 5.4: Click "Save changes"

**STEP 6: Enable static website hosting**

Sub-step 6.1: Go to "Properties" tab  
Sub-step 6.2: Scroll to "Static website hosting"  
Sub-step 6.3: Click "Edit"  
Sub-step 6.4: Select "Enable"  
Sub-step 6.5: Hosting type: **Host a static website**  
Sub-step 6.6: Index document: `frontend/index.html`  
Sub-step 6.7: Error document: `frontend/index.html`  
Sub-step 6.8: Click "Save changes"  
Sub-step 6.9: Copy the "Bucket website endpoint" URL (e.g., `http://aicloud-bharat-schemes.s3-website.ap-south-1.amazonaws.com`)

**STEP 7: Create CloudFront distribution**

Sub-step 7.1: Go to CloudFront console  
Sub-step 7.2: Click "Create distribution"  
Sub-step 7.3: Distribution name: ai-schemes-frontend-Cloudfront
Sub-step 7.4: press next button
Sub-step 7.5: orgin type: choose amazon s3
Sub-step 7.6: orgin(s3orgin):http://aicloud-bharat-schemes.s3-website.ap-south-1.amazonaws.com
The "Bucket website endpoint" was copied by us on Sub-step 6.9:
Sub-step 7.7: orginpath- `/frontend`
You have TWO valid options:
OPTION 1: Origin path = BLANK (my recommendation)
CloudFront URL: https://d1234abcd.cloudfront.net/frontend/index.html
CloudFront requests from S3: 
index.html ✅
User must type /frontend/ in the URL
OPTION 2: Origin path = /frontend (your current choice)

CloudFront URL: https://d1234abcd.cloudfront.net/index.html
CloudFront requests from S3: 
index.html ✅
Cleaner URL (no /frontend/ needed)
Actually, OPTION 2 is BETTER for user experience!

Sub-step 7.8: in settings:
origin settings: leave default ()Use recommended Origin settings
cache settings: leave default ()Use recommended cache settings tailored to serve s3 content
Sub-step 7.9: press next button

Sub-step 7.10:(disable WAF)-choose Do not enable security protections
WAF costs $5/month + $1 per million requests
  - Not needed for prototype/demo evaluation
  - Your app has no sensitive data and is read-only
Sub-step 7.11: press next button
Sub-step 7.12: Review
Sub-step 7.13: click "Create Distribution" button

**Note**: Using the S3 website endpoint (instead of the bucket endpoint) is recommended by AWS because it properly handles static website routing, including serving `index.html` as the default document for directory requests.

**STEP 8: Wait for deployment**

Sub-step 8.1: Wait for distribution status to change from "Deploying" to "Enabled" (5-10 minutes)  
Sub-step 8.2: Copy the CloudFront domain name (e.g., `d1234abcd.cloudfront.net`)  
Sub-step 8.3: Save this URL - this is your permanent demo link

**STEP 9: Test the CloudFront URL**

Sub-step 9.1: Open the CloudFront URL in your browser (e.g., `https://d1234abcd.cloudfront.net`)  
Sub-step 9.2: Verify the language selection page loads  
Sub-step 9.3: Click on each language tile to verify navigation works  
Sub-step 9.4: Verify form page loads with all fields

**Note**: Using the same S3 bucket with a `frontend/` folder is simpler and more cost-effective than creating a separate bucket. The `raw/` and `processed/` folders remain private, while only the `frontend/` folder is publicly accessible via CloudFront.

---

#### **TASK 11: Test Multilingual UI**

**Status**: [x] COMPLETED  
**Requirements**: Verify all 3 languages work correctly

**STEP 1: Test English language**

Sub-step 1.1: Open CloudFront URL  
Sub-step 1.2: Click "English" tile  
Sub-step 1.3: Verify all form labels are in English  
Sub-step 1.4: Verify state dropdown shows all 36 Indian states and UTs  
Sub-step 1.5: Verify category dropdown shows English names:
- Education & Skills
- Solar Subsidy
- Startup and Self Employment
- Housing Aid
- Water & Sanitation
- Agriculture
- Health Care
- Other Schemes

Sub-step 1.6: Verify income dropdown includes "Unemployed" option  
Sub-step 1.7: Fill out the form and verify validation works

**STEP 2: Test Hindi language**

Sub-step 2.1: Go back to home page  
Sub-step 2.2: Click "हिंदी" tile  
Sub-step 2.3: Verify all form labels are in Hindi  
Sub-step 2.4: Verify state dropdown label shows "राज्य *"  
Sub-step 2.5: Verify category dropdown shows Hindi names:
- शिक्षा और कौशल
- सौर सब्सिडी
- स्टार्टअप और स्वरोजगार
- आवास सहायता
- जल और स्वच्छता
- कृषि
- स्वास्थ्य देखभाल
- अन्य योजनाएं

Sub-step 2.6: Fill out the form and verify validation works

**STEP 3: Test Tamil language**

Sub-step 3.1: Go back to home page  
Sub-step 3.2: Click "தமிழ்" tile  
Sub-step 3.3: Verify all form labels are in Tamil  
Sub-step 3.4: Verify state dropdown label shows "மாநிலம் *"  
Sub-step 3.5: Verify category dropdown shows Tamil names:
- கல்வி மற்றும் திறன்கள்
- சூரிய மானியம்
- தொடக்க மற்றும் சுயதொழில்
- வீட்டு உதவி
- நீர் மற்றும் சுகாதாரம்
- விவசாயம்
- சுகாதார பராமரிப்பு
- பிற திட்டங்கள்

Sub-step 3.6: Fill out the form and verify validation works
- கல்வி கடன்
- தொடக்க ஆதரவு
- ஜல் ஜீவன் திட்டம்

Sub-step 3.5: Fill out the form and verify validation works

**STEP 4: Test responsive design**

Sub-step 4.1: Open browser developer tools (F12)  
Sub-step 4.2: Toggle device toolbar (Ctrl+Shift+M)  
Sub-step 4.3: Test on mobile view (375px width)  
Sub-step 4.4: Verify language tiles stack vertically  
Sub-step 4.5: Verify form is readable and usable  
Sub-step 4.6: Test on tablet view (768px width)  
Sub-step 4.7: Verify layout adapts correctly

**STEP 5: Test form validation**

Sub-step 5.1: Try submitting empty form - should show validation errors  
Sub-step 5.2: Enter age < 1 - should show error  
Sub-step 5.3: Enter age > 120 - should show error  
Sub-step 5.4: Leave category unselected - should show error  
Sub-step 5.5: Fill all required fields - should navigate to results page

**STEP 6: Verify PDF export button**

Sub-step 6.1: Navigate to results page  
Sub-step 6.2: Click "Download as PDF" button  
Sub-step 6.3: Verify alert shows "PDF export feature coming soon!"

---

### STAGE 3 — ChromaDB Vector Service on EC2 (P0 Critical)

**Priority**: Highest  
**Goal**: ChromaDB API running on EC2  
**Deliverable**: FastAPI service with 8 endpoints: /add, /search, /health, /delete, /delete_all, /rebuild, /stats, /collections

**Migration Note**: This stage was migrated from FAISS to ChromaDB for simpler setup and better debugging. ChromaDB provides automatic persistence, built-in metadata filtering, and human-readable SQLite storage. See CHROMADB_MIGRATION_GUIDE.md for details.

---

#### **TASK 12: Launch EC2 Instance for ChromaDB Service**

**Status**: [x] COMPLETED  
**Requirements**: EC2 t3.micro instance with Ubuntu 24.04 LTS

**STEP 1: Navigate to EC2 console**

Sub-step 1.1: Open AWS Console  
Sub-step 1.2: Verify region is **ap-south-1** (Mumbai)  
Sub-step 1.3: Search for "EC2" in the search bar  
Sub-step 1.4: Click on "EC2" service

**STEP 2: Launch instance**

Sub-step 2.1: Click "Launch instance" button  
Sub-step 2.2: Enter instance name: `chroma-vector-service`  
Sub-step 2.3: Under "Application and OS Images", select **Ubuntu**  
Sub-step 2.4: Select **Ubuntu Server 24.04 LTS (HVM), SSD Volume Type**  
Sub-step 2.5: Verify architecture is **64-bit (x86)**

**STEP 3: Choose instance type**

Sub-step 3.1: Under "Instance type", select **t3.micro**  
Sub-step 3.2: Verify specifications: 1 vCPU, 1 GB RAM  
Sub-step 3.3: Verify "Free tier eligible" label is visible

**STEP 4: Create key pair for SSH access**

Sub-step 4.1: Under "Key pair (login)", click "Create new key pair"  
Sub-step 4.2: Enter key pair name: `chroma-service-key`  
Sub-step 4.3: Key pair type: **RSA**  
Sub-step 4.4: Private key file format: **. pem** (for OpenSSH)  
Sub-step 4.5: Click "Create key pair"  
Sub-step 4.6: Save the downloaded `.pem` file securely (you'll need it for SSH access)

**STEP 5: Configure network settings**

Sub-step 5.1: Under "Network settings", click "Edit"  
Sub-step 5.2: VPC: Leave as default  
Sub-step 5.3: Subnet: Leave as default (no preference)  
Sub-step 5.4: Auto-assign public IP: **Enable**  
Sub-step 5.5: Under "Firewall (security groups)", select "Create security group"  
Sub-step 5.6: Security group name: `chroma-service-sg`  
Sub-step 5.7: Description: "Security group for ChromaDB FastAPI service"  
Sub-step 5.8: Add inbound rule 1:
- Type: **SSH**
- Protocol: TCP
- Port: 22
- Source: **My IP** (for SSH access from your computer)

Sub-step 5.9: Add inbound rule 2:
- Type: **Custom TCP**
- Protocol: TCP
- Port: 8000
- Source: **Anywhere (0.0.0.0/0)** (temporary - will restrict to Lambda later)

**STEP 6: Configure storage**

Sub-step 6.1: Under "Configure storage", set root volume size: **8 GB**  
Sub-step 6.2: Volume type: **gp3** (General Purpose SSD)  
Sub-step 6.3: Verify "Delete on termination" is checked  
Sub-step 6.4: Encryption: Leave as default (not encrypted for prototype)

**STEP 7: Review and launch**

Sub-step 7.1: Expand "Advanced details" (optional)  
Sub-step 7.2: Under "Number of instances", verify: **1**  
Sub-step 7.3: Click "Launch instance" button  
Sub-step 7.4: Wait for "Successfully initiated launch of instance" message  
Sub-step 7.5: Click "View all instances"

**STEP 8: Wait for instance to be ready**

Sub-step 8.1: Find your instance named `chroma-vector-service`  
Sub-step 8.2: Wait for "Instance state" to change from "Pending" to "Running" (1-2 minutes)  
Sub-step 8.3: Wait for "Status check" to show "2/2 checks passed" (2-3 minutes)  
Sub-step 8.4: Copy the "Public IPv4 address" (e.g., `13.232.45.67`) - you'll need this for SSH

**STEP 9: Test SSH connection**

Sub-step 9.1: Open your terminal (Command Prompt, PowerShell, or Git Bash on Windows)  
Sub-step 9.2: Navigate to the directory where you saved the `.pem` file  
Sub-step 9.3: Set correct permissions on the key file (Linux/Mac only):
```bash
chmod 400 chroma-service-key.pem
```

Sub-step 9.4: Connect via SSH:
```bash
ssh -i chroma-service-key.pem ubuntu@<PUBLIC_IP>
```
Replace `<PUBLIC_IP>` with the actual public IP from Sub-step 8.4

Sub-step 9.5: Type "yes" when prompted about authenticity  
Sub-step 9.6: Verify you see the Ubuntu welcome message  
Sub-step 9.7: You should now be logged into the EC2 instance

**Note**: Keep this SSH session open - you'll use it in the next tasks.

---

#### **TASK 13: Install Python and Dependencies on EC2**

**Status**: [ ]  
**Requirements**: Python 3.12 (pre-installed), pip, and system dependencies

**STEP 1: Update system packages**

Sub-step 1.1: In your SSH session, run:
```bash
sudo apt update
```

Sub-step 1.2: Wait for package list to update (30 seconds)  
Sub-step 1.3: Run:
```bash
sudo apt upgrade -y
```

Sub-step 1.4: Wait for packages to upgrade (2-3 minutes)

**STEP 2: Verify Python 3.12 (pre-installed on Ubuntu 24.04)**

Sub-step 2.1: Check Python version:
```bash
python3 --version
```

Sub-step 2.2: Expected output: `Python 3.12.3` (or similar 3.12.x)

Sub-step 2.3: Install python3-venv package:
```bash
sudo apt install python3.12-venv -y
```

**STEP 3: Install system dependencies**

Sub-step 3.1: Install build tools:
```bash
sudo apt install build-essential -y
```

Sub-step 3.2: Wait for installation to complete (1-2 minutes)

**STEP 4: Create application directory**

Sub-step 4.1: Create directory for ChromaDB service:
```bash
sudo mkdir -p /opt/chroma-service
```

Sub-step 4.2: Create data directory for persistent storage:
```bash
sudo mkdir -p /data/chroma
```

Sub-step 4.3: Set ownership to ubuntu user:
```bash
sudo chown -R ubuntu:ubuntu /opt/chroma-service /data
```

Sub-step 4.4: Navigate to application directory:
```bash
cd /opt/chroma-service
```

**STEP 5: Create Python virtual environment**

Sub-step 5.1: Create virtual environment:
```bash
python3 -m venv venv
```

Sub-step 5.2: Activate virtual environment:
```bash
source venv/bin/activate
```

Sub-step 5.3: Verify activation - prompt should show `(venv)` prefix  
Sub-step 5.4: Upgrade pip in virtual environment:
```bash
pip install --upgrade pip
```

---

#### **TASK 14: Install ChromaDB and FastAPI Dependencies**

**Status**: [ ]  
**Requirements**: ChromaDB, FastAPI, Uvicorn, and supporting libraries

**STEP 1: Install ChromaDB**

Sub-step 1.1: Ensure virtual environment is activated (you should see `(venv)` in prompt)  
Sub-step 1.2: Install ChromaDB:
```bash
pip install chromadb==0.5.2
```

Sub-step 1.3: Wait for installation (2-3 minutes)  
Sub-step 1.4: Verify ChromaDB installation:
```bash
python -c "import chromadb; print(f'ChromaDB version: {chromadb.__version__}')"
```

Sub-step 1.5: Expected output: `ChromaDB version: 0.5.2`

**STEP 2: Install FastAPI and Uvicorn**

Sub-step 2.1: Install FastAPI:
```bash
pip install fastapi==0.104.1
```

Sub-step 2.2: Install Uvicorn (ASGI server):
```bash
pip install "uvicorn[standard]"==0.24.0
```

Sub-step 2.3: Verify installations:
```bash
python -c "import fastapi; import uvicorn; print('FastAPI and Uvicorn installed successfully')"
```

**STEP 3: Install supporting libraries**

Sub-step 3.1: Install Pydantic for data validation:
```bash
pip install pydantic==2.5.0
```

Sub-step 3.2: Install NumPy:
```bash
pip install numpy==1.24.3
```

Sub-step 3.3: Install Python-dotenv for environment variables:
```bash
pip install python-dotenv==1.0.0
```

**STEP 4: Create requirements.txt file**

Sub-step 4.1: Create requirements.txt:
```bash
cat > requirements.txt << 'EOF'
chromadb==0.5.2
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
numpy==1.24.3
python-dotenv==1.0.0
EOF
```

Sub-step 4.2: Verify file was created:
```bash
cat requirements.txt
```

**STEP 5: Verify all installations**

Sub-step 5.1: Run verification script:
```bash
python << 'EOF'
import chromadb
import fastapi
import uvicorn
import pydantic
import numpy as np

print("✅ All dependencies installed successfully!")
print(f"   ChromaDB: {chromadb.__version__}")
print(f"   FastAPI: {fastapi.__version__}")
print(f"   Uvicorn: {uvicorn.__version__}")
print(f"   Pydantic: {pydantic.__version__}")
print(f"   NumPy: {np.__version__}")
EOF
```

Sub-step 5.2: Verify all packages show ✅ checkmark

---

#### **TASK 15: Create ChromaDB FastAPI Application**

**Status**: [ ]  
**Requirements**: FastAPI app with /add, /search, /health, /delete, /delete_all, /rebuild, /stats, /collections endpoints

**STEP 1: Create main application file**

Sub-step 1.1: Ensure you're in `/opt/chroma-service` directory  
Sub-step 1.2: Create `app.py` file:
```bash
nano app.py
```

Sub-step 1.3: Paste the following code:
```python
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
import numpy as np
import os
import uuid
from datetime import datetime

# Configuration
API_KEY = os.getenv("CHROMA_API_KEY", "dev-api-key-change-in-production")
CHROMA_PATH = "/data/chroma"
COLLECTION_NAME = "government_schemes"
DIMENSION = 1024  # Titan Embeddings V2 dimension

# Initialize FastAPI app
app = FastAPI(title="ChromaDB Vector Service", version="1.0.0")

# Global variables
chroma_client = None
collection = None

# Pydantic models
class Document(BaseModel):
    embedding: List[float] = Field(..., min_length=1024, max_length=1024)
    text: str = Field(..., min_length=1)
    metadata: Dict[str, Any]  # Must include: scheme_name, category, state, language

class AddDocumentsRequest(BaseModel):
    documents: List[Document]

class SearchRequest(BaseModel):
    query_embedding: List[float] = Field(..., min_length=1024, max_length=1024)
    top_k: int = Field(default=5, ge=1, le=20)
    category_filter: Optional[str] = None
    state_filter: Optional[str] = None
    gender_filter: Optional[str] = None  # "male", "female", "other", "any"
    age_filter: Optional[int] = None  # User's age for eligibility checking
    community_filter: Optional[str] = None  # "general", "obc", "pvtg", "sc", "st", "dnt", "any"
    physically_challenged_filter: Optional[str] = None  # "yes", "no", "any"

class SearchResult(BaseModel):
    doc_id: str  # UUID
    score: float
    text: str
    metadata: Dict[str, Any]

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_docs: int

class DeleteRequest(BaseModel):
    ids: Optional[List[str]] = None
    scheme_name: Optional[str] = None

# Helper functions
def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

def initialize_chroma():
    """Initialize ChromaDB client and collection"""
    global chroma_client, collection
    
    try:
        chroma_client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        collection = chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}  # Cosine similarity
        )
        
        print(f"✅ Initialized ChromaDB collection: {COLLECTION_NAME}")
        print(f"   Total documents: {collection.count()}")
    except Exception as e:
        print(f"❌ Error initializing ChromaDB: {e}")
        raise

def normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize metadata for consistent filtering"""
    normalized = {}
    
    for key, value in metadata.items():
        if key in ['category', 'state', 'eligible_gender', 'language', 'eligible_physically_challenged']:
            # Normalize to lowercase
            normalized[key] = value.lower() if isinstance(value, str) else value
        elif key == 'eligible_community':
            # Convert array to comma-separated string
            if isinstance(value, list):
                normalized[key] = ','.join([str(v).lower() for v in value])
            else:
                normalized[key] = str(value).lower()
        elif key in ['eligible_minage', 'eligible_maxage']:
            # Ensure integers
            normalized[key] = int(value) if value is not None else (0 if key == 'eligible_minage' else 120)
        else:
            normalized[key] = value
    
    return normalized

def denormalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Convert metadata back to API format (arrays for community)"""
    denormalized = metadata.copy()
    
    if 'eligible_community' in denormalized:
        community_str = denormalized['eligible_community']
        if isinstance(community_str, str) and ',' in community_str:
            denormalized['eligible_community'] = community_str.split(',')
    
    return denormalized

# API Endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize ChromaDB on startup"""
    initialize_chroma()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_vectors": collection.count() if collection else 0,
        "dimension": DIMENSION,
        "collection_name": COLLECTION_NAME,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/add")
async def add_documents(request: AddDocumentsRequest, x_api_key: str = Header(...)):
    """Add documents with embeddings to ChromaDB"""
    verify_api_key(x_api_key)
    
    try:
        # Validate required metadata fields
        for doc in request.documents:
            if 'scheme_name' not in doc.metadata:
                raise HTTPException(status_code=400, detail="metadata must include 'scheme_name'")
            if 'category' not in doc.metadata:
                raise HTTPException(status_code=400, detail="metadata must include 'category'")
            if 'state' not in doc.metadata:
                raise HTTPException(status_code=400, detail="metadata must include 'state'")
            if 'language' not in doc.metadata:
                raise HTTPException(status_code=400, detail="metadata must include 'language'")
        
        # Validate embedding dimensions
        for doc in request.documents:
            if len(doc.embedding) != DIMENSION:
                raise HTTPException(
                    status_code=400,
                    detail=f"Embedding dimension must be {DIMENSION}, got {len(doc.embedding)}"
                )
        
        # Prepare data for ChromaDB
        ids = [str(uuid.uuid4()) for _ in request.documents]
        embeddings = [doc.embedding for doc in request.documents]
        documents = [doc.text for doc in request.documents]
        metadatas = [normalize_metadata(doc.metadata) for doc in request.documents]
        
        # Add to collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        return {
            "status": "success",
            "added_count": len(request.documents),
            "added_ids": ids,
            "total_vectors": collection.count()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding documents: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest, x_api_key: str = Header(...)):
    """Search for similar vectors with eligibility filtering"""
    verify_api_key(x_api_key)
    
    try:
        if collection.count() == 0:
            return SearchResponse(results=[], total_docs=0)
        
        # Build where clause for ChromaDB native filtering
        where_clause = {}
        
        if request.category_filter:
            where_clause['category'] = request.category_filter.lower()
        
        if request.state_filter:
            # State filter: match exact state or "all"
            # Note: ChromaDB doesn't support OR, so we'll post-filter
            pass
        
        if request.gender_filter and request.gender_filter != 'any':
            # Gender filter: match exact gender or "any"
            # Note: ChromaDB doesn't support OR, so we'll post-filter
            pass
        
        # For community and physically_challenged filters, we need post-processing
        # Retrieve more results than requested
        needs_post_filter = (request.community_filter or request.physically_challenged_filter or 
                            request.age_filter is not None)
        retrieve_k = request.top_k * 3 if needs_post_filter else request.top_k
        retrieve_k = min(retrieve_k, collection.count())
        
        # Query ChromaDB
        results = collection.query(
            query_embeddings=[request.query_embedding],
            n_results=retrieve_k,
            where=where_clause if where_clause else None
        )
        
        # Process results
        search_results = []
        
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                doc_id = results['ids'][0][i]
                distance = results['distances'][0][i]
                text = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                
                # Convert distance to similarity score (0-1 range)
                # ChromaDB cosine distance: 0 = identical, 2 = opposite
                score = 1.0 - (distance / 2.0)
                
                # Post-filter for state (exact match or "all")
                if request.state_filter:
                    state = metadata.get('state', 'all')
                    if state != request.state_filter.lower() and state != 'all':
                        continue
                
                # Post-filter for gender (exact match or "any")
                if request.gender_filter and request.gender_filter != 'any':
                    eligible_gender = metadata.get('eligible_gender', 'any')
                    if eligible_gender != 'any' and eligible_gender != request.gender_filter.lower():
                        continue
                
                # Post-filter for age range
                if request.age_filter is not None:
                    eligible_minage = metadata.get('eligible_minage', 0)
                    eligible_maxage = metadata.get('eligible_maxage', 120)
                    if not (eligible_minage <= request.age_filter <= eligible_maxage):
                        continue
                
                # Post-filter for community (array contains)
                if request.community_filter and request.community_filter != 'any':
                    eligible_community = metadata.get('eligible_community', 'any')
                    if isinstance(eligible_community, str):
                        community_list = eligible_community.split(',')
                    else:
                        community_list = [eligible_community]
                    
                    if 'any' not in community_list and request.community_filter.lower() not in community_list:
                        continue
                
                # Post-filter for physically challenged
                if request.physically_challenged_filter and request.physically_challenged_filter != 'any':
                    eligible_pc = metadata.get('eligible_physically_challenged', 'any')
                    if eligible_pc != 'any' and eligible_pc != request.physically_challenged_filter.lower():
                        continue
                
                # Denormalize metadata for API response
                denormalized_meta = denormalize_metadata(metadata)
                
                search_results.append(SearchResult(
                    doc_id=doc_id,
                    score=score,
                    text=text,
                    metadata=denormalized_meta
                ))
        
        # Return top_k results after filtering
        return SearchResponse(
            results=search_results[:request.top_k],
            total_docs=collection.count()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")

@app.post("/delete")
async def delete_documents(request: DeleteRequest, x_api_key: str = Header(...)):
    """Delete documents by IDs or scheme name"""
    verify_api_key(x_api_key)
    
    try:
        if request.ids:
            # Delete by IDs
            collection.delete(ids=request.ids)
            return {
                "status": "success",
                "message": f"Deleted {len(request.ids)} documents",
                "deleted_ids": request.ids
            }
        elif request.scheme_name:
            # Delete by scheme name
            collection.delete(where={"scheme_name": request.scheme_name.lower()})
            return {
                "status": "success",
                "message": f"Deleted all documents for scheme: {request.scheme_name}"
            }
        else:
            raise HTTPException(status_code=400, detail="Must provide either 'ids' or 'scheme_name'")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")

@app.post("/delete_all")
async def delete_all(x_api_key: str = Header(...)):
    """Delete entire collection and recreate it"""
    verify_api_key(x_api_key)
    
    try:
        global collection
        
        # Delete collection
        chroma_client.delete_collection(name=COLLECTION_NAME)
        
        # Recreate collection
        collection = chroma_client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        return {
            "status": "success",
            "message": "Collection deleted and recreated",
            "total_vectors": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting collection: {str(e)}")

@app.post("/rebuild")
async def rebuild_collection(x_api_key: str = Header(...)):
    """Rebuild ChromaDB collection by reinitializing"""
    verify_api_key(x_api_key)
    
    try:
        old_count = collection.count() if collection else 0
        initialize_chroma()
        new_count = collection.count() if collection else 0
        
        return {
            "status": "success",
            "message": "Collection rebuilt",
            "old_vector_count": old_count,
            "new_vector_count": new_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rebuilding collection: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get detailed statistics about the ChromaDB collection (no auth required for debugging)"""
    try:
        # Get all documents to compute stats
        all_docs = collection.get()
        
        # Category distribution
        category_counts = {}
        state_counts = {}
        gender_counts = {}
        community_counts = {}
        physically_challenged_counts = {}
        language_counts = {}
        
        if all_docs['metadatas']:
            for metadata in all_docs['metadatas']:
                category = metadata.get('category', 'unknown')
                state = metadata.get('state', 'unknown')
                gender = metadata.get('eligible_gender', 'any')
                community = metadata.get('eligible_community', 'any')
                physically_challenged = metadata.get('eligible_physically_challenged', 'any')
                language = metadata.get('language', 'en')
                
                category_counts[category] = category_counts.get(category, 0) + 1
                state_counts[state] = state_counts.get(state, 0) + 1
                gender_counts[gender] = gender_counts.get(gender, 0) + 1
                language_counts[language] = language_counts.get(language, 0) + 1
                physically_challenged_counts[physically_challenged] = physically_challenged_counts.get(physically_challenged, 0) + 1
                
                if isinstance(community, str):
                    community_list = community.split(',')
                else:
                    community_list = [community]
                
                for comm in community_list:
                    community_counts[comm] = community_counts.get(comm, 0) + 1
        
        return {
            "status": "healthy",
            "collection_info": {
                "name": COLLECTION_NAME,
                "total_vectors": collection.count(),
                "dimension": DIMENSION,
                "distance_metric": "cosine"
            },
            "storage": {
                "persist_directory": CHROMA_PATH,
                "backend": "SQLite"
            },
            "metadata_stats": {
                "total_documents": len(all_docs['ids']) if all_docs['ids'] else 0,
                "categories": category_counts,
                "states": state_counts,
                "eligible_genders": gender_counts,
                "eligible_communities": community_counts,
                "eligible_physically_challenged": physically_challenged_counts,
                "languages": language_counts
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.get("/collections")
async def list_collections():
    """List all collections (no auth required for debugging)"""
    try:
        collections = chroma_client.list_collections()
        return {
            "status": "success",
            "collections": [{"name": c.name, "count": c.count()} for c in collections],
            "total_collections": len(collections)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing collections: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Sub-step 1.4: Press `Ctrl+X`, then `Y`, then `Enter` to save and exit

**STEP 2: Create environment file**

Sub-step 2.1: Create `.env` file:
```bash
nano .env
```

Sub-step 2.2: Add configuration:
```
CHROMA_API_KEY=my-super-secret-key-54321
```

Sub-step 2.3: Press `Ctrl+X`, then `Y`, then `Enter` to save

**STEP 3: Test the application**

Sub-step 3.1: Start the FastAPI server:
```bash
python app.py
```

Sub-step 3.2: Verify you see output like:
```
✅ Initialized ChromaDB collection: government_schemes
   Total documents: 0
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Sub-step 3.3: Open a NEW terminal window (keep the server running)  
Sub-step 3.4: SSH into the EC2 instance again (same command as before)  
Sub-step 3.5: Test health endpoint:
```bash
curl http://localhost:8000/health
```

Sub-step 3.6: Expected output:
```json
{"status":"healthy","total_vectors":0,"dimension":1024,"collection_name":"government_schemes","timestamp":"2026-03-07T..."}
```

Sub-step 3.7: Go back to the first terminal and press `Ctrl+C` to stop the server

---

#### **TASK 16: Create Systemd Service for Auto-Start**

**Status**: [ ]  
**Requirements**: Systemd service to run ChromaDB API on boot

**STEP 1: Create systemd service file**

Sub-step 1.1: Create service file:
```bash
sudo nano /etc/systemd/system/chroma-service.service
```

Sub-step 1.2: Paste the following content:
```ini
[Unit]
Description=ChromaDB Vector Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/chroma-service
Environment="PATH=/opt/chroma-service/venv/bin"
EnvironmentFile=/opt/chroma-service/.env
ExecStart=/opt/chroma-service/venv/bin/python /opt/chroma-service/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Sub-step 1.3: Press `Ctrl+X`, then `Y`, then `Enter` to save

**STEP 2: Enable and start the service**

Sub-step 2.1: Reload systemd daemon:
```bash
sudo systemctl daemon-reload
```

Sub-step 2.2: Enable service to start on boot:
```bash
sudo systemctl enable chroma-service
```

Sub-step 2.3: Start the service:
```bash
sudo systemctl start chroma-service
```

Sub-step 2.4: Check service status:
```bash
sudo systemctl status chroma-service
```

Sub-step 2.5: Verify output shows "active (running)" in green

**STEP 3: Test the service**

Sub-step 3.1: Test health endpoint:
```bash
curl http://localhost:8000/health
```

Sub-step 3.2: Verify JSON response with "status": "healthy"

**STEP 4: Test service persistence**

Sub-step 4.1: Reboot the EC2 instance:
```bash
sudo reboot
```

Sub-step 4.2: Wait 2 minutes for instance to restart  
Sub-step 4.3: SSH back into the instance  
Sub-step 4.4: Check if service is running:
```bash
sudo systemctl status chroma-service
```

Sub-step 4.5: Verify service is "active (running)"  
Sub-step 4.6: Test health endpoint again:
```bash
curl http://localhost:8000/health
```

---

#### **TASK 17: Test ChromaDB API Endpoints**

**Status**: [ ]  
**Requirements**: Verify all 8 endpoints work correctly

**STEP 1: Test /health endpoint**

Sub-step 1.1: SSH into EC2 instance  
Sub-step 1.2: Test health check:
```bash
curl http://localhost:8000/health
```

Sub-step 1.3: Verify response shows:
- "status": "healthy"
- "total_vectors": 0
- "dimension": 1024
- "collection_name": "government_schemes"

**STEP 2: Test /add endpoint**

Sub-step 2.1: Create test data file:
```bash
cat > test_add.json << 'EOF'
{
  "documents": [
    {
      "embedding": [0.1, 0.2, 0.3, ... (1024 values total)],
      "metadata": {
        "scheme_name": "PM Kisan Samman Nidhi",
        "category": "agriculture",
        "state": "all",
        "content": "Financial support to farmers"
      }
    }
  ]
}
EOF
```

Note: For testing, you'll need to generate a proper 1024-dimensional embedding. For now, we'll create a simple test script.

Sub-step 2.2: Create Python test script:
```bash
cat > test_api.py << 'EOF'
import requests
import numpy as np
import json

API_KEY = "my-super-secret-key-54321"
BASE_URL = "http://localhost:8000"

headers = {"X-API-Key": API_KEY}

# Test 1: Add documents with eligibility metadata
print("Test 1: Adding documents with eligibility metadata...")
embedding1 = np.random.rand(1024).tolist()
embedding2 = np.random.rand(1024).tolist()

add_payload = {
    "documents": [
        {
            "embedding": embedding1,
            "text": "PM Kisan Samman Nidhi provides financial support of Rs 6000 per year to farmers.",
            "metadata": {
                "scheme_name": "PM Kisan Samman Nidhi",
                "category": "agriculture",
                "state": "all",
                "language": "en",
                "eligible_gender": "any",
                "eligible_minage": 18,
                "eligible_maxage": 70,
                "eligible_community": ["general", "obc", "sc", "st"],
                "eligible_physically_challenged": "any",
                "chunk_index": 0,
                "source_doc": "pm_kisan_guidelines.pdf"
            }
        },
        {
            "embedding": embedding2,
            "text": "Pradhan Mantri Awas Yojana provides housing assistance to women.",
            "metadata": {
                "scheme_name": "PM Awas Yojana",
                "category": "housing_aid",
                "state": "all",
                "language": "en",
                "eligible_gender": "female",
                "eligible_minage": 21,
                "eligible_maxage": 55,
                "eligible_community": ["any"],
                "eligible_physically_challenged": "any",
                "chunk_index": 0,
                "source_doc": "pmay_guidelines.pdf"
            }
        }
    ]
}

response = requests.post(f"{BASE_URL}/add", json=add_payload, headers=headers)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {json.dumps(result, indent=2)}")
print(f"Added IDs: {result.get('added_ids', [])}\n")

# Test 2: Search without filters
print("Test 2: Searching without filters...")
search_payload = {
    "query_embedding": embedding1,
    "top_k": 5
}

response = requests.post(f"{BASE_URL}/search", json=search_payload, headers=headers)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Found {len(result['results'])} results")
if result['results']:
    print(f"Top result score: {result['results'][0]['score']:.4f}")
    print(f"Top result text: {result['results'][0]['text'][:80]}...")
print()

# Test 3: Search with category filter
print("Test 3: Searching with category filter (agriculture)...")
search_payload["category_filter"] = "agriculture"

response = requests.post(f"{BASE_URL}/search", json=search_payload, headers=headers)
result = response.json()
print(f"Found {len(result['results'])} results")
for r in result['results']:
    print(f"  - {r['metadata']['scheme_name']} (category: {r['metadata']['category']})")
print()

# Test 4: Search with gender filter
print("Test 4: Searching with gender filter (female)...")
search_payload = {
    "query_embedding": embedding2,
    "top_k": 5,
    "gender_filter": "female"
}

response = requests.post(f"{BASE_URL}/search", json=search_payload, headers=headers)
result = response.json()
print(f"Found {len(result['results'])} results")
for r in result['results']:
    print(f"  - {r['metadata']['scheme_name']} (eligible_gender: {r['metadata']['eligible_gender']})")
print()

# Test 5: Search with age filter
print("Test 5: Searching with age filter (age=25)...")
search_payload = {
    "query_embedding": embedding1,
    "top_k": 5,
    "age_filter": 25
}

response = requests.post(f"{BASE_URL}/search", json=search_payload, headers=headers)
result = response.json()
print(f"Found {len(result['results'])} results")
for r in result['results']:
    print(f"  - {r['metadata']['scheme_name']} (age range: {r['metadata']['eligible_minage']}-{r['metadata']['eligible_maxage']})")
print()

# Test 6: Search with community filter
print("Test 6: Searching with community filter (sc)...")
search_payload = {
    "query_embedding": embedding1,
    "top_k": 5,
    "community_filter": "sc"
}

response = requests.post(f"{BASE_URL}/search", json=search_payload, headers=headers)
result = response.json()
print(f"Found {len(result['results'])} results")
for r in result['results']:
    print(f"  - {r['metadata']['scheme_name']} (eligible_community: {r['metadata']['eligible_community']})")
print()

# Test 7: Search with physically challenged filter
print("Test 7: Searching with physically challenged filter (yes)...")
search_payload = {
    "query_embedding": embedding1,
    "top_k": 5,
    "physically_challenged_filter": "yes"
}

response = requests.post(f"{BASE_URL}/search", json=search_payload, headers=headers)
result = response.json()
print(f"Found {len(result['results'])} results")
for r in result['results']:
    print(f"  - {r['metadata']['scheme_name']} (eligible_physically_challenged: {r['metadata']['eligible_physically_challenged']})")
print()

# Test 8: Stats endpoint
print("Test 8: Stats endpoint...")
response = requests.get(f"{BASE_URL}/stats")
print(f"Status: {response.status_code}")
stats = response.json()
print(f"Total documents: {stats['metadata_stats']['total_documents']}")
print(f"Categories: {stats['metadata_stats']['categories']}")
print(f"Eligible genders: {stats['metadata_stats']['eligible_genders']}")
print(f"Eligible communities: {stats['metadata_stats']['eligible_communities']}")
print(f"Eligible physically challenged: {stats['metadata_stats']['eligible_physically_challenged']}")
print()

# Test 9: Rebuild endpoint
print("Test 9: Rebuild endpoint (reload from disk)...")
response = requests.post(f"{BASE_URL}/rebuild", headers=headers)
print(f"Status: {response.status_code}")
result = response.json()
print(f"Response: {json.dumps(result, indent=2)}")
print()

# Test 10: Health check
print("Test 10: Health check...")
response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
EOF
```

Sub-step 2.3: Install requests library:
```bash
source /opt/chroma-service/venv/bin/activate
pip install requests
```

Sub-step 2.4: Run test script:
```bash
python test_api.py
```

Sub-step 2.5: Verify all tests pass with status code 200

**STEP 3: Test /stats endpoint (debugging)**

Sub-step 3.1: Test stats endpoint (no API key required):
```bash
curl http://localhost:8000/stats
```

Sub-step 3.2: Verify response shows:
- "index_info": total_vectors, dimension, index_type, metric
- "storage": index_file_size_bytes, metadata_file_size_bytes, total_size_mb
- "metadata_stats": total_documents, next_doc_id, categories (breakdown by category), states (breakdown by state)

Sub-step 3.3: Example expected output:
```json
{
  "status": "healthy",
  "index_info": {
    "total_vectors": 1,
    "dimension": 1024,
    "index_type": "IndexFlatIP",
    "metric": "Inner Product (Cosine Similarity with normalized vectors)"
  },
  "storage": {
    "index_file_size_bytes": 4096,
    "metadata_file_size_bytes": 256,
    "total_size_mb": 0.00
  },
  "metadata_stats": {
    "total_documents": 1,
    "next_doc_id": 1,
    "categories": {
      "agriculture": 1
    },
    "states": {
      "all": 1
    }
  },
  "timestamp": "2026-03-05T..."
}
```

Sub-step 3.4: Verify category and state breakdowns are correct

**STEP 4: Test from external access**

Sub-step 4.1: From your local computer, test the public endpoint  
Sub-step 4.2: Replace `<PUBLIC_IP>` with your EC2 public IP:
```bash
curl http://<PUBLIC_IP>:8000/health
```

Sub-step 4.3: Verify you get a JSON response (confirms port 8000 is accessible)  
Sub-step 4.4: Test stats endpoint externally:
```bash
curl http://<PUBLIC_IP>:8000/stats
```

Sub-step 4.5: Verify stats response is accessible

**STEP 5: Document the API endpoint**

Sub-step 5.1: EC2 Public IP: 65.0.91.246  
Sub-step 5.2: API Key: my-super-secret-key-54321  
Sub-step 5.3: ChromaDB API URL: http://65.0.91.246:8000

**Note**: The ChromaDB service is now ready! In STAGE 4, Lambda functions will call these endpoints to store and retrieve vectors.

---

### STAGE 4 — Ingestion Pipeline (P0 Critical)

**Priority**: Highest  
**Goal**: PDF → chunks → embeddings → ChromaDB  
**Deliverable**: S3-triggered Lambda that processes PDFs and stores vectors in ChromaDB

**WSL Setup Note**: All STAGE 4 tasks should be run in WSL (not Windows PowerShell or Git Bash) to avoid cross-filesystem issues with pip installations. Access WSL through VS Code terminal.

---

#### **TASK 18: Create Lambda Deployment Package for Ingestion**

**Status**: [ ]  
**Requirements**: Lambda function with PDF processing and Bedrock integration

**STEP 1: Create project directory in WSL Linux filesystem**

Sub-step 1.1: Open WSL terminal in VS Code

Sub-step 1.2: Create project in Linux home directory (NOT on /mnt/e Windows drive):
```bash
mkdir -p ~/aws-lambda/lambda-ingestion
cd ~/aws-lambda/lambda-ingestion
```

**Important**: Using Linux filesystem (`~/`) instead of Windows mount (`/mnt/e/`) avoids pip cross-filesystem errors.

Sub-step 1.3: Create a virtual environment:
```bash
python3 -m venv venv
```

Sub-step 1.4: Activate virtual environment:
```bash
source venv/bin/activate
```

**STEP 2: Install required packages**

Sub-step 2.1: Install packages:
```bash
pip install boto3 pypdf requests python-dotenv
```

**Note**: We use `pypdf` (pure Python) instead of PyMuPDF to avoid GLIBC binary compatibility issues with Lambda's Python 3.11 runtime.

Sub-step 2.2: Verify installations:
```bash
pip list | grep -E "boto3|pypdf|requests"
```

**STEP 3: Create Lambda function code**

Sub-step 3.1: Create `lambda_function.py`:
```bash
nano lambda_function.py
```

Sub-step 3.2: Paste the following code:
```python
import json
import boto3
from pypdf import PdfReader  # pypdf (pure Python, Lambda-compatible)
import os
import uuid
import requests
from datetime import datetime
import time
import re

# Configuration
s3_client = boto3.client('s3', region_name='ap-south-1')
bedrock_client = boto3.client('bedrock-runtime', region_name='ap-south-1')

CHROMA_API_URL = os.environ.get('CHROMA_API_URL')
CHROMA_API_KEY = os.environ.get('CHROMA_API_KEY')
S3_BUCKET = os.environ.get('S3_BUCKET', 'aicloud-bharat-schemes')
EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'
BATCH_SIZE = 20  # Process chunks in batches (increased for large PDFs)
MAX_CHUNKS = 1200  # Protection for extremely large PDFs

def lambda_handler(event, context):
    """Process PDF from S3, generate embeddings, store in ChromaDB"""
    
    start_time = time.time()
    
    try:
        # Extract S3 event details
        s3_event = event['Records'][0]['s3']
        bucket = s3_event['bucket']['name']
        key = s3_event['object']['key']
        
        print(f"Processing PDF: s3://{bucket}/{key}")
        
        # Generate unique document_id for this PDF
        document_id = f"{os.path.basename(key).replace('.pdf', '')}_{int(time.time())}"
        
        # Download PDF from S3
        pdf_path = f'/tmp/{os.path.basename(key)}'
        s3_client.download_file(bucket, key, pdf_path)
        print(f"Downloaded PDF to {pdf_path}")
        
        # Extract text from PDF
        text, page_count = extract_text_from_pdf(pdf_path)
        print(f"Extracted {len(text)} characters from {page_count}-page PDF")
        
        if len(text) < 100:
            raise Exception("PDF text extraction failed or PDF is empty")
        
        # Clean text before chunking
        text = clean_text(text)
        print(f"Cleaned text: {len(text)} characters")
        
        # Extract metadata from S3 tags
        metadata = extract_metadata(bucket, key)
        print(f"Metadata: {metadata}")
        
        # Chunk text with adaptive sizing
        chunks = chunk_text(text, page_count)
        print(f"Created {len(chunks)} chunks")
        
        # Apply max chunk limit
        if len(chunks) > MAX_CHUNKS:
            print(f"WARNING: Document exceeds chunk limit ({len(chunks)} chunks). Processing first {MAX_CHUNKS} chunks only.")
            chunks = chunks[:MAX_CHUNKS]
        
        # Process chunks in batches to avoid memory issues
        total_added = 0
        total_embedding_time = 0
        
        for batch_start in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[batch_start:batch_start + BATCH_SIZE]
            
            # Generate embeddings and prepare documents
            documents = []
            batch_embedding_start = time.time()
            
            for i, chunk in enumerate(batch_chunks):
                chunk_index = batch_start + i
                
                # Generate embedding with retry logic
                embedding_start = time.time()
                embedding = generate_embedding_with_retry(chunk, max_retries=3)
                embedding_time = (time.time() - embedding_start) * 1000
                total_embedding_time += embedding_time
                
                # Generate unique chunk_id
                chunk_id = f"{document_id}_chunk_{chunk_index}"
                
                # Prepare document
                doc = {
                    "id": str(uuid.uuid4()),
                    "embedding": embedding,
                    "text": chunk,
                    "metadata": {
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "scheme_name": metadata['scheme_name'],
                        "category": metadata['category'],
                        "state": metadata['state'],
                        "language": metadata.get('language', 'en'),
                        "eligible_gender": metadata.get('eligible_gender', 'any'),
                        "eligible_minage": metadata.get('eligible_minage', 0),
                        "eligible_maxage": metadata.get('eligible_maxage', 120),
                        "eligible_community": metadata.get('eligible_community', 'any'),
                        "eligible_physically_challenged": metadata.get('eligible_physically_challenged', 'any'),
                        "chunk_index": chunk_index,
                        "source_doc": os.path.basename(key)
                    }
                }
                documents.append(doc)
            
            batch_embedding_time = (time.time() - batch_embedding_start) * 1000
            
            # Send batch to ChromaDB with retry logic
            response = send_to_chromadb_with_retry(documents, max_retries=3)
            total_added += response['added_count']
            
            print(f"Batch {batch_start//BATCH_SIZE + 1}: Added {response['added_count']} documents (Total: {total_added}/{len(chunks)}) - Embedding time: {batch_embedding_time:.0f}ms")
        
        # Move PDF to processed folder
        processed_key = key.replace('raw/', 'processed/')
        s3_client.copy_object(
            Bucket=bucket,
            CopySource={'Bucket': bucket, 'Key': key},
            Key=processed_key
        )
        s3_client.delete_object(Bucket=bucket, Key=key)
        print(f"Moved PDF to {processed_key}")
        
        # Calculate total processing time
        total_time = time.time() - start_time
        avg_embedding_time = total_embedding_time / len(chunks) if len(chunks) > 0 else 0
        
        # Log performance metrics
        metrics = {
            'total_processing_time_sec': round(total_time, 2),
            'total_embedding_time_ms': round(total_embedding_time, 0),
            'avg_embedding_time_ms': round(avg_embedding_time, 2),
            'chunks_processed': len(chunks),
            'vectors_added': total_added
        }
        print(f"Performance metrics: {json.dumps(metrics)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'PDF processed successfully',
                'pdf_name': os.path.basename(key),
                'document_id': document_id,
                'chunks_created': len(chunks),
                'vectors_added': total_added,
                'scheme_name': metadata['scheme_name'],
                'category': metadata['category'],
                'state': metadata['state'],
                'language': metadata.get('language', 'en'),
                'metrics': metrics
            })
        }
    
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        
        # Log error details for debugging
        error_details = {
            'error': str(e),
            'pdf_key': key if 'key' in locals() else 'unknown',
            'timestamp': datetime.utcnow().isoformat()
        }
        print(f"Error details: {json.dumps(error_details)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps(error_details)
        }

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pypdf"""
    reader = PdfReader(pdf_path)
    text = ""
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        text += page_text
        print(f"Extracted page {page_num + 1}/{len(reader.pages)}: {len(page_text)} chars")
    
    # Return text and page count for adaptive chunking
    return text, len(reader.pages)

def clean_text(text):
    """Clean extracted text by removing page numbers, headers, footers, and excessive whitespace"""
    # Remove page numbers (common patterns: "Page 1", "1 of 10", "- 1 -")
    text = re.sub(r'\b[Pp]age\s+\d+\b', '', text)
    text = re.sub(r'\b\d+\s+of\s+\d+\b', '', text)
    text = re.sub(r'-\s*\d+\s*-', '', text)
    
    # Remove common header/footer patterns
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)  # Standalone page numbers
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text

def chunk_text(text, page_count, chunk_size=700, overlap=120):
    """
    Split text into overlapping chunks with adaptive sizing for large documents.
    
    Adaptive Strategy:
    - Default (≤100 pages): 800-1000 tokens, 120-150 overlap
    - Large docs (>100 pages): 1200-1500 tokens, 200 overlap
    - Semantic boundary splitting: prefer paragraphs, sentences
    """
    
    # Adaptive chunk sizing based on document length
    if page_count > 100:
        chunk_size = 1350  # 1200-1500 range
        overlap = 200
        print(f"Large document detected ({page_count} pages). Using chunk_size={chunk_size}, overlap={overlap}")
    else:
        chunk_size = 900  # 800-1000 range
        overlap = 135  # 120-150 range
        print(f"Standard document ({page_count} pages). Using chunk_size={chunk_size}, overlap={overlap}")
    
    # Split by paragraphs first (semantic boundaries)
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = []
    current_word_count = 0
    
    for para in paragraphs:
        para_words = para.split()
        para_word_count = len(para_words)
        
        # If single paragraph exceeds chunk size, split by sentences
        if para_word_count > chunk_size:
            # Flush current chunk if exists
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_word_count = 0
            
            # Split large paragraph by sentences
            sentences = re.split(r'(?<=[.!?])\s+', para)
            for sentence in sentences:
                sentence_words = sentence.split()
                sentence_word_count = len(sentence_words)
                
                if current_word_count + sentence_word_count > chunk_size:
                    if current_chunk:
                        chunks.append(' '.join(current_chunk))
                        # Keep overlap words for context
                        current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                        current_word_count = len(current_chunk)
                
                current_chunk.extend(sentence_words)
                current_word_count += sentence_word_count
        
        # Normal paragraph processing
        elif current_word_count + para_word_count > chunk_size:
            # Chunk is full, save it
            if current_chunk:
                chunks.append(' '.join(current_chunk))
                # Keep overlap words for context
                current_chunk = current_chunk[-overlap:] if len(current_chunk) > overlap else []
                current_word_count = len(current_chunk)
            
            # Add current paragraph
            current_chunk.extend(para_words)
            current_word_count += para_word_count
        else:
            # Add paragraph to current chunk
            current_chunk.extend(para_words)
            current_word_count += para_word_count
    
    # Add remaining chunk
    if current_chunk and len(current_chunk) >= 50:  # Skip very short chunks
        chunks.append(' '.join(current_chunk))
    
    print(f"Created {len(chunks)} chunks with adaptive strategy")
    return chunks

def extract_metadata(bucket, key):
    """Extract metadata from S3 object tags"""
    try:
        # Get S3 object tags
        response = s3_client.get_object_tagging(Bucket=bucket, Key=key)
        tags = {tag['Key']: tag['Value'] for tag in response['TagSet']}
        
        # Parse eligible_minage and eligible_maxage (convert to integers)
        eligible_minage = int(tags.get('eligible_minage', '0'))
        eligible_maxage = int(tags.get('eligible_maxage', '120'))
        
        # Parse eligible_community (comma-separated string to list)
        eligible_community = tags.get('eligible_community', 'any')
        if isinstance(eligible_community, str) and eligible_community != 'any':
            eligible_community = [c.strip() for c in eligible_community.split(',')]
        
        # Parse eligible_physically_challenged (string: 'yes', 'no', or 'any')
        eligible_physically_challenged = tags.get('eligible_physically_challenged', 'any').lower()
        
        # Parse language code (default to 'en')
        language = tags.get('language', 'en').lower()
        
        metadata = {
            'scheme_name': tags.get('scheme_name', 'Unknown Scheme'),
            'category': tags.get('category', 'others'),
            'state': tags.get('state', 'all'),
            'language': language,
            'eligible_gender': tags.get('eligible_gender', 'any'),
            'eligible_minage': eligible_minage,
            'eligible_maxage': eligible_maxage,
            'eligible_community': eligible_community,
            'eligible_physically_challenged': eligible_physically_challenged
        }
        
        # Validate required fields
        if not metadata['scheme_name'] or metadata['scheme_name'] == 'Unknown Scheme':
            raise Exception("Missing required tag: scheme_name")
        if not metadata['category']:
            raise Exception("Missing required tag: category")
        
        return metadata
        
    except Exception as e:
        print(f"Error extracting metadata: {str(e)}")
        # Fallback: extract from filename
        filename = os.path.basename(key).replace('.pdf', '')
        print(f"Using fallback metadata from filename: {filename}")
        return {
            'scheme_name': filename.replace('_', ' ').title(),
            'category': 'others',
            'state': 'all',
            'language': 'en',
            'eligible_gender': 'any',
            'eligible_minage': 0,
            'eligible_maxage': 120,
            'eligible_community': 'any',
            'eligible_physically_challenged': 'any'
        }

def generate_embedding_with_retry(text, max_retries=3):
    """Generate embedding using Bedrock Titan Embeddings V2 with retry logic"""
    for attempt in range(max_retries):
        try:
            response = bedrock_client.invoke_model(
                modelId=EMBEDDING_MODEL,
                body=json.dumps({"inputText": text})
            )
            
            result = json.loads(response['body'].read())
            embedding = result['embedding']
            
            # Validate dimension
            if len(embedding) != 1024:
                raise Exception(f"Invalid embedding dimension: {len(embedding)}, expected 1024")
            
            return embedding
            
        except Exception as e:
            print(f"Embedding generation attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise

def send_to_chromadb_with_retry(documents, max_retries=3):
    """Send documents to ChromaDB with retry logic"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{CHROMA_API_URL}/add",
                headers={"X-API-Key": CHROMA_API_KEY},
                json={"documents": documents},
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"ChromaDB API error: {response.status_code} - {response.text}")
            
            return response.json()
            
        except Exception as e:
            print(f"ChromaDB API attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

Sub-step 3.3: Save and exit (Ctrl+X, Y, Enter)

**STEP 4: Create deployment package**

**WSL Important**: You should already be in `~/aws-lambda/lambda-ingestion` directory (Linux filesystem). If you copied from Windows drive earlier, the files are already here.

Sub-step 4.1: Clean and prepare package directory:
```bash
rm -rf package
mkdir package
```

Sub-step 4.2: Install dependencies (pypdf is pure Python, no binary issues):
```bash
pip install --target ./package boto3 pypdf requests python-dotenv
```

**Note**: We use `pypdf` instead of PyMuPDF because:
- Pure Python implementation (no C binaries)
- No GLIBC version dependencies
- Fully compatible with AWS Lambda Python 3.11 runtime (Amazon Linux 2)
- Smaller package size

Sub-step 4.3: Copy lambda function to package:
```bash
cp lambda_function.py package/
```

Sub-step 4.4: Create ZIP file:
```bash
python3 -c "import shutil; shutil.make_archive('ingestion-lambda', 'zip', 'package')"
```

**Important**: Run this from `lambda-ingestion` directory (NOT inside `package`).

Sub-step 4.5: Verify ZIP file was created:
```bash
ls -lh ingestion-lambda.zip
```

Expected: File size should be 10-20 MB (pypdf is smaller than PyMuPDF)

---

#### **TASK 19: Deploy Ingestion Lambda Function**

**Status**: [ ]  
**Requirements**: Lambda function deployed with correct IAM role and environment variables

**Note**: Run TASK 19 from the `~/aws-lambda/lambda-ingestion` folder in WSL where your ingestion-lambda.zip file is located.

**STEP 1: Get IAM role ARN**

Sub-step 1.1: Get the SchemeIngestionLambdaRole ARN:
```bash
aws iam get-role --role-name SchemeIngestionLambdaRole --query 'Role.Arn' --output text
```

Sub-step 1.2: Copy the ARN (format: `arn:aws:iam::ACCOUNT_ID:role/SchemeIngestionLambdaRole`)

**STEP 2: Create Lambda function**

Sub-step 2.1: Create the Lambda function:
```bash
aws lambda create-function \
  --function-name SchemeIngestionFunction \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/SchemeIngestionLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://ingestion-lambda.zip \
  --timeout 600 \
  --memory-size 1536 \
  --region ap-south-1
```

Replace `ACCOUNT_ID` with your AWS account ID

**Note**: Timeout is set to 600 seconds (10 minutes) to handle large PDFs (250+ pages). Memory is 1536 MB to handle PDF extraction, text cleaning, and batch processing efficiently.

Sub-step 2.2: Wait for function creation (30-60 seconds)

**STEP 3: Configure environment variables**

Sub-step 3.1: Update Lambda environment variables:
```bash
aws lambda update-function-configuration \
  --function-name SchemeIngestionFunction \
  --environment Variables="{CHROMA_API_URL=http://65.0.91.246:8000,CHROMA_API_KEY=my-super-secret-key-54321,S3_BUCKET=aicloud-bharat-schemes}" \
  --region ap-south-1
```

Replace:
- `65.0.91.246` with your EC2 public IP if different
- `my-super-secret-key-54321` with your actual API key if different

Sub-step 3.2: Verify environment variables:
```bash
aws lambda get-function-configuration --function-name SchemeIngestionFunction --query 'Environment' --region ap-south-1
```

**STEP 4: Add S3 trigger**

Sub-step 4.1: Add permission for S3 to invoke Lambda:
```bash
aws lambda add-permission \
  --function-name SchemeIngestionFunction \
  --statement-id s3-trigger-permission \
  --action lambda:InvokeFunction \
  --principal s3.amazonaws.com \
  --source-arn arn:aws:s3:::aicloud-bharat-schemes \
  --region ap-south-1
```

Sub-step 4.2: Create S3 event notification configuration file:
```bash
nano s3-notification.json
```

Sub-step 4.3: Paste the following content:
```json
{
  "LambdaFunctionConfigurations": [
    {
      "Id": "pdf-ingestion-trigger",
      "LambdaFunctionArn": "arn:aws:lambda:ap-south-1:ACCOUNT_ID:function:SchemeIngestionFunction",
      "Events": ["s3:ObjectCreated:*"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {"Name": "prefix", "Value": "raw/"},
            {"Name": "suffix", "Value": ".pdf"}
          ]
        }
      }
    }
  ]
}
```

Replace `ACCOUNT_ID` with your AWS account ID

Sub-step 4.4: Save and exit (Ctrl+X, Y, Enter)

Sub-step 4.5: Apply S3 notification configuration:
```bash
aws s3api put-bucket-notification-configuration \
  --bucket aicloud-bharat-schemes \
  --notification-configuration file://s3-notification.json
```

Sub-step 4.6: Verify notification configuration:
```bash
aws s3api get-bucket-notification-configuration --bucket aicloud-bharat-schemes
```

---

#### **TASK 20: Prepare Test PDF with Metadata Tags**

**Status**: [ ]  
**Requirements**: Single detailed PDF with proper S3 tags for testing

**STEP 1: Select or create test PDF**

Sub-step 1.1: Choose ONE detailed government scheme PDF (10-20 pages recommended)
- Example: PM Kisan Samman Nidhi guidelines
- Example: Pradhan Mantri Awas Yojana documentation
- Example: State-specific solar subsidy scheme

Sub-step 1.2: Rename the PDF file to a descriptive name:
```
Ayushman_Bharat_PMJAY.pdf
```

**STEP 2: Upload PDF to S3 with metadata tags**

Sub-step 2.1: add missing IAM role policy 
**Note**: Lambda role SchemeIngestionLambdaRole does not have permission to read S3 object tags, Because of that: Using fallback metadata from filename.
```bash
nano s3-tag-permission.json
```
Paste the following content:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObjectTagging",
        "s3:PutObjectTagging"
      ],
      "Resource": "arn:aws:s3:::aicloud-bharat-schemes/*"
    }
  ]
}
```
Attach it:
```bash
aws iam put-role-policy \
--role-name SchemeIngestionLambdaRole \
--policy-name S3TagReadPolicy \
--policy-document file://s3-tag-permission.json
```


Sub-step 2.2: Upload PDF with tags to S3 :
```bash
aws s3api put-object \
--bucket aicloud-bharat-schemes \
--key raw/Ayushman_Bharat_PMJAY.pdf \
--body "/mnt/c/Users/Krish/Downloads/gov_schemes/HealthCare/Ayushman_Bharat_PMJAY.pdf" \
--tagging "scheme_name=ayushman_bharat_pmjay&category=healthcare&language=en&eligible_minage=0&eligible_maxage=120&eligible_gender=any&eligible_employment=any&eligible_community=any&eligible_physically_challenged=any&state=any" \
--region ap-south-1
```
**Note**:  Always upload using:
"aws s3api put-object" avoid using "aws s3 cp" 
- aws s3 cp does NOT support the --tagging parameter.
- Tagging works with the S3 API - command, not the high-level aws s3 command.
- Most importantly the trigger listens to: s3:ObjectCreated:*

**Tag values to use:**
- `scheme_name`: Full official name (e.g., "Ayushman Bharat PMJAY")
- `category`: One of (education_skill, solar_subsidy, startup_selfemployment, housing_aid, water_sanitation, agriculture, healthcare, others)
- `language`: ISO-639-1 code (en, hi, ta) - default is "en"
- `eligible_minage`: Minimum age (0-120, default: 0)
- `eligible_maxage`: Maximum age (0-120, default: 120)
- `eligible_gender`: any, male, female, other
- `eligible_employment`: "any" OR comma-separated list (unemployed,employed,self_employed)
- `eligible_community`: Comma-separated list (general,obc,pvtg,sc,st,dnt) OR "any"
- `eligible_physically_challenged`: any, yes, no
- `state`: State code (e.g., tamil_nadu, maharashtra) OR "any" for central schemes


**Note**: For 250+ page PDFs, the upload may take 1-2 minutes depending on file size and network speed. Use underscores instead of commas in `eligible_employment` to avoid CLI parsing issues.

Sub-step 2.3: Verify upload:
```bash
aws s3 ls s3://aicloud-bharat-schemes/raw/
```

Sub-step 2.4: Verify tags were applied:
```bash
aws s3api get-object-tagging --bucket aicloud-bharat-schemes --key raw/Ayushman_Bharat_PMJAY.pdf
```


---

#### **TASK 21: Monitor Lambda Execution and Verify Ingestion**

**Status**: [ ]  
**Requirements**: Verify PDF was processed and vectors stored in ChromaDB

**STEP 1: Verify S3 notification is configured**

Sub-step 1.1: Check if S3 notification configuration exists:
```bash
aws s3api get-bucket-notification-configuration --bucket aicloud-bharat-schemes
```

Sub-step 1.2: If output is empty `{}`, apply the notification configuration:
```bash
aws s3api put-bucket-notification-configuration \
  --bucket aicloud-bharat-schemes \
  --notification-configuration file://s3-notification.json
```

Sub-step 1.3: Verify notification was applied:
```bash
aws s3api get-bucket-notification-configuration --bucket aicloud-bharat-schemes
```

You should see the Lambda function configuration in the output.

**STEP 2: Trigger Lambda execution**

Sub-step 2.1: Check if PDF is still in raw folder:
```bash
aws s3 ls s3://aicloud-bharat-schemes/raw/
```

Sub-step 2.2: If PDF is in raw folder, choose one option to trigger Lambda:

**Option A: Re-upload the PDF** (recommended - simpler):
```bash
aws s3 cp /c/Users/Krish/Downloads/gov_schemes/HealthCare/Ayushman_Bharat_PMJAY.pdf s3://aicloud-bharat-schemes/raw/Ayushman_Bharat_PMJAY.pdf
```

**Option B: Manually invoke Lambda**:
```bash
aws lambda invoke \
  --function-name SchemeIngestionFunction \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  --payload '{"Records":[{"s3":{"bucket":{"name":"aicloud-bharat-schemes"},"object":{"key":"raw/Ayushman_Bharat_PMJAY.pdf"}}}]}' \
  response.json
```

Then check the response:
```bash
cat response.json
```

**STEP 3: Monitor Lambda execution**

Sub-step 3.1: Wait 1-2 minutes after triggering Lambda

Sub-step 3.2: Check Lambda logs in CloudWatch:
```bash
aws logs tail /aws/lambda/SchemeIngestionFunction --follow --region ap-south-1
```

Sub-step 3.3: Look for these log messages:
- "Processing PDF: s3://aicloud-bharat-schemes/raw/..."
- "Downloaded PDF to /tmp/..."
- "Extracted X characters from PDF"
- "Created X chunks"
- "Added X documents to ChromaDB"
- "Moved PDF to processed/..."

Sub-step 3.4: Press Ctrl+C to stop tailing logs

**STEP 4: Verify PDF was moved to processed folder**

Sub-step 4.1: Check processed folder:
```bash
aws s3 ls s3://aicloud-bharat-schemes/processed/
```

Sub-step 4.2: Verify your PDF appears in the processed folder

Sub-step 4.3: Verify raw folder is empty:
```bash
aws s3 ls s3://aicloud-bharat-schemes/raw/
```

**STEP 5: Verify vectors in ChromaDB**

Sub-step 5.1: SSH into EC2 instance

Sub-step 5.2: Check ChromaDB stats:
```bash
curl http://localhost:8000/stats
```

Sub-step 5.3: Verify output shows:
- `total_vectors` > 0 (should match number of chunks)
- `categories` includes your scheme's category
- `states` includes your scheme's state

Sub-step 5.4: Check collections:
```bash
curl http://localhost:8000/collections
```

Sub-step 5.5: Verify `government_schemes` collection has documents

**STEP 6: Test vector search**

Sub-step 6.1: Create a test search script:
```bash
nano test_search.py
```

Sub-step 6.2: Paste the following code:
```python
import requests
import boto3
import json

# Configuration
CHROMA_API_URL = "http://localhost:8000"
CHROMA_API_KEY = "my-super-secret-key-54321"
bedrock_client = boto3.client('bedrock-runtime', region_name='ap-south-1')

# Generate query embedding
query_text = "financial support for farmers"
response = bedrock_client.invoke_model(
    modelId='amazon.titan-embed-text-v2:0',
    body=json.dumps({"inputText": query_text})
)
result = json.loads(response['body'].read())
query_embedding = result['embedding']

# Search ChromaDB
search_response = requests.post(
    f"{CHROMA_API_URL}/search",
    headers={"X-API-Key": CHROMA_API_KEY},
    json={
        "query_embedding": query_embedding,
        "top_k": 3,
        "category_filter": "agriculture"
    }
)

print(f"Status: {search_response.status_code}")
results = search_response.json()
print(f"Found {len(results['results'])} results")

for i, result in enumerate(results['results']):
    print(f"\nResult {i+1}:")
    print(f"  Score: {result['score']:.4f}")
    print(f"  Scheme: {result['metadata']['scheme_name']}")
    print(f"  Text: {result['text'][:100]}...")
```

Sub-step 4.3: Save and exit (Ctrl+X, Y, Enter)

Sub-step 4.4: Run test search:
```bash
python test_search.py
```

Sub-step 4.5: Verify you get relevant results with scores > 0.5

**STEP 5: Troubleshoot if ingestion failed**

If Lambda execution failed:

Sub-step 5.1: Check Lambda logs for errors:
```bash
aws logs tail /aws/lambda/SchemeIngestionFunction --since 10m --region ap-south-1
```

Sub-step 5.2: Common issues:
- **Timeout error**: Increase Lambda timeout to 600 seconds (already set)
- **Memory error**: Increase Lambda memory to 1536 MB (already set)
- **ChromaDB API error**: Verify CHROMA_API_URL and CHROMA_API_KEY are correct
- **Bedrock error**: Verify IAM role has bedrock:InvokeModel permission
- **Missing language tag**: If language tag is missing, defaults to "en"

Sub-step 5.3: Re-upload PDF to trigger Lambda again:
```bash
aws s3 cp pm_kisan_scheme.pdf s3://aicloud-bharat-schemes/raw/pm_kisan_scheme.pdf --tagging "..."
```

---

#### **TASK 22: Validate Ingestion Pipeline End-to-End**

**Status**: [ ]  
**Requirements**: Complete ingestion flow working correctly

**STEP 1: Verify complete flow**

Sub-step 1.1: Confirm PDF is in processed folder:
```bash
aws s3 ls s3://aicloud-bharat-schemes/processed/
```

Sub-step 1.2: Confirm vectors in ChromaDB:
```bash
curl http://65.0.91.246:8000/stats
```

Sub-step 1.3: Verify metadata is correct:
- Category matches your PDF
- State matches your PDF
- Language is "en" (or your specified language)
- Chunk count is reasonable (10-20 page PDF should create 20-50 chunks)

**STEP 2: Test search with different queries**

Sub-step 2.1: Test query 1 (exact match):
```bash
# Use test_search.py with query related to your PDF content
# Example: "farmer subsidy" for PM Kisan
```

Sub-step 2.2: Test query 2 (semantic match):
```bash
# Use test_search.py with related but different wording
# Example: "agriculture financial help" for PM Kisan
```

Sub-step 2.3: Verify both queries return relevant results with good scores (>0.5)

**STEP 3: Document ingestion results**

Sub-step 3.1: Note down:
- PDF name and size
- Number of chunks created
- Number of vectors stored
- Sample search query and top result score

Sub-step 3.2: Save this information for STAGE 5 testing

---

### STAGE 5 — RAG Orchestrator (P0 Critical)

**Priority**: Highest  
**Goal**: Query → embedding → ChromaDB → retrieved chunks → Bedrock  
**Deliverable**: API Gateway + Lambda that handles user queries and returns scheme recommendations

**WSL Note**: All Lambda development tasks should be run in WSL Linux filesystem (`~/aws-lambda/`) to avoid cross-filesystem pip issues.

---

#### **TASK 23: Create RAG Orchestrator Lambda Function**

**Status**: [ ]  
**Requirements**: Lambda function that orchestrates the RAG pipeline

**STEP 1: Create project directory in WSL**
Sub-step 1.0: go to correct directory:
if you are inside any venv then come out of it, Exit current venv.
```bash
deactivate
```
TASK 23 needs its OWN venv in a NEW directory.
so if you  are in /home/krish/aws-lambda/lambda-ingestion or any other
Go to parent directory
```bash
cd ~/aws-lambda
```
Sub-step 1.1: Create project in Linux home directory:
```bash
mkdir -p ~/aws-lambda/rag-orchestrator
cd ~/aws-lambda/rag-orchestrator
```

Sub-step 1.2: Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

**STEP 2: Install required packages**

Sub-step 2.1: Install packages:
```bash
pip install boto3 requests python-dotenv
```

Sub-step 2.2: Verify installations:
```bash
pip list | grep -E "boto3|requests"
```

**STEP 3: Create RAG Orchestrator Lambda function code**
**Note**:Create here `~/aws-lambda/rag-orchestrator/lambda_function.py` with this code

Sub-step 3.1: Create `lambda_function.py`:
```bash
nano lambda_function.py
```

Sub-step 3.2: Copy the complete RAG Orchestrator code below and paste it inside `lambda_function.py` file
```python
import json
import boto3
import requests
import os
from datetime import datetime
import time
import uuid

# Configuration
bedrock_client = boto3.client('bedrock-runtime', region_name='ap-south-1')

CHROMA_API_URL = os.environ.get('CHROMA_API_URL')
CHROMA_API_KEY = os.environ.get('CHROMA_API_KEY')
EMBEDDING_MODEL = 'amazon.titan-embed-text-v2:0'
LLM_MODEL = 'global.amazon.nova-2-lite-v1:0'

# Language code to full name mapping
LANGUAGE_MAP = {'en': 'English', 'hi': 'Hindi', 'ta': 'Tamil'}

def lambda_handler(event, context):
    start_time = time.time()
    
    # Handle OPTIONS preflight request
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': ''
        }
    
    # Fix 12: Generate query ID for traceability
    query_id = str(uuid.uuid4())
    
    # Fix 11: CORS headers for all responses
    cors_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }
    
    try:
        # Fix 1: Parse body correctly
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        
        # Fix 7: Debug logging - print raw body
        print(f"[DEBUG] Query ID: {query_id}")
        print(f"[DEBUG] Raw body: {json.dumps(body)}")
        
        # Validate required fields
        required = ['name', 'age', 'state', 'category', 'community', 'physically_challenged', 'language', 'query']
        for field in required:
            if field not in body or not body[field]:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'error': f'Missing: {field}', 'query_id': query_id})
                }
        
        # Extract inputs
        user_name = body['name']
        user_age = body['age']
        user_gender = body.get('gender', '')
        user_community = body['community']
        user_physically_challenged = body['physically_challenged']
        language_code = body['language']
        user_query = body['query']
        response_language = LANGUAGE_MAP.get(language_code, 'English')
        
        # Fix 2: Normalize category
        user_category = body.get('category', '').lower()
        category_map = {
            'health care': 'healthcare',
            'health-care': 'healthcare',
            'health': 'healthcare',
            'education & skills': 'education_skill',
            'education and skills': 'education_skill',
            'startup & self employment': 'startup_selfemployment',
            'startup and self employment': 'startup_selfemployment'
        }
        user_category = category_map.get(user_category, user_category)
        
        # Fix 3: Normalize state
        user_state = body.get('state', '').lower().replace(' ', '_')
        
        # Fix 7: Debug logging - print normalized values
        print(f"[DEBUG] Normalized category: {user_category}")
        print(f"[DEBUG] Normalized state: {user_state}")
        print(f"[DEBUG] Query: {user_query}")
        
        # Fix 8: Defensive query validation
        if not user_query or len(user_query.strip()) == 0:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Query cannot be empty', 'query_id': query_id})
            }
        
        if len(user_query.strip()) < 5:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Query too short. Please provide more details.', 'query_id': query_id})
            }
        
        print(f"Query: {user_query[:50]}... (lang: {response_language}, cat: {user_category})")
        
        # Generate query embedding
        query_embedding = generate_embedding(user_query)
        print(f"[DEBUG] Generated embedding with {len(query_embedding)} dimensions")
        
        # Search ChromaDB with eligibility filters
        results = search_chromadb(query_embedding, user_category, user_state, user_gender, 
                                 user_age, user_community, user_physically_challenged, 
                                 language_code, top_k=5)
        
        # Fix 7: Debug logging - print retrieved documents
        print(f"[DEBUG] Retrieved {len(results)} documents from ChromaDB")
        for i, result in enumerate(results[:3]):
            print(f"[DEBUG] Doc {i+1}: {result.get('metadata', {}).get('scheme_name', 'Unknown')} (score: {result.get('score', 0):.3f})")
        
        # Gatekeeper: Check relevance
        if not results or results[0]['score'] < 0.3:
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'response': 'No relevant schemes found. Try different category or rephrase query.',
                    'sources': [],
                    'query_id': query_id
                })
            }
        
        # Construct prompt
        prompt = construct_prompt(user_name, user_age, user_state, user_gender, 
                                 user_community, user_physically_challenged, user_category, 
                                 user_query, results, response_language)
        
        # Call LLM
        llm_response = call_bedrock_llm(prompt, response_language)
        
        # Fix 9: Extract unique sources (no duplicates)
        unique_schemes = []
        seen_schemes = set()
        for r in results[:5]:
            scheme_name = r['metadata'].get('scheme_name', 'Unknown Scheme')
            if scheme_name not in seen_schemes:
                unique_schemes.append(f"{scheme_name} (Score: {r['score']:.2f})")
                seen_schemes.add(scheme_name)
        
        # Fix 10: Ensure response format remains compatible with frontend
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'response': llm_response,
                'sources': unique_schemes[:3],  # Return top 3 unique sources
                'query_id': query_id
            })
        }
        
    except Exception as e:
        print(f"[ERROR] Query ID: {query_id}, Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': str(e), 'query_id': query_id})
        }

def generate_embedding(text):
    response = bedrock_client.invoke_model(
        modelId=EMBEDDING_MODEL,
        body=json.dumps({"inputText": text})
    )
    return json.loads(response['body'].read())['embedding']

def search_chromadb(query_embedding, category, state, gender, age, community, 
                   physically_challenged, language, top_k=5):
    # Fix 4: Pure vector search first (no metadata filtering in Chroma)
    payload = {
        "query_embedding": query_embedding,
        "top_k": top_k * 3  # Retrieve more for post-filtering
    }
    
    response = requests.post(
        f"{CHROMA_API_URL}/search",
        headers={"X-API-Key": CHROMA_API_KEY},
        json=payload,
        timeout=10
    )
    
    if response.status_code != 200:
        raise Exception(f"ChromaDB error: {response.status_code}")
    
    results = response.json()['results']
    
    # Fix 5: Apply metadata filtering after retrieval
    filtered_results = []
    for result in results:
        metadata = result.get('metadata', {})
        
        # Category match
        scheme_category = metadata.get('category', '').lower()
        category_match = (scheme_category == category or category == '' or category == 'any')
        
        # State match
        scheme_state = metadata.get('state', 'any').lower()
        state_match = (scheme_state in ['any', 'all', state] or state in ['any', 'all'])
        
        # Gender match
        scheme_gender = metadata.get('eligible_gender', 'any').lower()
        gender_match = (scheme_gender == 'any' or gender == '' or scheme_gender == gender)
        
        # Age match
        scheme_minage = metadata.get('eligible_minage', 0)
        scheme_maxage = metadata.get('eligible_maxage', 120)
        age_match = (scheme_minage <= age <= scheme_maxage)
        
        # Community match
        scheme_community = metadata.get('eligible_community', 'any')
        if isinstance(scheme_community, str):
            community_list = scheme_community.split(',') if ',' in scheme_community else [scheme_community]
        else:
            community_list = [scheme_community]
        community_match = ('any' in community_list or community in community_list)
        
        # Physically challenged match
        scheme_pc = metadata.get('eligible_physically_challenged', 'any').lower()
        pc_match = (scheme_pc == 'any' or scheme_pc == physically_challenged)
        
        if category_match and state_match and gender_match and age_match and community_match and pc_match:
            filtered_results.append(result)
    
    # Fix 6: Fallback logic - if no matches, return top vector results
    if not filtered_results:
        print(f"No filtered results, returning top {min(top_k, len(results))} vector results")
        filtered_results = results[:top_k]
    
    return filtered_results[:top_k]

def construct_prompt(name, age, state, gender, community, physically_challenged, 
                    category, query, chunks, lang):
    profile = [f"Name: {name}", f"Age: {age}", f"State: {state}"]
    if gender: profile.append(f"Gender: {gender}")
    profile.append(f"Community: {community}")
    profile.append(f"Physically Challenged: {physically_challenged}")
    profile.append(f"Category: {category}")
    
    context = "\n".join([
        f"[Source {i+1}] {c['metadata']['scheme_name']} (Score: {c['score']:.2f})\n{c['text']}\n"
        for i, c in enumerate(chunks[:5])
    ])
    
    return f"""You are a government scheme assistant. Recommend relevant schemes based on user profile and query.

User Profile:
{chr(10).join(profile)}

Query: {query}

Context:
{context}

Instructions:
1. Recommend 2-3 relevant schemes from context
2. Explain eligibility, benefits, and how to apply
3. Check if user matches eligibility criteria
4. Cite sources using [Source X]
5. Respond in {lang}
6. Be concise

Response:"""

def call_bedrock_llm(prompt, language):
    response = bedrock_client.converse(
        modelId=LLM_MODEL,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 1000,
            "temperature": 0.7,
            "topP": 0.9
        }
    )
    
    return response['output']['message']['content'][0]['text']
```
Then save (Ctrl+X, Y, Enter)

**STEP 4: Create deployment package**

Sub-step 4.1: Clean and prepare package:
```bash
rm -rf package
mkdir package
```

Sub-step 4.2: Install dependencies:
```bash
pip install --target ./package boto3 requests python-dotenv
```

Sub-step 4.3: Copy lambda function:
```bash
cp lambda_function.py package/
```

Sub-step 4.4: Create ZIP:
```bash
python3 -c "import shutil; shutil.make_archive('rag-orchestrator', 'zip', 'package')"
```

Sub-step 4.5: Verify ZIP:
```bash
ls -lh rag-orchestrator.zip
```

Expected: 5-10 MB

---

#### **TASK 24: Deploy RAG Orchestrator Lambda**

**Status**: [ ]  
**Requirements**: Lambda deployed with environment variables

**STEP 1: Create Lambda function**

Sub-step 1.1: Get IAM role ARN:
```bash
aws iam get-role --role-name RAGOrchestratorLambdaRole --query 'Role.Arn' --output text
```

Sub-step 1.2: Create Lambda:
```bash
aws lambda create-function \
  --function-name RAGOrchestratorFunction \
  --runtime python3.11 \
  --role arn:aws:iam::442004016723:role/RAGOrchestratorLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://rag-orchestrator.zip \
  --timeout 30 \
  --memory-size 512 \
  --region ap-south-1
```

Replace `442004016723` with your account ID.

**STEP 2: Configure environment variables**

Sub-step 2.1: Update environment:
```bash
aws lambda update-function-configuration \
  --function-name RAGOrchestratorFunction \
  --environment Variables="{CHROMA_API_URL=http://65.0.91.246:8000,CHROMA_API_KEY=my-super-secret-key-54321}" \
  --region ap-south-1
```

Sub-step 2.2: Verify:
```bash
aws lambda get-function-configuration --function-name RAGOrchestratorFunction --query 'Environment' --region ap-south-1
```

**STEP 3: Test Lambda**

Sub-step 3.1: Create test event:
```bash
cat > test-event.json << 'EOF'
{
  "body": "{\"name\":\"Ravi\",\"age\":32,\"gender\":\"male\",\"community\":\"general\",\"physically_challenged\":\"no\",\"state\":\"tamil_nadu\",\"category\":\"agriculture\",\"language\":\"en\",\"query\":\"Am I eligible for farmer schemes?\"}"
}
EOF
```

Sub-step 3.2: Invoke:
```bash
aws lambda invoke \
  --function-name RAGOrchestratorFunction \
  --region ap-south-1 \
  --cli-binary-format raw-in-base64-out \
  --payload file://test-event.json \
  response.json
```

Sub-step 3.3: Check response:
```bash
cat response.json
```

---

#### **TASK 25: Create API Gateway**

**Status**: [ ]  
**Requirements**: HTTP API with Lambda integration

**STEP 1: Create API**
TASK 25 (Create API Gateway): Exit venv first
deactivate
cd ~

Sub-step 1.1: Create HTTP API:
```bash
aws apigatewayv2 create-api \
  --name GovernmentSchemeAPI \
  --protocol-type HTTP \
  --region ap-south-1
```

Sub-step 1.2: Save API ID from output

Sub-step 1.3: Set variable:
```bash
API_ID=<paste_api_id>
```

**STEP 2: Create integration**

Sub-step 2.1: Create Lambda integration:
```bash
aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:ap-south-1:442004016723:function:RAGOrchestratorFunction \
  --payload-format-version 2.0 \
  --region ap-south-1
```

Sub-step 2.2: Save Integration ID

Sub-step 2.3: Set variable:
```bash
INTEGRATION_ID=<paste_integration_id>
```

**STEP 3: Create route**

Sub-step 3.1: Create POST /query:
```bash
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'POST /query' \
  --target integrations/$INTEGRATION_ID \
  --region ap-south-1
```

**STEP 4: Create stage**

Sub-step 4.1: Create $default stage:
```bash
aws apigatewayv2 create-stage \
  --api-id $API_ID \
  --stage-name '$default' \
  --auto-deploy \
  --region ap-south-1
```

Sub-step 4.2: Get endpoint URL:
```bash
echo "https://$API_ID.execute-api.ap-south-1.amazonaws.com"
```

**STEP 5: Add permissions**

Sub-step 5.1: Add Lambda permission:
```bash
aws lambda add-permission \
  --function-name RAGOrchestratorFunction \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:ap-south-1:442004016723:$API_ID/*/*" \
  --region ap-south-1
```

**STEP 6: Enable CORS**

Sub-step 6.1: Update API:
```bash
aws apigatewayv2 update-api \
  --api-id $API_ID \
  --cors-configuration AllowOrigins='*',AllowMethods='POST,OPTIONS',AllowHeaders='Content-Type' \
  --region ap-south-1
```

---

#### **TASK 26: Update Frontend with API Endpoint**

**Status**: [ ]  
**Requirements**: Frontend calls API Gateway

**STEP 1: Update app.js**

Sub-step 1.1: Navigate to frontend:
```bash
cd /mnt/e/ProgramPractice/govt-scheme-rag/frontend
```

Sub-step 1.2: Edit app.js:
```bash
nano app.js
```

Sub-step 1.3: Replace line 2 with your API URL:
```javascript
const API_ENDPOINT = 'https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/query';
```

Sub-step 1.4: Save (Ctrl+X, Y, Enter)

**STEP 2: Upload to S3**

Sub-step 2.1: Upload:
```bash
aws s3 cp app.js s3://aicloud-bharat-schemes/frontend/app.js --content-type "application/javascript"
```

Sub-step 2.2: Verify:
```bash
aws s3 ls s3://aicloud-bharat-schemes/frontend/
```

**STEP 3: Test end-to-end**

Sub-step 3.1: Open CloudFront URL in browser

Sub-step 3.2: Select language and fill form

Sub-step 3.3: Submit and verify results appear

---

### STAGE 6 — Observability (P1 Important)

**Priority**: Important  
**Goal**: Basic monitoring for production readiness  
**Deliverable**: CloudWatch Logs Insights queries for debugging

---

#### **TASK 27: View Lambda Logs in CloudWatch**

**Status**: [ ]  
**Requirements**: Access Lambda execution logs

**STEP 1: View real-time logs**

Sub-step 1.1: Open terminal

Sub-step 1.2: Run tail command to see live logs:
```bash
aws logs tail /aws/lambda/RAGOrchestratorFunction --since 10m --follow --region ap-south-1
```

Sub-step 1.3: Keep this running in a separate terminal window during testing

Sub-step 1.4: Press Ctrl+C to stop when done

**STEP 2: View historical logs**

Sub-step 2.1: View last 1 hour of logs:
```bash
aws logs tail /aws/lambda/RAGOrchestratorFunction --since 1h --region ap-south-1
```

Sub-step 2.2: Search for errors only:
```bash
aws logs tail /aws/lambda/RAGOrchestratorFunction --since 1h --filter-pattern "ERROR" --region ap-south-1
```

Sub-step 2.3: Search for specific query ID:
```bash
aws logs tail /aws/lambda/RAGOrchestratorFunction --since 1h --filter-pattern "query_id_here" --region ap-south-1
```

---

#### **TASK 28: Query Logs with CloudWatch Insights**

**Status**: [ ]  
**Requirements**: Analyze logs for patterns and errors

**STEP 1: Count errors by type**

Sub-step 1.1: Start query:
```bash
aws logs start-query \
  --log-group-name /aws/lambda/RAGOrchestratorFunction \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @message | filter @message like /ERROR/ | stats count() by @message' \
  --region ap-south-1
```

Sub-step 1.2: Copy the query ID from output

Sub-step 1.3: Get results (replace QUERY_ID):
```bash
aws logs get-query-results --query-id QUERY_ID --region ap-south-1
```

**STEP 2: Find slow requests**

Sub-step 2.1: Query for requests taking >5 seconds:
```bash
aws logs start-query \
  --log-group-name /aws/lambda/RAGOrchestratorFunction \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, @duration | filter @duration > 5000 | sort @duration desc' \
  --region ap-south-1
```

Sub-step 2.2: Get results using query ID from output

**STEP 3: Track query IDs**

Sub-step 3.1: Find all queries in last hour:
```bash
aws logs start-query \
  --log-group-name /aws/lambda/RAGOrchestratorFunction \
  --start-time $(date -d '1 hour ago' +%s) \
  --end-time $(date +%s) \
  --query-string 'fields @timestamp, query_id | filter query_id like //' \
  --region ap-south-1
```

Sub-step 3.2: Get results using query ID from output

---

#### **TASK 29: Monitor Lambda Metrics**

**Status**: [ ]  
**Requirements**: Check Lambda performance metrics

**STEP 1: Check invocation count**

Sub-step 1.1: Get total invocations in last hour:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=RAGOrchestratorFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region ap-south-1
```

Sub-step 1.2: Note the "Sum" value in output

**STEP 2: Check error count**

Sub-step 2.1: Get total errors in last hour:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=RAGOrchestratorFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region ap-south-1
```

Sub-step 2.2: If Sum > 0, investigate using TASK 27 or 28

**STEP 3: Check average duration**

Sub-step 3.1: Get average execution time:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=RAGOrchestratorFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average \
  --region ap-south-1
```

Sub-step 3.2: Average should be <5000ms (5 seconds)

Sub-step 3.3: If higher, check ChromaDB or Bedrock response times

**STEP 4: Check throttles**

Sub-step 4.1: Get throttle count:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Throttles \
  --dimensions Name=FunctionName,Value=RAGOrchestratorFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Sum \
  --region ap-south-1
```

Sub-step 4.2: If Sum > 0, increase Lambda concurrency limit

---

### STAGE 7 — Response Persistence & PDF Export (P2 Optional)

**Priority**: Optional  
**Goal**: S3 Storage + PDF export  
**Deliverable**: Store responses and PDF download

**Note**: Future Scope - button shows "Coming soon". No tasks for prototype.

---

### STAGE 8 — Gatekeeper (P1 Important)

**Priority**: Important  
**Goal**: Similarity threshold check  
**Deliverable**: Logic to validate retrieval quality

**Note**: Gatekeeper logic is integrated in TASK 22 (checks if top_score < 0.3). No additional tasks needed.

---

### STAGE 9 — Testing & Validation (P0 Critical)

**Priority**: Highest  
**Goal**: End-to-end testing and validation  
**Deliverable**: Comprehensive test suite covering all components

---

#### **TASK 35: End-to-End Testing**

**Status**: [ ]  
**Requirements**: Complete system validation

**STEP 1: Test API endpoint**

Sub-step 1.1: Test English query:
```bash
curl -X POST https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/query \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","age":30,"gender":"male","employment":"employed","income_range":"1-3L","state":"tamil_nadu","category":"agriculture","language":"en","query":"What farmer schemes are available?"}'
```

Sub-step 1.2: Verify response contains scheme recommendations

**STEP 2: Test multilingual support**

Sub-step 2.1: Test Hindi:
```bash
curl -X POST https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/query \
  -H "Content-Type: application/json" \
  -d '{"name":"राज","age":28,"gender":"male","employment":"unemployed","income_range":"<1L","state":"uttar_pradesh","category":"education_skill","language":"hi","query":"मुझे शिक्षा योजनाओं के बारे में बताएं"}'
```

Sub-step 2.2: Verify Hindi response

Sub-step 2.3: Test Tamil:
```bash
curl -X POST https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/query \
  -H "Content-Type: application/json" \
  -d '{"name":"முருகன்","age":35,"gender":"male","employment":"self_employed","income_range":"3-5L","state":"tamil_nadu","category":"solar_subsidy","language":"ta","query":"சூரிய மானியம் பெற என்ன செய்ய வேண்டும்?"}'
```

Sub-step 2.4: Verify Tamil response

**STEP 3: Test frontend**

Sub-step 3.1: Open CloudFront URL

Sub-step 3.2: Test English interface

Sub-step 3.3: Test Hindi interface

Sub-step 3.4: Test Tamil interface

Sub-step 3.5: Verify all work correctly

**STEP 4: Performance validation**

Sub-step 4.1: Check Lambda duration:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Duration \
  --dimensions Name=FunctionName,Value=RAGOrchestratorFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --region ap-south-1
```

Sub-step 4.2: Verify avg < 10 seconds

Sub-step 4.3: Check errors:
```bash
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=RAGOrchestratorFunction \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum \
  --region ap-south-1
```

Sub-step 4.4: Verify error count = 0

---