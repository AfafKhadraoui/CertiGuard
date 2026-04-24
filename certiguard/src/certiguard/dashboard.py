from __future__ import annotations
import http.server
import socketserver
import webbrowser
import os
import threading
import time

def review_audit_logs(audit_log_path: str, port: int = 8080) -> None:
    """
    Vendor Server (Optional) Dashboard component.
    Used to review logs at renewal time.
    """
    # Locate the built UI directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ui_dist_dir = os.path.join(current_dir, 'ui', 'dist')
    
    if not os.path.exists(ui_dist_dir):
        print(f"Error: Dashboard UI not found at {ui_dist_dir}")
        print("Please ensure the UI has been built (npm run build).")
        return

    # Change to the dist directory so SimpleHTTPRequestHandler serves from there
    os.chdir(ui_dist_dir)
    
    class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()
            
    Handler = NoCacheHandler
    
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving dashboard at http://localhost:{port}")
        print("Press Ctrl+C to stop the server.")
        
        # Open the browser in a separate thread after a short delay
        def open_browser():
            time.sleep(1)
            webbrowser.open(f"http://localhost:{port}?nocache={time.time()}")
            
        threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down the dashboard server.")
            httpd.server_close()
