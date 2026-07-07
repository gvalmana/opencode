#!/usr/bin/env python3
"""
Fetch Google Calendar and Chat data for the daily-focus skill.
Reads refresh tokens from opencode's mcp-auth.json, refreshes them via Google OAuth,
and calls the regular Google Calendar and Chat APIs directly.
Outputs JSON to stdout.

Usage:
  python3 fetch-focus-data.py                # today (default)
  python3 fetch-focus-data.py --date=2026-07-07
  python3 fetch-focus-data.py --yesterday
"""
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

# Add parent directory to path for google_auth module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from google_auth import validate_google_auth, get_google_token

AUTH_FILE = os.path.expanduser("~/.local/share/opencode/mcp-auth.json")
TOKEN_URL = "https://oauth2.googleapis.com/token"
CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
CHAT_SPACES_URL = "https://chat.googleapis.com/v1/spaces"
CHAT_MESSAGES_URL_TMPL = "https://chat.googleapis.com/v1/{space}/messages"

FOCUS_PATTERNS = ["focus", "deep work", "no meetings", "do not disturb", "blocked", "heads down"]


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


def parse_date_arg(arg):
    local_tz = datetime.now().astimezone().tzinfo
    today_start = datetime.now(local_tz).replace(hour=0, minute=0, second=0, microsecond=0)

    if not arg or arg.lower() == "today":
        start = today_start
        end = start.replace(hour=23, minute=59, second=59)
        return start, end, start.strftime("%Y-%m-%d")

    if arg.lower() == "yesterday":
        start = today_start - timedelta(days=1)
        end = start.replace(hour=23, minute=59, second=59)
        return start, end, start.strftime("%Y-%m-%d")

    try:
        start = datetime.fromisoformat(arg).replace(
            hour=0, minute=0, second=0, microsecond=0, tzinfo=local_tz
        )
        end = start.replace(hour=23, minute=59, second=59)
        return start, end, start.strftime("%Y-%m-%d")
    except ValueError:
        print(
            json.dumps({"error": f"Invalid date argument: '{arg}'. Expected YYYY-MM-DD"}),
            file=sys.stderr,
        )
        sys.exit(1)


def get_time_range(arg=None):
    start_dt, end_dt, label = parse_date_arg(arg)
    local_tz = start_dt.tzinfo
    return (
        start_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        end_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        str(local_tz),
        label,
    )


