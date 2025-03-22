# import datetime
# import openai
# import os
# import re
# import json
# from bson import json_util
# from dateutil import parser


# import logging
# # Configure logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# logger = logging.getLogger("Open AI Model")

# class OpenAIModels:
#     _instance = None

#     def __new__(cls):
#         if cls._instance is None:
#             api_key = os.getenv("OPENAI_API_KEY")
#             openai.api_key = api_key
#             cls._instance = super(OpenAIModels, cls).__new__(cls)
#             cls._instance.init_models()
#         return cls._instance
    
#     def init_models(self):
#         # List of free OpenAI models (as of available free-tier options)
#         self.models = {
#             "gpt-3.5-turbo": "gpt-3.5-turbo",
#             "gpt-3.5-turbo-1106": "gpt-3.5-turbo-1106",
#             "text-embedding-ada-002": "text-embedding-ada-002"
#         }
    
#     def get_gpt_3_5_turbo(self):
#         return self.models["gpt-3.5-turbo"]
    
#     def get_gpt_3_5_turbo_1106(self):
#         return self.models["gpt-3.5-turbo-1106"]
    
#     def get_text_embedding_ada_002(self):
#         return self.models["text-embedding-ada-002"]
    
#     def chat_with_gpt_3_5_turbo(self, messages):
#         return openai.ChatCompletion.create(
#             model=self.models["gpt-3.5-turbo"],
#             messages=messages
#         )
    
#     def chat_with_gpt_3_5_turbo_1106(self, messages):
#         return openai.ChatCompletion.create(
#             model=self.models["gpt-3.5-turbo-1106"],
#             messages=messages
#         )
    
#     def generate_text_embedding(self, text):
#         return openai.Embedding.create(
#             model=self.models["text-embedding-ada-002"],
#             input=text
#         )
    
#     def complete_text(self, prompt, max_tokens=100):
#         return openai.Completion.create(
#             model=self.models["gpt-3.5-turbo"],
#             prompt=prompt,
#             max_tokens=max_tokens
#         )
    
#     def summarize_text(self, text):
#         prompt = f"Summarize the following text:\n{text}"
#         return self.complete_text(prompt)
    
#     def answer_question(self, question, context):
#         prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
#         return self.complete_text(prompt)
    
#     def generate_code(self, prompt):
#         return self.complete_text(f"Write a Python function for: {prompt}")
    
#     def get_applicant_details(self, document):
#         try:
#             resume_text = document.get("resume_text", "")
#             scores = document.get("scores", {})
            
#             prompt = f"""
#             Extract and structure resume information into a MongoDB-compatible JSON document following these requirements:
            
#             1. Use snake_case for all field names
#             2. Convert dates to ISO format (YYYY-MM-DD) where possible
#             3. Structure nested documents appropriately
#             4. Include empty arrays for missing list fields
#             5. Add a parsing timestamp
            
#             Required structure:
#             {{
#                 "metadata": {{
#                     "source": "resume_parser",
#                     "parse_date": "Current ISO datetime",
#                     "version": "1.0"
#                 }},
#                 "applicant": {{
#                     "full_name": "",
#                     "contact": {{
#                         "phones": [],
#                         "emails": [],
#                         "links": {{
#                             "linkedin": "",
#                             "github": "",
#                             "portfolio": ""
#                         }}
#                     }},
#                     "skills": [
#                         {{
#                             "name": "",
#                             "category": "",
#                             "years_experience": null,
#                             "last_used": null
#                         }}
#                     ],
#                     "experience": [
#                         {{
#                             "role": "",
#                             "company": "",
#                             "location": "",
#                             "start_date": "",
#                             "end_date": "",
#                             "current": false,
#                             "description": "",
#                             "technologies": []
#                         }}
#                     ],
#                     "education": [
#                         {{
#                             "degree": "",
#                             "institution": "",
#                             "field_of_study": "",
#                             "start_year": null,
#                             "end_year": null
#                         }}
#                     ],
#                     "projects": [
#                         {{
#                             "name": "",
#                             "description": "",
#                             "role": "",
#                             "technologies": [],
#                             "start_date": "",
#                             "end_date": "",
#                             "url": ""
#                         }}
#                     ],
#                     "certifications": [],
#                     "languages": [
#                     ]
#                 }},
#                 "analysis": {{
#                     "keywords": [],
#                     "summary": "",
#                     "completeness_score": null
#                 }}
#             }}
            
#             Resume Text: {resume_text}
            
#             Instructions:
#             - Current datetime format: ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)
#             - Convert duration strings to numerical years
#             - Split combined fields (e.g., "React/Node.js" -> separate list items)
#             - Validate email formats
#             - Categorize skills (Technical, Language, Soft Skill, etc.)
#             - Estimate missing dates where possible
#             - For technologies, specify versions when mentioned (e.g., "Python 3.8")
#             - Generate summary with focus on technical capabilities
#             """
            
