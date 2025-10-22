import re
import PyPDF2
import docx
import pdfplumber
import spacy
import json
from typing import Dict, List

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"Error loading spaCy model: {e}")
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    nlp = None

class CVParser:
    def __init__(self):
        self.skills_keywords = [
            'python', 'java', 'javascript', 'c++', 'sql', 'html', 'css', 'react', 'node',
            'django', 'flask', 'mongodb', 'postgresql', 'git', 'docker', 'kubernetes', 'aws',
            'azure', 'machine learning', 'data analysis', 'project management', 'communication',
            'leadership', 'teamwork'
        ]

    def extract_text_from_pdf(self, filepath: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
        except Exception:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += (page.extract_text() or "") + "\n"
        return text

    def extract_text_from_docx(self, filepath: str) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""

    def extract_email(self, text: str) -> str:
        """Extract email address"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""

    def extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else ""

    def extract_name(self, text: str) -> str:
        """Extract name using spaCy NER"""
        if not nlp:
            lines = text.split('\n')
            return lines[0].strip() if lines else ""
        doc = nlp(text[:500])
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return ""

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills from text"""
        text_lower = text.lower()
        found_skills = []
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        return list(set(found_skills))

    def extract_experience(self, text: str) -> int:
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience)?',
            r'experience[:\s]+(\d+)\+?\s*(?:years?|yrs?)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                return int(matches[0])
        return 0

    def extract_education(self, text: str) -> str:
        """Extract education information"""
        education_keywords = ['bachelor', 'master', 'phd', 'bsc', 'msc', 'mba', 'diploma']
        lines = text.split('\n')
        education_info = []
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in education_keywords):
                education_info.append(line.strip())
        return " | ".join(education_info[:3])

    def detect_country(self, text: str) -> str:
        """Detect country from CV"""
        countries = {
            'bangladesh': ['bangladesh', 'dhaka', 'chittagong', 'sylhet', '+880'],
            'india': ['india', 'delhi', 'mumbai', 'bangalore', '+91'],
            'pakistan': ['pakistan', 'karachi', 'lahore', 'islamabad', '+92'],
            'usa': ['usa', 'united states', 'new york', 'california', '+1'],
        }
        text_lower = text.lower()
        for country, keywords in countries.items():
            if any(keyword in text_lower for keyword in keywords):
                return country
        return 'unknown'

    def parse_cv(self, filepath: str) -> Dict:
        """Main function to parse CV and extract all information"""
        if filepath.endswith('.pdf'):
            text = self.extract_text_from_pdf(filepath)
        elif filepath.endswith('.docx'):
            text = self.extract_text_from_docx(filepath)
        else:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX.")

        cv_data = {
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'country': self.detect_country(text),
            'experience_years': self.extract_experience(text),
            'skills': self.extract_skills(text),
            'education': self.extract_education(text),
            'raw_text': text
        }
        return cv_data

# Test the CVParser when running the module directly
if __name__ == '__main__':
    import sys
    parser = CVParser()
    if len(sys.argv) != 2:
        print("Usage: python cv_parser.py <path_to_cv_file>")
        sys.exit(1)
    filepath = sys.argv[1]
    try:
        cv_data = parser.parse_cv(filepath)
        print("Parsed CV Data:")
        print(json.dumps(cv_data, indent=2))
    except Exception as e:
        print(f"Error parsing CV: {e}")
        sys.exit(1)