def fetch_calendar(access_token, time_min, time_max, tz_name):
    result = {"events": [], "total_busy_minutes": 0, "error": None}
    try:
        params = urllib.parse.urlencode({
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": tz_name,
            "singleEvents": "true",
            "orderBy": "startTime",
            "maxResults": 50,
        })
        req = urllib.request.Request(
            f"{CALENDAR_EVENTS_URL}?{params}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        data = json.loads(urllib.request.urlopen(req).read())

        for ev in data.get("items", []):
            if "date" in ev.get("start", {}):
                continue
            etype = ev.get("eventType", "default")
            if etype in ("focusTime", "outOfOffice"):
                continue
            summary_lower = ev.get("summary", "").lower()
            if any(p in summary_lower for p in FOCUS_PATTERNS):
                continue
            attendees = ev.get("attendees", [])
            hangout = ev.get("hangoutLink")
            if hangout:
                mtype = "meet"
            elif any(a.get("self") for a in attendees):
                mtype = "in-person"
            else:
                mtype = "call"
            start = ev.get("start", {}).get("dateTime", "")
            end = ev.get("end", {}).get("dateTime", "")
            dur = None
            if start and end:
                try:
                    s = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    e = datetime.fromisoformat(end.replace("Z", "+00:00"))
                    dur = int((e - s).total_seconds() / 60)
                    result["total_busy_minutes"] += dur
                except (ValueError, TypeError):
                    pass
            result["events"].append({
                "summary": ev.get("summary", "(sin titulo)"),
                "start": start,
                "end": end,
                "duration_minutes": dur,
                "attendees": [a.get("email", "") for a in attendees if a.get("email")],
                "type": mtype,
                "hangoutLink": hangout,
            })
    except Exception as e:
        result["error"] = str(e)
    return result


def get_user_identity(access_token, auth_data):
    stored_id = auth_data.get("google-chat", {}).get("userId")
    if stored_id:
        return stored_id
    try:
        req = urllib.request.Request(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        info = json.loads(urllib.request.urlopen(req).read())
        return info.get("id")
    except Exception:
        return None


def fetch_chat_mentions_and_threads(access_token, time_min, time_max, auth_data):
    """Fetch messages that mention the user OR are in threads the user is active in."""
    result = {"mentions": [], "active_threads": [], "error": None}
    try:
        user_id = get_user_identity(access_token, auth_data)
        if not user_id:
            result["error"] = "Could not determine user ID"
            return result

        user_resource = f"users/{user_id}"

        req = urllib.request.Request(
            f"{CHAT_SPACES_URL}?pageSize=100",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        data = json.loads(urllib.request.urlopen(req).read())
        spaces = data.get("spaces", [])

        seen_threads = set()

        for space in spaces:
            space_name = space.get("name", "")
            space_display = space.get("displayName", space_name)
            filter_param = f'createTime > "{time_min}" AND createTime < "{time_max}"'
            params = urllib.parse.urlencode({"pageSize": 50, "filter": filter_param})
            try:
                req2 = urllib.request.Request(
                    f"{CHAT_MESSAGES_URL_TMPL.format(space=space_name)}?{params}",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                msg_data = json.loads(urllib.request.urlopen(req2).read())
                for msg in msg_data.get("messages", []):
                    msg_text = msg.get("text", "")
                    msg_name = msg.get("name", "")
                    thread_name = msg.get("thread", {}).get("name", "")
                    sender = msg.get("sender", {})
                    sender_name = sender.get("name", "")

                    # Check if message mentions the user
                    mentioned = False
                    if user_resource in msg_text:
                        mentioned = True
                    for ann in msg.get("annotations", []):
                        if ann.get("userMention", {}).get("user", {}).get("name") == user_resource:
                            mentioned = True
                            break

                    if mentioned:
                        result["mentions"].append({
                            "space": space_display,
                            "text": msg_text[:200],
                            "time": msg.get("createTime", ""),
                            "from": sender.get("displayName", sender_name),
                            "thread": thread_name,
                        })

                    # Track active threads (where user participates)
                    if thread_name and thread_name not in seen_threads:
                        if sender_name == user_resource:
                            seen_threads.add(thread_name)
                            if not mentioned:
                                result["active_threads"].append({
                                    "space": space_display,
                                    "text": msg_text[:200],
                                    "time": msg.get("createTime", ""),
                                    "from": sender.get("displayName", sender_name),
                                    "thread": thread_name,
                                })

            except urllib.error.HTTPError:
                continue
    except Exception as e:
        result["error"] = str(e)
    return result


def main():
    date_arg = None
    for arg in sys.argv[1:]:
        if arg.startswith("--date="):
            date_arg = arg.split("=", 1)[1]
        elif arg == "--yesterday":
            date_arg = "yesterday"

    # Validate Google authentication
    auth_ok, auth_msg = validate_google_auth(services=["google-calendar", "google-chat"])
    if not auth_ok:
        print(json.dumps({"error": f"Google authentication failed: {auth_msg}"}), file=sys.stderr)
        print("Please run: python3 skills/google_auth.py to check authentication status", file=sys.stderr)
        sys.exit(1)

    client_id = os.environ.get("GOOGLE_MCP_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_MCP_CLIENT_SECRET")
    if not client_id or not client_secret:
        print(json.dumps({"error": "GOOGLE_MCP_CLIENT_ID or GOOGLE_MCP_CLIENT_SECRET not set"}), file=sys.stderr)
        sys.exit(1)

    with open(AUTH_FILE, "r") as f:
        auth_data = json.load(f)

    cal_refresh = auth_data.get("google-calendar", {}).get("tokens", {}).get("refreshToken")
    chat_refresh = auth_data.get("google-chat", {}).get("tokens", {}).get("refreshToken")

    time_min, time_max, tz_name, date_str = get_time_range(date_arg)

    output = {
        "date": date_str,
        "calendar": {"events": [], "total_busy_minutes": 0, "error": None},
        "chat": {"mentions": [], "active_threads": [], "error": None},
    }

    # Calendar
    if cal_refresh:
        try:
            cal_token = refresh_access_token(cal_refresh, client_id, client_secret)
            output["calendar"] = fetch_calendar(cal_token, time_min, time_max, tz_name)
        except Exception as e:
            output["calendar"]["error"] = f"Token refresh failed: {e}"
    else:
        output["calendar"]["error"] = "No refresh token for google-calendar"

    # Chat (mentions + active threads)
    if chat_refresh:
        try:
            chat_token = refresh_access_token(chat_refresh, client_id, client_secret)
            output["chat"] = fetch_chat_mentions_and_threads(chat_token, time_min, time_max, auth_data)
        except Exception as e:
            output["chat"]["error"] = f"Token refresh failed: {e}"
    else:
        output["chat"]["error"] = "No refresh token for google-chat"

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
