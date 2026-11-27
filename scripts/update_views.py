import json, re, subprocess, datetime, time
html = open('index.html', encoding='utf-8').read()
works = re.findall(r'<section id="work".*?</section>', html, re.S)
ids = []
for w in works:
    for m in re.findall(r'youtu\.be/([\w-]{11})', w):
        if m not in ids:
            ids.append(m)
m = re.search(r'var PIN=\[(.*?)\];', html, re.S)
if m:
    for x in re.findall(r'id:"([\w-]{11})"', m.group(1)):
        if x not in ids:
            ids.append(x)
OWN = "UCoPRcf3z3_1qdQBdwgq9t1A"
try:
    stats = json.load(open('stats.json', encoding='utf-8'))
except Exception:
    stats = {"channel_views_base": 5346624, "videos": {}}
vids = stats.get("videos", {})

def fetch(vid):
    out = subprocess.run(["yt-dlp", "--skip-download", "--no-warnings",
                          "--print", "%(view_count)s|%(channel_id)s",
                          "https://youtu.be/" + vid],
                         capture_output=True, text=True, timeout=120)
    lines = out.stdout.strip().splitlines()
    if not lines:
        return "", ""
    parts = lines[0].split("|")
    return parts[0], (parts[1] if len(parts) > 1 else "")

for vid in ids:
    try:
        views_s, ch = fetch(vid)
        if not views_s and not ch:
            time.sleep(20)
            views_s, ch = fetch(vid)
        if ch == OWN:
            vids.pop(vid, None)
            continue
        if not views_s:
            print("SCRAPE-FAILED", vid)
            continue
        vids[vid] = int(views_s)
    except Exception as e:
        print("SCRAPE-FAILED", vid, type(e).__name__)
for vid in list(vids):
    if vid not in ids:
        del vids[vid]
stats["videos"] = vids
stats["external_total"] = sum(vids.values())
stats["updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
json.dump(stats, open('stats.json', 'w', encoding='utf-8'), indent=1)
print("total", stats["external_total"], "videos", len(vids), "ids", len(ids))
