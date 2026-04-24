from __future__ import annotations
import os
import threading
import time
import webbrowser
import json
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

def review_audit_logs(audit_log_path: str, port: int = 8080) -> None:
    """
    Vendor Dashboard Server.
    Serves the React UI and provides an API to read real audit logs.
    """
    app = Flask(__name__, static_folder=None)
    CORS(app)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    ui_dist_dir = os.path.join(current_dir, 'ui', 'dist')

    @app.route("/api/logs")
    def get_logs():
        path = Path(audit_log_path)
        if not path.exists():
            return jsonify([])
        
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
            logs = []
            for i, line in enumerate(lines):
                try:
                    entry = json.loads(line)
                    # Flatten for easier UI consumption
                    logs.append({
                        "id": i,
                        "timestamp": entry.get("ts", ""),
                        "event": entry.get("event", ""),
                        "payload": entry.get("payload", {}),
                        "hash": entry.get("entry_hash", ""),
                        "severity": "high" if "fail" in entry.get("event", "").lower() or "mismatch" in entry.get("event", "").lower() else "info"
                    })
                except Exception:
                    continue
            return jsonify(logs[::-1]) # Return newest first
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/logs/ingest", methods=["POST"])
    def ingest_logs():
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        logs = data.get("logs", [])
        path = Path(audit_log_path)
        
        with path.open("a", encoding="utf-8") as f:
            for log in logs:
                f.write(json.dumps(log) + "\n")
                
        return jsonify({"status": "ok", "count": len(logs)})

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if not os.path.exists(ui_dist_dir):
            return f"Error: UI dist directory not found at {ui_dist_dir}. Please run 'npm run build' in the UI folder.", 404
            
        if path != "" and os.path.exists(os.path.join(ui_dist_dir, path)):
            return send_from_directory(ui_dist_dir, path)
        else:
            return send_from_directory(ui_dist_dir, 'index.html')

    print(f"[*] Starting CertiGuard Dashboard on http://localhost:{port}")
    
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(f"http://localhost:{port}")
        
    threading.Thread(target=open_browser, daemon=True).start()
    
    app.run(host='0.0.0.0', port=port, debug=False)
