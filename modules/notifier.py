from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
from typing import List, Dict
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, app=None, db=None, mail=None):
        self.app = app
        self.db = db
        self.mail = mail
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()

    def schedule_deadline_checks(self):
        """Schedule periodic checks for upcoming deadlines. Runs every 6 hours."""
        self.scheduler.add_job(
            func=self.check_deadlines,
            trigger='interval',
            hours=6,
            id='deadline_checker',
            replace_existing=True
        )

    def check_deadlines(self):
        """Check for jobs with upcoming deadlines and create notifications."""
        if not self.db or not self.app:
            logger.error("App or DB not initialized")
            return
        try:
            from models.database import Job, Notification, User
            with self.app.app_context():
                three_days_later = datetime.now() + timedelta(days=3)
                upcoming_jobs = Job.query.filter(
                    Job.deadline <= three_days_later,
                    Job.deadline >= datetime.now(),
                    Job.is_notified == False
                ).all()
                for job in upcoming_jobs:
                    self.create_notification(job)
        except Exception as e:
            logger.error(f"Error in check_deadlines: {e}")

    def create_notification(self, job):
        """Create a notification for a job deadline."""
        try:
            from models.database import Notification, User
            with self.app.app_context():
                user = User.query.get(job.user_id)
                if not user:
                    return
                days_left = (job.deadline - datetime.now()).days
                message = f"Reminder: Job deadline approaching!\n"
                message += f"Position: {job.title}\n"
                message += f"Company: {job.company}\n"
                message += f"Deadline: {job.deadline.strftime('%Y-%m-%d')}\n"
                message += f"Days left: {days_left}\n"
                message += f"Apply here: {job.job_url}"

                notification = Notification(
                    user_id=user.id,
                    job_id=job.id,
                    notification_date=datetime.now(),
                    message=message,
                    is_sent=False
                )
                self.db.session.add(notification)
                job.is_notified = True
                self.db.session.commit()

                if self.mail and user.email:
                    self.send_email_notification(user.email, job, message)
                return notification
        except Exception as e:
            logger.error(f"Error in create_notification: {e}")

    def send_email_notification(self, email: str, job, message: str):
        """Send email notification for job deadline."""
        try:
            msg = Message(
                subject=f'Job Deadline Reminder: {job.title}',
                recipients=[email],
                body=message,
                sender=self.app.config.get('MAIL_DEFAULT_SENDER', 'noreply@jobassistant.com')
            )
            self.mail.send(msg)
            return True
        except Exception as e:
            logger.error(f"Email sending error: {e}")
            return False

    def get_pending_notifications(self, user_id: int) -> List[Dict]:
        """Get all pending notifications for a user."""
        try:
            from models.database import Notification
            with self.app.app_context():
                notifications = Notification.query.filter_by(
                    user_id=user_id,
                    is_sent=False
                ).all()
                return [{
                    'id': n.id,
                    'message': n.message,
                    'date': n.notification_date.strftime('%Y-%m-%d %H:%M'),
                    'job_id': n.job_id
                } for n in notifications]
        except Exception as e:
            logger.error(f"Error in get_pending_notifications: {e}")
            return []

    def mark_notification_sent(self, notification_id: int):
        """Mark a notification as sent."""
        try:
            from models.database import Notification
            with self.app.app_context():
                notification = Notification.query.get(notification_id)
                if notification:
                    notification.is_sent = True
                    self.db.session.commit()
        except Exception as e:
            logger.error(f"Error in mark_notification_sent: {e}")

    def get_upcoming_deadlines(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get all jobs with deadlines in the next X days."""
        try:
            from models.database import Job
            with self.app.app_context():
                deadline_date = datetime.now() + timedelta(days=days)
                jobs = Job.query.filter(
                    Job.user_id == user_id,
                    Job.deadline <= deadline_date,
                    Job.deadline >= datetime.now(),
                    Job.is_applied == False
                ).order_by(Job.deadline.asc()).all()
                return [{
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'deadline': job.deadline.strftime('%Y-%m-%d'),
                    'days_left': (job.deadline - datetime.now()).days,
                    'url': job.job_url,
                    'match_score': job.match_score
                } for job in jobs]
        except Exception as e:
            logger.error(f"Error in get_upcoming_deadlines: {e}")
            return []