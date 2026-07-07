#!/usr/bin/env python3
"""
Post a message to a Google Chat space or DM.
Reuses the refresh token stored in opencode's mcp-auth.json (entry google-chat).

Usage:
  python3 post-to-chat.py --space="tmd-ac-ledger" --text="..."
  python3 post-to-chat.py --space-id="spaces/AAAA1234" --text="..."
  python3 post-to-chat.py --dm="someone@alegra.com" --text="..."
  python3 post-to-chat.py --text="..."                  # uses DAILY_CHAT_SPACE env var

Options:
  --space     Space display name to search for (first match)
  --space-id  Exact space resource name (spaces/XXX)
  --dm        Email of the user to send a direct message to
  --text      Message text (plain text, Chat markdown supported: **bold**, *italic*, lists)
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.parse

AUTH_FILE = os.path.expanduser("~/.local/share/opencode/mcp-auth.json")
TOKEN_URL = "https://oauth2.googleapis.com/token"
CHAT_SPACES_URL = "https://chat.googleapis.com/v1/spaces"
CHAT_CREATE_MSG_URL_TMPL = "https://chat.googleapis.com/v1/{space}/messages"
CHAT_FIND_DM_URL = "https://chat.googleapis.com/v1/spaces:findDirectMessage"

MAX_MSG_BYTES = 32000


def refresh_access_token(refresh_token, client_id, client_secret):
    data = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return json.loads(urllib.request.urlopen(req).read())["access_token"]


def list_spaces(access_token):
    req = urllib.request.Request(
        f"{CHAT_SPACES_URL}?pageSize=100",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return json.loads(urllib.request.urlopen(req).read()).get("spaces", [])


def find_dm(access_token, email):
    params = urllib.parse.urlencode({"name": email})
    req = urllib.request.Request(
        f"{CHAT_FIND_DM_URL}?{params}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    return json.loads(urllib.request.urlopen(req).read()).get("name")


def resolve_space(access_token, args):
    if args.space_id:
        return args.space_id
    if args.space:
        spaces = list_spaces(access_token)
        for s in spaces:
            display = s.get("displayName", "")
            if display.lower() == args.space.lower():
                return s.get("name")
        print(json.dumps({
            "error": f"Space '{args.space}' not found",
            "available_spaces": [s.get("displayName", s.get("name")) for s in spaces],
        }, indent=2, ensure_ascii=False))
        sys.exit(1)
    if args.dm:
        try:
            return find_dm(access_token, args.dm)
        except urllib.error.HTTPError as e:
            print(json.dumps({"error": f"Could not find DM with {args.dm}: {e.read().decode()}"}, indent=2))
            sys.exit(1)
    default_space = os.environ.get("DAILY_CHAT_SPACE")
    if default_space:
        spaces = list_spaces(access_token)
        for s in spaces:
            display = s.get("displayName", "")
            if display.lower() == default_space.lower():
                return s.get("name")
        print(json.dumps({"error": f"Default space '{default_space}' from DAILY_CHAT_SPACE not found"}, indent=2))
        sys.exit(1)
    print(json.dumps({"error": "No space specified. Use --space, --space-id, --dm, or set DAILY_CHAT_SPACE env var."}, indent=2))
    sys.exit(1)


def send_message(access_token, space_name, text):
    if len(text.encode("utf-8")) > MAX_MSG_BYTES:
        print(json.dumps({"error": f"Message exceeds {MAX_MSG_BYTES} bytes limit"}))
        sys.exit(1)
    body = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(
        CHAT_CREATE_MSG_URL_TMPL.format(space=space_name),
        data=body,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    return json.loads(urllib.request.urlopen(req).read())


def main():
    parser = argparse.ArgumentParser(description="Post a message to Google Chat")
    parser.add_argument("--space", help="Space display name")
    parser.add_argument("--space-id", help="Space resource name (spaces/XXX)")
    parser.add_argument("--dm", help="Email for direct message")
    parser.add_argument("--text", required=True, help="Message text")
    args = parser.parse_args()

    client_id = os.environ.get("GOOGLE_MCP_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_MCP_CLIENT_SECRET")
    if not client_id or not client_secret:
        print(json.dumps({"error": "GOOGLE_MCP_CLIENT_ID or GOOGLE_MCP_CLIENT_SECRET not set"}), file=sys.stderr)
        sys.exit(1)

    with open(AUTH_FILE, "r") as f:
        auth_data = json.load(f)

    chat_entry = auth_data.get("google-chat", {})
    refresh_token = chat_entry.get("tokens", {}).get("refreshToken")
    if not refresh_token:
        print(json.dumps({"error": "No refresh token for google-chat in mcp-auth.json"}))
        sys.exit(1)

    try:
        access_token = refresh_access_token(refresh_token, client_id, client_secret)
    except Exception as e:
        print(json.dumps({"error": f"Token refresh failed: {e}"}))
        sys.exit(1)

    space_name = resolve_space(access_token, args)

    try:
        result = send_message(access_token, space_name, args.text)
        print(json.dumps({
            "success": True,
            "space": space_name,
            "messageId": result.get("name", ""),
            "createTime": result.get("createTime", ""),
        }, indent=2, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(json.dumps({
            "error": f"Failed to send message: HTTP {e.code}",
            "details": body[:500],
        }, indent=2, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
