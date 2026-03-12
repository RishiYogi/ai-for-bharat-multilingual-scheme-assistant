# Requirements Document

## Introduction

The Multilingual Government Scheme Assistant is a hybrid serverless AI-powered system designed to help rural Indian citizens discover government welfare schemes they are eligible for. The system uses Retrieval-Augmented Generation (RAG) with Amazon Bedrock's Titan and Nova models and ChromaDB vector database to interpret complex eligibility conditions from official government scheme documents, providing simplified explanations in regional languages and suggesting next steps for application.

**Prototype Scope**: This requirements document describes the full vision. The initial prototype focuses on core RAG functionality with text-based interaction, ChromaDB vector storage on EC2, and static web frontend. Voice support and offline capabilities are reserved for future iterations.

## Why Rule-Based Systems Fail and AI is Required

Government scheme eligibility involves complex, contextual conditions that cannot be effectively handled by traditional rule-based systems:

**Complex and Contextual Eligibility Rules**: Scheme eligibility criteria are not simple yes/no conditions. They involve nuanced interpretations such as "small and marginal farmers," "economically weaker sections," or "priority given to women-headed households." These terms require contextual understanding that varies by state, district, and socio-economic context.

**Language Diversity and Semantic Understanding**: India has 22 official languages and hundreds of dialects. Rural citizens express their needs in regional languages using varied vocabulary. Keyword matching and static translation fail to capture semantic intent. For example, a farmer asking about "खेती के लिए मदद" (help for farming) should match schemes about agricultural subsidies, irrigation support, and crop insurance - not just exact keyword matches.

**Dynamic and Evolving Schemes**: Government schemes are frequently updated, merged, or replaced. New schemes are launched regularly. Rule-based systems require manual updates to decision trees and filters for every change, making them impossible to maintain at scale across hundreds of schemes and multiple languages.

**Socio-Economic Variation**: Eligibility criteria adapt based on local conditions. Income thresholds, land ownership limits, and priority categories differ between states. A rigid rule-based system cannot handle this geographic and demographic variation without exponential complexity.

**AI Semantic Reasoning is Essential**: Large language models with RAG provide:
- **Contextual interpretation** of eligibility conditions rather than rigid pattern matching
- **Multilingual semantic understanding** that captures intent across languages
- **Adaptive retrieval** from a knowledge base that can be updated without rewriting rules
- **Natural language explanation** of complex criteria in simple, regional language

This is why AI is not just beneficial but necessary for making government schemes accessible to rural India at scale.

## Glossary

- **System**: The Multilingual Government Scheme Assistant
- **User**: A rural Indian citizen seeking information about government schemes
- **Scheme**: A government welfare program with specific eligibility criteria
- **RAG_Engine**: The Retrieval-Augmented Generation component that retrieves and processes scheme information
- **Vector_Database**: ChromaDB vector database on EC2 (prototype) or Amazon OpenSearch Service (production)
- **LLM**: Amazon Bedrock Nova 2 Lite (global.amazon.nova-2-lite-v1:0) used for interpretation and generation
- **Embedding_Model**: Amazon Bedrock Titan Embeddings V2 (amazon.titan-embed-text-v2:0) for generating 1024-dimensional vectors
- **Scheme_Document**: Official government documentation in PDF format from public portals
- **ChromaDB_Service**: FastAPI application running on EC2 serving vector search endpoints
- **VectorStore_Interface**: Abstract interface allowing pluggable vector database backends

## Implementation Stages

The system is developed incrementally across 9 stages:

1. **STAGE 1 — AWS Infrastructure Setup**: S3 buckets, IAM roles, Bedrock access (✅ Completed)
2. **STAGE 2 — Frontend Deployment**: 3-page multilingual UI with CloudFront (✅ Completed)
3. **STAGE 3 — ChromaDB Vector Service on EC2**: FastAPI service with /add, /search, /health, /delete, /delete_all, /rebuild, /stats, /collections endpoints (✅ Completed)
4. **STAGE 4 — Ingestion Pipeline**: PDF → chunks → embeddings → ChromaDB (✅ Completed)
5. **STAGE 5 — RAG Orchestrator**: Query → embedding → ChromaDB → retrieved chunks → Bedrock (✅ Completed)
6. **STAGE 6 — Observability**: CloudWatch Logs Insights queries for debugging (✅ Completed)
7. **STAGE 7 — Response Persistence & PDF Export**: S3 storage + download API (⏳ Future Scope)
8. **STAGE 8 — Gatekeeper**: Similarity threshold check before LLM invocation (✅ Completed - integrated in RAG Orchestrator)
9. **STAGE 9 — Testing & Validation**: End-to-end test suite (⏳ Pending)

