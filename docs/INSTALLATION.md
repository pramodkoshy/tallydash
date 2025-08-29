# Installation Guide

This guide will help you install and configure TallyDash on your system.

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 18.04+
- **Python**: 3.9 or higher
- **Memory**: 4 GB RAM
- **Storage**: 2 GB free space
- **Network**: Internet connection for AI features

### Recommended Requirements
- **Operating System**: Windows 11, macOS 12+, or Ubuntu 20.04+
- **Python**: 3.11 or higher
- **Memory**: 8 GB RAM
- **Storage**: 5 GB free space
- **CPU**: Multi-core processor for better performance

### Software Dependencies
- **Tally ERP/Prime**: Version 6.0 or higher with ODBC enabled
- **Node.js**: Version 16 or higher (for Reflex frontend)
- **Redis**: Optional, for caching (recommended for production)
- **Git**: For version control and updates

## Pre-Installation Steps

### 1. Tally Configuration

Before installing TallyDash, ensure Tally ERP/Prime is configured correctly:

1. **Enable ODBC Server in Tally**:
   ```
   • Open Tally ERP/Prime
   • Press F12 (Configure)
   • Navigate to Advanced Configuration
   • Set "Enable ODBC Server" to "Yes"
   • Set ODBC Port (default: 9000)
   • Save configuration and restart Tally
   ```

2. **Verify ODBC Connectivity**:
   ```bash
   # On Windows, check if port is open
   netstat -an | findstr 9000
   
   # On Linux/macOS
   netstat -an | grep 9000
   ```

3. **Configure Data Access**:
   - Ensure the company you want to access is loaded in Tally
   - Set appropriate user permissions if using Tally's security features

### 2. Python Environment Setup

#### Option A: Using Conda (Recommended)

1. **Install Anaconda or Miniconda**:
   ```bash
   # Download from https://www.anaconda.com/
   # Or install Miniconda for a lighter footprint
   ```

2. **Create Python Environment**:
   ```bash
   conda create -n tallydash python=3.11
   conda activate tallydash
   ```

#### Option B: Using venv

1. **Check Python Version**:
   ```bash
   python --version  # Should be 3.9 or higher
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv tallydash-env
   
   # Activate on Windows
   tallydash-env\Scripts\activate
   
   # Activate on Linux/macOS
   source tallydash-env/bin/activate
   ```

### 3. Node.js Setup

