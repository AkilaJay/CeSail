import os
from openai import OpenAI
from typing import Dict, Any, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
import json
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
)

class SimpleLLMInterface:
    """
    Simplified LLM interface for the simple agent.
    """
    
    def __init__(self):
        self.model = "gpt-4o"
        self.temperature = 0.3
        self.max_tokens = 4000
        
        # System messages for different purposes
        self.system_messages = {
            'breakdown': """You are an AI assistant that breaks down complex UI tasks into clear, executable steps. 
                Each step should be atomic and specific enough to be executed independently.
                Include success criteria for verification.""",
                
            'react': """You are an AI agent on a webpage. Analyze the current situation and generate UI actions to execute.
                Be precise and actionable in your decisions.""",
                
            'react_loop': """You are an AI agent on a webpage. Analyze the current situation and generate UI actions to execute.
                Be precise and actionable in your decisions.""",
                
            'observation': """You are an AI assistant that analyzes the results of UI actions.
                Determine if actions were successful and what should be done next."""
        }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def get_completion(self, 
                      messages: List[Dict[str, str]], 
                      purpose: str = 'general',
                      screenshot: str = None) -> str:
        """
        Gets completion from the language model with retry logic.
        """
        try:
            # Add appropriate system message based on purpose
            if purpose in self.system_messages:
                messages.insert(0, {
                    "role": "system",
                    "content": self.system_messages[purpose]
                })
            
            # Add screenshot if provided
            if screenshot:
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": screenshot
                            }
                        }
                    ]
                })
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            logger.info(f"LLM response: {response.choices[0].message.content}")
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in LLM call: {str(e)}")
            raise

    def get_structured_completion(self, 
                                messages: List[Dict[str, str]], 
                                output_format: Dict[str, Any],
                                purpose: str = 'general',
                                screenshot: str = None) -> Dict[str, Any]:
        """
        Gets completion and parses it into a structured format.
        """
        # Add format instructions
        format_instruction = f"""
        You must return a JSON object with EXACTLY these fields:
        {json.dumps(output_format, indent=2)}
        
        Rules:
        1. The response must be a valid JSON object
        2. The response must contain ONLY the fields shown above
        3. The response must not contain any additional fields
        4. The response must not contain any markdown formatting
        5. The response must match the field types exactly
        """
        
        messages.append({
            "role": "system",
            "content": format_instruction
        })
        
        response = self.get_completion(messages, purpose, screenshot)
        
        try:
            # Clean the response - remove any markdown formatting
            if response.startswith("```"):
                response = response.split("```")[1]
                if response.startswith("json"):
                    response = response[4:]
            response = response.strip()
            
            # Parse the JSON response
            parsed = json.loads(response)
            logger.info(f"Successfully parsed JSON: {parsed}")
            
            # Validate that ONLY the required fields are present
            if set(parsed.keys()) != set(output_format.keys()):
                raise ValueError(f"Response contains unexpected fields. Expected: {list(output_format.keys())}, Got: {list(parsed.keys())}")
            
            return parsed
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed. Error: {str(e)}")
            logger.error(f"Response that failed to parse: {response}")
            raise

# Create a global instance
llm_interface = SimpleLLMInterface()

def get_llm_response(prompt: str, 
                    purpose: str = 'general', 
                    output_format: Optional[Dict[str, Any]] = None,
                    screenshot: str = None) -> Any:
    """
    Utility function for getting LLM responses.
    """
    messages = [{"role": "user", "content": prompt}]
    
    if output_format:
        return llm_interface.get_structured_completion(
            messages, output_format, purpose, screenshot
        )
    else:
        return llm_interface.get_completion(messages, purpose, screenshot) 