## Requirements

### Requirement 1: Minimal User Input Collection

**User Story:** As a rural citizen, I want to provide minimal information to get started, so that I can quickly find relevant schemes without lengthy forms.

#### Acceptance Criteria

1. THE System SHALL collect name, age, state, category, community, physically_challenged, preferred language, and query as required inputs
2. THE System SHALL optionally collect gender as an additional filter
3. THE System SHALL provide a state dropdown with all 36 Indian states and union territories using snake_case values (e.g., tamil_nadu, andhra_pradesh, delhi)
4. THE System SHALL provide a category dropdown with 8 values: Education & Skills, Startup and Self Employment, Agriculture, Health Care, Solar Subsidy, Housing Aid, Water & Sanitation, Other Schemes
5. THE System SHALL map category display values to API values: education_skill, startup_selfemployment, agriculture, healthcare, solar_subsidy, housing_aid, water_sanitation, others
6. THE category field SHALL be REQUIRED input for all queries
7. THE state field SHALL be REQUIRED input for all queries to enable state-based filtering
8. THE community field SHALL be REQUIRED input with values: General, OBC, PVTG, SC, ST, DNT
9. THE physically_challenged field SHALL be REQUIRED input with values: Yes, No
10. WHEN a user selects a preferred language, THE System SHALL display all subsequent interactions in that language
11. THE System SHALL support 3 languages: English (default), Hindi, Tamil
12. THE System SHALL translate all UI elements (labels, buttons, dropdown options, error messages) to the selected language
13. THE System SHALL NOT collect sensitive personal information including Aadhaar numbers, bank details, date of birth, or government IDs
14. THE System SHALL provide a simple web form with clear labels and validation for required fields
15. THE System SHALL allow users to submit queries without registration or account creation
16. WHEN optional fields (gender) are skipped, THE System SHALL still return general scheme recommendations
17. THE API request payload SHALL include: name, age, gender, state, community, physically_challenged, category, language, and query
18. THE API values for all fields SHALL remain in English (snake_case) regardless of UI language

**Prototype Note**: The state field replaces the city field to enable better state-based scheme filtering. All dropdown options are translated to the selected language while API values remain in English for backend compatibility.

### Requirement 2: Automated PDF Ingestion Pipeline with Enhanced Metadata

**User Story:** As a system administrator, I want to upload scheme PDFs to S3 and have them automatically processed with rich metadata, so that the system can perform precise category and state-based filtering during retrieval.

#### Acceptance Criteria

1. WHEN a PDF is uploaded to the S3 raw/ folder, THE System SHALL automatically trigger the ingestion Lambda function
2. THE System SHALL extract text content from PDFs preserving structure and formatting using pdfplumber or PyMuPDF
3. THE System SHALL chunk extracted text using token-based splitting with the following configuration:
   - Chunk size: 700 tokens
   - Overlap: 120 tokens
4. THE System SHALL generate embeddings for each chunk using Amazon Bedrock Titan Embeddings V2 (amazon.titan-embed-text-v2:0) producing 1024-dimensional vectors
5. THE System SHALL store embeddings and metadata in the ChromaDB vector database via the ChromaDB API
6. THE System SHALL include the following metadata for each chunk:
   - `scheme_name`: Official name of the scheme
   - `category`: One of (education_skill, solar_subsidy, startup_selfemployment, housing_aid, water_sanitation, agriculture, healthcare, others)
   - `state`: State code (e.g., tamil_nadu, maharashtra) OR "all" for central/pan-India schemes
   - `eligible_gender`: Gender eligibility (any, male, female)
   - `eligible_minage`: Minimum age requirement (0-120)
   - `eligible_maxage`: Maximum age requirement (0-120)
   - `eligible_community`: Community eligibility (any, general, obc, pvtg, sc, st, dnt)
   - `eligible_physically_challenged`: Physically challenged eligibility (any, yes, no)
