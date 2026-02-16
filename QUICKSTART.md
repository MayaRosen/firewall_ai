# Quick Start Guide - AI Firewall Service

## 🚀 Getting Started in 3 Minutes

### Step 1: Install Dependencies

```bash
# Make sure you're in the project directory
cd "c:\interview\firewall ai"

# Install required packages
pip install -r requirements.txt
```

### Step 2: Start the Service

```bash
# Start the server
python -m app.main
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Test It Out!

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📝 Quick Test Sequence

### 1. Create a Policy (Block SSH)

```bash
curl -X POST "http://localhost:8000/policy" -H "Content-Type: application/json" -d "{\"policy_id\":\"P-001\",\"conditions\":[{\"field\":\"destination_port\",\"operator\":\"=\",\"value\":\"22\"}],\"action\":\"block\"}"
```

### 2. Test Connection (Should BLOCK)

```bash
curl -X POST "http://localhost:8000/connection" -H "Content-Type: application/json" -d "{\"source_ip\":\"192.168.1.10\",\"destination_ip\":\"10.0.0.5\",\"destination_port\":22,\"protocol\":\"TCP\",\"timestamp\":\"2025-04-30T12:34:56Z\"}"
```

Expected response:
```json
{
  "connection_id": "...",
  "decision": "block",
  "anomaly_score": 0.0,
  "matched_policy": "P-001"
}
```

### 3. Test Normal Connection (Should ALLOW)

```bash
curl -X POST "http://localhost:8000/connection" -H "Content-Type: application/json" -d "{\"source_ip\":\"192.168.1.10\",\"destination_ip\":\"10.0.0.5\",\"destination_port\":443,\"protocol\":\"TCP\",\"timestamp\":\"2025-04-30T12:34:56Z\"}"
```

Expected response:
```json
{
  "connection_id": "...",
  "decision": "allow",
  "anomaly_score": 0.42,
  "matched_policy": null
}
```

## 🎯 Using the Interactive Docs

1. Go to http://localhost:8000/docs
2. Click on any endpoint (e.g., "POST /connection")
3. Click "Try it out"
4. Edit the JSON payload
5. Click "Execute"
6. See the response!

## 🧪 Run Tests

```bash
# Run all tests
pytest

# Run tests with output
pytest -v

# Run tests with coverage
pytest --cov=app
```

## 💡 What's Next?

- See [EXAMPLES.md](EXAMPLES.md) for more API request examples
- Read [README.md](README.md) for architecture details
- Check `app/` directory to explore the code

## 🔧 Troubleshooting

### Port already in use?
Change the port in the command:
```bash
python -m app.main
# or
uvicorn app.main:app --port 8001
```

### Import errors?
Make sure you're in the project root directory and dependencies are installed:
```bash
pip install -r requirements.txt
```

### Can't access from another machine?
The server binds to 0.0.0.0 by default, which allows external access. Check your firewall settings.

## 📚 Key Files

- `app/main.py` - FastAPI application entry point
- `app/routes/` - API endpoints
- `app/services/` - Business logic
- `app/models/` - Data models (Pydantic)
- `README.md` - Full documentation
- `EXAMPLES.md` - API request examples

Enjoy! 🎉
