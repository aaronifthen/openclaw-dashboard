import os
import json
import glob
from flask import Flask, render_template, jsonify, send_from_directory

app = Flask(__name__)

# Paths
WORKSPACE_DIR = os.getenv('OPENCLAW_WORKSPACE', '/data/.openclaw/workspace')
SESSIONS_DIR = os.getenv('OPENCLAW_SESSIONS', '/data/.openclaw/agents/main/sessions')
# Transcripts in main session are usually stored in the sessions dir
TRANSCRIPTS_DIR = os.getenv('OPENCLAW_SESSIONS', '/data/.openclaw/agents/main/sessions')

@app.route('/')
def index():
    # Basic debug logging to container logs (stdout)
    print(f"DEBUG: Checking WORKSPACE_DIR: {WORKSPACE_DIR}")
    print(f"DEBUG: Exists? {os.path.exists(WORKSPACE_DIR)}")
    if os.path.exists(WORKSPACE_DIR):
        print(f"DEBUG: Files: {os.listdir(WORKSPACE_DIR)[:5]}")
    return render_template('index.html')

@app.route('/api/files')
def get_files():
    md_files = []
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        for file in files:
            if file.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(root, file), WORKSPACE_DIR)
                md_files.append(rel_path)
    return jsonify(md_files)

@app.route('/api/agents')
def get_agents():
    # In OpenClaw, cron/scheduled tasks represent our scheduled agents/jobs
    # This is a simplified fetch; real OpenClaw uses a SQLite DB or JSON state for cron
    # We will try to read the sessions.json for agent metadata
    sessions_path = os.path.join(SESSIONS_DIR, 'sessions.json')
    if os.path.exists(sessions_path):
        with open(sessions_path, 'r') as f:
            data = json.load(f)
            return jsonify(data.get('sessions', []))
    return jsonify([])

@app.route('/api/history')
def get_history():
    # List recent transcripts (.jsonl files)
    transcripts = glob.glob(os.path.join(TRANSCRIPTS_DIR, '*.jsonl'))
    history = [os.path.basename(t) for t in transcripts]
    return jsonify(history)

@app.route('/workspace/<path:filename>')
def serve_md(filename):
    return send_from_directory(WORKSPACE_DIR, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
