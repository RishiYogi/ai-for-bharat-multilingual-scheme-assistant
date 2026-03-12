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
        modelId='global.amazon.nova-2-lite-v1:0',  # Use inference profile ID
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
