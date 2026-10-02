#!/usr/bin/env python3
"""Pull/push the Custom Code block of a Kajabi landing page.

  python3 kajabi.py pull for-teams for-teams.html
  python3 kajabi.py push for-teams for-teams.html

Creds live in .kajabi/env (gitignored): KAJABI_TOKEN (authorization header),
KAJABI_CSRF (x-csrf-token header), KAJABI_COOKIE (cookie header). The
session expires in ~1 day - Kajabi's, not ours, nothing here can extend it.

To refresh: in the Kajabi admin, open devtools Network tab, click any
request to app.kajabi.com of type Fetch/XHR (not Document - a page
navigation won't have the headers we need), right-click it -> Copy ->
Copy as cURL, paste the whole thing into a file, then:

  python3 kajabi.py creds path/to/pasted_curl.txt

or pipe it directly: pbpaste | python3 kajabi.py creds
"""
import json, os, re, sys, urllib.request

# name -> theme_id, from the editor URL /admin/themes/<theme_id>/settings/edit
PAGES = {
    "for-teams": 2167439756,     # AI For Teams: train a team on RAG/agents
    "ai-dev": 2164183145,        # AI for Web Developers: the bootcamp
    "for-business": 2167439690,  # AI For Business: automation
    "how-it-works": 2167535129,  # How to become an AI engineer: VSL
    "agentic-engineering-101": 2167731896,  # standalone Saturday workshop, $495
}

BASE = "https://app.kajabi.com/admin/themes/{}/settings"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36"


def env():
    e = {}
    for line in open(os.path.join(os.path.dirname(__file__), ".kajabi", "env")):
        k, _, v = line.strip().partition("=")
        if k:
            e[k] = v.strip("'\"")
    return e


def call(method, url, body=None):
    e = env()
    req = urllib.request.Request(url, method=method, data=body and json.dumps(body).encode())
    for k, v in {
        "accept": "application/json", "content-type": "application/json",
        "authorization": e["KAJABI_TOKEN"], "x-csrf-token": e["KAJABI_CSRF"],
        "cookie": e["KAJABI_COOKIE"], "user-agent": UA, "origin": "https://app.kajabi.com",
    }.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as err:
        if err.code in (401, 403):
            sys.exit("Kajabi session expired (HTTP %d). Paste a fresh curl from a Fetch/XHR "
                     "request to app.kajabi.com and run: python3 kajabi.py creds <file>" % err.code)
        raise


def parse_curl(text):
    headers = {}
    for pat in (r"-H\s+'([^:]+):\s*([^']*)'", r'-H\s+"([^:]+):\s*([^"]*)"'):
        for m in re.finditer(pat, text):
            headers.setdefault(m.group(1).strip().lower(), m.group(2).strip())

    cookie = None
    for pat in (r"(?:-b|--cookie)\s+'([^']*)'", r'(?:-b|--cookie)\s+"([^"]*)"'):
        m = re.search(pat, text)
        if m:
            cookie = m.group(1)
            break
    if not cookie:
        cookie = headers.get("cookie")

    return headers.get("authorization"), headers.get("x-csrf-token"), cookie


def creds_cmd(path):
    text = open(path).read() if path else sys.stdin.read()
    token, csrf, cookie = parse_curl(text)

    env_path = os.path.join(os.path.dirname(__file__), ".kajabi", "env")
    os.makedirs(os.path.dirname(env_path), exist_ok=True)
    current = env() if os.path.exists(env_path) else {}

    found = {}
    if token:
        found["KAJABI_TOKEN"] = token
    if csrf:
        found["KAJABI_CSRF"] = csrf
    if cookie:
        found["KAJABI_COOKIE"] = cookie
    current.update(found)

    with open(env_path, "w") as f:
        for k in ("KAJABI_TOKEN", "KAJABI_CSRF", "KAJABI_COOKIE"):
            if k in current:
                f.write(f"{k}={current[k]}\n")

    if found:
        print(f"updated: {', '.join(found)}")
    missing = [k for k in ("KAJABI_TOKEN", "KAJABI_CSRF", "KAJABI_COOKIE") if k not in current]
    if missing:
        print(f"still missing: {', '.join(missing)}")
        print("paste a curl from a Fetch/XHR request to app.kajabi.com, not a page navigation "
              "(e.g. open the theme editor and copy the request that loads the page settings)")


def code_block(sections):
    for sid, sec in sections.items():
        for blk in sec.get("blocks", {}).values():
            if blk.get("type") == "code":
                return sid, sec, blk
    sys.exit("no Custom Code block found on this page")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "creds":
        return creds_cmd(sys.argv[2] if len(sys.argv) > 2 else None)

    cmd, page, path = sys.argv[1:4]
    theme_id = PAGES[page]
    resp = call("GET", BASE.format(theme_id))
    theme, file_id = resp["theme"]["data"]["attributes"], resp["file"]["data"]["id"]
    settings = theme["settings"]
    sid, sec, blk = code_block(settings["sections"])

    if cmd == "pull":
        open(path, "w").write(blk["settings"]["code"])
        print(f"pulled {len(blk['settings']['code'])} chars -> {path}")
    elif cmd == "push":
        blk["settings"]["code"] = open(path).read()
        call("PUT", BASE.format(theme_id), {
            "file_id": file_id,
            "theme_setting": {"sections": {sid: sec}, "content_for_index": settings["content_for_index"]},
            "based_on": theme["updatedAt"],
        })
        print(f"pushed {path} -> {page} ({theme['themeable']['title']})")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
