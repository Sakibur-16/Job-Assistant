// Global variables
let currentUserId = null;
let allJobs = [];

// API base URL
const API_BASE = window.location.origin;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // Setup file upload
    const fileInput = document.getElementById('cv-file');
    fileInput.addEventListener('change', handleFileUpload);

    // Setup search button
    const searchBtn = document.getElementById('search-jobs-btn');
    searchBtn.addEventListener('click', searchJobs);

    // Setup filter tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => filterJobs(btn.dataset.filter));
    });

    // Request notification permission
    if ('Notification' in window) {
        Notification.requestPermission();
    }

    // Check for notifications every minute
    setInterval(checkNotifications, 60000);
}

// Handle CV file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    const statusDiv = document.getElementById('upload-status');
    statusDiv.textContent = 'Uploading and parsing CV...';
    statusDiv.className = 'status-message';
    statusDiv.style.display = 'block';

    const formData = new FormData();
    formData.append('cv_file', file);

    try {
        const response = await fetch(`${API_BASE}/api/upload-cv`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.success) {
            currentUserId = data.user_id;
            displayCVData(data.cv_data);
            statusDiv.textContent = '✓ CV uploaded and parsed successfully!';
            statusDiv.className = 'status-message success';
            document.getElementById('upload-section').classList.remove('active');
            document.getElementById('cv-info-section').classList.add('active');
        } else {
            throw new Error(data.error || 'Upload failed');
        }
    } catch (error) {
        statusDiv.textContent = `✗ Error: ${error.message}`;
        statusDiv.className = 'status-message error';
    }
}

// Display parsed CV data
function displayCVData(cvData) {
    const cvDataDiv = document.getElementById('cv-data');
    const skillsHTML = cvData.skills.map(skill => `<span class="skill-tag">${skill}</span>`).join('');
    cvDataDiv.innerHTML = `
        <div class="cv-field">
            <strong>Name</strong>
            <span>${cvData.name || 'Not found'}</span>
        </div>
        <div class="cv-field">
            <strong>Email</strong>
            <span>${cvData.email || 'Not found'}</span>
        </div>
        <div class="cv-field">
            <strong>Phone</strong>
            <span>${cvData.phone || 'Not found'}</span>
        </div>
        <div class="cv-field">
            <strong>Country</strong>
            <span>${cvData.country || 'Not detected'}</span>
        </div>
        <div class="cv-field">
            <strong>Experience</strong>
            <span>${cvData.experience_years} years</span>
        </div>
        <div class="cv-field">
            <strong>Skills</strong>
            <div class="skills-list">${skillsHTML || 'No skills detected'}</div>
        </div>
        <div class="cv-field">
            <strong>Education</strong>
            <span>${cvData.education || 'Not found'}</span>
        </div>
    `;
}

// Search for matching jobs
async function searchJobs() {
    if (!currentUserId) return;
    const searchBtn = document.getElementById('search-jobs-btn');
    searchBtn.textContent = 'Searching...';
    searchBtn.disabled = true;
    try {
        const response = await fetch(`${API_BASE}/api/search-jobs/${currentUserId}`);
        const data = await response.json();
        if (data.success) {
            allJobs = data.jobs;
            displayJobStats(data.categorized);
            displayJobs(allJobs);
            document.getElementById('cv-info-section').classList.remove('active');
            document.getElementById('jobs-section').classList.add('active');
            checkNotifications();
        } else {
            throw new Error(data.error || 'Job search failed');
        }
    } catch (error) {
        alert(`Error searching jobs: ${error.message}`);
    } finally {
        searchBtn.textContent = 'Search Matching Jobs';
        searchBtn.disabled = false;
    }
}

// Display job statistics
function displayJobStats(categorized) {
    const statsDiv = document.getElementById('job-stats');
    statsDiv.innerHTML = `
        <div class="stat-card">
            <h3>${categorized.excellent}</h3>
            <p>Excellent Match</p>
        </div>
        <div class="stat-card">
            <h3>${categorized.good}</h3>
            <p>Good Match</p>
        </div>
        <div class="stat-card">
            <h3>${categorized.fair}</h3>
            <p>Fair Match</p>
        </div>
        <div class="stat-card">
            <h3>${categorized.possible}</h3>
            <p>Possible Match</p>
        </div>
    `;
}

// Display jobs list
function displayJobs(jobs) {
    const jobsList = document.getElementById('jobs-list');
    if (jobs.length === 0) {
        jobsList.innerHTML = '<p class="loading">No matching jobs found.</p>';
        return;
    }
    jobsList.innerHTML = jobs.map(job => createJobCard(job)).join('');
    document.querySelectorAll('.btn-apply').forEach(btn => {
        btn.addEventListener('click', () => markAsApplied(btn.dataset.jobId));
    });
}

