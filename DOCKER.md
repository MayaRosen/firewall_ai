# Docker Deployment Guide

This guide covers how to deploy the AI Firewall backend using Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

Build and run the container:

```bash
# Build the image
docker-compose build

# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

The API will be available at `http://localhost:8000`

## Docker Commands

### Build Image

```bash
docker build -t firewall-ai:latest .
```

### Run Container Manually

```bash
docker run -d \
  --name firewall-ai \
  -p 8000:8000 \
  -e ENV=production \
  firewall-ai:latest
```

### Container Management

```bash
# View running containers
docker ps

# View logs
docker logs firewall-ai
docker logs -f firewall-ai  # Follow logs

# Execute commands in container
docker exec -it firewall-ai bash
docker exec -it firewall-ai python -c "print('Hello')"

# Stop container
docker stop firewall-ai

# Remove container
docker rm firewall-ai

# View container resource usage
docker stats firewall-ai
```

## Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View logs
docker-compose logs -f firewall-ai

# Scale services (if needed)
docker-compose up -d --scale firewall-ai=3

# Execute command in service
docker-compose exec firewall-ai pytest
```

## Environment Variables

Create a `.env` file for environment-specific configuration:

```env
ENV=production
LOG_LEVEL=info
```

The `.env` file is mounted as read-only in the container.

## Health Checks

The container includes a health check that pings the `/health` endpoint:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' firewall-ai

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' firewall-ai
```

## Image Optimization

The production image is optimized for size:

- Based on `python:3.13-slim` (~150MB)
- Multi-stage build principles
- No cache for pip packages
- Runs as non-root user for security

## Networking

### Access from Host

The service is exposed on port 8000:

```bash
curl http://localhost:8000/health
```

### Container-to-Container Communication

Services communicate via the `firewall-network`:

```yaml
networks:
  firewall-network:
    driver: bridge
```

## Security Best Practices

1. **Non-root User**: Container runs as `appuser` (UID 1000)
2. **Read-only Volumes**: `.env` mounted as read-only
3. **No Secrets in Image**: Use environment variables or mounted secrets
4. **Health Checks**: Automatic container restart on failure

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker-compose logs firewall-ai
```

### Permission Issues

If you encounter permission issues with volumes:
```bash
# On Linux/Mac
sudo chown -R 1000:1000 ./app

# Or run container as root (not recommended)
docker-compose exec --user root firewall-ai bash
```

### Port Already in Use

Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8080:8000"  # Host:Container
```

### Clear Everything and Start Fresh

```bash
# Stop and remove containers, networks
docker-compose down

# Remove images
docker rmi firewall-ai:latest

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

## Testing in Docker

Run tests inside the container:

```bash
# Using docker-compose
docker-compose exec firewall-ai pytest

# Using docker directly
docker exec -it firewall-ai pytest -v

# Run specific test file
docker-compose exec firewall-ai pytest tests/test_api.py
```

## Production Considerations

1. **Use orchestration**: Consider Kubernetes or Docker Swarm for production
2. **Add reverse proxy**: Use nginx or Traefik for SSL/TLS and load balancing
3. **External database**: Replace in-memory storage with PostgreSQL/Redis
4. **Monitoring**: Add Prometheus/Grafana for metrics
5. **Logging**: Use centralized logging (ELK stack, Splunk)
6. **Secrets management**: Use Docker secrets or external vault

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
- name: Build Docker image
  run: docker build -t firewall-ai:${{ github.sha }} .

- name: Run tests in container
  run: |
    docker run --rm firewall-ai:${{ github.sha }} pytest

- name: Push to registry
  run: |
    docker tag firewall-ai:${{ github.sha }} registry.example.com/firewall-ai:latest
    docker push registry.example.com/firewall-ai:latest
```

## Updating the Application

To update with new code:

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
