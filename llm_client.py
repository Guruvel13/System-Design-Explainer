# llm_client.py
# Enhanced Groq Llama client with retry logic, caching, and comprehensive error handling

import os
import hashlib
import json
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System prompt for architecture generation
SYSTEM_PROMPT = """
You are a senior system architect.
Your output MUST contain EXACTLY TWO SECTIONS and NOTHING ELSE.

[EXPLANATION]
Write a clear, structured, highly detailed system design (max ~700 words).
Use plain headings, short paragraphs, simple lists. No code blocks. No decorative separators.

Mandatory subsections:
1) Problem Summary
2) Functional Breakdown
3) Non-Functional Impact
4) High-Level Architecture (justification)
5) Layered Architecture View
6) Step-by-Step Data Flow (use → arrows)
7) Component Responsibilities
8) Detailed Diagram Explanation (explain EVERY node + EVERY edge)
9) Scalability & Partitioning
10) Storage Strategy
11) Caching Strategy
12) Load Balancing & Traffic Management
13) Security & Compliance
14) Fault Tolerance & Recovery
15) Observability & SLOs
16) Deployment & DevOps
17) Trade-offs & Alternatives
18) Recommended Tech Stack

[DIAGRAM_JSON]
Return STRICT VALID JSON ONLY (only JSON, nothing else). Must include:
nodes, edges, annotations, layers, edge_types.
3-12 components. Annotations <=10 words per node.
Output must end immediately after the closing brace.
"""

# Simple in-memory cache for LLM responses
_response_cache: Dict[str, str] = {}
_cache_enabled = True
_max_cache_size = 100


def _generate_cache_key(requirement: str, model_name: str) -> str:
    """Generate a cache key from requirement and model name."""
    combined = f"{requirement}::{model_name}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()


def _get_cached_response(cache_key: str) -> Optional[str]:
    """Retrieve cached response if available."""
    if not _cache_enabled:
        return None
    return _response_cache.get(cache_key)


def _cache_response(cache_key: str, response: str) -> None:
    """Cache a response with size limit."""
    if not _cache_enabled:
        return
    
    # Simple LRU: if cache is full, remove oldest entries
    if len(_response_cache) >= _max_cache_size:
        # Remove 20% of oldest entries
        keys_to_remove = list(_response_cache.keys())[:_max_cache_size // 5]
        for key in keys_to_remove:
            _response_cache.pop(key, None)
    
    _response_cache[cache_key] = response


def clear_cache() -> None:
    """Clear the response cache."""
    global _response_cache
    _response_cache = {}
    logger.info("LLM response cache cleared")


def set_cache_enabled(enabled: bool) -> None:
    """Enable or disable caching."""
    global _cache_enabled
    _cache_enabled = enabled
    logger.info(f"LLM caching {'enabled' if enabled else 'disabled'}")


def _extract_content_from_completion(completion: Any) -> str:
    """
    Robust extraction of content from Groq completion object.
    Handles multiple SDK versions and response formats.
    """
    if not completion:
        raise ValueError("Received empty completion object")
    
    if not hasattr(completion, "choices") or not completion.choices:
        raise ValueError("Completion object has no choices")
    
    choice = completion.choices[0]
    
    # Try common response shapes
    try:
        if hasattr(choice, "message") and hasattr(choice.message, "content"):
            content = choice.message.content
            if content:
                return str(content).strip()
    except Exception:
        pass
    
    # Try dict-based message
    if hasattr(choice, "message") and isinstance(choice.message, dict):
        msg = choice.message
        content = msg.get("content") or msg.get("text")
        if content:
            return str(content).strip()
    
    # Try text attribute
    if hasattr(choice, "text") and isinstance(choice.text, str):
        return choice.text.strip()
    
    # Fallback: stringify the choice
    result = str(choice).strip()
    if result:
        return result
    
    raise ValueError("Could not extract content from completion")


def call_llm(
    requirement: str,
    model_name: Optional[str] = "llama-3.1-8b-instant",
    max_retries: int = 3,
    use_cache: bool = True,
    temperature: float = 0.15,
    max_tokens: int = 1400
) -> str:
    """
    Sends SYSTEM_PROMPT + requirement to Groq and returns assistant content.
    
    Args:
        requirement: User's system design requirement
        model_name: Groq model to use
        max_retries: Number of retry attempts on failure
        use_cache: Whether to use response caching
        temperature: Model temperature (0-1)
        max_tokens: Maximum tokens in response
    
    Returns:
        str: LLM-generated response text
    
    Raises:
        RuntimeError: If API key is missing or all retries fail
        ValueError: If response format is invalid
    """
    # Validate inputs
    if not requirement or not requirement.strip():
        raise ValueError("Requirement cannot be empty")
    
    requirement = requirement.strip()
    
    # Check cache first
    if use_cache and _cache_enabled:
        cache_key = _generate_cache_key(requirement, model_name)
        cached = _get_cached_response(cache_key)
        if cached:
            logger.info(f"Cache hit for requirement hash: {cache_key[:8]}...")
            return cached
    
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY missing. Set environment variable or add to Streamlit Secrets: "
            "GROQ_API_KEY = \"gsk_your_key\""
        )
    
    # Initialize client
    try:
        client = Groq(api_key=api_key)
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Groq client: {e}")
    
    # Build prompt
    prompt = f"{SYSTEM_PROMPT}\n\nUSER REQUIREMENT:\n{requirement}"
    
    # Retry loop
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info(f"Calling Groq API (attempt {attempt + 1}/{max_retries})")
            
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9
            )
            
            # Extract content
            content = _extract_content_from_completion(completion)
            
            # Validate response
            if len(content) < 50:
                raise ValueError(f"Response too short ({len(content)} chars)")
            
            # Cache successful response
            if use_cache and _cache_enabled:
                cache_key = _generate_cache_key(requirement, model_name)
                _cache_response(cache_key, content)
                logger.info(f"Cached response for hash: {cache_key[:8]}...")
            
            logger.info(f"Successfully received response ({len(content)} chars)")
            return content
            
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            
            # Don't retry on certain errors
            if "api_key" in str(e).lower() or "authentication" in str(e).lower():
                raise RuntimeError(f"Authentication error: {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < max_retries - 1:
                import time
                wait_time = 2 ** attempt  # 1s, 2s, 4s...
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
    
    # All retries failed
    raise RuntimeError(
        f"All {max_retries} attempts failed. Last error: {last_error}"
    )


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return {
        "enabled": _cache_enabled,
        "size": len(_response_cache),
        "max_size": _max_cache_size,
        "entries": list(_response_cache.keys())
    }


def validate_api_key() -> bool:
    """
    Validate that a Groq API key is configured.
    
    Returns:
        bool: True if API key exists, False otherwise
    """
    return bool(os.getenv("GROQ_API_KEY"))
