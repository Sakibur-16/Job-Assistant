# 🎯 Job Search Assistant

**AI-Powered CV-Based Job Matching System with Deadline Notifications**

Upload your CV, get matched with relevant jobs from multiple sources, and never miss a deadline!

---

## ✨ Features

- 📄 **Smart CV Parsing** - Extracts name, email, skills, experience from PDF/DOCX
- 🔍 **Multi-Source Job Search** - Scrapes jobs from Bangladesh sites + global APIs
- 🎯 **Intelligent Matching** - Scores jobs 0-100% based on your profile
- ⏰ **Deadline Tracking** - Browser & email notifications for upcoming deadlines
- 🌍 **Country-Specific** - Automatically searches relevant job sites based on your location
- 📊 **Job Categorization** - Excellent, Good, Fair, and Possible matches
- ✅ **Application Tracking** - Mark jobs as applied
- 🌐 **Global Access** - Run locally, access globally via ngrok

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Internet connection

### Installation

```bash
# 1. Clone/Download the project
cd job-assistant

# 2. Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Create .env file
echo "SECRET_KEY=your-secret-key" > .env
echo "REMOTEOK_API_ENABLED=true" >> .env

# 4. Run the app
python app.py

# 5. Open browser
# Go to: http://localhost:5000
```

**That's it!** See `QUICK_START.md` for detailed 5-minute setup.

---

## 📚 Documentation

| File | Description |
|------|-------------|
| `QUICK_START.md` | Get
