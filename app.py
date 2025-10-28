import os
import json
import logging
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_mail import Mail
from werkzeug.utils import secure_filename
from sqlalchemy.orm import scoped_session, sessionmaker
from models.database import db, User, Job, Notification
from modules.cv_parser import CVParser
from modules.job_scraper import JobScraper
from modules.matcher import JobMatcher
from modules.notifier import NotificationManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Use absolute path for SQLite database (Windows-compatible)
base_dir = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.join(base_dir, 'data')
db_path = os.path.join(data_dir, 'job_assistant.db').replace('\\', '/')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'static', 'Uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration (optional)
if os.getenv('MAIL_USERNAME') and os.getenv('MAIL_PASSWORD'):
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

# Initialize extensions
db.init_app(app)
mail = Mail(app) if os.getenv('MAIL_USERNAME') and os.getenv('MAIL_PASSWORD') else None

# Initialize modules
cv_parser = CVParser()
job_scraper = JobScraper()
job_matcher = JobMatcher()
notifier = NotificationManager(app=app, db=db, mail=mail)

# Create directories
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(data_dir, exist_ok=True)
    logger.info(f"Created directories: {app.config['UPLOAD_FOLDER']}, {data_dir}")
except Exception as e:
    logger.error(f"Failed to create directories: {e}")
    raise

# Test SQLite connection
try:
    conn = sqlite3.connect(db_path)
    conn.close()
    logger.info(f"Successfully tested SQLite connection to {db_path}")
except sqlite3.OperationalError as e:
    logger.error(f"SQLite connection test failed: {e}")
    raise

# Create database tables
try:
    with app.app_context():
        db.create_all()
        logger.info(f"Database tables created at {db_path}")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise

# Start notification scheduler
try:
    notifier.schedule_deadline_checks()
    logger.info("Notification scheduler started")
except Exception as e:
    logger.error(f"Failed to start notification scheduler: {e}")
    raise

# Routes
@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/upload-cv', methods=['POST'])
def upload_cv():
    """Upload and parse CV"""
    try:
        if 'cv_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        file = request.files['cv_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        if not file.filename.endswith(('.pdf', '.docx')):
            return jsonify({'error': 'Only PDF and DOCX files are supported'}), 400

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        cv_data = cv_parser.parse_cv(filepath)

        with app.app_context():
            # Create a new session
            session = db.session
            user = User(
                name=cv_data.get('name', 'Unknown'),
                email=cv_data.get('email', ''),
                phone=cv_data.get('phone', ''),
                country=cv_data.get('country', 'unknown'),
                experience_years=cv_data.get('experience_years', 0),
                skills=json.dumps(cv_data.get('skills', [])),
                education=cv_data.get('education', ''),
                cv_filename=filename
            )
            session.add(user)
            session.commit()
            # Fetch attributes within the session
            user_data = {
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'country': user.country,
                'experience_years': user.experience_years,
                'skills': json.loads(user.skills),
                'education': user.education
            }
            user_id = user.id
            # Explicitly close the session
            session.close()

        return jsonify({
            'success': True,
            'user_id': user_id,
            'cv_data': user_data
        })
    except Exception as e:
        logger.error(f"Error in upload_cv: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-jobs/<int:user_id>', methods=['GET'])
def search_jobs(user_id):
    """Search and match jobs for a user"""
    try:
        with app.app_context():
            session = db.session
            user = session.get(User, user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            cv_data = {
                'name': user.name,
                'country': user.country,
                'experience_years': user.experience_years,
                'skills': json.loads(user.skills),
                'education': user.education
            }
            if user.country.lower() == 'bangladesh':
                scraped_jobs = job_scraper.scrape_all_bd_jobs(
                    keywords=cv_data['skills'],
                    experience=cv_data['experience_years']
                )
            else:
                scraped_jobs = job_scraper.get_mock_jobs()
            matched_jobs = job_matcher.filter_applicable_jobs(cv_data, scraped_jobs, min_score=30.0)
            for job_data in matched_jobs:
                job = Job(
                    user_id=user.id,
                    title=job_data.get('title', 'N/A'),
                    company=job_data.get('company', 'N/A'),
                    location=job_data.get('location', ''),
                    job_url=job_data.get('job_url', ''),
                    deadline=job_data.get('deadline'),
                    source=job_data.get('source', 'unknown'),
                    requirements=job_data.get('requirements', ''),
                    match_score=job_data.get('match_score', 0)
                )
                session.add(job)
            session.commit()
            categorized = job_matcher.categorize_jobs(matched_jobs)
            session.close()
        return jsonify({
            'success': True,
            'total_jobs': len(matched_jobs),
            'categorized': {
                'excellent': len(categorized['excellent']),
                'good': len(categorized['good']),
                'fair': len(categorized['fair']),
                'possible': len(categorized['possible'])
            },
            'jobs': matched_jobs[:50]
        })
    except Exception as e:
        logger.error(f"Error in search_jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:user_id>', methods=['GET'])
def get_user_jobs(user_id):
    """Get all jobs for a user"""
    try:
        with app.app_context():
            session = db.session
            jobs = session.query(Job).filter_by(user_id=user_id).order_by(Job.match_score.desc()).all()
            jobs_list = [{
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'job_url': job.job_url,
                'deadline': job.deadline.strftime('%Y-%m-%d') if job.deadline else None,
                'source': job.source,
                'match_score': job.match_score,
                'is_applied': job.is_applied,
                'days_left': (job.deadline - datetime.now()).days if job.deadline else None
            } for job in jobs]
            session.close()
        return jsonify({'success': True, 'jobs': jobs_list})
    except Exception as e:
        logger.error(f"Error in get_user_jobs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mark-applied/<int:job_id>', methods=['POST'])
def mark_applied(job_id):
    """Mark a job as applied"""
    try:
        with app.app_context():
            session = db.session
            job = session.get(Job, job_id)
            if not job:
                return jsonify({'error': 'Job not found'}), 404
            job.is_applied = True
            session.commit()
            session.close()
        return jsonify({'success': True, 'message': 'Job marked as applied'})
    except Exception as e:
        logger.error(f"Error in mark_applied: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    """Get pending notifications for a user"""
    try:
        notifications = notifier.get_pending_notifications(user_id)
        upcoming = notifier.get_upcoming_deadlines(user_id, days=7)
        return jsonify({
            'success': True,
            'notifications': notifications,
            'upcoming_deadlines': upcoming
        })
    except Exception as e:
        logger.error(f"Error in get_notifications: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


   # Existing imports and initializations remain the same

if __name__ == '__main__':
    # Initialize the scraper
    scraper = JobScraper()

    # Test with some keywords and experience level
    jobs = scraper.scrape_all_bd_jobs(['python', 'django', 'postgresql'], 2)

    # Print the scraped jobs
    for job in jobs:
        print(job)

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

