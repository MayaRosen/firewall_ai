# Example API Requests for AI Firewall Service

## Prerequisites
Make sure the service is running on http://localhost:8000

```bash
python -m app.main
```

## Health Check

```bash
curl -X GET "http://localhost:8000/health"
```

## 1. Create Security Policies

### Policy P-001: Block port 22 (SSH)
```bash
curl -X POST "http://localhost:8000/policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "P-001",
    "conditions": [
      {"field": "destination_port", "operator": "=", "value": "22"}
    ],
    "action": "block"
  }'
```

### Policy P-002: Block specific source IP on port 443
```bash
curl -X POST "http://localhost:8000/policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "P-002",
    "conditions": [
      {"field": "destination_port", "operator": "=", "value": "443"},
      {"field": "source_ip", "operator": "=", "value": "192.168.1.100"}
    ],
    "action": "block"
  }'
```

### Policy P-003: Alert on Telnet connections
```bash
curl -X POST "http://localhost:8000/policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "P-003",
    "conditions": [
      {"field": "destination_port", "operator": "=", "value": "23"}
    ],
    "action": "alert"
  }'
```

### Policy P-004: Allow HTTP traffic
```bash
curl -X POST "http://localhost:8000/policy" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_id": "P-004",
    "conditions": [
      {"field": "destination_port", "operator": "=", "value": "80"}
    ],
    "action": "allow"
  }'
```

## 2. Submit Connections for Evaluation

### Connection 1: Normal HTTPS traffic (should ALLOW with low AI score)
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

### Connection 2: SSH attempt (should BLOCK via policy P-001)
```bash
curl -X POST "http://localhost:8000/connection" \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.15",
    "destination_ip": "10.0.0.10",
    "destination_port": 22,
    "protocol": "TCP",
    "timestamp": "2025-04-30T12:35:00Z"
  }'
```

### Connection 3: Suspicious IP on HTTPS (should BLOCK via policy P-002)
```bash
curl -X POST "http://localhost:8000/connection" \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.100",
    "destination_ip": "10.0.0.5",
    "destination_port": 443,
    "protocol": "TCP",
    "timestamp": "2025-04-30T12:36:00Z"
  }'
```

### Connection 4: Telnet attempt (should ALERT via policy + high AI score)
```bash
curl -X POST "http://localhost:8000/connection" \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.20",
    "destination_ip": "10.0.0.8",
    "destination_port": 23,
    "protocol": "TCP",
    "timestamp": "2025-04-30T12:37:00Z"
  }'
```

### Connection 5: HTTP traffic (should ALLOW via policy P-004)
```bash
curl -X POST "http://localhost:8000/connection" \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.25",
    "destination_ip": "10.0.0.20",
    "destination_port": 80,
    "protocol": "TCP",
    "timestamp": "2025-04-30T12:38:00Z"
  }'
```

### Connection 6: Unknown port with no policy (AI-based decision)
```bash
curl -X POST "http://localhost:8000/connection" \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.30",
    "destination_ip": "10.0.0.30",
    "destination_port": 8080,
    "protocol": "TCP",
    "timestamp": "2025-04-30T12:39:00Z"
  }'
```

### Connection 7: RDP attempt (high AI score, should BLOCK)
```bash
curl -X POST "http://localhost:8000/connection" \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.35",
    "destination_ip": "10.0.0.40",
    "destination_port": 3389,
    "protocol": "TCP",
    "timestamp": "2025-04-30T12:40:00Z"
  }'
```

## 3. Retrieve Connection Details

Replace {connection_id} with actual ID from previous response:

```bash
curl -X GET "http://localhost:8000/connection/{connection_id}"
```

Example:
```bash
curl -X GET "http://localhost:8000/connection/550e8400-e29b-41d4-a716-446655440000"
```

## 4. Update a Policy

Update policy P-003 to block instead of alert:

```bash
curl -X PUT "http://localhost:8000/policy/P-003" \
  -H "Content-Type: application/json" \
  -d '{
    "conditions": [
      {"field": "destination_port", "operator": "=", "value": "23"}
    ],
    "action": "block"
  }'
```

## 5. Get Specific Policy

```bash
curl -X GET "http://localhost:8000/policy/P-001"
```

## 6. Delete a Policy

```bash
curl -X DELETE "http://localhost:8000/policy/P-004"
```

## PowerShell Examples (Windows)

### Create Policy (PowerShell)
```powershell
$body = @{
    policy_id = "P-001"
    conditions = @(
        @{
            field = "destination_port"
            operator = "="
            value = "22"
        }
    )
    action = "block"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/policy" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

### Submit Connection (PowerShell)
```powershell
$body = @{
    source_ip = "192.168.1.10"
    destination_ip = "10.0.0.5"
    destination_port = 443
    protocol = "TCP"
    timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/connection" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

## Expected Behaviors

| Connection | Source IP | Port | Expected Decision | Reason |
|------------|-----------|------|-------------------|---------|
| 1 | 192.168.1.10 | 443 | ALLOW | No policy match, low AI score |
| 2 | 192.168.1.15 | 22 | BLOCK | Policy P-001 (SSH blocked) |
| 3 | 192.168.1.100 | 443 | BLOCK | Policy P-002 (suspicious IP) |
| 4 | 192.168.1.20 | 23 | ALERT/BLOCK | Policy P-003 + high AI score |
| 5 | 192.168.1.25 | 80 | ALLOW | Policy P-004 (HTTP allowed) |
| 6 | 192.168.1.30 | 8080 | ALLOW/ALERT | AI-based (depends on score) |
| 7 | 192.168.1.35 | 3389 | BLOCK | High AI score (RDP suspicious) |
