Job Assistant - Setup Instructions
📋 Prerequisites

Python 3.8 or higher
pip (Python package manager)
Internet connection for job scraping

🚀 Step-by-Step Setup
1. Create Project Structure
bash
# Create main directory
mkdir job-assistant
cd job-assistant

# Create subdirectories
mkdir -p modules models static/css static/js static/uploads templates data

2. Create Files
Copy all the provided code into their respective files:
Full PowerShell script (works in VS Code terminal)
# Make sure you're inside your desired parent folder first
# Example: cd C:\Users\sakib\SRN\PersonalProjects

mkdir job-assistant
cd job-assistant

# Create main directories
mkdir modules, models, static, templates, data

# Create subdirectories
mkdir static/css, static/js, static/uploads

# Create files
ni app.py, requirements.txt, .env
ni modules/__init__.py, modules/cv_parser.py, modules/job_scraper.py, modules/matcher.py, modules/notifier.py
ni models/__init__.py, models/database.py
ni static/css/style.css, static/js/main.js
ni templates/index.html


3. Create Empty init.py Files
# Create empty __init__.py files
touch modules/__init__.py
touch models/__init__.py

4. Install Dependencies
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Download spaCy English model
python -m spacy download en_core_web_sm

5. Configure Environment Variables
Edit the .env file with your settings:
# Minimal configuration (email is optional)
SECRET_KEY=your-secret-random-key-here

6. Run the Application
# Start the Flask server
python app.py

The server will start at: http://localhost:5000
🌍 Making Server Globally Accessible
Option 1: Using ngrok (Easiest for Testing)

Download ngrok from https://ngrok.com/
Run: ngrok http 5000
Use the provided public URL (e.g., https://abc123.ngrok.io)

Option 2: Port Forwarding (For Home Network)

Find your local IP: ipconfig (Windows) or ifconfig (Mac/Linux)
Configure port forwarding on your router (port 5000)
Use your public IP address

Option 3: Cloud Deployment (For Production)
Deploy to Heroku:
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create heroku app
heroku create your-app-name
git push heroku main

Deploy to PythonAnywhere:

Sign up at https://www.pythonanywhere.com
Upload your files
Configure web app in dashboard

Deploy to AWS/Google Cloud/Azure:

Use EC2, App Engine, or Azure App Service
Follow cloud provider's deployment guide

📱 Usage Instructions
1. Upload CV

Click "Upload CV" button
Select PDF or DOCX file
Wait for parsing to complete

2. Review Extracted Information

Check name, email, phone, country
Verify skills and experience
Click "Search Matching Jobs"

3. Browse Job Matches

Jobs are categorized by match quality
Use filter tabs to view specific categories
Click "View Job Details" to see full posting
Click "Mark as Applied" to track applications

4. Monitor Deadlines

Check notification panel on bottom right
Enable browser notifications for alerts
Receive email notifications (if configured)

🔧 Troubleshooting
Common Issues
1. spaCy model not found
python -m spacy download en_core_web_sm
2. Database errors
# Delete existing database and restart
rm data/job_assistant.db
python app.py
3. Port already in use
# Change port in app.py
app.run(host='0.0.0.0', port=5001, debug=True)

4. CV parsing issues

Ensure CV is in PDF or DOCX format
Check file size (max 16MB)
Try with a different CV file

5. Job scraping returns no results

Check internet connection
Website structure may have changed
Mock data is included for testing

📧 Email Notifications Setup (Optional)
Using Gmail:

Enable 2-factor authentication on Gmail
Generate an app password:

Go to Google Account → Security
App passwords → Generate


Update .env:
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password

4. Uncomment email configuration in app.py

🎯 Features Checklist

✅ CV upload and parsing (PDF/DOCX)
✅ Information extraction (name, email, skills, experience)
✅ Country detection
✅ Job scraping from BD sites (BDJobs, Chakri, Prothom Alo)
✅ CV-to-job matching algorithm
✅ Match score calculation
✅ Job categorization (Excellent/Good/Fair/Possible)
✅ Deadline tracking
✅ Browser notifications
✅ Email notifications (optional)
✅ Mark jobs as applied
✅ Responsive UI
✅ Local server with global access capability
✅ SQLite database (easy cloud migration)

🔄 Future Enhancements

More Job Sources:

Add LinkedIn API integration
Add Indeed scraper
Add Glassdoor integration


Advanced Features:

Auto-apply to jobs
Cover letter generation
Interview preparation tips
Salary insights


Cloud Deployment:

Migrate to PostgreSQL
Deploy on AWS/Heroku
Add user authentication
Multi-user support


Mobile App:

React Native mobile app
Push notifications
Offline mode



📞 Support
For issues or questions:

Check console logs for errors
Verify all dependencies are installed
Ensure database is created properly
Test with sample CV first

🎉 You're All Set!
Your Job Assistant is ready to use. Upload a CV and start finding matching jobs!


Visit: http://localhost:5000