#### Option A: Direct Download
1. Visit [nodejs.org](https://nodejs.org/)
2. Download and install Node.js 16 LTS or higher

#### Option B: Using Package Manager

**Windows (Chocolatey)**:
```bash
choco install nodejs
```

**macOS (Homebrew)**:
```bash
brew install node
```

**Ubuntu/Debian**:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## Installation Methods

### Method 1: Quick Installation (Recommended)

1. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/tallydash.git
   cd tallydash
   ```

2. **Run Setup Script**:
   ```bash
   # This will install dependencies and set up the environment
   make install-dev
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

4. **Initialize Application**:
   ```bash
   make init
   ```

### Method 2: Manual Installation

1. **Clone Repository**:
   ```bash
   git clone https://github.com/yourusername/tallydash.git
   cd tallydash
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit Hooks**:
   ```bash
   pre-commit install
   ```

4. **Install Node.js Dependencies**:
   ```bash
   npm install  # If package.json exists
   ```

### Method 3: Docker Installation

1. **Install Docker**:
   ```bash
   # Follow instructions at https://docs.docker.com/get-docker/
   ```

2. **Clone and Build**:
   ```bash
   git clone https://github.com/yourusername/tallydash.git
   cd tallydash
   make docker-build
   ```

3. **Run Container**:
   ```bash
   make docker-run
   ```

## Configuration

### 1. Environment Configuration

Create and configure your environment file:

```bash
cp .env.example .env
```

Edit `.env` with your specific configuration:

```env
# Tally ODBC Settings
TALLY_HOST=localhost
TALLY_PORT=9000
ODBC_DRIVER=Tally ODBC Driver

# AI Service Keys (optional but recommended)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Settings
PORT=3000
DEBUG=false
SECRET_KEY=your-secure-secret-key

# Database Settings (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
```

### 2. Reflex Configuration

The `rxconfig.py` file contains Reflex-specific settings:

```python
import reflex as rx

config = rx.Config(
    app_name="tallydash",
    frontend_port=3000,
    backend_port=8000,
    db_url="sqlite:///reflex.db",
    # Add custom configurations
)
```

### 3. Logging Configuration

Configure logging in your environment:

```env
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

## Verification

### 1. Test Installation

```bash
# Test Python environment
python -c "import tallydash; print('TallyDash imported successfully')"

# Test Reflex
reflex --version

# Test Tally connection
python -c "from src.tallydash.services import TallyService; print(TallyService().test_connection())"
```

### 2. Run Application

```bash
# Development mode
make dev

# Or directly
reflex run
```

### 3. Access Application

Open your browser and navigate to:
- **Local**: http://localhost:3000
- **Network**: http://your-ip-address:3000

You should see the TallyDash dashboard with connection status.

## Post-Installation Setup

### 1. AI Services Setup (Optional)

If you want to use AI features:

1. **OpenAI Setup**:
   - Get API key from https://platform.openai.com/
   - Add to `.env`: `OPENAI_API_KEY=your_key`

2. **Anthropic Setup**:
   - Get API key from https://console.anthropic.com/
   - Add to `.env`: `ANTHROPIC_API_KEY=your_key`

### 2. Redis Setup (Production)

For production deployments with caching:

#### Windows:
```bash
# Using Chocolatey
choco install redis-64

# Or download from Redis website
```

#### macOS:
```bash
brew install redis
brew services start redis
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 3. Database Setup

Initialize the database:

```bash
# Initialize Reflex database
reflex db init

# Run migrations if any
reflex db migrate
```

## Troubleshooting

### Common Installation Issues

#### Issue 1: Python Version Conflicts
```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m pip install -e ".[dev]"
```

#### Issue 2: ODBC Connection Failed
```bash
# Check Tally is running
# Verify ODBC is enabled in Tally
# Test port connectivity
telnet localhost 9000
```

#### Issue 3: Node.js Issues
```bash
# Check Node.js version
node --version
npm --version

# Clear npm cache if needed
npm cache clean --force
```

#### Issue 4: Permission Issues (Linux/macOS)
```bash
# Fix Python package permissions
pip install --user -e ".[dev]"

# Or use sudo (not recommended)
sudo pip install -e ".[dev]"
```

#### Issue 5: Reflex Build Issues
```bash
# Clear Reflex cache
rm -rf .web

# Reinstall Reflex
pip uninstall reflex
pip install reflex

# Initialize again
reflex init
```

### Performance Optimization

1. **Enable Caching**:
   ```env
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

2. **Adjust Connection Pool**:
   ```env
   MAX_CONNECTIONS=10
   CONNECTION_TIMEOUT=30
   ```

3. **Optimize Query Limits**:
   ```env
   MAX_QUERY_RESULTS=5000
   QUERY_TIMEOUT=60
   ```

## Security Considerations

### 1. Network Security
- Configure firewall to limit Tally ODBC access
- Use VPN for remote access
- Enable HTTPS in production

### 2. Application Security
- Change default secret keys
- Use strong passwords
- Regular security updates

### 3. Data Protection
- Regular backups
- Access logging
- User access controls

## Uninstallation

If you need to uninstall TallyDash:

### Complete Removal

```bash
# Remove Python environment
conda remove -n tallydash --all

# Or for venv
rm -rf tallydash-env

# Remove application files
rm -rf tallydash

# Remove Redis (if installed)
# Windows: choco uninstall redis-64
# macOS: brew uninstall redis
# Linux: sudo apt remove redis-server
```

### Partial Removal (Keep Data)

```bash
# Just remove Python packages
pip uninstall -y $(pip freeze | grep -v "^-e")

# Keep configuration and data files
```

## Getting Help

If you encounter issues during installation:

1. **Check System Requirements**: Ensure all prerequisites are met
2. **Review Logs**: Check installation and application logs
3. **Search Issues**: Look for similar issues in GitHub Issues
4. **Ask for Help**: Create a new issue with detailed information

### Required Information for Support
- Operating System and version
- Python version (`python --version`)
- Node.js version (`node --version`)
- Tally version and configuration
- Error messages and logs
- Installation method used

---

**Installation complete! 🎉**

Next steps:
- Configure your Tally connection
- Set up AI services (optional)
- Explore the dashboard features
- Read the [User Guide](USER_GUIDE.md)