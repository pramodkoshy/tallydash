# TallyDash 🚀

**AI-Powered Tally ERP Dashboard with Natural Language Interactions**

TallyDash is a modern web application that seamlessly integrates with Tally ERP/Prime through ODBC connectivity, providing real-time data visualization, AI-powered analytics, and natural language query capabilities.

## 🌟 Features

- **Real-time Tally Integration**: Direct ODBC connectivity to Tally ERP/Prime
- **AI-Powered Analytics**: Natural language queries powered by OpenAI/Anthropic
- **Interactive Dashboard**: Modern, responsive web interface built with Reflex
- **Comprehensive Reports**: Financial statements, cash flow, and business intelligence
- **Security First**: SQL injection protection and input validation
- **Multi-Company Support**: Handle multiple Tally companies seamlessly
- **Real-time Updates**: Live data synchronization with Tally

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Reflex Web    │    │   Python Backend │    │   Tally ERP     │
│   Frontend      │◄──►│   + AI Services  │◄──►│   ODBC Server   │
│                 │    │                  │    │                 │
│ • Dashboard UI  │    │ • ODBC Connector │    │ • Ledgers       │
│ • AI Chat       │    │ • Data Models    │    │ • Vouchers      │
│ • Visualizations│    │ • Security Layer │    │ • Reports       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Tally ERP/Prime with ODBC enabled
- Node.js 16+ (for Reflex frontend)
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/tallydash.git
cd tallydash
```

2. **Set up Python environment**
```bash
# Using pip
make install-dev

# Using conda
make setup-env
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize Reflex**
```bash
make init
```

5. **Run the application**
```bash
# Development mode
make dev

# Production mode
make run
```

## 🔧 Configuration

### Tally ODBC Setup

1. **Enable ODBC in Tally**:
   - Press `F12` (Configure)
   - Go to Advanced Configuration
   - Enable ODBC Server (default port: 9000)

2. **Test Connection**:
```bash
# Test ODBC connectivity
python -c "from src.tallydash.services import TallyService; print(TallyService().test_connection())"
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TALLY_HOST` | Tally server host | localhost |
| `TALLY_PORT` | Tally ODBC port | 9000 |
| `OPENAI_API_KEY` | OpenAI API key for AI features | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `DEBUG` | Enable debug mode | false |
| `PORT` | Application port | 3000 |

## 📊 Usage

### Dashboard Features

- **Financial Overview**: Real-time metrics and KPIs
- **Interactive Charts**: Sales trends, expense analysis, cash flow
- **Recent Transactions**: Latest vouchers and entries
- **Top Customers/Suppliers**: Performance analytics

### AI-Powered Queries

Ask natural language questions like:

- *"Show me sales for this month"*
- *"What are my top 5 customers by revenue?"*
- *"Analyze cash flow for the last 30 days"*
- *"Show expense breakdown by category"*

### API Endpoints

```python
# Get financial summary
GET /api/financial-summary

# Query vouchers
GET /api/vouchers?type=Sales&date_from=2024-01-01

# AI query
POST /api/ai-query
{
    "query": "Show me top customers",
    "filters": {"date_from": "2024-01-01"}
}
```

## 🛡️ Security

TallyDash implements multiple security layers:

- **SQL Injection Protection**: Parameterized queries and input validation
- **Query Whitelisting**: Only approved SQL patterns allowed
- **Input Sanitization**: All user inputs are cleaned and validated
- **CORS Protection**: Configured allowed origins
- **Session Security**: Secure session management

### Security Best Practices

1. **Network Security**:
   - Restrict Tally ODBC access to trusted IPs
   - Use VPN for remote access
   - Enable firewall rules

2. **Application Security**:
   - Change default secret keys
   - Use HTTPS in production
   - Regular security updates

3. **Data Protection**:
   - Backup your data regularly
   - Monitor access logs
   - Implement user access controls

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test suite
pytest tests/test_tally_service.py -v

