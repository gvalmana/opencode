#!/usr/bin/env python3
"""
Re-authorize Google Calendar with write scope (calendar.events).
Run this script to add write permission for creating calendar events.
"""
import json
import os
import sys
import urllib.request
import urllib.parse
import http.server
import threading
import webbrowser
from datetime import datetime

AUTH_FILE = os.path.expanduser("~/.local/share/opencode/mcp-auth.json")
CLIENT_ID = os.environ.get("GOOGLE_MCP_CLIENT_ID")
CLIENT_SECRET = os.environ.get("GOOGLE_MCP_CLIENT_SECRET")
REDIRECT_URI = "http://127.0.0.1:19876/mcp/oauth/callback"
SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.events.readonly",
    "https://www.googleapis.com/auth/calendar.events.freebusy",
    "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
]
AUTH_URL_TMPL = "https://accounts.google.com/o/oauth2/v2/auth?{params}"
TOKEN_URL = "https://oauth2.googleapis.com/token"

auth_code = None


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        if "/callback" in self.path:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            auth_code = params.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Autorizado! Puedes cerrar esta ventana.</h1>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("Error: GOOGLE_MCP_CLIENT_ID and GOOGLE_MCP_CLIENT_SECRET must be set", file=sys.stderr)
        sys.exit(1)

    params = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    })
    auth_url = AUTH_URL_TMPL.format(params=params)

    print("=" * 60)
    print("RE-AUTH GOOGLE CALENDAR - WRITE SCOPE")
    print("=" * 60)
    print()
    print("1. Abre esta URL en tu navegador:")
    print()
    print(auth_url)
    print()
    print("2. Autoriza la aplicacion")
    print("3. Copia el codigo de autorizacion")
    print()

    # Open browser automatically
    webbrowser.open(auth_url)

    server = http.server.HTTPServer(("127.0.0.1", 19876), CallbackHandler)
    thread = threading.Thread(target=server.handle_request)
    thread.daemon = True
    thread.start()

    print("Esperando autorizacion en http://127.0.0.1:19876/mcp/oauth/callback ...")
    print()

    thread.join(timeout=300)

    if not auth_code:
        print("Error: No se recibio el codigo de autorizacion", file=sys.stderr)
        sys.exit(1)

    data = urllib.parse.urlencode({
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    tokens = json.loads(urllib.request.urlopen(req).read())

    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            auth_data = json.load(f)
    else:
        auth_data = {}

    if "google-calendar" not in auth_data:
        auth_data["google-calendar"] = {}
    auth_data["google-calendar"]["tokens"] = {
        "accessToken": tokens.get("access_token"),
        "refreshToken": tokens.get("refresh_token"),
        "scope": " ".join(SCOPES),
        "tokenType": tokens.get("token_type", "Bearer"),
        "expiresAt": datetime.utcnow().isoformat() + "Z",
    }

    with open(AUTH_FILE, "w") as f:
        json.dump(auth_data, f, indent=2)

    print()
    print("=" * 60)
    print("Autorizacion exitosa!")
    print(f"Scopes: {' '.join(SCOPES)}")
    print(f"Token guardado en: {AUTH_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
