from sqlmodel import SQLModel, Field
from typing import Optional
import json

class TranslationTask(SQLModel, table=True):
    """
    Model representing a translation task.
    
    Attributes:
        id (Optional[str]): The unique identifier for the task.
        text (str): The text to be translated.
        languages (str): A JSON-encoded string representing the list of target languages.
        status (str): The current status of the task (default is "in_progress").
        translations (Optional[str]): A JSON-encoded string representing the translations.
    """
    id: Optional[str] = Field(default=None, primary_key=True)
    text: str
    languages: str
    status: str = Field(default="in_progress")
    translations: Optional[str] = Field(default=None)

    def set_languages(self, languages: list[str]):
        """
        Sets the target languages for the translation task.
        
        Args:
            languages (list[str]): A list of target languages.
        """
        self.languages = json.dumps(languages) # Serialize obj to a JSON formatted str.

    def get_languages(self) -> list[str]:
        """
        Retrieves the list of target languages for the translation task.
        
        Returns:
            list[str]: The list of target languages.
        """
        return json.loads(self.languages) # Deserialize s (a str instance containing a JSON document) to a Python object.

    def set_translations(self, translations: dict):
        """
        Sets the translations for the translation task.
        
        Args:
            translations (dict): A dictionary containing the translations.
        """
        self.translations = json.dumps(translations) # Serialize obj to a JSON formatted str.


    def get_translations(self) -> Optional[dict]:
        """
        Retrieves the translations for the translation task.
        
        Returns:
            Optional[dict]: The translations if they exist, otherwise None.
        """
        if self.translations:
            return json.loads(self.translations) # Deserialize s (a str instance containing a JSON document) to a Python object.
        return None
