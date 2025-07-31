# Telegram Coaching Bot

A content-agnostic Telegram coaching bot that ingests coaching materials, vectorizes them, and provides intelligent responses via any LLM backend.

## Architecture

```
client ──▶ ingress-bot (NestJS)
                 │
                 ▼
         LLM-gateway (interface + adapters)
                 │
                 ▼
       retrieval-svc (FastAPI + Chroma)
                 │
        ┌────────┴────────┐
        ▼                 ▼
 ingest-worker     postgres/redis
```

## Features

- **Multi-LLM Support**: Switch between OpenAI, Anthropic, or local Ollama
- **Document Ingestion**: Automatically process PDFs, DOCX, Markdown, and more
- **Vector Search**: Fast semantic search using ChromaDB
- **Audit Logging**: Complete audit trail for compliance and analytics
- **Scalable**: Microservices architecture with independent scaling
- **Production Ready**: Docker, CI/CD, and Terraform infrastructure

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Telegram Bot Token
- LLM API Key (OpenAI/Anthropic)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd telegram-coaching-bot
   make setup
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

3. **Start services**:
   ```bash
   make dev
   ```

4. **Ingest documents**:
   ```bash
   # Add your coaching materials to ./corpus/
   make ingest
   ```

5. **Test the bot**:
   - Send a message to your Telegram bot
   - The bot will respond with coaching guidance

### Environment Variables

Key environment variables in `.env`:

```bash
# Telegram Bot
TELEGRAM_TOKEN=your_bot_token

# LLM Configuration
LLM_PROVIDER=openai  # openai, anthropic, ollama
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Service URLs
RETRIEVAL_URL=http://retrieval-service:8080
LLM_GATEWAY_URL=http://ingress-bot:3000
```

## Services

### Ingress Bot (NestJS + Telegraf)
- Handles Telegram webhook updates
- Orchestrates retrieval and LLM calls
- Manages response streaming and audit logging

### LLM Gateway
- Provider-agnostic interface for LLM calls
- Supports OpenAI, Anthropic, and Ollama
- Centralized token usage and cost tracking

### Retrieval Service (FastAPI + ChromaDB)
- Vector search for relevant document chunks
- Embedding generation and storage
- Health checks and monitoring

### Ingest Worker
- Automated document processing
- Supports multiple file formats (PDF, DOCX, etc.)
- Incremental updates with file change detection

## Development

### Running Tests
```bash
make test-ingress    # Jest tests for ingress bot
make test-retrieval  # PyTest tests for retrieval service
```

### Building Services
```bash
make build           # Build all services
make build-ingress   # Build only ingress bot
```

### Logs and Monitoring
```bash
make logs            # All service logs
make logs-ingress    # Ingress bot logs only
make health          # Service health checks
```

## Production Deployment

### AWS Infrastructure

The project includes Terraform configurations for AWS:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

This provisions:
- ECS Fargate cluster
- Application Load Balancer
- RDS PostgreSQL
- ElastiCache Redis
- ECR repositories
- VPC and security groups

### CI/CD Pipeline

GitHub Actions workflow includes:
- Multi-service testing
- Security scanning
- Docker image building
- Infrastructure validation

## API Reference

### Retrieval Service

**Search for relevant documents**:
```bash
POST /search
{
  "query": "How to build resilience?",
  "k": 5
}
```

**Add documents to vector store**:
```bash
POST /add
{
  "texts": ["document text..."],
  "metadata": [{"source": "file.pdf"}]
}
```

### LLM Gateway

**Generate completion**:
```bash
POST /v1/completions
{
  "model": "gpt-4o-mini",
  "prompt": "system prompt + user question",
  "stream": false,
  "max_tokens": 512
}
```

## Message Flow

1. **User sends message** → Telegram delivers to `/telegram/webhook`
2. **Ingress Bot** calls Retrieval Service → gets top-k relevant chunks
3. **Ingress Bot** builds prompt with system directive + chunks + user question
4. **LLM Gateway** forwards to configured provider (OpenAI/Anthropic/Ollama)
5. **LLM** returns answer + token usage
6. **Ingress Bot** streams response to Telegram & logs audit

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Create a GitHub issue
- Check the documentation
- Review the test examples 