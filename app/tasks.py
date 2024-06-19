import httpx
import asyncio
import os
import logging
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db import engine
from app.models import TranslationTask
from httpx import HTTPStatusError, RequestError
from app.prompt.prompt_extract import extract_prompts

# Set up basic logging configuration to capture informational messages and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve API key from environment variables for security and configurability
API_KEY = os.getenv("OPENAI_API_KEY")

# Path to the prompt.yaml file containing the prompt templates
PROMPT_YAML_PATH = os.path.join(os.path.dirname(__file__), 'prompt', 'prompt.yaml')

# Function to translate text to a specified language
async def translate_text(text: str, language: str) -> str:
    # Extract prompts from the prompt.yaml file using replacements
    replacements = {"text": text, "language": language}
    system_prompt, user_prompt = extract_prompts(PROMPT_YAML_PATH, **replacements)
    
    try:
        # Create an HTTP client with a timeout to prevent hanging requests
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Make a POST request to the OpenAI API for translation
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {API_KEY}"
                },
                json={
                    "model": "gpt-4-turbo",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                }
            )
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = response.json()  # Parse the JSON response
            # Return the translated text from the response
            return response_data['choices'][0]['message']['content']
    except HTTPStatusError as exc:
        logger.error(f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}")
        raise
    except RequestError as exc:
        logger.error(f"Request error occurred: {exc}")
        raise
    except Exception as exc:
        logger.error(f"An unexpected error occurred: {exc}")
        raise

# Function to start the translation task
async def start_translation_task(task_id: str, text: str, languages: list[str]):
    translations = {}
    async with AsyncSession(engine) as session:
        try:
            # Retrieve the task from the database using its ID
            task = await session.get(TranslationTask, task_id)
            if not task:
                logger.error(f"Task with id {task_id} not found.")
                return

            # Translate text to each specified language
            for index, language in enumerate(languages):
                logger.info(f"Translating text to {language}...")
                translation = await translate_text(text, language)
                translations[language] = translation
                completion_percentage = ((index + 1) / len(languages)) * 100
                logger.info(f"Translation to {language} completed. Task ID:{task_id} -- Compilation: {completion_percentage:.0f}%")

            # Update the task with the translations and mark it as completed
            task.set_translations(translations)
            task.status = "completed"
            await session.commit()
            logger.info(f"Task {task_id} marked as completed.")
        except Exception as e:
            logger.error(f"Error during translation task {task_id}: {e}", exc_info=True)
            # Mark the task as failed in case of any error
            task.status = "failed"
            await session.commit()
