import google.generativeai as genai
import os
import datetime
import json
import logging
from typing import Dict, Any
from bson import json_util
from dateutil import parser
from google.api_core import exceptions as google_exceptions
from google.generativeai.types import generation_types

from myUtils.document_validator import validate_and_extract_resume_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GeminiModel")

class GeminiModel:
    _instance = None
    _BASE_RESUME_STRUCTURE = {
        "metadata": {
            "source": "resume_parser",
            "parse_date": "2024-01-01T00:00:00Z",
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
            "experience": [{
                "role": "",
                "company": "",
                "location": "",
                "start_date": "",
                "end_date": "",
                "current": False,
                "description": "",
                "technologies": []
            }],
            "education": [{
                "degree": "",
                "institution": "",
                "field_of_study": "",
                "start_year": "",
                "end_year": ""
            }],
            "skills": [{
                "name": "",
                "category": "",
                "years_experience": 0,  # Changed to integer for better handling
                "last_used": None  # Changed to None for unknown values
            }],
            "projects": [{
                "name": "",
                "description": "",
                "role": "",
                "technologies": [],
                "start_date": "",
                "end_date": "",
                "url": ""
            }],
            "certifications": [],
            "languages": [{
                "language": "",
                "proficiency": ""
            }]
        },
        "analysis": {
            "keywords": [],
            "summary": "",
            "completeness_score": None
        }
    }

    def __new__(cls):
        if cls._instance is None:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            
            try:
                genai.configure(api_key=api_key)
                cls._instance = super().__new__(cls)
                cls._instance.model = genai.GenerativeModel('gemini-pro')
                cls._instance.chat = cls._instance.model.start_chat()
            except google_exceptions.GoogleAPIError as e:
                logger.error("Google API configuration failed: %s", e)
                raise
            except Exception as e:
                logger.error("Unexpected initialization error: %s", e)
                raise
        return cls._instance
    
    def _generate_content(self, prompt: str) -> generation_types.GenerateContentResponse:
        """Handle content generation with error handling"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.95,
                    max_output_tokens=4000
                )
            )
            return response  # Return the full response object
        except google_exceptions.GoogleAPIError as e:
            logger.error("API request failed: %s", e)
            raise
        except ValueError as e:
            logger.error("Content generation error: %s", e)
            raise
        except Exception as e:
            logger.error("Unexpected generation error: %s", e)
            raise

    def _extract_gemini_response(self, response: generation_types.GenerateContentResponse) -> str:
        """Extracts the AI-generated text from Gemini response."""
        try:
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'result'):
                return response.result.text
            elif hasattr(response, 'candidates') and response.candidates:
                return response.candidates[0].content.parts[0].text
            else:
                logger.warning("Unexpected response structure")
                return str(response)
        except (IndexError, AttributeError) as e:
            logger.error("Failed to extract AI response: %s", e)
            return ""
    def _process_response(self, response: generation_types.GenerateContentResponse, document: dict) -> Dict[str, Any]:
        """Process and validate the AI response for MongoDB insertion."""
        try:
            # Extract AI-generated text using the helper method
            ai_response_text = self._extract_gemini_response(response)

            # Try to parse the AI response as JSON
            parsed_resume_data = {}
            if ai_response_text.strip().startswith('{'):
                try:
                    parsed_resume_data = json.loads(ai_response_text)
                    # Validate and extract the data
                    validated_data = validate_and_extract_resume_data(parsed_resume_data)
                    if validated_data is None:
                        logger.warning("Resume data validation failed")
                        validated_data = {}
                except json.JSONDecodeError:
                    logger.warning("Failed to parse AI response as JSON")
                    validated_data = {}
            else:
                logger.warning("AI response is not in JSON format")
                validated_data = {}

            # Construct MongoDB-compatible document
            processed_document = {
                "ai_responses": {
                    "gemini": ai_response_text,
                    "previous_ai": document.get("ai_response", None)
                },
                "resume_data": validated_data
            }

            return processed_document
        
        except Exception as e:
            logger.error(f"Response processing error: {str(e)}")
            return {}
    def get_applicant_details(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process document and return structured data"""
        try:
            if not document.get("resume_text"):
                raise ValueError("Missing resume_text in document")

            prompt = f"""Extract resume information into this JSON structure:
            {json.dumps(self._BASE_RESUME_STRUCTURE, indent=2)}
            
            Follow these rules:
            1. Use snake_case field names
            2. Convert dates to ISO 8601 format
            3. Use null for missing data
            4. Validate email formats
            5. Categorize skills (Technical, Language, etc.)
            
            Resume Text: {document['resume_text'][:10000]}  # Truncate to 10k chars
            
            Return ONLY the JSON structure with the extracted information. No additional text or explanation.
            """

            response = self._generate_content(prompt)
            return self._process_response(response, document)
            
        except ValueError as e:
            logger.error("Validation error: %s", str(e))
            return {}
        except Exception as e:
            logger.error("Processing error: %s", str(e))
            return {}
def get_model() -> GeminiModel:
    return GeminiModel()