7. WHEN a scheme applies to all states, THE metadata state field SHALL be set to "all"
8. WHEN a scheme is state-specific, THE metadata state field SHALL use the snake_case state code (e.g., "tamil_nadu", "andhra_pradesh")
9. WHEN processing is complete, THE System SHALL move the PDF from raw/ to processed/ folder
10. THE System SHALL log all processing steps to CloudWatch for audit and debugging
11. THE System SHALL handle processing failures gracefully with retry logic and error notifications

**Prototype Note**: Manual PDF upload to S3 is used instead of automated web scraping. Administrators upload 5-10 sample scheme PDFs for prototype evaluation. Category and state metadata must be specified during upload (e.g., via filename convention or S3 object tags).

### Requirement 3: Pluggable Vector Database Architecture with Enhanced Metadata Storage

**User Story:** As a system architect, I want a pluggable vector database layer with rich metadata support, so that the system can start with ChromaDB for prototyping and migrate to OpenSearch for production without changing application code.

#### Acceptance Criteria

1. THE System SHALL implement a VectorStore abstract interface with methods: add_documents(), search(), delete_index(), health_check()
2. THE System SHALL provide a ChromaDBVectorStore implementation that communicates with the ChromaDB FastAPI service on EC2
3. THE System SHALL provide an OpenSearchVectorStore placeholder implementation for future migration
4. THE System SHALL use a VectorStoreFactory that selects the backend based on VECTOR_DB_TYPE environment variable
5. THE Lambda functions SHALL use VectorStoreFactory.get_store() and never directly reference ChromaDB or OpenSearch
6. WHEN VECTOR_DB_TYPE is "chromadb", THE System SHALL use the ChromaDB backend on EC2
7. WHEN VECTOR_DB_TYPE is "opensearch", THE System SHALL use the OpenSearch Service backend (future)
8. THE ChromaDB service SHALL persist the collection to disk storage (/data/chroma) and reload on startup
9. THE ChromaDB service SHALL use cosine similarity for vector search matching Titan Embeddings V2 dimension (1024)
10. THE ChromaDB service SHALL store metadata alongside embeddings including: scheme_name, category, state
11. THE vector storage format SHALL be: vector_id → {text_chunk, scheme_name, category, state}
12. THE metadata SHALL enable filtering by category and state before or after vector search

**Prototype Note**: ChromaDB on EC2 t3.micro is the default for cost optimization. The collection uses 1024 dimensions to match Titan Embeddings V2. Migration to OpenSearch Service requires only changing the environment variable and implementing the OpenSearchVectorStore class.

### Requirement 4: Semantic Scheme Retrieval with Category and State Filtering

**User Story:** As a rural citizen, I want the system to understand my query semantically and return relevant schemes filtered by my selected category and state, so that I get highly targeted results.

#### Acceptance Criteria

1. WHEN a user submits a query, THE System SHALL generate a query embedding using Amazon Bedrock Titan Embeddings V2 (1024 dimensions)
2. THE System SHALL perform k-NN similarity search in the vector database with k=5 to retrieve the top 5 most relevant chunks
3. THE System SHALL use inner product (IP) as the distance metric for vector search (matching IndexFlatIP configuration)
4. THE System SHALL filter results based on user's selected category using metadata filtering
5. THE System SHALL filter results based on user's selected state using the following logic:
   - Include chunks where metadata.state == user_selected_state
   - OR include chunks where metadata.state == "all" (central/pan-India schemes)
6. THE filtering logic SHALL be: `(metadata.category == user_category) AND (metadata.state == user_state OR metadata.state == "all")`
7. WHEN no results match the category and state filters, THE System SHALL perform a fallback search without category filtering
8. THE System SHALL rank results by relevance score (similarity score from vector search)
9. WHEN no results have similarity score above 0.4, THE System SHALL return a "no relevant schemes found" message
10. THE System SHALL return results within 500 milliseconds for the vector search operation
11. THE retrieval configuration SHALL use top_k=5 to balance relevance and noise

**Example**: User selects state="tamil_nadu" and category="solar_subsidy"
- System retrieves chunks with (category="solar_subsidy") AND (state="tamil_nadu" OR state="all")
- This returns Tamil Nadu-specific solar schemes + Central solar schemes
- Excludes Karnataka solar schemes and Tamil Nadu agriculture schemes

