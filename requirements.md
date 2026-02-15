# Requirements Document

## Introduction

The Multilingual Government Scheme Assistant is an AI-powered system designed to help rural Indian citizens discover government welfare schemes they are eligible for. The system uses Retrieval-Augmented Generation (RAG) with a multilingual large language model to interpret complex eligibility conditions from official government scheme documents, providing simplified explanations in regional languages and suggesting next steps for application.

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
- **Vector_Database**: The database storing embedded scheme documents for semantic search
- **LLM**: The multilingual large language model used for interpretation and generation
- **Department_Category**: A classification of schemes by domain (Agriculture, Housing, Employment, Education, Startup, Business Loan, Water, Electricity, Solar)
- **Scheme_Document**: Official government documentation in PDF format from public portals
- **Structured_JSON**: The converted format of scheme documents for RAG processing

## Requirements

### Requirement 1: Minimal User Input Collection

**User Story:** As a rural citizen, I want to provide minimal information to get started, so that I can quickly find relevant schemes without lengthy forms.

#### Acceptance Criteria

1. THE System SHALL collect city, preferred language, communication mode (voice or text), and department category as required inputs
2. WHEN a user selects a preferred language, THE System SHALL display all subsequent interactions in that language
3. THE System SHALL present department categories as a predefined list including Agriculture, Housing, Employment, Education, Startup, Business Loan, Water, Electricity, and Solar
4. WHEN a user selects communication mode, THE System SHALL enable either voice input/output or text input/output accordingly
5. THE System SHALL support input in Hindi, English, Tamil, Telugu, Bengali, Marathi, Gujarati, Kannada, Malayalam, and Punjabi
6. WHEN eligibility checking requires additional information, THE System SHALL optionally collect age, gender, and educational qualification
7. WHEN optional information is requested, THE System SHALL explain why it is needed for specific scheme eligibility
8. THE System SHALL allow users to skip optional fields and still receive general scheme recommendations

### Requirement 2: Scheme PDF Collection and Conversion

**User Story:** As a system administrator, I want to collect scheme PDFs from official government portals, so that the system has authentic and up-to-date scheme information.

#### Acceptance Criteria

1. THE System SHALL ingest PDF documents from official government portals including MyScheme, state government websites, and ministry portals
2. WHEN a PDF is ingested, THE System SHALL extract text content preserving structure and formatting
3. WHEN text is extracted, THE System SHALL convert it to structured JSON format with fields for scheme name, department, eligibility criteria, benefits, and application process
4. WHEN JSON conversion is complete, THE System SHALL validate the structure against a predefined schema
5. THE System SHALL store the original PDF URL and last updated timestamp with each converted scheme

### Requirement 3: Vector Database Indexing

**User Story:** As a system administrator, I want structured scheme data indexed in a vector database, so that the RAG system can efficiently retrieve relevant schemes.

#### Acceptance Criteria

1. WHEN structured JSON is created, THE System SHALL chunk each scheme document into semantically meaningful segments of 200-500 words
2. WHEN chunks are created, THE RAG_Engine SHALL generate multilingual embeddings using a model supporting all 10 supported languages
3. WHEN embeddings are generated, THE Vector_Database SHALL store them with metadata including scheme name, department category, state, and source URL
4. THE Vector_Database SHALL support semantic similarity search with cosine distance metric
5. WHEN scheme documents are updated, THE System SHALL re-index only the modified schemes

### Requirement 4: Department-Based Scheme Retrieval

**User Story:** As a rural citizen, I want to see schemes from my selected department category, so that I get relevant information without being overwhelmed.

#### Acceptance Criteria

1. WHEN a user selects a department category, THE RAG_Engine SHALL filter schemes to only that department
2. WHEN a department filter is applied, THE Vector_Database SHALL retrieve the top 10 most relevant schemes from that department based on the user's city
3. WHEN multiple schemes are retrieved, THE System SHALL rank them by relevance score combining semantic similarity and geographic applicability
4. THE System SHALL include both central government and state-specific schemes applicable to the user's city
5. WHEN no schemes match the department and city combination, THE System SHALL suggest the closest available schemes from neighboring regions

### Requirement 5: LLM-Based Contextual Explanation

**User Story:** As a rural citizen with limited literacy, I want scheme information explained in simple language in my regional language, so that I can understand complex eligibility conditions.

#### Acceptance Criteria

1. WHEN relevant schemes are retrieved, THE LLM SHALL generate a simplified explanation in the user's preferred language
2. THE System SHALL include the scheme name, key benefits, eligibility summary, and application process in the explanation
3. WHEN generating explanations, THE LLM SHALL use vocabulary appropriate for users with basic literacy levels
4. THE LLM SHALL interpret complex eligibility conditions contextually rather than using rigid rule-based matching
5. WHEN technical terms are unavoidable, THE System SHALL provide simple definitions in parentheses

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

### Requirement 10: Offline Capability

**User Story:** As a rural citizen with limited internet connectivity, I want to access basic scheme information offline, so that I can use the system even without internet.

#### Acceptance Criteria

1. THE System SHALL cache the most common 50 schemes per department category for offline access
2. WHEN internet connectivity is unavailable, THE System SHALL perform RAG-based retrieval using cached embeddings and scheme data
3. WHEN operating offline, THE System SHALL clearly indicate that recommendations are based on cached data
4. WHEN connectivity is restored, THE System SHALL sync with the latest scheme information from the vector database
5. THE System SHALL prioritize caching schemes applicable to the user's state based on usage patterns

### Requirement 11: Voice Input and Output Support

**User Story:** As a rural citizen with limited literacy, I want to use voice to interact with the system, so that I can access schemes without typing.

#### Acceptance Criteria

1. WHEN a user selects voice communication mode, THE System SHALL enable speech-to-text for all supported regional languages
2. WHEN voice input is received, THE System SHALL transcribe speech to text with at least 85% accuracy
3. WHEN transcription confidence is below 70%, THE System SHALL ask the user to repeat the input
4. WHEN schemes are retrieved, THE System SHALL provide text-to-speech output in the user's preferred language
5. WHEN voice mode is active, THE System SHALL confirm understood information before proceeding to retrieval

### Requirement 12: Performance and Scalability

**User Story:** As a system administrator, I want the RAG system to handle high user volumes efficiently, so that rural citizens get fast responses during peak times.

#### Acceptance Criteria

1. WHEN a user submits a query, THE System SHALL return scheme recommendations within 3 seconds
2. THE System SHALL support at least 1000 concurrent users without performance degradation
3. WHEN vector database similarity search is performed, THE System SHALL return top-k results within 500 milliseconds
4. THE System SHALL cache frequently accessed embeddings and scheme JSON in memory
5. WHEN system load exceeds 80% capacity, THE System SHALL scale horizontally by adding compute resources

### Requirement 13: Dynamic Scheme Updates

**User Story:** As a system administrator, I want the system to handle dynamic scheme updates from government portals, so that users always get current information.

#### Acceptance Criteria

1. THE System SHALL check official government portals for scheme updates on a weekly basis
2. WHEN a scheme PDF is updated on the source portal, THE System SHALL detect the change by comparing timestamps or checksums
3. WHEN an update is detected, THE System SHALL re-process the PDF through the conversion and indexing pipeline
4. WHEN re-indexing is complete, THE Vector_Database SHALL replace old embeddings with updated ones atomically
5. THE System SHALL maintain a version history showing when each scheme was last updated
