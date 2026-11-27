import json, re, subprocess, datetime
html = open('index.html', encoding='utf-8').read()
works = re.findall(r'<section id="work".*?</section>', html, re.S)
ids = []
for w in works:
    for m in re.findall(r'youtu\.be/([\w-]{11})', w):
        if m not in ids:
            ids.append(m)
OWN = "UCoPRcf3z3_1qdQBdwgq9t1A"
try:
    stats = json.load(open('stats.json', encoding='utf-8'))
except Exception:
    stats = {"channel_views_base": 5346624, "videos": {}}
vids = stats.get("videos", {})
for vid in ids:
    try:
        out = subprocess.run(["yt-dlp", "--skip-download", "--no-warnings",
                              "--print", "%(view_count)s|%(channel_id)s",
                              "https://youtu.be/" + vid],
                             capture_output=True, text=True, timeout=120)
        lines = out.stdout.strip().splitlines()
        if not lines:
            continue
        parts = lines[0].split("|")
        views_s, ch = parts[0], (parts[1] if len(parts) > 1 else "")
        if ch == OWN:
            vids.pop(vid, None)
            continue
        vids[vid] = int(views_s)
    except Exception:
        pass
for vid in list(vids):
    if vid not in ids:
        del vids[vid]
stats["videos"] = vids
stats["external_total"] = sum(vids.values())
stats["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(stats, open('stats.json', 'w', encoding='utf-8'), indent=1)
print("total", stats["external_total"], "videos", len(vids))