# Run with coverage
pytest --cov=src --cov-report=html
```

### Test Coverage

- **Unit Tests**: Service layer, data models, utilities
- **Integration Tests**: Database connectivity, API endpoints
- **Security Tests**: Input validation, SQL injection prevention
- **UI Tests**: Component functionality, user interactions

## 📈 Performance

### Optimization Features

- **Connection Pooling**: Efficient ODBC connection management
- **Query Caching**: Redis-based caching for frequent queries
- **Data Pagination**: Handle large datasets efficiently
- **Lazy Loading**: Components load on demand
- **Background Processing**: Non-blocking operations

### Performance Metrics

- Query response time: < 2 seconds
- Dashboard load time: < 3 seconds
- Real-time data sync: 5-second intervals
- Concurrent users: 50+ supported

## 🐳 Deployment

### Docker Deployment

```bash
# Build and run with Docker
make docker-build
make docker-run

# Access the application
open http://localhost:3000
```

### Production Deployment

1. **Environment Setup**:
```bash
export ENVIRONMENT=production
export DEBUG=false
export SECRET_KEY=your-secure-secret-key
```

2. **Database Setup**:
```bash
# Initialize production database
reflex db init
reflex db migrate
```

3. **Build and Deploy**:
```bash
# Build optimized version
make build

# Export static files
make export

# Deploy to your preferred platform
```

### Supported Platforms

- **Docker**: Containerized deployment
- **AWS**: EC2, ECS, Lambda
- **Azure**: App Service, Container Instances
- **Google Cloud**: Cloud Run, Compute Engine
- **Heroku**: Direct deployment
- **On-Premise**: Linux/Windows servers

## 🔍 Troubleshooting

### Common Issues

**1. ODBC Connection Failed**
```bash
# Check Tally ODBC service
netstat -an | grep 9000

# Verify Tally configuration
# Ensure ODBC Server is enabled in Tally
```

**2. AI Features Not Working**
```bash
# Check API keys
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
```

**3. Slow Performance**
```bash
# Enable Redis caching
pip install redis
export REDIS_HOST=localhost

# Check database indexes
# Optimize Tally data structure
```

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export DEBUG=true
python run.py
```

## 📚 API Documentation

### Data Models

```python
# Company Model
{
    "company_name": "string",
    "start_date": "date",
    "end_date": "date",
    "currency": "string"
}

# Ledger Model
{
    "ledger_name": "string",
    "parent": "string",
    "opening_balance": "decimal",
    "closing_balance": "decimal",
    "is_asset": "boolean"
}

# Voucher Model
{
    "voucher_date": "date",
    "voucher_number": "string",
    "voucher_type": "enum",
    "amount": "decimal",
    "party_name": "string"
}
```

### Service Layer

```python
# TallyService
from tallydash.services import TallyService

service = TallyService()
companies = service.get_companies()
ledgers = service.get_ledgers()
vouchers = service.get_vouchers(voucher_type="Sales")

# AIService
from tallydash.services import AIService

ai_service = AIService()
response = ai_service.process_natural_language_query({
    "query_text": "Show me monthly sales",
    "filters": {"date_from": "2024-01-01"}
})
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md).

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards

- **Python**: Follow PEP 8, use type hints
- **Testing**: Maintain >90% test coverage
- **Documentation**: Document all public APIs
- **Security**: Follow security best practices

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **GitHub Issues**: [Report bugs](https://github.com/yourusername/tallydash/issues)
- **Discussions**: [Community discussions](https://github.com/yourusername/tallydash/discussions)
- **Email**: support@tallydash.com

## 🚧 Roadmap

### Version 2.0 (Planned)
- [ ] Multi-tenant architecture
- [ ] Advanced ML analytics
- [ ] Mobile application
- [ ] Workflow automation
- [ ] Advanced reporting engine

### Version 1.5 (In Progress)
- [x] AI-powered insights
- [x] Real-time dashboards
- [ ] Custom report builder
- [ ] API for third-party integrations

### Version 1.0 (Current)
- [x] Tally ODBC integration
- [x] Basic dashboard
- [x] Security implementation
- [x] Docker deployment

## 🙏 Acknowledgments

- **Reflex Framework**: For the amazing Python web framework
- **Tally Solutions**: For the comprehensive ERP system
- **OpenAI/Anthropic**: For AI capabilities
- **Community**: For feedback and contributions

---

**Built with ❤️ for the Tally community**# tallydash
