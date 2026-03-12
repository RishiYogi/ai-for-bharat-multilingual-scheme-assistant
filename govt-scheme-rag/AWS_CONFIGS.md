# AWS Configuration Reference

This document contains all IAM policies, OpenSearch mappings, and configuration snippets for easy copy-paste during implementation.

## IAM Policies

### 1. SchemeIngestionLambdaRole - S3 Access Policy

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
    },
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::aicloud-bharat-schemes"
    }
  ]
}
```

### 2. SchemeIngestionLambdaRole - Bedrock Access Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v1"
    }
  ]
}
```

### 3. SchemeIngestionLambdaRole - OpenSearch Access Policy

**Note**: Replace `ACCOUNT_ID` with your AWS account ID

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "es:ESHttpPut",
        "es:ESHttpPost",
        "es:ESHttpGet"
      ],
      "Resource": "arn:aws:es:ap-south-1:ACCOUNT_ID:domain/govt-schemes-cluster/*"
    }
  ]
}
```

### 4. RAGOrchestratorLambdaRole - Bedrock Access Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": [
        "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-embed-text-v1",
        "arn:aws:bedrock:ap-south-1::foundation-model/amazon.titan-text-express-v1"
      ]
    }
  ]
}
```

### 5. RAGOrchestratorLambdaRole - OpenSearch Access Policy

**Note**: Replace `ACCOUNT_ID` with your AWS account ID

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "es:ESHttpGet",
        "es:ESHttpPost"
      ],
      "Resource": "arn:aws:es:ap-south-1:ACCOUNT_ID:domain/govt-schemes-cluster/*"
    }
  ]
}
```

### 6. OpenSearch Domain Access Policy

**Note**: Replace `ACCOUNT_ID` with your AWS account ID

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": [
          "arn:aws:iam::ACCOUNT_ID:role/SchemeIngestionLambdaRole",
          "arn:aws:iam::ACCOUNT_ID:role/RAGOrchestratorLambdaRole"
        ]
      },
      "Action": "es:*",
      "Resource": "arn:aws:es:ap-south-1:ACCOUNT_ID:domain/govt-schemes-cluster/*"
    }
  ]
}
```

## OpenSearch Index Mapping

### Create Index with k-NN Mapping

**Index Name**: `govt-schemes-index`

```json
{
  "settings": {
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 512,
      "number_of_shards": 1,
      "number_of_replicas": 1
    }
  },
  "mappings": {
    "properties": {
      "scheme_id": {
        "type": "keyword"
      },
      "scheme_name": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "chunk_text": {
        "type": "text"
      },
      "chunk_index": {
        "type": "integer"
      },
      "department": {
        "type": "keyword"
      },
      "state": {
        "type": "keyword"
      },
      "city": {
        "type": "keyword"
      },
      "source_url": {
        "type": "keyword"
      },
      "last_updated": {
        "type": "date"
      },
      "embedding": {
        "type": "knn_vector",
        "dimension": 1536,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib",
          "parameters": {
            "ef_construction": 512,
            "m": 16
          }
        }
      }
    }
  }
}
```

### Python Script to Create Index

```python
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

# AWS credentials
session = boto3.Session()
credentials = session.get_credentials()
region = 'ap-south-1'
service = 'es'

awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

# OpenSearch client
host = 'YOUR_OPENSEARCH_ENDPOINT'  # e.g., 'search-govt-schemes-cluster-xxx.ap-south-1.es.amazonaws.com'
client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Index mapping
index_body = {
    "settings": {
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 512,
            "number_of_shards": 1,
            "number_of_replicas": 1
        }
    },
    "mappings": {
        "properties": {
            "scheme_id": {"type": "keyword"},
            "scheme_name": {
                "type": "text",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "chunk_text": {"type": "text"},
            "chunk_index": {"type": "integer"},
            "department": {"type": "keyword"},
            "state": {"type": "keyword"},
            "city": {"type": "keyword"},
            "source_url": {"type": "keyword"},
            "last_updated": {"type": "date"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 1536,
                "method": {
                    "name": "hnsw",
                    "space_type": "cosinesimil",
                    "engine": "nmslib",
                    "parameters": {
                        "ef_construction": 512,
                        "m": 16
                    }
                }
            }
        }
    }
}

# Create index
response = client.indices.create(
    index='govt-schemes-index',
    body=index_body
)

print(f"Index created: {response}")
```

## Lambda Environment Variables

### SchemeIngestionFunction

```
OPENSEARCH_ENDPOINT=search-govt-schemes-cluster-xxx.ap-south-1.es.amazonaws.com
INDEX_NAME=govt-schemes-index
BEDROCK_MODEL_ID=amazon.titan-embed-text-v1
S3_BUCKET=aicloud-bharat-schemes
AWS_REGION=ap-south-1
```

### RAGOrchestratorFunction