**Prototype Note**: Category and state-based filtering significantly improves retrieval precision by narrowing results to the user's specific needs. The fallback mechanism ensures users still get results even if no exact matches exist.

### Requirement 5: LLM-Based Contextual Explanation with Eligibility Reasoning

**User Story:** As a rural citizen with limited literacy, I want scheme information explained in simple language with clear eligibility reasoning, so that I understand why I may qualify and what benefits I can receive.

#### Acceptance Criteria

1. WHEN relevant schemes are retrieved, THE System SHALL use Amazon Bedrock Nova 2 Lite to generate a simplified explanation in the user's preferred language
2. THE System SHALL construct prompts that include user profile information: age, gender, state, income_range, category
3. THE prompt template SHALL instruct the LLM to explain:
   - Which schemes the user may qualify for
   - Why they may be eligible (based on age, state, income, category)
   - Key benefits of each scheme
   - Steps or links to apply
4. THE System SHALL use vocabulary appropriate for users with basic literacy levels (Flesch Reading Ease > 60)
5. THE LLM SHALL interpret complex eligibility conditions contextually rather than using rigid rule-based matching
6. WHEN technical terms are unavoidable, THE System SHALL provide simple definitions in parentheses
7. THE System SHALL construct prompts with clear instructions to respond only based on retrieved context
8. THE System SHALL implement guardrails to prevent hallucination by requiring source citations for all claims
9. THE System SHALL generate responses within 2 seconds (p95 latency)
10. THE response format SHALL include structured sections for each scheme:
    - Scheme Name
    - Why you may qualify (eligibility reasoning with checkmarks)
    - Benefits (bulleted list)
    - How to apply (steps or links)
11. THE System SHALL respond in the user's selected language (English, Hindi, or Tamil) without requiring translation services

**Example Prompt Structure**:
```
You are an AI assistant helping Indian citizens discover government welfare schemes.

User Profile:
- Age: {age}
- Gender: {gender}
- State: {state}
- Income Range: {income_range}
- Category: {category}

Retrieved Scheme Information:
{context_chunks}

Based on the user's profile and the scheme information above, recommend relevant government schemes.

For each scheme, explain:
1. Which schemes the user may qualify for
2. Why they may be eligible (based on age, state, income, etc.)
3. Key benefits of the scheme
4. Steps or links to apply

User's Question: {query}

Respond in English. Keep explanations simple and clear.
```

**Note**: The `{language}` placeholder will be replaced with the full language name ("English", "Hindi", or "Tamil") based on the user's selection. The RAG Orchestrator converts the ISO-639-1 code received from the frontend ("en", "hi", "ta") to the full language name before constructing the prompt.

**Prototype Note**: The enhanced prompt template improves reasoning quality by providing user context to the LLM. Nova 2 Lite supports multilingual generation natively, eliminating the need for translation services.

### Requirement 6: Source Citation and Transparency

**User Story:** As a user, I want to know where the scheme information comes from, so that I can trust the recommendations and verify details.

#### Acceptance Criteria

1. WHEN a scheme is recommended, THE System SHALL display the official source document name and URL from the government portal
2. WHEN eligibility criteria are explained, THE System SHALL cite the specific document section or page number used by the RAG system
3. THE System SHALL indicate the last updated date of the scheme document
4. WHEN the LLM cannot determine eligibility with confidence, THE System SHALL explicitly state uncertainty and suggest contacting officials
5. THE System SHALL provide a confidence score for each scheme recommendation based on retrieval relevance

### Requirement 7: Privacy and Minimal Data Storage

**User Story:** As a rural citizen, I want my information to be kept private with minimal data collection, so that I feel safe using the system.

#### Acceptance Criteria

1. THE System SHALL only store city, preferred language, communication mode, and department category - no personally identifiable information
2. WHEN user interactions are logged, THE System SHALL anonymize all logs by removing any identifying information
3. WHEN user data is transmitted, THE System SHALL use TLS encryption for all network communications
4. THE System SHALL not require user registration or account creation for basic scheme search
5. WHEN a user session ends, THE System SHALL clear all temporary user preferences unless explicitly saved

### Requirement 8: Bias Monitoring and Fairness

**User Story:** As a system administrator, I want to monitor for bias in scheme recommendations, so that all user groups receive fair access to information.

#### Acceptance Criteria

