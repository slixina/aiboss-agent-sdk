import subprocess
import time
import re
from typing import Dict, Any
from ..executor import Executor

class PingExecutor(Executor):
    @property
    def task_type(self) -> str:
        return "ping"

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        target = payload.get("target")
        if not target:
            raise ValueError("Missing 'target' in payload for PingExecutor")
            
        # Security: Validate target format to prevent command injection
        if not re.match(r"^[a-zA-Z0-9.-]+$", target):
             return {"success": False, "error": "Invalid target format (Security Violation)"}

        try:
            # Simple ping implementation (Windows specific since environment is windows)
            # -n 1 sends 1 packet
            output = subprocess.check_output(
                ["ping", "-n", "1", target],
                stderr=subprocess.STDOUT,
                timeout=5
            ).decode("utf-8")
            
            latency = self._parse_latency(output)
            
            return {
                "success": True,
                "target": target,
                "latency_ms": latency,
                "output": output
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _parse_latency(self, output: str) -> float:
        # Example output line: "Reply from 1.1.1.1: bytes=32 time=14ms TTL=57"
        # We need to extract 'time=14ms' -> 14.0
        try:
            if "time=" in output:
                part = output.split("time=")[1]
                ms = part.split("ms")[0]
                return float(ms)
            return -1.0
        except:
            return -1.0
