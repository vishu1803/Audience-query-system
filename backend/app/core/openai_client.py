"""
OpenAI client configuration and utilities.
"""

from openai import AsyncOpenAI
from app.core.config import settings

# Initialize async OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def test_openai_connection() -> bool:
    """Test if OpenAI API key is valid"""
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'connected'"}],
            max_tokens=10
        )
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False
