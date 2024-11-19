# app/utils/openai_helper.py
import openai
from typing import List, Dict, Optional
import logging
import os
from dotenv import load_dotenv
from ..models.chat import Message

load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIHelper:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4"  # You can also use "gpt-4-1106-preview" for the latest version
        self.max_tokens = 8000  # Adjust based on your needs
        self.system_prompt = """You are a personal fashion stylist AI assistant. You help users with fashion advice, 
        outfit combinations, and style recommendations. Your responses should be professional, 
        friendly, and tailored to each user's specific needs and preferences."""

    def _prepare_messages(self, chat_history: List[Message], include_system: bool = True) -> List[Dict]:
        """Prepare messages for the OpenAI API format."""
        messages = []
        
        # Add system prompt if requested
        if include_system:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })

        # Add chat history
        for msg in chat_history:
            # Skip system messages if we already added our own
            if include_system and msg.role == "system":
                continue
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return messages

    async def get_completion(
        self, 
        chat_history: List[Message],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Get a completion from GPT-4 based on the chat history.
        
        Args:
            chat_history: List of previous messages
            temperature: Controls randomness (0.0-1.0)
            max_tokens: Maximum tokens in response
            
        Returns:
            str: The AI's response
        """
        try:
            messages = self._prepare_messages(chat_history)
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens or self.max_tokens,
                n=1,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )
            
            return response.choices[0].message.content

        except openai.error.InvalidRequestError as e:
            if "tokens" in str(e).lower():
                # If we hit token limit, try again with truncated history
                logger.warning("Token limit exceeded, retrying with truncated history")
                truncated_history = chat_history[-5:]  # Keep last 5 messages
                return await self.get_completion(truncated_history, temperature, max_tokens)
            raise

        except Exception as e:
            logger.error(f"Error in OpenAI completion: {str(e)}")
            raise

    async def get_structured_completion(
        self,
        chat_history: List[Message],
        structure_prompt: str,
        temperature: float = 0.7
    ) -> Dict:
        """
        Get a structured completion (e.g., for outfit recommendations).
        
        Args:
            chat_history: List of previous messages
            structure_prompt: Prompt specifying the required JSON structure
            temperature: Controls randomness (0.0-1.0)
            
        Returns:
            dict: Structured response
        """
        try:
            messages = self._prepare_messages(chat_history)
            
            # Add structure prompt
            messages.append({
                "role": "system",
                "content": f"Please provide your response in the following JSON structure:\n{structure_prompt}"
            })
            
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=self.max_tokens,
                n=1,
                presence_penalty=0.1,
                frequency_penalty=0.1,
                response_format={ "type": "json_object" }  # Ensure JSON response
            )
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in structured completion: {str(e)}")
            raise

    async def analyze_style(self, image_url: str) -> Dict:
        """
        Analyze style elements in an image using GPT-4 Vision.
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            dict: Analysis of the style elements
        """
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "Analyze the fashion and style elements in this image."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please analyze this outfit and provide details about:"},
                            {"type": "image_url", "image_url": image_url}
                        ]
                    }
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error in style analysis: {str(e)}")
            raise

# Create a singleton instance
openai_helper = OpenAIHelper()

# Convenience function for chat routes
async def get_ai_response(messages: List[Message]) -> str:
    """
    Get an AI response for the chat feature.
    
    Args:
        messages: List of previous messages in the conversation
        
    Returns:
        str: The AI's response
    """
    return await openai_helper.get_completion(messages)