# AI Firewall Backend Service

A professional, enterprise-grade backend service for an AI-driven network firewall. This service evaluates network connections using rule-based security policies and AI-powered anomaly detection to make real-time security decisions.

## 📋 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Running the Service](#running-the-service)
- [API Documentation](#api-documentation)
- [Design Decisions](#design-decisions)
- [Testing](#testing)
- [Project Structure](#project-structure)

## ✨ Features

- **Policy Management**: Create, update, retrieve, and delete security policies
- **Real-time Connection Evaluation**: Process network connections and make instant security decisions
- **AI-Powered Anomaly Detection**: ML-based scoring for suspicious connection patterns
- **Intelligent Decision Engine**: Combines policy rules with AI insights
- **RESTful API**: Clean, well-documented HTTP endpoints
- **Professional Architecture**: Service layer, repository pattern, dependency injection
- **Comprehensive Error Handling**: Custom exceptions and proper HTTP status codes
- **Interactive Documentation**: Auto-generated Swagger UI and ReDoc
- **Health Monitoring**: Built-in health check endpoint

## 🏗️ Architecture

### Layered Architecture

The application follows a professional layered architecture pattern:

```
┌─────────────────────────────────────┐
│         API Layer (Routes)          │  ← FastAPI routers
├─────────────────────────────────────┤
│      Business Logic (Services)      │  ← Core logic & orchestration
├─────────────────────────────────────┤
│    Data Access (Repositories)       │  ← Storage abstraction
├─────────────────────────────────────┤
│          Data Models                │  ← Pydantic models
└─────────────────────────────────────┘
```

### Decision Logic Flow

```
Connection Request
       ↓
  Check Policies (OR logic - ANY condition match)
       ↓
  Policy Match Found?
   ├─ Yes → Action = allow/block? → Return Immediate Decision
   │         Action = alert? → Continue to AI
   └─ No → Get AI Anomaly Score
               ↓
         Apply AI Thresholds:
         • > 0.8  → BLOCK
         • 0.5-0.8 → ALERT  
         • < 0.5  → ALLOW
```

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Setup Steps

1. **Clone or navigate to the project directory**
   ```bash
   cd "c:\interview\firewall ai"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🎯 Running the Service

### Development Mode

```bash
# From the project root directory
python -m app.main
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The service will start on `http://localhost:8000`

### Access Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Documentation

### Quick Testing

**Postman Collection**: Import [postman_collection.json](postman_collection.json) into Postman for a complete collection of all API endpoints.

**Curl Examples**: See [API_EXAMPLES.md](API_EXAMPLES.md) for comprehensive curl command examples.

**Interactive Docs**: Visit http://localhost:8000/docs to test endpoints directly in your browser.

### Submit Connection for Evaluation

**POST /connection**

```bash
curl -X POST "http://localhost:8000/connection" \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.10",
    "destination_ip": "10.0.0.5",
    "destination_port": 443,
    "protocol": "TCP",
    "timestamp": "2025-04-30T12:34:56Z"
  }'
```

Response:
```json
{
  "connection_id": "550e8400-e29b-41d4-a716-446655440000",
  "decision": "allow",
  "anomaly_score": 0.42,
  "matched_policy": null
}
```

### Create Security Policy

**POST /policy**

```bash
curl -X POST "http://localhost:8000/policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "P-002",
    "conditions": [
      {"field": "destination_port", "operator": "=", "value": "443"},
      {"field": "source_ip", "operator": "=", "value": "192.168.1.10"}
    ],
    "action": "block"
  }'
```

Response:
```json
{
  "policy_id": "P-002",
  "status": "created",
  "message": "Policy successfully created"
}
```

### Update Policy

**PUT /policy/{policy_id}**

```bash
curl -X PUT "http://localhost:8000/policy/P-002" \
  -H "Content-Type: application/json" \
  -d '{
    "conditions": [
      {"field": "destination_port", "operator": "=", "value": "80"}
    ],
    "action": "alert"
  }'
```

### Get Connection Details

**GET /connection/{connection_id}**

```bash
curl -X GET "http://localhost:8000/connection/550e8400-e29b-41d4-a716-446655440000"
```

## 🎨 Design Decisions

### 1. Layered Architecture

**Why**: Separation of concerns, maintainability, testability
- **Routes Layer**: Pure HTTP handling, no business logic
- **Services Layer**: Business logic, orchestration between components
- **Repository Layer**: Data access abstraction, easy to swap implementations
- **Models Layer**: Type safety and validation with Pydantic

### 2. Policy Matching Logic: OR (ANY)

**Decision**: If ANY condition in a policy matches, the policy triggers
**Rationale**: 
- More flexible for security rules
- Allows blocking multiple threat vectors with one policy
- Matches requirement specification

### 3. AI Scoring Approach

**Mock Implementation**: 
- Random baseline scores
- Elevated scores for known suspicious IPs/ports
- Simulates real ML model behavior

**Production Approach**:
- Replace with actual ML model (scikit-learn, TensorFlow, PyTorch)
- Use feature engineering: packet size, frequency, time-of-day patterns
- Implement model versioning and A/B testing
- Add model retraining pipeline

### 4. PostgreSQL Database

**Implementation**: Raw SQL with connection pooling via psycopg3

**Why PostgreSQL**:
- **ACID Compliance**: Critical for security policies - no data loss or corruption
- **JSONB Support**: Native JSON storage for flexible policy conditions without schema migrations
- **Performance**: Excellent indexing (B-tree, GIN for JSONB) and query optimization
- **Reliability**: Proven stability in enterprise environments, robust backup/recovery
- **Scalability**: Handles high-throughput connection logging with proper indexing
- **Raw SQL Choice**: Direct control over queries, no ORM overhead, easier performance tuning

**Schema Design**:
- Policies table with JSONB conditions for flexible rule matching
- Connections table with foreign key to matched policies
- Strategic indexes: primary keys, foreign keys, timestamp ranges
- Auto-update triggers for timestamp management

### 5. Error Handling Strategy

- Custom exception hierarchy for domain errors
- HTTP-appropriate status codes
- Structured error responses
- Comprehensive logging at all layers

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services.py
```

### Test Structure

Tests should cover:
- **Unit Tests**: Individual services, policy evaluation logic
- **Integration Tests**: API endpoints with mocked dependencies
- **E2E Tests**: Full flow from API to storage

## 📁 Project Structure

```
firewall ai/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   │
│   ├── models/                 # Pydantic data models
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── policy.py
│   │
│   ├── routes/                 # API endpoints
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── policy.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── connection_service.py
│   │   ├── policy_service.py
│   │   ├── decision_service.py
│   │   └── ai_service.py
│   │
│   ├── repositories/           # Data access
│   │   ├── __init__.py
│   │   └── storage.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       └── exceptions.py
│
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

Configuration via environment variables (`.env` file):

```env
# Application
APP_NAME=AI Firewall Service
APP_VERSION=1.0.0
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO

# AI Thresholds
AI_SCORE_THRESHOLD_BLOCK=0.8
AI_SCORE_THRESHOLD_ALERT=0.5
```

## 🚧 Known Limitations

1. **Mock AI Model**: Currently uses simplified scoring algorithm instead of trained ML model
2. **No Authentication**: Production requires API keys, OAuth, or JWT authentication
3. **No Rate Limiting**: Missing per-client request throttling
4. **Single Instance**: No horizontal scaling or load balancing implemented
5. **Basic Monitoring**: Limited metrics and observability features
6. **No Policy Versioning**: Policy changes aren't tracked historically

## 🔮 Future Enhancements

1. **Real AI Model**: Train actual ML model with feature engineering (packet size, frequency, behavioral patterns)
2. **Time-Series Optimization**: Consider TimescaleDB for connection log analytics
3. **Caching Layer**: Redis for policy evaluation caching and rate limiting
4. **Authentication**: JWT-based API authentication with role-based access control
5. **Rate Limiting**: Per-client request throttling with token bucket algorithm
6. **Metrics & Monitoring**: Prometheus + Grafana for real-time observability
7. **Async Processing**: Message queue (RabbitMQ/Kafka) for high-throughput connection processing
8. **Policy Versioning**: Audit trail for policy changes with rollback capability
9. **Horizontal Scaling**: Load balancing with multiple service instances
10. **Advanced Analytics**: ML-based threat intelligence and pattern detection

## 📝 License

This is a prototype assessment project.

## 👤 Author

Developed as part of the AI Firewall Engineering Assessment
