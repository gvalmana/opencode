#!/usr/bin/env python3
"""
Google OAuth authentication helper for daily-focus and daily-dev-summary skills.
Validates tokens and provides clear error messages when authentication is missing.

Usage:
  from google_auth import validate_google_auth, get_google_token
  
  # Validate all required scopes
  validate_google_auth(services=["calendar.events", "chat.messages.readonly"])
  
  # Get a valid access token
  token = get_google_token("google-calendar")
"""
import json
import os
import sys
import urllib.request
import urllib.parse

AUTH_FILE = os.path.expanduser("~/.local/share/opencode/mcp-auth.json")
CONFIG_FILE = os.path.expanduser("~/.config/opencode/opencode.json")
TOKEN_URL = "https://oauth2.googleapis.com/token"
TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

# Required scopes for each service (as configured in opencode.json)
REQUIRED_SCOPES = {
    "google-calendar": [
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/calendar.events.readonly",
        "https://www.googleapis.com/auth/calendar.calendarlist.readonly",
    ],
    "google-chat": [
        "https://www.googleapis.com/auth/chat.spaces.readonly",
        "https://www.googleapis.com/auth/chat.messages.readonly",
        "https://www.googleapis.com/auth/chat.messages.create",
    ],
}


def check_config_file():
    """Check if opencode.json config file exists and has Google MCP configs."""
    if not os.path.exists(CONFIG_FILE):
        return False, f"Config file not found: {CONFIG_FILE}"
    
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        
        mcp_config = config.get("mcp", {})
        has_calendar = "google-calendar" in mcp_config
        has_chat = "google-chat" in mcp_config
        
        if not has_calendar and not has_chat:
            return False, "No Google MCP configurations found in opencode.json"
        
        return True, config
    except json.JSONDecodeError:
        return False, f"Invalid JSON in config file: {CONFIG_FILE}"


def check_env_vars():
    """Check if required environment variables are set."""
    client_id = os.environ.get("GOOGLE_MCP_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_MCP_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        return False, "GOOGLE_MCP_CLIENT_ID or GOOGLE_MCP_CLIENT_SECRET not set in environment"
    
    return True, (client_id, client_secret)


def check_mcp_tokens(service):
    """Check if MCP token exists for a service in mcp-auth.json."""
    if not os.path.exists(AUTH_FILE):
        return False, f"Auth file not found: {AUTH_FILE}"
    
    try:
        with open(AUTH_FILE, "r") as f:
            auth_data = json.load(f)
        
        if service not in auth_data:
            return False, f"NO_TOKENS"
        
        tokens = auth_data[service].get("tokens", {})
        refresh_token = tokens.get("refreshToken")
        
        if not refresh_token:
            return False, f"NO_TOKENS"
        
        return True, refresh_token
    except json.JSONDecodeError:
        return False, f"Invalid JSON in auth file: {AUTH_FILE}"


def refresh_access_token(refresh_token, client_id, client_secret):
    """Refresh the access token using the refresh token."""
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
    
    try:
        response = json.loads(urllib.request.urlopen(req).read())
        return response.get("access_token")
    except Exception as e:
        return None


def validate_token_scopes(access_token, required_scopes):
    """Validate that the access token has the required scopes."""
    try:
        req = urllib.request.Request(
            f"{TOKENINFO_URL}?access_token={access_token}",
        )
        response = json.loads(urllib.request.urlopen(req).read())
        granted_scopes = response.get("scope", "").split()
        
        missing_scopes = [s for s in required_scopes if s not in granted_scopes]
        if missing_scopes:
            return False, f"Missing scopes: {', '.join(missing_scopes)}"
        
        return True, "OK"
    except Exception as e:
        return False, f"Failed to validate token: {e}"


def validate_google_auth(services=None, required_scopes=None):
    """
    Validate Google authentication for specified services.
    
    Args:
        services: List of service names (e.g., ["google-calendar", "google-chat"])
        required_scopes: List of specific scopes to validate (optional)
    
    Returns:
        Tuple of (is_valid, message)
    """
    if services is None:
        services = ["google-calendar", "google-chat"]
    
    # Check config file
    config_ok, config_data = check_config_file()
    if not config_ok:
        return False, config_data
    
    # Check env vars
    env_ok, env_result = check_env_vars()
    if not env_ok:
        return False, env_result
    client_id, client_secret = env_result
    
    # Check tokens for each service
    for service in services:
        token_ok, token_result = check_mcp_tokens(service)
        if not token_ok:
            if token_result == "NO_TOKENS":
                return False, f"NO_TOKENS:{service}"
            return False, token_result
        
        # Try to refresh the token
        access_token = refresh_access_token(token_result, client_id, client_secret)
        if not access_token:
            return False, f"Failed to refresh token for {service}. Please re-authorize."
        
        # Validate scopes if required
        if required_scopes:
            scope_ok, scope_msg = validate_token_scopes(access_token, required_scopes)
            if not scope_ok:
                return False, f"{service}: {scope_msg}"
    
    return True, "Authentication OK"


def get_google_token(service):
    """
    Get a valid access token for a Google service.
    
    Args:
        service: Service name (e.g., "google-calendar")
    
    Returns:
        Access token string or None if failed
    """
    # Check config file
    config_ok, config_data = check_config_file()
    if not config_ok:
        print(json.dumps({"error": config_data}), file=sys.stderr)
        return None
    
    # Check env vars
    env_ok, env_result = check_env_vars()
    if not env_ok:
        print(json.dumps({"error": env_result}), file=sys.stderr)
        return None
    client_id, client_secret = env_result
    
    # Check tokens
    token_ok, token_result = check_mcp_tokens(service)
    if not token_ok:
        if token_result == "NO_TOKENS":
            print(json.dumps({
                "error": f"No tokens found for {service}",
                "action": "run_reauth",
                "service": service,
                "command": f"python3 skills/{'daily-focus' if service == 'google-calendar' else 'daily-dev-summary'}/reauth-{'calendar' if service == 'google-calendar' else 'chat'}.py"
            }), file=sys.stderr)
        else:
            print(json.dumps({"error": token_result}), file=sys.stderr)
        return None
    
    # Refresh token
    access_token = refresh_access_token(token_result, client_id, client_secret)
    if not access_token:
        print(json.dumps({"error": f"Failed to refresh token for {service}. Please re-authorize."}), file=sys.stderr)
        return None
    
    return access_token


def print_auth_status():
    """Print authentication status for all services."""
    config_ok, config_data = check_config_file()
    env_ok, env_result = check_env_vars()
    
    print("=" * 60)
    print("GOOGLE AUTHENTICATION STATUS")
    print("=" * 60)
    print()
    
    print(f"Config file: {'✓' if config_ok else '✗'} ({CONFIG_FILE})")
    print(f"Env vars: {'✓' if env_ok else '✗'}")
    print()
    
    if config_ok:
        for service in ["google-calendar", "google-chat"]:
            token_ok, token_result = check_mcp_tokens(service)
            if token_ok:
                print(f"{service}: ✓ Token found")
            else:
                print(f"{service}: ✗ {token_result}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    print_auth_status()
