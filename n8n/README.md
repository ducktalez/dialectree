# N8N – Twitter Import Workflow

## Overview
This workflow imports Twitter/X threads and maps them to argument nodes in Dialectree.

## Workflow Steps
1. **Trigger**: Manual or scheduled (e.g. every 6 hours)
2. **Twitter API**: Fetch thread replies for a given conversation ID
3. **Code Node**: Analyse tweets and classify position (PRO / CONTRA / NEUTRAL)
4. **Dialectree API**: Create ArgumentNodes via `POST /api/arguments/`

## Setup
1. Install N8N: `npm install -g n8n` or use Docker
2. Import `twitter_import_workflow.json` into N8N
3. Configure Twitter API v2 Bearer Token in credentials
4. Set Dialectree backend URL (default: `http://localhost:8000`)