// Create job card HTML
function createJobCard(job) {
    const matchClass = getMatchClass(job.match_score);
    const matchLabel = getMatchLabel(job.match_score);
    const deadlineWarning = job.days_left <= 3 ? 'deadline-warning' : '';
    return `
        <div class="job-card" data-match="${matchClass}">
            <div class="job-header">
                <div>
                    <h3 class="job-title">${job.title}</h3>
                    <p class="job-company">${job.company}</p>
                </div>
                <span class="match-badge match-${matchClass}">
                    ${Math.round(job.match_score)}% Match - ${matchLabel}
                </span>
            </div>
            <div class="job-details">
                <div class="job-detail-item">
                    📍 <span>${job.location}</span>
                </div>
                <div class="job-detail-item">
                    🌐 <span>Source: ${job.source}</span>
                </div>
                <div class="job-detail-item ${deadlineWarning}">
                    ⏰ <span>Deadline: ${job.deadline || 'Not specified'} ${job.days_left ? `(${job.days_left} days left)` : ''}</span>
                </div>
            </div>
            <div class="job-actions">
                <a href="${job.job_url}" target="_blank" class="btn btn-small btn-primary">
                    View Job Details
                </a>
                ${job.is_applied ? '<button class="btn btn-small btn-applied" disabled>✓ Applied</button>' : `<button class="btn btn-small  btn-apply" data-job-id="${job.id}">Mark as Applied</button>`}
            </div>
        </div>
    `;
}

// Get match class based on score
function getMatchClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'fair';
    return 'possible';
}

// Get match label based on score
function getMatchLabel(score) {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Possible';
}

// Filter jobs by match quality
function filterJobs(filter) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.filter === filter) {
            btn.classList.add('active');
        }
    });
    let filteredJobs = allJobs;
    if (filter !== 'all') {
        filteredJobs = allJobs.filter(job => {
            const matchClass = getMatchClass(job.match_score);
            return matchClass === filter;
        });
    }
    displayJobs(filteredJobs);
}

// Mark job as applied
async function markAsApplied(jobId) {
    try {
        const response = await fetch(`${API_BASE}/api/mark-applied/${jobId}`, {
            method: 'POST'
        });
        const data = await response.json();
        if (data.success) {
            const btn = document.querySelector(`[data-job-id="${jobId}"]`);
            btn.outerHTML = '<button class="btn btn-small btn-applied" disabled>✓ Applied</button>';
            const job = allJobs.find(j => j.id == jobId);
            if (job) job.is_applied = true;
        }
    } catch (error) {
        console.error('Error marking job as applied:', error);
    }
}

// Check for notifications
async function checkNotifications() {
    if (!currentUserId) return;
    try {
        const response = await fetch(`${API_BASE}/api/notifications/${currentUserId}`);
        const data = await response.json();
        if (data.success) {
            displayNotifications(data.upcoming_deadlines);
            data.upcoming_deadlines.forEach(deadline => {
                if (deadline.days_left <= 3 && deadline.days_left >= 0) {
                    showBrowserNotification(deadline);
                }
            });
        }
    } catch (error) {
        console.error('Error checking notifications:', error);
    }
}

// Display notifications in panel
function displayNotifications(deadlines) {
    const notificationsList = document.getElementById('notifications-list');
    if (deadlines.length === 0) {
        notificationsList.innerHTML = '<p style="color: #666;">No upcoming deadlines</p>';
        return;
    }
    notificationsList.innerHTML = deadlines.map(deadline => `
        <div class="notification-item">
            <p><strong>${deadline.title}</strong></p>
            <p>${deadline.company}</p>
            <p>⏰ ${deadline.deadline} (${deadline.days_left} days left)</p>
            <p>Match: ${Math.round(deadline.match_score)}%</p>
            <a href="${deadline.url}" target="_blank" style="color: #667eea; text-decoration: none;">
                View Job →
            </a>
        </div>
    `).join('');
}

// Show browser notification
function showBrowserNotification(deadline) {
    if (!('Notification' in window) || Notification.permission !== 'granted') {
        return;
    }
    const notification = new Notification('Job Deadline Reminder', {
        body: `${deadline.title} at ${deadline.company}\nDeadline: ${deadline.deadline} (${deadline.days_left} days left)`,
        icon: '/static/icon.png',
        tag: `job-${deadline.id}`,
        requireInteraction: false
    });
    notification.onclick = () => {
        window.focus();
        window.open(deadline.url, '_blank');
        notification.close();
    };
}

// Utility function to format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}