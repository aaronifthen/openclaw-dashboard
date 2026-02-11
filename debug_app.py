import os
import json
from flask import Flask, jsonify

app = Flask(__name__)

PATHS = [
    '/data/.openclaw',
    '/data/.openclaw/workspace',
    '/data/.openclaw/agents/main/sessions',
    os.getenv('OPENCLAW_DATA_PATH', 'Not Set')
]

@app.route('/')
def debug():
    results = {}
    for p in PATHS:
        exists = os.path.exists(p)
        is_dir = os.path.isdir(p) if exists else False
        content = os.listdir(p)[:5] if is_dir else []
        results[p] = {
            "exists": exists,
            "is_dir": is_dir,
            "sample_content": content
        }
    
    env_vars = {k: v for k, v in os.environ.items() if 'OPENCLAW' in k}
    
    return jsonify({
        "paths_check": results,
        "environment_variables": env_vars,
        "user_id": os.getuid()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
