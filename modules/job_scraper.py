import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict
import re
import os
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        }
        self.scraping_delay = int(os.getenv('SCRAPING_DELAY', 2))  # Delay between requests
        # API Keys from .env file
        self.adzuna_app_id = os.getenv('ADZUNA_APP_ID')
        self.adzuna_app_key = os.getenv('ADZUNA_APP_KEY')
        self.themuse_api_key = os.getenv('THEMUSE_API_KEY')
        self.reed_api_key = os.getenv('REED_API_KEY')
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        # Site toggles from .env file
        self.bdjobs_enabled = os.getenv('BDJOBS_ENABLED', 'true').lower() == 'true'
        self.chakri_enabled = os.getenv('CHAKRI_ENABLED', 'true').lower() == 'true'
        self.remoteok_enabled = os.getenv('REMOTEOK_API_ENABLED', 'true').lower() == 'true'

    def scrape_bdjobs(self, keywords: List[str], experience: int) -> List[Dict]:
        """Scrape jobs from BDJobs.com"""
        jobs = []
        try:
            search_query = '+'.join(keywords[:3])  # Use top 3 skills from the CV
            url = f'https://www.bdjobs.com/jobsearch.asp?q={search_query}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Check if request was successful
            if response.status_code != 200:
                print(f"Failed to retrieve BDJobs page, status code: {response.status_code}")
                return jobs

            soup = BeautifulSoup(response.content, 'html.parser')

            # Find job listings (update class names based on current website structure)
            job_cards = soup.find_all('div', class_='job-list')[:10]  # Get top 10 jobs
            for card in job_cards:
                try:
                    title = card.find('h3').text.strip() if card.find('h3') else 'N/A'
                    company = card.find('p', class_='company').text.strip() if card.find('p', class_='company') else 'N/A'
                    job_url = 'https://www.bdjobs.com' + card.find('a')['href'] if card.find('a') else ''
                    deadline = self.extract_deadline(card.text)
                    source = 'bdjobs'
                    requirements = card.text[:500]  # Extract first 500 characters as requirements
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': 'Bangladesh',
                        'job_url': job_url,
                        'deadline': deadline,
                        'source': source,
                        'requirements': requirements
                    }
                    jobs.append(job)
                except Exception as e:
                    print(f"Error extracting job details from BDJobs: {e}")
                    continue
        except Exception as e:
            print(f"BDJobs scraping error: {e}")
        return jobs

    def scrape_prothomalo_jobs(self) -> List[Dict]:
        """Scrape jobs from Prothom Alo Jobs section"""
        jobs = []
        try:
            url = 'https://www.prothomalo.com/jobs'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Check if request was successful
            if response.status_code != 200:
                print(f"Failed to retrieve Prothom Alo page, status code: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find job listings (update class names based on current website structure)
            job_cards = soup.find_all('div', class_='story-card')[:10]  # Get top 10 jobs
            for card in job_cards:
                try:
                    title_tag = card.find('h2') or card.find('h3')
                    link_tag = card.find('a')

                    if title_tag and link_tag:
                        job = {
                            'title': title_tag.text.strip(),
                            'company': 'Various',  # Prothom Alo doesn't always specify company name
                            'location': 'Bangladesh',
                            'job_url': 'https://www.prothomalo.com' + link_tag['href'],
                            'deadline': self.extract_deadline(card.text),
                            'source': 'prothomalo',
                            'requirements': card.text[:500]  # Extract first 500 characters as requirements
                        }
                        jobs.append(job)
                except Exception as e:
                    print(f"Error extracting job details from Prothom Alo: {e}")
                    continue
        except Exception as e:
            print(f"Prothom Alo scraping error: {e}")
        return jobs

    def scrape_chakri_com(self, keywords: List[str]) -> List[Dict]:
        """Scrape jobs from Chakri.com"""
        jobs = []
        try:
            search_query = '+'.join(keywords[:3])
            url = f'https://www.chakri.com/jobs?q={search_query}'
            response = requests.get(url, headers=self.headers, timeout=10)
            
            # Check if request was successful
            if response.status_code != 200:
                print(f"Failed to retrieve Chakri.com page, status code: {response.status_code}")
                return jobs
            
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find job items on Chakri.com
            job_cards = soup.find_all('div', class_='job-item')[:10]  # Get top 10 jobs
            for card in job_cards:
                try:
                    title = card.find('h2').text.strip() if card.find('h2') else 'N/A'
                    company = card.find('span', class_='company').text.strip() if card.find('span', class_='company') else 'N/A'
                    job_url = card.find('a')['href'] if card.find('a') else ''
                    deadline = self.extract_deadline(card.text)
                    source = 'chakri'
                    requirements = card.text[:500]  # Extract first 500 characters as requirements

                    job = {
                        'title': title,
                        'company': company,
                        'location': 'Bangladesh',
                        'job_url': job_url,
                        'deadline': deadline,
                        'source': source,
                        'requirements': requirements
                    }
                    jobs.append(job)
                except Exception as e:
                    print(f"Error extracting job details from Chakri: {e}")
                    continue
        except Exception as e:
            print(f"Chakri.com scraping error: {e}")
        return jobs


    def scrape_all_bd_jobs(self, keywords: List[str], experience: int) -> List[Dict]:
        """Aggregate jobs from all Bangladeshi job sites"""
        all_jobs = []
        all_jobs.extend(self.scrape_bdjobs(keywords, experience))
        all_jobs.extend(self.scrape_prothomalo_jobs())
        all_jobs.extend(self.scrape_chakri_com(keywords))
        return all_jobs

    def extract_deadline(self, text: str) -> datetime:
        """Extract deadline from job """
        deadline_patterns = [
            r'deadline[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'apply by[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
            r'last date[:\s]+(\d{1,2})[/-](\d{1,2})[/-](\d{4})',
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    day, month, year = match.groups()
                    return datetime(int(year), int(month), int(day))
                except Exception as e:
                    print(f"Error parsing deadline: {e}")
                    pass
        return datetime.now() + timedelta(days=30)  # Default: return 30 days from now if no deadline is found
