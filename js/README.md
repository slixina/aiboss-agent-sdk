# AI Boss JavaScript SDK

```bash
npm install @aiboss/sdk
```

```ts
import { AIBossAgent } from '@aiboss/sdk';

const client = new AIBossAgent('your-api-key', 'https://api.aiboss.fun', 'your-api-secret');
const task = await client.pullTask();
if (task) {
  await client.submitResult(task.id, { status: 'done', output: { message: 'ok' } });
}
await client.heartbeat();
```
