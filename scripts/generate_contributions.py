import os
import requests

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = "alihusseini07"

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
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
)
response.raise_for_status()

weeks = response.json()["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

all_days = []
for week in weeks:
    all_days.extend(week["contributionDays"])
all_days.sort(key=lambda d: d["date"])
last_30 = all_days[-30:]

counts = [d["contributionCount"] for d in last_30]
dates = [d["date"] for d in last_30]
max_count = max(counts) if max(counts) > 0 else 1

W, H = 960, 280
pad_l, pad_r, pad_t, pad_b = 52, 24, 44, 48
plot_w = W - pad_l - pad_r
plot_h = H - pad_t - pad_b
n = len(last_30)


def xp(i):
    return pad_l + (i / (n - 1)) * plot_w


def yp(v):
    return pad_t + plot_h - (v / max_count) * plot_h


points = [(xp(i), yp(counts[i])) for i in range(n)]
path_d = "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in points)
path_len = int(sum(
    ((points[i + 1][0] - points[i][0]) ** 2 + (points[i + 1][1] - points[i][1]) ** 2) ** 0.5
    for i in range(len(points) - 1)
)) + 10

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
    lines.append(f'  <circle cx="{px:.2f}" cy="{py:.2f}" r="3.5" fill="{dot_color}" filter="url(#glow)" opacity="0"><animate attributeName="opacity" from="0" to="1" dur="0.25s" fill="freeze" begin="{delay}s"/></circle>')

lines.append("</svg>")

os.makedirs("assets", exist_ok=True)
with open("assets/contributions-graph.svg", "w") as f:
    f.write("\n".join(lines))

print(f"Generated assets/contributions-graph.svg ({n} days, max={max_count})")
