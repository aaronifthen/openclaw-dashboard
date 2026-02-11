import os
import json
import asyncio
import websockets
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Config for OpenClaw API
# On Hostinger, 'openclaw' should be the name of the container or the VPS IP
OPENCLAW_URL = os.getenv('OPENCLAW_URL', 'ws://openclaw:63362')
OPENCLAW_TOKEN = os.getenv('OPENCLAW_TOKEN', 'KcDU7jBwXgbyUGDYpflfR7KbOgD0Lh1A')

async def openclaw_rpc(method, params=None):
    """Helper to talk to OpenClaw via WebSocket RPC."""
    try:
        async with websockets.connect(OPENCLAW_URL) as websocket:
            # Auth
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "id": "auth",
                "method": "auth.login",
                "params": {"token": OPENCLAW_TOKEN}
            }))
            await websocket.recv()

            # Command
            rpc_id = method.replace('.', '_')
            await websocket.send(json.dumps({
                "jsonrpc": "2.0",
                "id": rpc_id,
                "method": method,
                "params": params or {}
            }))
            response = await websocket.recv()
            return json.loads(response).get('result', {})
    except Exception as e:
        print(f"RPC Error: {e}")
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files')
def get_files():
    # List workspace files via RPC
    # We use 'exec' to run an ls command through the agent
    res = asyncio.run(openclaw_rpc('agent.run', {
        "message": "list all .md files in workspace",
        "tools": ["read"] 
    }))
    # Note: For a robust dashboard, we'd use a dedicated 'fs.list' RPC if available, 
    # but 'agent.run' or direct 'exec' is the universal way.
    return jsonify(res.get('files', ['SOUL.md', 'USER.md', 'AGENTS.md']))

@app.route('/api/agents')
def get_agents():
    # Use built-in sessions.list RPC
    res = asyncio.run(openclaw_rpc('sessions.list', {"limit": 10}))
    return jsonify(res.get('sessions', []))

@app.route('/api/history')
def get_history():
    # Mocking for now, as history often requires individual session reads
    return jsonify(["main-session.jsonl"])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
