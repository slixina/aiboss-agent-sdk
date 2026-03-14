import requests
from typing import Dict, Any
from bs4 import BeautifulSoup
from ..executor import Executor
from ..sandbox import Sandbox, SandboxError
from ..config import get_allowed_domains
from ..utils import safe_regex_search

from urllib.parse import urlparse

class ScrapeExecutor(Executor):
    def __init__(self):
        # Whitelisted domains as per security requirement
        # Loaded from config
        self.allowed_domains = get_allowed_domains()
        self.sandbox = Sandbox(allowed_domains=self.allowed_domains)

    @property
    def task_type(self) -> str:
        return "scrape"

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = payload.get("url")
        selector = payload.get("selector")
        regex_pattern = payload.get("regex")

        if not url:
            # raise ValueError("Missing 'url' in payload for ScrapeExecutor")
            # Instead of raising, return failure so runner can report it
            return {"success": False, "error": "Missing 'url'"}

        try:
            # Sandbox validation (Get resolved IP to prevent Rebinding)
            resolved_ip = self.sandbox.validate_url(url)
            
            parsed = urlparse(url)
            target_url = url
            headers = {'User-Agent': 'OpenClaw-Agent/1.0'}

            # For HTTP, use IP directly to prevent DNS Rebinding
            if parsed.scheme == 'http':
                target_url = url.replace(parsed.hostname, resolved_ip, 1)
                headers['Host'] = parsed.hostname
            
            # For HTTPS, we cannot easily replace hostname due to SNI/Cert validation
            # So we rely on the check we just did. 
            # (In production, use a custom TransportAdapter to force connection to resolved_ip)

            response = requests.get(target_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            content = response.text
            
            # Selector extraction
            if selector:
                try:
                    soup = BeautifulSoup(content, 'lxml')
                    elements = soup.select(selector)
                    content = "\n".join([e.get_text(strip=True) for e in elements])
                except Exception as e:
                    return {"success": False, "url": url, "error": f"Selector error: {str(e)}"}

            # Regex filtering (ReDoS Protected)
            if regex_pattern:
                try:
                    match = safe_regex_search(regex_pattern, content)
                    if match:
                        content = match
                    else:
                        return {"success": False, "url": url, "error": "Regex pattern not found"}
                except Exception as e:
                    return {"success": False, "url": url, "error": f"Regex error: {str(e)}"}
            
            return {
                "success": True,
                "url": url,
                "status_code": response.status_code,
                "content_length": len(response.content),
                "content": content[:5000] 
            }
        except (requests.exceptions.RequestException, SandboxError) as e:
            return {
                "success": False, 
                "url": url,
                "error": str(e)
            }
