import os
import requests
from datetime import date, timedelta

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = "alihusseini07"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

query = """
query($username: String!) {
  user(login: $username) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"username": USERNAME}},
    headers=HEADERS,
)
response.raise_for_status()

weeks = response.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

all_days = []
for week in weeks:
    all_days.extend(week["contributionDays"])
all_days.sort(key=lambda d: d["date"])

today = date.today().isoformat()
if all_days and all_days[-1]["date"] < today:
    known = {d["date"] for d in all_days}
    cursor = date.fromisoformat(all_days[-1]["date"]) + timedelta(days=1)
    end = date.today()
    while cursor <= end:
        s = cursor.isoformat()
        if s not in known:
            all_days.append({"date": s, "contributionCount": 0})
        cursor += timedelta(days=1)

# Events API is real-time; override today's count in case GraphQL hasn't caught up yet
today_commits = 0
page = 1
while True:
    ev_resp = requests.get(
        f"https://api.github.com/users/{USERNAME}/events",
        headers=HEADERS,
        params={"per_page": 100, "page": page},
    )
    ev_resp.raise_for_status()
    events = ev_resp.json()
    if not events:
        break
    for e in events:
        if e.get("type") == "PushEvent" and e.get("created_at", "")[:10] == today:
            today_commits += len(e["payload"].get("commits", []))
    # Events are newest-first; stop once we're past today
    if events[-1].get("created_at", "")[:10] < today:
        break
    page += 1

if today_commits > 0:
    for d in all_days:
        if d["date"] == today:
            d["contributionCount"] = max(d["contributionCount"], today_commits)
            break

last_30 = all_days[-30:]

counts = [d["contributionCount"] for d in last_30]
dates = [d["date"] for d in last_30]
max_count = max(counts) if max(counts) > 0 else 1

W, H = 960, 280
pad_l, pad_r, pad_t, pad_b = 52, 24, 44, 48
plot_w = W - pad_l - pad_r
plot_h = H - pad_t - pad_b
n = len(last_30)
DOT_R = 3.5


def xp(i):
    return pad_l + (i / (n - 1)) * plot_w


def yp(v):
    # Inset by DOT_R so dots at extremes sit inside bounds, not straddling axes
    return pad_t + DOT_R + (plot_h - 2 * DOT_R) * (1 - v / max_count)


points = [(xp(i), yp(counts[i])) for i in range(n)]

def monotone_path(pts):
    n = len(pts)
    dx = [pts[i+1][0] - pts[i][0] for i in range(n-1)]
    dy = [pts[i+1][1] - pts[i][1] for i in range(n-1)]
    slopes = [dy[i] / dx[i] if dx[i] != 0 else 0 for i in range(n-1)]

    tangents = [0.0] * n
    tangents[0] = slopes[0]
    tangents[-1] = slopes[-1]
    for i in range(1, n-1):
        tangents[i] = (slopes[i-1] + slopes[i]) / 2

    for i in range(n-1):
        if slopes[i] == 0:
            tangents[i] = tangents[i+1] = 0
        else:
            a = tangents[i] / slopes[i]
            b = tangents[i+1] / slopes[i]
            h = (a**2 + b**2) ** 0.5
            if h > 3:
                tangents[i] = 3 * a / h * slopes[i]
                tangents[i+1] = 3 * b / h * slopes[i]

    d = [f"M {pts[0][0]:.2f},{pts[0][1]:.2f}"]
    for i in range(n-1):
        x1, y1 = pts[i]
        x2, y2 = pts[i+1]
        s = dx[i]
        d.append(f"C {x1 + s/3:.2f},{y1 + tangents[i]*s/3:.2f} {x2 - s/3:.2f},{y2 - tangents[i+1]*s/3:.2f} {x2:.2f},{y2:.2f}")
    return " ".join(d)

path_d = monotone_path(points)
path_len = int(sum(
    ((points[i + 1][0] - points[i][0]) ** 2 + (points[i + 1][1] - points[i][1]) ** 2) ** 0.5
    for i in range(len(points) - 1)
) * 1.15) + 10

tick_count = 5
y_ticks = [(round((i / tick_count) * max_count), yp(round((i / tick_count) * max_count))) for i in range(tick_count + 1)]
x_labels = [(i, dates[i][8:10].lstrip("0") or "0") for i in range(n)]

lines = []
lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
lines.append("""  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#06080C"/>
      <stop offset="1" stop-color="#0A1118"/>
    </linearGradient>
    <linearGradient id="lg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#22D3EE"/>
      <stop offset="1" stop-color="#4ADE80"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>""")

lines.append(f'  <rect width="{W}" height="{H}" rx="12" fill="url(#bg)"/>')
lines.append(f'  <rect width="{W}" height="{H}" rx="12" fill="none" stroke="#1B2733" stroke-width="1.5"/>')

for _, y in y_ticks[1:]:
    lines.append(f'  <line x1="{pad_l}" y1="{y:.2f}" x2="{W - pad_r}" y2="{y:.2f}" stroke="#1B2733" stroke-width="1"/>')

lines.append(f'  <text x="{W // 2}" y="24" text-anchor="middle" fill="#7E94A8" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="12">Recent Contributions</text>')

for val, y in y_ticks:
    lines.append(f'  <text x="{pad_l - 8}" y="{y + 4:.2f}" text-anchor="end" fill="#5C7388" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="11">{val}</text>')

for i, label in x_labels:
    lines.append(f'  <text x="{xp(i):.2f}" y="{H - pad_b + 16}" text-anchor="middle" fill="#5C7388" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="10">{label}</text>')

lines.append(f'  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{pad_t + plot_h}" stroke="#2A3B4C" stroke-width="1"/>')
lines.append(f'  <line x1="{pad_l}" y1="{pad_t + plot_h}" x2="{W - pad_r}" y2="{pad_t + plot_h}" stroke="#2A3B4C" stroke-width="1"/>')

lines.append(f'''  <path d="{path_d}" fill="none" stroke="url(#lg)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)" stroke-dasharray="{path_len}" stroke-dashoffset="{path_len}">
    <animate attributeName="stroke-dashoffset" from="{path_len}" to="0" dur="1.8s" calcMode="spline" keyTimes="0;1" keySplines="0.4 0 0.2 1" fill="freeze" begin="0.2s"/>
  </path>''')

for i, (px, py) in enumerate(points):
    delay = round(0.2 + (i / (n - 1)) * 1.8, 3)
    dot_color = "#22D3EE" if counts[i] == 0 else "#4ADE80"
    lines.append(f'  <circle cx="{px:.2f}" cy="{py:.2f}" r="{DOT_R}" fill="{dot_color}" filter="url(#glow)" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.25s" fill="freeze" begin="{delay}s"/></circle>')

lines.append("</svg>")

os.makedirs("assets", exist_ok=True)
with open("assets/contributions-v2.svg", "w") as f:
    f.write("\n".join(lines))

print(f"Generated assets/contributions-v2.svg ({n} days, max={max_count})")
