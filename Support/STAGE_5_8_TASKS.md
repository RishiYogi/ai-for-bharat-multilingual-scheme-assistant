# STAGE 5-8 Tasks (WSL-Compatible)

## TASK 22: RAG Orchestrator Lambda Code

Create `~/aws-lambda/rag-orchestrator/lambda_function.py` with this code:

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

## TASK 22 Deployment Steps

```bash
# From ~/aws-lambda/rag-orchestrator
rm -rf package
mkdir package
pip install --target ./package boto3 requests python-dotenv
cp lambda_function.py package/
python3 -c "import shutil; shutil.make_archive('rag-orchestrator', 'zip', 'package')"
ls -lh rag-orchestrator.zip
```

## TASK 23: Deploy RAG Lambda

```bash
# Get IAM role ARN
aws iam get-role --role-name RAGOrchestratorLambdaRole --query 'Role.Arn' --output text

# Create Lambda
aws lambda create-function \
  --function-name RAGOrchestratorFunction \
  --runtime python3.11 \
  --role arn:aws:iam::442004016723:role/RAGOrchestratorLambdaRole \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://rag-orchestrator.zip \
  --timeout 30 \
  --memory-size 512 \
  --region ap-south-1

# Configure environment
aws lambda update-function-configuration \
  --function-name RAGOrchestratorFunction \
  --environment Variables="{CHROMA_API_URL=http://65.0.91.246:8000,CHROMA_API_KEY=my-super-secret-key-54321}" \
  --region ap-south-1
```

## TASK 24: Create API Gateway

```bash
# Create API
aws apigatewayv2 create-api \
  --name GovernmentSchemeAPI \
  --protocol-type HTTP \
  --region ap-south-1

# Save API ID
API_ID=<paste_from_output>

# Create integration
aws apigatewayv2 create-integration \
  --api-id $API_ID \
  --integration-type AWS_PROXY \
  --integration-uri arn:aws:lambda:ap-south-1:442004016723:function:RAGOrchestratorFunction \
  --payload-format-version 2.0 \
  --region ap-south-1

# Save Integration ID
INTEGRATION_ID=<paste_from_output>

# Create route
aws apigatewayv2 create-route \
  --api-id $API_ID \
  --route-key 'POST /query' \
  --target integrations/$INTEGRATION_ID \
  --region ap-south-1

# Create stage
aws apigatewayv2 create-stage \
  --api-id $API_ID \
  --stage-name '$default' \
  --auto-deploy \
  --region ap-south-1

# Get endpoint URL
echo "https://$API_ID.execute-api.ap-south-1.amazonaws.com"

# Add Lambda permission
aws lambda add-permission \
  --function-name RAGOrchestratorFunction \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:ap-south-1:442004016723:$API_ID/*/*" \
  --region ap-south-1

# Enable CORS
aws apigatewayv2 update-api \
  --api-id $API_ID \
  --cors-configuration AllowOrigins='*',AllowMethods='POST,OPTIONS',AllowHeaders='Content-Type' \
  --region ap-south-1
```

## TASK 25: Update Frontend

```bash
# Navigate to frontend (Windows filesystem is OK for editing)
cd /mnt/e/ProgramPractice/govt-scheme-rag/frontend

# Edit app.js - replace API_ENDPOINT with your API Gateway URL
nano app.js

# Upload to S3
aws s3 cp app.js s3://aicloud-bharat-schemes/frontend/app.js --content-type "application/javascript"

# Test in browser
# Open CloudFront URL and submit a test query
```

## STAGE 8: Observability (TASK 26)

```bash
# Create CloudWatch dashboard
cat > dashboard-config.json << 'EOF'
{
  "widgets": [
    {
      "type": "metric",
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
          [".", "Errors", {"stat": "Sum"}],
          [".", "Duration", {"stat": "Average"}]
        ],
        "period": 300,
        "region": "ap-south-1",
        "title": "Lambda Metrics"
      }
    }
  ]
}
EOF

aws cloudwatch put-dashboard \
  --dashboard-name GovtSchemeRAG \
  --dashboard-body file://dashboard-config.json \
  --region ap-south-1
```

## STAGE 9: Testing (TASK 27)

```bash
# Test API endpoint
curl -X POST https://YOUR_API_ID.execute-api.ap-south-1.amazonaws.com/query \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","age":30,"gender":"male","community":"general","physically_challenged":"no","state":"tamil_nadu","category":"agriculture","language":"en","query":"What farmer schemes are available?"}'
```
