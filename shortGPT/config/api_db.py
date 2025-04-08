import enum
import os
from shortGPT.database.db_document import TinyMongoDocument

# DO NOT use load_dotenv on Hugging Face – secrets are already in os.environ

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

        # First try: Hugging Face secret (env variable)
        env_key = key.replace(" ", "_").upper()
        api_key = os.environ.get(env_key)
        if api_key:
            return api_key

        # Second try: database fallback
        api_key = cls.api_key_doc_manager._get(key)
        if api_key:
            return api_key

        return ""

    @classmethod
    def set_api_key(cls, key: str | ApiProvider, value: str):
        if isinstance(key, ApiProvider):
            key = key.value
        return cls.api_key_doc_manager._save({key: value})
