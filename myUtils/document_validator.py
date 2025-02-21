import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

def validate_and_extract_resume_data(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validates and extracts resume data from the Gemini response.
    Returns a MongoDB-compatible document with validated fields.
    """
    def validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        return bool(email_pattern.match(email))

    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-numeric characters
        cleaned = re.sub(r'\D', '', phone)
        return len(cleaned) >= 10

    def validate_url(url: str) -> bool:
        """Validate URL format"""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))

    def validate_date(date_str: str) -> str:
        """Validate and format date to ISO 8601"""
        try:
            if not date_str:
                return ""
            # Parse the date string and convert to ISO format
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            return parsed_date.isoformat()
        except ValueError:
            return ""

    try:
        # Initialize validated data structure
        validated_data = {
            "metadata": {
                "source": "resume_parser",
                "parse_date": datetime.utcnow().isoformat(),
                "version": "1.0"
            },
            "applicant": {
                "full_name": "",
                "contact": {
                    "phones": [],
                    "emails": [],
                    "links": {
                        "linkedin": "",
                        "github": "",
                        "portfolio": ""
                    }
                },
                "experience": [],
                "education": [],
                "skills": [],
                "projects": [],
                "certifications": [],
                "languages": []
            },
            "analysis": {
                "keywords": [],
                "summary": "",
                "completeness_score": 0.0
            }
        }

        # Extract and validate basic information
        applicant_data = response_data.get("applicant", {})
        
        # Validate name
        validated_data["applicant"]["full_name"] = applicant_data.get("full_name", "").strip()

        # Validate contact information
        contact_data = applicant_data.get("contact", {})
        
        # Validate emails
        emails = contact_data.get("emails", [])
        validated_data["applicant"]["contact"]["emails"] = [
            email for email in emails if validate_email(email)
        ]

        # Validate phones
        phones = contact_data.get("phones", [])
        validated_data["applicant"]["contact"]["phones"] = [
            phone for phone in phones if validate_phone(phone)
        ]

        # Validate links
        links = contact_data.get("links", {})
        validated_links = {}
        for key, url in links.items():
            if isinstance(url, str) and validate_url(url):
                validated_links[key] = url
            else:
                validated_links[key] = ""
        validated_data["applicant"]["contact"]["links"] = validated_links

        # Validate experience entries
        experiences = applicant_data.get("experience", [])
        validated_experiences = []
        for exp in experiences:
            if isinstance(exp, dict):
                validated_exp = {
                    "role": exp.get("role", "").strip(),
                    "company": exp.get("company", "").strip(),
                    "location": exp.get("location", "").strip(),
                    "start_date": validate_date(exp.get("start_date", "")),
                    "end_date": validate_date(exp.get("end_date", "")),
                    "current": bool(exp.get("current", False)),
                    "description": exp.get("description", "").strip(),
                    "technologies": [tech.strip() for tech in exp.get("technologies", [])]
                }
                validated_experiences.append(validated_exp)
        validated_data["applicant"]["experience"] = validated_experiences

        # Validate education entries
        education = applicant_data.get("education", [])
        validated_education = []
        for edu in education:
            if isinstance(edu, dict):
                validated_edu = {
                    "degree": edu.get("degree", "").strip(),
                    "institution": edu.get("institution", "").strip(),
                    "field_of_study": edu.get("field_of_study", "").strip(),
                    "start_year": str(edu.get("start_year", "")).strip(),
                    "end_year": str(edu.get("end_year", "")).strip()
                }
                validated_education.append(validated_edu)
        validated_data["applicant"]["education"] = validated_education

        # Validate skills
        skills = applicant_data.get("skills", [])
        validated_skills = []
        for skill in skills:
            if isinstance(skill, dict):
                validated_skill = {
                    "name": skill.get("name", "").strip(),
                    "category": skill.get("category", "").strip(),
                    "years_experience": int(skill.get("years_experience", 0)),
                    "last_used": validate_date(skill.get("last_used", ""))
                }
                validated_skills.append(validated_skill)
        validated_data["applicant"]["skills"] = validated_skills

        # Validate projects
        projects = applicant_data.get("projects", [])
        validated_projects = []
        for project in projects:
            if isinstance(project, dict):
                validated_project = {
                    "name": project.get("name", "").strip(),
                    "description": project.get("description", "").strip(),
                    "role": project.get("role", "").strip(),
                    "technologies": [tech.strip() for tech in project.get("technologies", [])],
                    "start_date": validate_date(project.get("start_date", "")),
                    "end_date": validate_date(project.get("end_date", "")),
                    "url": project.get("url", "") if validate_url(project.get("url", "")) else ""
                }
                validated_projects.append(validated_project)
        validated_data["applicant"]["projects"] = validated_projects

        # Validate certifications
        certifications = applicant_data.get("certifications", [])
        validated_data["applicant"]["certifications"] = [cert.strip() for cert in certifications if isinstance(cert, str)]

        # Validate languages
        languages = applicant_data.get("languages", [])
        validated_languages = []
        for lang in languages:
            if isinstance(lang, dict):
                validated_lang = {
                    "language": lang.get("language", "").strip(),
                    "proficiency": lang.get("proficiency", "").strip()
                }
                validated_languages.append(validated_lang)
        validated_data["applicant"]["languages"] = validated_languages

        # Calculate completeness score
        required_fields = ["full_name", "emails", "phones"]
        filled_fields = sum(1 for field in required_fields if validated_data["applicant"].get(field))
        validated_data["analysis"]["completeness_score"] = round(filled_fields / len(required_fields) * 100, 2)

        # Extract keywords
        all_skills = [skill["name"] for skill in validated_skills]
        all_techs = [tech for exp in validated_experiences for tech in exp["technologies"]]
        validated_data["analysis"]["keywords"] = list(set(all_skills + all_techs))

        # Generate summary
        validated_data["analysis"]["summary"] = (
            f"Resume for {validated_data['applicant']['full_name']}. "
            f"Has {len(validated_experiences)} work experiences, "
            f"{len(validated_education)} educational qualifications, "
            f"and {len(validated_skills)} skills."
        )

        return validated_data

    except Exception as e:
        logger.error(f"Error validating resume data: {str(e)}")
        return None