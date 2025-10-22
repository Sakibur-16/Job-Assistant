from typing import Dict, List
import re

class JobMatcher:
    def __init__(self):
        pass

    def calculate_match_score(self, cv_data: Dict, job: Dict) -> float:
        """Calculate how well a CV matches a job posting (0-100 score)"""
        score = 0.0
        max_score = 100.0
        # Skills matching (50 points)
        skills_score = self.match_skills(cv_data.get('skills', []), job.get('requirements', ''))
        score += skills_score * 0.5
        # Experience matching (30 points)
        experience_score = self.match_experience(cv_data.get('experience_years', 0), job.get('requirements', ''))
        score += experience_score * 0.3
        # Location matching (20 points)
        location_score = self.match_location(cv_data.get('country', ''), job.get('location', ''))
        score += location_score * 0.2
        return min(score, max_score)

    def match_skills(self, cv_skills: List[str], job_requirements: str) -> float:
        """Match CV skills with job requirements"""
        if not cv_skills or not job_requirements:
            return 0.0
        job_requirements_lower = job_requirements.lower()
        matched_skills = 0
        for skill in cv_skills:
            if skill.lower() in job_requirements_lower:
                matched_skills += 1
        if len(cv_skills) == 0:
            return 0.0
        match_percentage = (matched_skills / len(cv_skills)) * 100
        return min(match_percentage, 100.0)

    def match_experience(self, cv_experience: int, job_requirements: str) -> float:
        """Match experience level with job requirements"""
        required_exp = self.extract_required_experience(job_requirements)
        if required_exp == 0:
            return 100.0
        if cv_experience >= required_exp:
            return 100.0
        elif cv_experience >= required_exp * 0.7:
            return 70.0
        elif cv_experience >= required_exp * 0.5:
            return 50.0
        else:
            return 30.0

    def extract_required_experience(self, job_requirements: str) -> int:
        """Extract years of experience required from job description"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience)?',
            r'experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)',
            r'minimum\s*(\d+)\s*(?:years?|yrs?)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, job_requirements.lower())
            if matches:
                return int(matches[0])
        return 0

    def match_location(self, cv_country: str, job_location: str) -> float:
        """Match location/country"""
        if not cv_country or not job_location:
            return 50.0
        cv_country_lower = cv_country.lower()
        job_location_lower = job_location.lower()
        if cv_country_lower in job_location_lower:
            return 100.0
        south_asia = ['bangladesh', 'india', 'pakistan', 'sri lanka', 'nepal']
        if cv_country_lower in south_asia and any(country in job_location_lower for country in south_asia):
            return 70.0
        return 30.0

    def filter_applicable_jobs(self, cv_data: Dict, jobs: List[Dict], min_score: float = 30.0) -> List[Dict]:
        """Filter and rank jobs based on CV match"""
        scored_jobs = []
        for job in jobs:
            score = self.calculate_match_score(cv_data, job)
            if score >= min_score:
                job['match_score'] = round(score, 2)
                scored_jobs.append(job)
        scored_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        return scored_jobs

    def categorize_jobs(self, jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize jobs by match quality"""
        categories = {
            'excellent': [],  # 80-100% match
            'good': [],      # 60-79% match
            'fair': [],      # 40-59% match
            'possible': []   # 30-39% match
        }
        for job in jobs:
            score = job.get('match_score', 0)
            if score >= 80:
                categories['excellent'].append(job)
            elif score >= 60:
                categories['good'].append(job)
            elif score >= 40:
                categories['fair'].append(job)
            else:
                categories['possible'].append(job)
        return categories