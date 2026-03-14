import re
import multiprocessing
import logging
from typing import Optional

logger = logging.getLogger("OpenClaw.Utils")

def _regex_worker(pattern: str, text: str, queue: multiprocessing.Queue):
    try:
        match = re.search(pattern, text)
        queue.put(match.group(0) if match else None)
    except Exception as e:
        queue.put(e)

def safe_regex_search(pattern: str, text: str, timeout_seconds: float = 0.5) -> Optional[str]:
    """
    Safely execute regex search with timeout and length limit to prevent ReDoS.
    Uses multiprocessing to ensure hard timeout enforcement.
    """
    # 1. Length Limit
    if len(pattern) > 100:
        raise ValueError(f"Regex pattern too long ({len(pattern)} > 100 chars)")
    
    # 2. Timeout Execution
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=_regex_worker, args=(pattern, text, queue))
    p.start()
    
    p.join(timeout_seconds)
    
    if p.is_alive():
        p.terminate()
        p.join()
        raise TimeoutError(f"Regex execution timed out (> {timeout_seconds}s)")
        
    if queue.empty():
        return None
        
    result = queue.get()
    if isinstance(result, Exception):
        raise result
        
    return result