1. THE System SHALL log scheme recommendations with associated city and department category for analysis
2. THE LLM SHALL not use demographic assumptions to filter schemes - only explicit eligibility criteria from official documents
3. THE System SHALL track recommendation distribution across different cities and states on a monthly basis
4. WHEN recommendation disparities exceed 30% between comparable regions for the same department, THE System SHALL generate an alert for review
5. THE System SHALL provide an audit trail showing which document chunks were retrieved for each recommendation

### Requirement 9: Application Guidance

**User Story:** As a rural citizen, I want clear next steps for applying to schemes, so that I know what to do after finding relevant schemes.

#### Acceptance Criteria

1. WHEN a scheme is recommended, THE System SHALL extract and display step-by-step application instructions from the scheme document
2. THE System SHALL include required documents, application deadlines, and contact information for local offices
3. WHEN online application is available, THE System SHALL provide the direct application URL from the official portal
4. WHEN offline application is required, THE System SHALL provide the nearest office location based on user's city
5. THE System SHALL indicate estimated processing time when available in the scheme document

### Requirement 10: Offline Capability (Future Scope)

**User Story:** As a rural citizen with limited internet connectivity, I want to access basic scheme information offline, so that I can use the system even without internet.

**Status**: Deferred to future iterations. The prototype requires internet connectivity.

#### Acceptance Criteria (Future Implementation)

1. THE System SHALL cache the most common 50 schemes per department category for offline access
2. WHEN internet connectivity is unavailable, THE System SHALL perform RAG-based retrieval using cached embeddings and scheme data
3. WHEN operating offline, THE System SHALL clearly indicate that recommendations are based on cached data
4. WHEN connectivity is restored, THE System SHALL sync with the latest scheme information from the vector database
5. THE System SHALL prioritize caching schemes applicable to the user's state based on usage patterns

**Prototype Note**: Offline capability requires Progressive Web App (PWA) implementation with service workers and IndexedDB. This is not included in the initial prototype to maintain simplicity and focus on core RAG functionality.

### Requirement 11: Voice Input and Output Support (Future Scope)

**User Story:** As a rural citizen with limited literacy, I want to use voice to interact with the system, so that I can access schemes without typing.

**Status**: Deferred to future iterations. The prototype uses text-based interaction only.

#### Acceptance Criteria (Future Implementation)

1. WHEN a user selects voice communication mode, THE System SHALL enable speech-to-text for all supported regional languages
2. WHEN voice input is received, THE System SHALL transcribe speech to text with at least 85% accuracy using Amazon Transcribe
3. WHEN transcription confidence is below 70%, THE System SHALL ask the user to repeat the input
4. WHEN schemes are retrieved, THE System SHALL provide text-to-speech output in the user's preferred language using Amazon Polly
5. WHEN voice mode is active, THE System SHALL confirm understood information before proceeding to retrieval

**Prototype Note**: Voice support requires integration with Amazon Transcribe and Amazon Polly, adding complexity and cost. The prototype focuses on text-based interaction via a simple web form. Voice can be added in future iterations once core RAG functionality is validated.

### Requirement 12: Performance and Scalability

**User Story:** As a system administrator, I want the RAG system to handle user requests efficiently, so that rural citizens get fast responses.

#### Acceptance Criteria

1. WHEN a user submits a query, THE System SHALL return scheme recommendations within 3 seconds (p95 latency)
2. THE System SHALL support at least 100 concurrent users without performance degradation (prototype scale)
3. WHEN vector database similarity search is performed, THE System SHALL return top-k results within 200 milliseconds
4. THE Lambda functions SHALL have reserved concurrency limits to prevent runaway costs
5. THE API Gateway SHALL implement throttling at 100 requests/second to prevent abuse
6. THE FAISS service on EC2 SHALL handle at least 50 requests/second for vector search
7. THE System SHALL use CloudWatch metrics to monitor latency, errors, and throughput
8. WHEN system errors exceed 5%, THE System SHALL trigger CloudWatch alarms

**Prototype Note**: The prototype is optimized for evaluation with 100 concurrent users. Production scaling to 1000+ users requires migrating to OpenSearch Service with multi-node clusters and implementing caching layers.

### Requirement 13: Manual Scheme Updates

**User Story:** As a system administrator, I want to manually upload new scheme PDFs to keep the system updated, so that users always get current information.

