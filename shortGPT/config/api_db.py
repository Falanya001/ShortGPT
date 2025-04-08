import enum
import os
from shortGPT.database.db_document import TinyMongoDocument
from dotenv import load_dotenv
load_dotenv('./.env')
class ApiProvider(enum.Enum):
    OPENAI = "OPENAI_API_KEY"
    GEMINI = "GEMINI_API_KEY"
    ELEVEN_LABS = "ELEVENLABS_API_KEY"
    PEXELS = "PEXELS_API_KEY"


class ApiKeyManager:
    api_key_doc_manager = TinyMongoDocument("api_db", "api_keys", "key_doc", create=True)

    @classmethod
    def get_api_key(cls, key: str | ApiProvider):
        if isinstance(key, ApiProvider):
            key = key.value
        # Format the key to match the environment variable naming style
        env_key = key.replace(" ", "_").upper()
        
        # Retrieve from HF Secrets via environment variable
        return os.getenv(env_key, "")

    @classmethod
    def set_api_key(cls, key: str | ApiProvider, value: str):
        if isinstance(key, ApiProvider):
            key = key.value
        return cls.api_key_doc_manager._save({key: value})
