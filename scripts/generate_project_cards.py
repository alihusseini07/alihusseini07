import os
import textwrap

FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
FS = 13
CHAR_W = 7.82
LINE_H = 21

CYAN = "#22D3EE"
GREEN = "#4ADE80"
WHITE = "#E6F1FB"
DIM = "#5C7388"
BG = "#05080C"
CARD_BG = "#070D14"
BORDER = "#1B2733"

W = 960
COLS = 2
GAP = 10
CARD_W = (W - GAP * (COLS + 1)) // COLS
PAD_X = 18
PAD_Y = 16
TEXT_W = CARD_W - PAD_X * 2

LABEL_STACK = "stack:   "
LABEL_SUMMARY = "summary: "
STACK_CHARS = max(10, int((TEXT_W - len(LABEL_STACK) * CHAR_W) / CHAR_W))
SUMMARY_CHARS = max(10, int((TEXT_W - len(LABEL_SUMMARY) * CHAR_W) / CHAR_W))

projects = [
    {
        "name": "ChefIt/",
        "url": "https://github.com/MatthewKim07/chef-it",
        "stack": "SwiftUI · Node.js · Express · PostgreSQL · OpenAI Vision",
        "summary": "Social cooking platform with pantry scanning, recipe matching, social posting, reviews, and smart shopping flows.",
    },
    {
        "name": "Clarus/",
        "url": "https://github.com/athravseruwam07/clarus",
        "stack": "TypeScript · Next.js · React · Fastify · Prisma · Playwright",
        "summary": "Student dashboard that syncs D2L course data and uses an LLM-powered planning layer to rank deadlines and guide daily academic work.",
    },
    {
        "name": "WaterlooWorks+/",
        "url": "https://github.com/MatthewKim07/waterloo-works-plus",
        "stack": "JavaScript · Node.js · PDF.js · Chrome Extension APIs",
        "summary": "Co-op job discovery extension that parses resumes, scores fit, highlights gaps, and reorders postings by compatibility.",
    },
    {
        "name": "ATS360-Netdynamic/",
        "url": None,
        "stack": "SuiteScript · AWS Lambda · S3 · Transcribe · Bedrock",
        "summary": "Built AI video screening, scheduling workflows, and resume scoring QA for 30+ enterprise hiring teams in production.",
    },
]


def wrap(text, chars):
    return textwrap.wrap(text, width=chars) or [""]


def card_lines(p):
    return wrap(p["stack"], STACK_CHARS) + wrap(p["summary"], SUMMARY_CHARS)


def card_height(p):
    n = len(card_lines(p))
    # title + sep + content lines + padding
    return PAD_Y + LINE_H + 10 + 8 + n * LINE_H + PAD_Y


rows = [(projects[0], projects[1]), (projects[2], projects[3])]
row_heights = [max(card_height(a), card_height(b)) for a, b in rows]
total_h = GAP + sum(row_heights) + GAP * len(rows)

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {total_h}" width="{W}" height="{total_h}">')
out.append(f'  <rect width="{W}" height="{total_h}" rx="10" fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>')

y0 = GAP
for row_i, (pa, pb) in enumerate(rows):
    ch = row_heights[row_i]
    for col_i, p in enumerate([pa, pb]):
        cx = GAP + col_i * (CARD_W + GAP)
        cy = y0

        out.append(f'  <rect x="{cx}" y="{cy}" width="{CARD_W}" height="{ch}" rx="7" fill="{CARD_BG}" stroke="{BORDER}" stroke-width="1"/>')

        tx = cx + PAD_X
        ty = cy + PAD_Y + FS

        # Title
        out.append(f'  <text x="{tx}" y="{ty}" font-family="{FONT}" font-size="{FS}" font-weight="700" fill="{WHITE}">{p["name"]}<tspan fill="{DIM}"> README.md</tspan></text>')

        # Separator
        sep_y = ty + 10
        out.append(f'  <line x1="{tx}" y1="{sep_y}" x2="{cx + CARD_W - PAD_X}" y2="{sep_y}" stroke="{BORDER}" stroke-width="1"/>')

        # Stack
        cy_text = sep_y + 8 + FS
        stack_lines = wrap(p["stack"], STACK_CHARS)
        lx = tx + len(LABEL_STACK) * CHAR_W
        out.append(f'  <text x="{tx}" y="{cy_text}" font-family="{FONT}" font-size="{FS}" fill="{CYAN}">{LABEL_STACK.rstrip()}</text>')
        for i, line in enumerate(stack_lines):
            out.append(f'  <text x="{lx:.1f}" y="{cy_text + i * LINE_H}" font-family="{FONT}" font-size="{FS}" fill="{GREEN}">{line}</text>')

        # Summary
        cy_text2 = cy_text + len(stack_lines) * LINE_H
        summary_lines = wrap(p["summary"], SUMMARY_CHARS)
        lx2 = tx + len(LABEL_SUMMARY) * CHAR_W
        out.append(f'  <text x="{tx}" y="{cy_text2}" font-family="{FONT}" font-size="{FS}" fill="{CYAN}">{LABEL_SUMMARY.rstrip()}</text>')
        for i, line in enumerate(summary_lines):
            out.append(f'  <text x="{lx2:.1f}" y="{cy_text2 + i * LINE_H}" font-family="{FONT}" font-size="{FS}" fill="{GREEN}">{line}</text>')

    y0 += ch + GAP

out.append("</svg>")

os.makedirs("assets", exist_ok=True)
with open("assets/project-cards.svg", "w") as f:
    f.write("\n".join(out))

print("Generated assets/project-cards.svg")