#### Acceptance Criteria

1. THE System SHALL provide an S3 bucket with a raw/ folder for administrators to upload scheme PDFs
2. WHEN a PDF is uploaded to the raw/ folder, THE System SHALL automatically trigger the ingestion pipeline within 1 minute
3. THE System SHALL process the PDF, generate embeddings, and store them in the vector database
4. WHEN processing is complete, THE System SHALL move the PDF to the processed/ folder
5. THE System SHALL log all ingestion activities to CloudWatch for audit
6. THE System SHALL send SNS notifications on ingestion success or failure
7. THE System SHALL support re-processing of existing schemes by uploading with the same filename
8. THE System SHALL maintain idempotency to prevent duplicate processing of the same PDF

**Prototype Note**: Automated web scraping and scheduled updates are deferred to future iterations. The prototype uses manual PDF upload to S3 for simplicity and cost control. Administrators upload 5-10 sample scheme PDFs for evaluation.

### Requirement 14: Multilingual 3-Page Frontend with CloudFront

**User Story:** As a rural citizen, I want to access the system through a simple web interface with language selection, so that I can easily submit queries and view results in my preferred language with all UI elements translated.

#### Acceptance Criteria

1. THE System SHALL provide a static HTML/JavaScript frontend hosted on Amazon S3
2. THE System SHALL distribute the frontend via Amazon CloudFront for fast global access
3. THE frontend SHALL implement a 3-page flow: Language Selection → User Input Form → Results Display
4. **Page 1 - Language Selection**: THE System SHALL display 3 language tiles (English, Hindi, Tamil) for user selection with English as the default language
5. WHEN a user selects a language, THE System SHALL dynamically populate all dropdown options (state, category, gender, income) in the selected language
6. **Page 2 - User Input Form**: THE System SHALL provide a form with fields for name, age, gender, state, category, income range, and query
7. THE state dropdown SHALL display all 36 Indian states and union territories translated to the selected language
8. THE category dropdown SHALL display 8 categories translated to the selected language: Education & Skills, Startup and Self Employment, Agriculture, Health Care, Solar Subsidy, Housing Aid, Water & Sanitation, Other Schemes
9. THE gender dropdown SHALL display options translated to the selected language: Male, Female, Other, Prefer not to say
10. THE income dropdown SHALL display ranges translated to the selected language: Unemployed, Less than 1 Lakh, 1-3 Lakhs, 3-5 Lakhs, 5-10 Lakhs, More than 10 Lakhs
11. THE frontend SHALL validate required fields (name, age, state, category, query) before submission
12. THE frontend SHALL send API values in English (snake_case) regardless of UI language
13. THE frontend SHALL use HTTPS for all communications with the API Gateway
14. **Page 3 - Results Display**: THE System SHALL display scheme results with scheme name, eligibility reasoning, benefits, application steps, and source citations
15. THE results page SHALL include a "Download as PDF" button placeholder (Future Scope)
16. THE results page SHALL include a "Back" button to return to the input form
17. THE frontend SHALL display confidence scores (High/Medium/Low) for each scheme recommendation
18. THE frontend SHALL provide error messages for failed requests with actionable guidance in the selected language
19. THE CloudFront URL SHALL serve as the permanent demo link for evaluation
20. THE frontend SHALL work on mobile devices with responsive design
21. THE frontend SHALL use vanilla JavaScript to dynamically populate dropdowns from translation objects

**Prototype Note**: The frontend implements full multilingual UI with all dropdown options translated dynamically using JavaScript. The translation object includes all 36 states, 8 categories, gender options, and income ranges in English, Hindi, and Tamil. API values remain in English for backend compatibility.

### Requirement 15: PDF Export Capability (Future Scope - STAGE 7)

**User Story:** As a user, I want to download scheme results as PDF for offline reference, so that I can review recommendations without internet access.

**Status**: Future Scope - to be implemented in STAGE 7 (Response Persistence & PDF Export) after core functionality is validated.

#### Acceptance Criteria

