# kroki_renderer.py
# Enhanced renderer with retry logic, caching, fallback, and better error handling

import requests
import hashlib
import logging
from typing import Literal, Optional, Dict, Any
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
KROKI_BASE = "https://kroki.io"
KROKI_TIMEOUT = 30
MAX_RETRIES = 3
CACHE_ENABLED = True

# Simple in-memory cache for rendered diagrams
_render_cache: Dict[str, bytes] = {}
_max_cache_size = 50


def _generate_cache_key(source: str, format: str, diagram_type: str) -> str:
    """Generate cache key from source and format."""
    combined = f"{diagram_type}:{format}:{source}"
    return hashlib.md5(combined.encode('utf-8')).hexdigest()


def _get_cached_render(cache_key: str) -> Optional[bytes]:
    """Retrieve cached render if available."""
    if not CACHE_ENABLED:
        return None
    return _render_cache.get(cache_key)


def _cache_render(cache_key: str, data: bytes) -> None:
    """Cache rendered diagram."""
    if not CACHE_ENABLED or not data:
        return
    
    # Simple LRU: if cache is full, remove oldest entries
    if len(_render_cache) >= _max_cache_size:
        keys_to_remove = list(_render_cache.keys())[:_max_cache_size // 5]
        for key in keys_to_remove:
            _render_cache.pop(key, None)
    
    _render_cache[cache_key] = data


def _post_kroki(
    format: Literal["png", "svg", "pdf"],
    diagram_type: Literal["graphviz", "plantuml", "mermaid"],
    source: str,
    max_retries: int = MAX_RETRIES,
    timeout: int = KROKI_TIMEOUT,
    use_cache: bool = True
) -> bytes:
    """
    Render diagram using Kroki.io API with retry logic and caching.
    
    Args:
        format: Output format (png, svg, pdf)
        diagram_type: Diagram type (graphviz, plantuml, mermaid)
        source: Diagram source code
        max_retries: Number of retry attempts
        timeout: Request timeout in seconds
        use_cache: Whether to use caching
    
    Returns:
        Rendered diagram as bytes
    
    Raises:
        requests.HTTPError: If API request fails after all retries
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if not source or not source.strip():
        raise ValueError("Diagram source cannot be empty")
    
    valid_formats = ["png", "svg", "pdf"]
    if format not in valid_formats:
        raise ValueError(f"Format must be one of {valid_formats}")
    
    valid_types = ["graphviz", "plantuml", "mermaid"]
    if diagram_type not in valid_types:
        raise ValueError(f"Diagram type must be one of {valid_types}")
    
    # Check cache first
    if use_cache:
        cache_key = _generate_cache_key(source, format, diagram_type)
        cached = _get_cached_render(cache_key)
        if cached:
            logger.info(f"Cache hit for {diagram_type} {format} (hash: {cache_key[:8]}...)")
            return cached
    
    # Build request
    url = f"{KROKI_BASE}/{diagram_type}/{format}"
    headers = {"Content-Type": "text/plain"}
    data = source.encode("utf-8")
    
    logger.info(f"Rendering {diagram_type} to {format} (size: {len(data)} bytes)")
    
    # Retry loop
    last_error = None
    for attempt in range(max_retries):
        try:
            logger.info(f"Kroki API request (attempt {attempt + 1}/{max_retries})")
            
            response = requests.post(
                url,
                data=data,
                headers=headers,
                timeout=timeout
            )
            
            # Check for HTTP errors
            response.raise_for_status()
            
            # Validate response
            content = response.content
            if not content:
                raise ValueError("Received empty response from Kroki")
            
            if len(content) < 100:
                raise ValueError(f"Response suspiciously small ({len(content)} bytes)")
            
            # Cache successful render
            if use_cache:
                cache_key = _generate_cache_key(source, format, diagram_type)
                _cache_render(cache_key, content)
                logger.info(f"Cached render (hash: {cache_key[:8]}...)")
            
            logger.info(f"Successfully rendered {len(content)} bytes")
            return content
            
        except requests.Timeout as e:
            last_error = e
            logger.warning(f"Request timeout on attempt {attempt + 1}")
            
        except requests.HTTPError as e:
            last_error = e
            status_code = e.response.status_code if e.response else "unknown"
            logger.warning(f"HTTP error {status_code} on attempt {attempt + 1}: {e}")
            
            # Don't retry on client errors (4xx)
            if e.response and 400 <= e.response.status_code < 500:
                raise
            
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries - 1:
            import time
            wait_time = 2 ** attempt  # 1s, 2s, 4s...
            logger.info(f"Waiting {wait_time}s before retry...")
            time.sleep(wait_time)
    
    # All retries failed
    raise RuntimeError(
        f"Failed to render diagram after {max_retries} attempts. "
        f"Last error: {last_error}"
    )


def generate_png_from_dot(dot_source: str, **kwargs) -> bytes:
    """
    Generate PNG from Graphviz DOT source.
    
    Args:
        dot_source: Graphviz DOT source code
        **kwargs: Additional arguments for _post_kroki
    
    Returns:
        PNG image as bytes
    """
    return _post_kroki("png", "graphviz", dot_source, **kwargs)


def generate_svg_from_dot(dot_source: str, **kwargs) -> bytes:
    """
    Generate SVG from Graphviz DOT source.
    
    Args:
        dot_source: Graphviz DOT source code
        **kwargs: Additional arguments for _post_kroki
    
    Returns:
        SVG image as bytes
    """
    return _post_kroki("svg", "graphviz", dot_source, **kwargs)


def generate_pdf_from_dot(dot_source: str, **kwargs) -> bytes:
    """
    Generate PDF from Graphviz DOT source.
    
    Args:
        dot_source: Graphviz DOT source code
        **kwargs: Additional arguments for _post_kroki
    
    Returns:
        PDF document as bytes
    """
    return _post_kroki("pdf", "graphviz", dot_source, **kwargs)


def render_diagram(
    source: str,
    diagram_type: Literal["graphviz", "plantuml", "mermaid"] = "graphviz",
    format: Literal["png", "svg", "pdf"] = "png",
    **kwargs
) -> bytes:
    """
    Universal diagram rendering function.
    
    Args:
        source: Diagram source code
        diagram_type: Type of diagram
        format: Output format
        **kwargs: Additional arguments for _post_kroki
    
    Returns:
        Rendered diagram as bytes
    """
    return _post_kroki(format, diagram_type, source, **kwargs)


def clear_cache() -> None:
    """Clear the render cache."""
    global _render_cache
    _render_cache = {}
    logger.info("Render cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    total_size = sum(len(v) for v in _render_cache.values())
    
    return {
        "enabled": CACHE_ENABLED,
        "entries": len(_render_cache),
        "max_entries": _max_cache_size,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }


def test_kroki_connection(timeout: int = 5) -> bool:
    """
    Test connection to Kroki service.
    
    Args:
        timeout: Connection timeout in seconds
    
    Returns:
        True if service is reachable, False otherwise
    """
    try:
        # Simple test with minimal diagram
        test_source = "digraph { A -> B; }"
        response = requests.post(
            f"{KROKI_BASE}/graphviz/svg",
            data=test_source.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
            timeout=timeout
        )
        response.raise_for_status()
        logger.info("Kroki service is reachable")
        return True
    except Exception as e:
        logger.error(f"Kroki service unreachable: {e}")
        return False


def get_supported_formats() -> Dict[str, list]:
    """Get supported diagram types and output formats."""
    return {
        "diagram_types": ["graphviz", "plantuml", "mermaid"],
        "output_formats": ["png", "svg", "pdf"]
    }
