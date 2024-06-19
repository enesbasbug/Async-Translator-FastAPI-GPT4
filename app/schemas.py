from pydantic import BaseModel
from typing import List

class TranslationRequest(BaseModel):
    """
    Schema representing a request to translate text.
    
    Attributes:
        text (str): The text to be translated.
        languages (List[str]): A list of target languages for the translation.
    """
    text: str
    languages: List[str]
