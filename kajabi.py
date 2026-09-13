#!/usr/bin/env python3
"""Pull/push the Custom Code block of a Kajabi landing page.

  python3 kajabi.py pull for-teams for-teams.html
  python3 kajabi.py push for-teams for-teams.html

Creds live in .kajabi/env (gitignored). Grab them from the browser devtools
on a request to app.kajabi.com: KAJABI_TOKEN (authorization header),
KAJABI_CSRF (x-csrf-token header), KAJABI_COOKIE (cookie header). The token
expires in ~1 day; refresh when you get a 401.
"""
import json, os, sys, urllib.request

# name -> theme_id, from the editor URL /admin/themes/<theme_id>/settings/edit
PAGES = {
    "for-teams": 2167439756,     # AI For Teams: train a team on RAG/agents
    "ai-dev": 2164183145,        # AI for Web Developers: the bootcamp
    "for-business": 2167439690,  # AI For Business: automation
    "how-it-works": 2167535129,  # How to become an AI engineer: VSL
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
    with urllib.request.urlopen(req) as r:
        return json.load(r)


def code_block(sections):
    for sid, sec in sections.items():
        for blk in sec.get("blocks", {}).values():
            if blk.get("type") == "code":
                return sid, sec, blk
    sys.exit("no Custom Code block found on this page")


def main():
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
