#!/usr/bin/env python3
"""
Development HTTP server with proper no-cache headers
Prevents browser caching issues during development
"""
import http.server
import socketserver
from pathlib import Path

PORT = 8080

class NoCacheHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler that prevents browser caching"""

    def end_headers(self):
        """Add no-cache headers to all responses"""
        # Prevent all caching during development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def log_message(self, format, *args):
        """Override to provide cleaner log messages"""
        # Only log actual requests, not every asset
        if not args[0].endswith(('favicon.ico', '.css', '.js')):
            super().log_message(format, *args)

if __name__ == '__main__':
    # Change to frontend directory
    frontend_dir = Path(__file__).parent

    with socketserver.TCPServer(("", PORT), NoCacheHTTPRequestHandler) as httpd:
        print("=" * 80)
        print("🚀 THE DAILY WORKER - DEVELOPMENT SERVER")
        print("=" * 80)
        print(f"\n✅ Server running at: http://localhost:{PORT}/")
        print(f"📁 Serving from: {frontend_dir}")
        print("\n📌 No-Cache Headers Enabled:")
        print("   • Cache-Control: no-store, no-cache, must-revalidate")
        print("   • No hard refreshes needed during development")
        print("\n🔗 Quick Links:")
        print(f"   Homepage:        http://localhost:{PORT}/")
        print(f"   Article Example: http://localhost:{PORT}/article.html?id=1")
        print(f"   Admin Dashboard: http://localhost:{PORT}/admin/")
        print("\n💡 Press Ctrl+C to stop the server")
        print("=" * 80)
        print()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped")
