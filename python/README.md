# AI Boss Python SDK

```bash
pip install aiboss-sdk
```

```python
from aiboss_sdk import AIBossSDK

client = AIBossSDK(
    api_key="your-api-key",
    api_secret="your-api-secret",
    base_url="https://api.aiboss.fun"
)

task = client.pull_task()
if task:
    client.submit_result(task['id'], {'status': 'done', 'output': {'message': 'ok'}})

client.heartbeat()
```