1. THE results page SHALL include a "Download as PDF" button
2. WHEN the download button is clicked, THE System SHALL generate a PDF containing all scheme details shown on screen
3. THE PDF SHALL include the user's query, timestamp, and all scheme recommendations with eligibility, benefits, and application steps
4. THE PDF SHALL be formatted for readability with proper spacing, headers, and sections
5. THE System SHALL store generated PDFs in the S3 bucket download/ folder
6. THE PDF SHALL include source citations for each scheme recommendation
7. THE PDF SHALL be generated in the user's selected language
8. THE System SHALL generate and deliver the PDF within 5 seconds of button click

**Prototype Note**: PDF export is marked as Future Scope and will be implemented in STAGE 7 (Response Persistence & PDF Export). This feature requires PDF generation library integration (e.g., jsPDF or server-side PDF generation with ReportLab/WeasyPrint) and additional S3 storage configuration.

---

## Prototype vs Production Scope

### Included in Prototype

✅ **Core RAG Functionality**:
- PDF ingestion with S3 event triggers
- Text extraction and semantic chunking
- Embedding generation with Bedrock Titan Embeddings V2 (1024 dimensions)
- ChromaDB vector database on EC2
- k-NN similarity search with category-based metadata filtering
- LLM-based explanation with Bedrock Nova 2 Lite
- Multilingual support (3 languages: English, Hindi, Tamil)

✅ **User Interface**:
- 3-page frontend flow: Language Selection → User Input Form → Results Display
- Full multilingual UI (all labels, buttons, error messages in selected language)
- Category dropdown with 5 scheme categories
- CloudFront distribution (permanent demo link)
- Text-based interaction
- Responsive design for mobile
- Back navigation from results to input form

✅ **Infrastructure**:
- AWS Lambda for serverless compute
- API Gateway for REST endpoints
- S3 for storage
- CloudWatch for monitoring
- IAM roles for security

✅ **Architecture**:
- Pluggable VectorStore interface
- Easy migration path to OpenSearch
- Cost-optimized for free tier

### Deferred to Future Iterations

❌ **PDF Export Feature** (Requirement 15):
- Download as PDF button functionality
- PDF generation with user query and results
- S3 download/ folder storage
- Multilingual PDF formatting
- Note: To be implemented in STAGE 7 (Response Persistence & PDF Export) after core functionality is validated

❌ **Voice Support** (Requirement 11):
- Amazon Transcribe for speech-to-text
- Amazon Polly for text-to-speech
- Voice mode toggle in UI

❌ **Offline Capability** (Requirement 10):
- Progressive Web App (PWA)
- Service workers and IndexedDB
- Cached embeddings for offline search

❌ **Automated Web Scraping**:
- Scheduled crawling of government portals
- Automatic change detection
- Version history tracking

❌ **Advanced Features**:
- User authentication and accounts
- Personalized recommendations
- Feedback and rating system
- Analytics dashboard

### Migration Path to Production

When scaling from prototype to production:

1. **Vector Database**: Change `VECTOR_DB_TYPE` from "chromadb" to "opensearch"
2. **Implement OpenSearchVectorStore**: Same interface, boto3 client
3. **Deploy OpenSearch Service**: 3-node cluster with k-NN plugin
4. **Add Caching**: ElastiCache for frequent queries
5. **Add Voice**: Integrate Transcribe and Polly
6. **Add Offline**: Implement PWA with service workers
7. **Add Analytics**: Track usage patterns and popular schemes
8. **Scale Infrastructure**: Increase Lambda concurrency, add CloudFront edge locations

## Summary

This requirements document describes a hybrid serverless RAG-based system for government scheme discovery. The prototype focuses on core functionality with ChromaDB vector database, text-based interaction, and a 3-page frontend flow with full multilingual UI support and category-based filtering. The architecture is designed for easy migration to production-grade infrastructure (OpenSearch Service) without changing application code.

**Key Design Principles**:
- **Cost-Optimized**: Free tier eligible components ($6-12/month)
- **Pluggable Architecture**: Easy migration from ChromaDB to OpenSearch
- **Minimal Complexity**: Simple, stable, reliable for evaluation
- **Scalable Foundation**: Clear path to production scaling

**Evaluation Criteria**:
- Functional RAG pipeline with accurate scheme retrieval
- Multilingual support with quality explanations
- 3-page frontend flow with language selection, user input form, and results display
- Category-based filtering for targeted scheme recommendations
- Fast response times (<3 seconds)
- Stable permanent demo link (CloudFront URL)
- Clean, maintainable code with proper documentation
