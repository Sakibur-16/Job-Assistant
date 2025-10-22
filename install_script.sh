#!/bin/bash

# Job Assistant - Automated Installation Script
# For Linux and macOS

echo "=================================="
echo "  JOB ASSISTANT - INSTALLER"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
echo ""

# Check if pip is installed
echo "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip is not installed${NC}"
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi
echo -e "${GREEN}✓ pip found${NC}"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
    read -p "Recreate it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded${NC}"
echo ""

# Install requirements
echo "Installing Python packages..."
echo "This may take a few minutes..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All packages installed${NC}"
else
    echo -e "${RED}✗ Package installation failed${NC}"
    echo "Please check requirements.txt and try again"
    exit 1
fi
echo ""

# Download spaCy model
echo "Downloading spaCy English model..."
python -m spacy download en_core_web_sm

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ spaCy model downloaded${NC}"
else
    echo -e "${RED}✗ spaCy model download failed${NC}"
    exit 1
fi
echo ""

# Create necessary directories
echo "Creating project directories..."
mkdir -p static/uploads
mkdir -p data
mkdir -p modules
mkdir -p models
touch modules/__init__.py
touch models/__init__.py
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')

# Database
DATABASE_URL=sqlite:///data/job_assistant.db

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Job Search APIs (Add your keys here)
ADZUNA_APP_ID=
ADZUNA_APP_KEY=
THEMUSE_API_KEY=
REED_API_KEY=
RAPIDAPI_KEY=
REMOTEOK_API_ENABLED=true

# Job Sites
BDJOBS_ENABLED=true
CHAKRI_ENABLED=true
PROTHOMALO_ENABLED=true

# Scraping Configuration
SCRAPING_DELAY=2
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36

# Email (Optional - leave empty if not using)
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env to add your API keys${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists${NC}"
fi
echo ""

# Test installation
echo "Testing installation..."
python test_apis.py

echo ""
echo "=================================="
echo "  INSTALLATION COMPLETE! 🎉"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add API keys (optional)"
echo "   - See API_SETUP_GUIDE.md for instructions"
echo ""
echo "2. Start the application:"
echo -e "   ${GREEN}python app.py${NC}"
echo ""
echo "3. Open your browser:"
echo -e "   ${GREEN}http://localhost:5000${NC}"
echo ""
echo "4. Upload a CV and start searching!"
echo ""
echo "Documentation:"
echo "  - QUICK_START.md - 5-minute quick start"
echo "  - API_SETUP_GUIDE.md - Get free API keys"
echo "  - README.md - Full documentation"
echo ""
echo "Happy job hunting! 🚀"
echo ""