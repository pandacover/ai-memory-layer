CHROMA_PORT = 8081
CHROMA_COLLECTION_NAME = "memories"
DEFAULT_MEMORY_RESULT_COUNT = 5

MEMORY_EMBEDDING_MODEL = "nomic-embed-text:v1.5"
OLLAMA_EMBEDDING_URL = "http://localhost:11434/api/embeddings"
CHAT_MODEL = "nemotron-3-super:cloud"
OLLAMA_BASE_URL = "https://ollama.com"

CORS_ALLOW_ORIGINS = ["http://localhost:5173"]

SYSTEM_PROMPT = """
- the tools you have access to
    - retrieve_memory: uses memories specific to given queries
"""

MEMORY_EXTRACTION_PROMPT = """
You are an expert observer and interpreter. Given a user query, you:
- infer correct observations limited to the informations provided, and don't overreach
- return only the observations that should be saved and discard the rest
- return only observations, separated by lines. No label or markdown is needed. Just plain string.
- if there's no good observation then you can ignore since you are not obliged to save anything
- provide distilled 0-N memories out of that given query.

For example:
query:
    human: Hey dude, I am Luv. I am a software engineer.
    ai: Hey Luv, nice to meet you.

good obsverations:
    user name is Luv.
    Luv is a software engineer.
    Luv must like to talk about coding and technology in general.

bad observations:
    user greeted me with (hey dude) so he must be in a jolly mood.
    hey dude is a positive greeting, so user must be a happy person.
"""
