# app/utils/openai_helper.py
import openai
from typing import List, Dict, Optional
import logging
import os
from dotenv import load_dotenv
from ..models.chat import Message
import tiktoken


load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIHelper:
    def __init__(self):
        self.max_context_length = 8192
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4"  # You can also use "gpt-4-1106-preview" for the latest version
        self.max_tokens = 800  # Adjusted to a reasonable value
        self.max_context_length = 8192  # GPT-4 context length
        self.system_prompt = """You are a personal fashion stylist AI assistant. You help users with fashion advice, 
        outfit combinations, and style recommendations. Your responses should be professional, 
        friendly, and tailored to each user's specific needs and preferences."""

    def _prepare_messages(self, chat_history: List[Message], user_context: Optional[Dict] = None) -> List[Dict]:
        """Prepare messages for the OpenAI API format."""
        messages = []
        
        # Add system prompt with context if available
        system_content = self.system_prompt
        if user_context:
            system_content += "\n\nUser's Current Context:"
            if 'wardrobe_items' in user_context:
                items = user_context['wardrobe_items']
                system_content += f"\nWardrobe ({len(items)} items):"
                for item in items:
                    item_desc = f"\n- {item['name']}: {item['category']}"
                    if item.get('brand'): item_desc += f", by {item['brand']}"
                    if item.get('color'): item_desc += f", in {', '.join(item['color'])}"
                    if item.get('size'): item_desc += f", size {item['size']}"
                    if item.get('notes'): item_desc += f" ({item['notes']})"
                    system_content += item_desc

            if 'user_details' in user_context:
                details = user_context['user_details']
                if 'body_measurements' in details:
                    measurements = details['body_measurements']
                    system_content += "\n\nBody Measurements:"
                    if measurements.get('height'): system_content += f"\n- Height: {measurements['height']}cm"
                    if measurements.get('weight'): system_content += f"\n- Weight: {measurements['weight']}kg"
                    if measurements.get('body_type'): system_content += f"\n- Body Type: {measurements['body_type']}"

                if 'style_preferences' in details:
                    prefs = details['style_preferences']
                    system_content += "\n\nStyle Preferences:"
                    if prefs.get('favorite_colors'): 
                        system_content += f"\n- Favorite Colors: {', '.join(prefs['favorite_colors'])}"
                    if prefs.get('preferred_brands'): 
                        system_content += f"\n- Preferred Brands: {', '.join(prefs['preferred_brands'])}"
                    if prefs.get('lifestyle_choices'):
                        system_content += f"\n- Lifestyle: {', '.join(prefs['lifestyle_choices'])}"
                    if prefs.get('budget'):
                        system_content += f"\n- Budget Range: ${prefs['budget']['min_amount']} - ${prefs['budget']['max_amount']}"

        messages.append({
            "role": "system",
            "content": system_content
        })

        # Add chat history
        for msg in chat_history:
            if msg.role != "system":  # Skip original system messages
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        return messages
    
    def _count_tokens(self, messages: List[Dict]) -> int:
        encoding = tiktoken.encoding_for_model(self.model)
        num_tokens = 0
        for message in messages:
            num_tokens += len(encoding.encode(message['content']))
        return num_tokens

    async def get_completion(
        self, 
        chat_history: List[Message],
        user_context: Optional[Dict] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        retry_count: int = 0
    ) -> str:
        try:
            messages = self._prepare_messages(chat_history, user_context)
            token_count = self._count_tokens(messages)
            max_available_tokens = self.max_context_length - token_count

            if max_available_tokens <= 0:
                raise ValueError("Messages are too long. Cannot generate any response.")

            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=min(max_tokens or self.max_tokens, max_available_tokens),
                n=1,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            return response.choices[0].message.content

        except openai.error.RateLimitError as e:
            if retry_count < 5:
                wait_time = (2 ** retry_count) * 5  # Exponential backoff
                logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                return await self.get_completion(
                    chat_history, user_context, temperature, max_tokens, retry_count + 1
                )
            else:
                logger.error("Maximum retry attempts reached. Rate limit error persists.")
                raise

        except openai.error.InvalidRequestError as e:
            if "tokens" in str(e).lower():
                logger.warning("Token limit exceeded, retrying with truncated history")
                truncated_history = chat_history[-5:]
                return await self.get_completion(truncated_history, user_context, temperature, max_tokens)
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
                # Note: The 'response_format' parameter is not officially supported
                # Remove it or adjust according to OpenAI's actual API if necessary
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
async def get_ai_response(messages: List[Message], user_context: Optional[Dict] = None) -> str:
    """
    Get an AI response for the chat feature.
    
    Args:
        messages: List of previous messages in the conversation
        user_context: Optional dictionary containing user's wardrobe and preferences
        
    Returns:
        str: The AI's response
    """
    return await openai_helper.get_completion(messages, user_context)