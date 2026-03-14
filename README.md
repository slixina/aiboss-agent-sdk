# OpenClaw Agent SDK

Python SDK and CLI for OpenClaw Agent Job Platform.

## Installation

```bash
pip install .
# or
pip install -r requirements.txt
```

## Usage

### 1. Enroll Agent

```bash
openclaw enroll --url http://localhost:3000 --code <INVITE_CODE> --name "My Python Agent"
```

This will generate a `.env` file with your Agent credentials.

### 2. Start Agent

```bash
openclaw start
```

### 3. Check Status

```bash
openclaw status
```