```
OPENSEARCH_ENDPOINT=search-govt-schemes-cluster-xxx.ap-south-1.es.amazonaws.com
INDEX_NAME=govt-schemes-index
BEDROCK_EMBEDDING_MODEL=amazon.titan-embed-text-v1
BEDROCK_LLM_MODEL=amazon.titan-text-express-v1
AWS_REGION=ap-south-1
```

## S3 Bucket Policy (for CloudFront OAI)

**Note**: Replace `CLOUDFRONT_OAI_ID` with your CloudFront Origin Access Identity ID

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontOAI",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::cloudfront:user/CloudFront Origin Access Identity CLOUDFRONT_OAI_ID"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::aicloud-bharat-schemes-frontend/*"
    }
  ]
}
```

## API Gateway CORS Configuration

```json
{
  "allowOrigins": ["*"],
  "allowMethods": ["POST", "OPTIONS"],
  "allowHeaders": ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key"],
  "maxAge": 300
}
```

## CloudWatch Log Groups

Create these log groups with 30-day retention:

```
/aws/lambda/SchemeIngestionFunction
/aws/lambda/RAGOrchestratorFunction
/aws/apigateway/GovtSchemeAPI
```

## Sample k-NN Query

```python
query_body = {
    "size": 5,
    "query": {
        "knn": {
            "embedding": {
                "vector": query_embedding,  # 1536-dimensional vector
                "k": 5
            }
        }
    },
    "_source": ["scheme_id", "scheme_name", "chunk_text", "department", "state", "city", "source_url"]
}

response = client.search(
    index='govt-schemes-index',
    body=query_body
)
```

## Bedrock API Calls

### Generate Embedding

```python
import boto3
import json

bedrock = boto3.client('bedrock-runtime', region_name='ap-south-1')

def generate_embedding(text):
    body = json.dumps({
        "inputText": text
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=body,
        contentType='application/json',
        accept='application/json'
    )
    
    response_body = json.loads(response['body'].read())
    embedding = response_body['embedding']  # 1536-dimensional vector
    return embedding
```

### Generate LLM Response

```python
def generate_response(prompt):
    body = json.dumps({
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 2048,
            "temperature": 0.3,
            "topP": 0.9,
            "stopSequences": []
        }
    })
    
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-express-v1',
        body=body,
        contentType='application/json',
        accept='application/json'
    )
    
    response_body = json.loads(response['body'].read())
    generated_text = response_body['results'][0]['outputText']
    return generated_text
```

## CloudWatch Alarm Examples

### Lambda Error Rate Alarm

```json
{
  "AlarmName": "SchemeIngestionFunction-HighErrorRate",
  "MetricName": "Errors",
  "Namespace": "AWS/Lambda",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 1,
  "Threshold": 5,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "FunctionName",
      "Value": "SchemeIngestionFunction"
    }
  ],
  "AlarmActions": ["arn:aws:sns:ap-south-1:ACCOUNT_ID:AlarmTopic"]
}
```

### API Gateway 5XX Alarm

```json
{
  "AlarmName": "GovtSchemeAPI-High5XXErrors",
  "MetricName": "5XXError",
  "Namespace": "AWS/ApiGateway",
  "Statistic": "Sum",
  "Period": 300,
  "EvaluationPeriods": 1,
  "Threshold": 10,
  "ComparisonOperator": "GreaterThanThreshold",
  "Dimensions": [
    {
      "Name": "ApiName",
      "Value": "GovtSchemeAPI"
    }
  ],
  "AlarmActions": ["arn:aws:sns:ap-south-1:ACCOUNT_ID:AlarmTopic"]
}
```

## AWS CLI Commands

### Test Bedrock Access

```bash
aws bedrock list-foundation-models --region ap-south-1 --query 'modelSummaries[?contains(modelId, `titan`)]'
```

### Invoke Lambda Manually

```bash
aws lambda invoke \
  --function-name RAGOrchestratorFunction \
  --payload '{"body": "{\"name\":\"Test\",\"age\":30,\"city\":\"Mumbai\",\"language\":\"English\",\"query\":\"solar subsidy\"}"}' \
  --region ap-south-1 \
  response.json
```

### Query OpenSearch

```bash
curl -X GET "https://YOUR_OPENSEARCH_ENDPOINT/govt-schemes-index/_count" \
  --aws-sigv4 "aws:amz:ap-south-1:es" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY"
```

### Upload to S3

```bash
aws s3 cp scheme.pdf s3://aicloud-bharat-schemes/raw/ --region ap-south-1
```

### Invalidate CloudFront Cache

```bash
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

## Notes

- Replace all `ACCOUNT_ID` placeholders with your AWS account ID
- Replace all `YOUR_OPENSEARCH_ENDPOINT` with your actual OpenSearch endpoint
- Replace all `CLOUDFRONT_OAI_ID` with your CloudFront Origin Access Identity ID
- All resources must be in `ap-south-1` region
- Use AWS CLI v2 for best compatibility