#             response = self.chat_with_gpt_3_5_turbo([
#                 {"role": "system", "content": "You are a MongoDB document structuring assistant."},
#                 {"role": "user", "content": prompt}
#             ])
            
#             # Parse and validate response
#             structured_data = json.loads(response["choices"][0]["message"]["content"])
            
#             # Convert string dates to proper datetime objects
#             for exp in structured_data.get("applicant", {}).get("experience", []):
#                 for date_field in ["start_date", "end_date"]:
#                     if exp.get(date_field):
#                         exp[date_field] = parser.parse(exp[date_field])
            
#             # Add scores with proper typing
#             structured_data["scores"] = {
#                 "score_card": scores,
#                 "last_updated": datetime.datetime.utcnow(),
#                 "version": "1.0"
#             }
            
#             # Add database fields with proper MongoDB types
#             structured_data.update({
#                 "created_at": datetime.datetime.utcnow(),
#                 "updated_at": datetime.datetime.utcnow(),
#                 "status": "new",
#                 "processing_metadata": {
#                     "parser_version": "2.3.1",
#                     "workflow": "v3"
#                 }
#             })
            
#             # Ensure proper BSON types
#             return json_util.loads(json_util.dumps(structured_data))
            
#         except json.JSONDecodeError as e:
#             logger.error(f"JSON parsing failed: {e}")
#             return {}
#         except KeyError as e:
#             logger.error(f"Missing key in AI response: {e}")
#             return {}
#         except Exception as e:
#             logger.error(f"Unexpected error in processing: {str(e)}")
#             return {}
        
# # Function to get the model instance
# def get_openai_model():
#     return OpenAIModels()


import datetime
import json
import logging
import os
from typing import Dict, Any

from bson import json_util
from dateutil import parser
from openai import OpenAI, APIConnectionError, APIError, RateLimitError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OpenAIModel")

class OpenAIModels:
    _instance = None
    _SUPPORTED_MODELS = {
        "chat": ["gpt-3.5-turbo", "gpt-3.5-turbo-1106", "gpt-4-turbo"],
        "embedding": ["text-embedding-3-small", "text-embedding-3-large"]
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            cls._instance.client = OpenAI(api_key=api_key)
            cls._instance.default_chat_model = "gpt-3.5-turbo-1106"
            cls._instance.default_embedding_model = "text-embedding-3-small"
            
        return cls._instance

    def _handle_api_error(self, error: Exception) -> None:
        """Handle common API errors"""
        if isinstance(error, APIConnectionError):
            logger.error("Connection error: %s", error)
        elif isinstance(error, RateLimitError):
            logger.error("Rate limit exceeded: %s", error)
        elif isinstance(error, APIError):
            logger.error("API error: %s", error)
        else:
            logger.error("Unexpected error: %s", error)

    def chat_completion(
        self,
        messages: list[dict],
        model: str = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """Generic chat completion with error handling"""
        model = model or self.default_chat_model
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            self._handle_api_error(e)
            raise

    def generate_embedding(self, text: str, model: str = None) -> list[float]:
        """Generate text embeddings"""
        model = model or self.default_embedding_model
        try:
            response = self.client.embeddings.create(
                input=text,
                model=model
            )
            return response.data[0].embedding
        except Exception as e:
            self._handle_api_error(e)
            raise

    def get_applicant_details(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process document and return structured MongoDB data"""
        try:
            resume_text = document.get("resume_text", "")
            scores = document.get("scores", {})

            system_prompt = """You are a MongoDB document structuring assistant. 
                Generate valid JSON documents with proper typing following these rules:
                1. Use snake_case field names
                2. ISO date formats
                3. Empty arrays for missing data
                4. Proper null handling"""

            user_prompt = f"""Extract resume information into this structure:
                {json.dumps(_BASE_RESUME_STRUCTURE, indent=2)}
                Resume Text: {resume_text}"""

            response = self.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000
            )

            structured_data = self._process_response(response, scores)
            return json_util.loads(json_util.dumps(structured_data))

        except json.JSONDecodeError as e:
            logger.error("JSON parsing failed: %s", e)
            return {}
        except Exception as e:
            logger.error("Processing error: %s", e)
            return {}

    def _process_response(self, response: str, scores: dict) -> Dict[str, Any]:
        """Process and validate the AI response"""
        data = json.loads(response)
        
        # Date parsing
        for exp in data.get("applicant", {}).get("experience", []):
            for field in ["start_date", "end_date"]:
                if exp.get(field):
                    exp[field] = parser.parse(exp[field])

        # Add metadata
        data.update({
            "system_metadata": {
                "created_at": datetime.datetime.utcnow(),
                "updated_at": datetime.datetime.utcnow(),
                "processing_version": "2.4.0"
            },
            "scores": {
                "score_card": scores,
                "last_updated": datetime.datetime.utcnow()
            }
        })
        return data
# Base document structure
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

def get_openai_model() -> OpenAIModels:
    return OpenAIModels()