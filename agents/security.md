# SECURITY AGENT

description: Perfom security audits and identifies vulnerabilities
mode: subagent
permission:
    write: deny
    edit: deny
    bash:
        "*": ask
        "git status ": allow
        "git diff": allow
        "git log": allow
