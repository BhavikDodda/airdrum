import pygame
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
import requests

pygame.init()

ROWS = ["HH", "SN", "FT", "CR"]

COLOR = {
    "HH": (50, 230, 70),
    "SN": (70, 190, 255),
    "FT": (255, 180, 40),
    "CR": (255, 80, 220)
}

# --------------- DEFAULTS ----------------
BPM = 60
STEP_TIME = 60 / BPM / 4
target_step_time = STEP_TIME

PATTERN = {r: [0] * 16 for r in ROWS}

current_step = 0
current_hit = "HH"
running = True
# ----------------------------------------

W, H = 1280, 800
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Airdrum Tutor")

font_big = pygame.font.SysFont("Arial", 120, True)
font_med = pygame.font.SysFont("Arial", 42, True)
font_small = pygame.font.SysFont("Arial", 24)
clock = pygame.time.Clock()


def glow_circle(x, y, r, color):
    for i in range(30):
        a = max(0, 80 - i * 3)
        rr = r + i * 4
        s = pygame.Surface((rr * 2, rr * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*color, a), (rr, rr), rr)
        screen.blit(s, (x - rr, y - rr))


def next_note(offset):
    step = (current_step + offset + 1) % 16
    for r in ROWS:
        if PATTERN[r][step] == 1:
            return r
    return "HH"


# --------- PATTERN PARSER (from LLM text) ----------
def parse_lane_from_text(text):
    """
    Expected model output format like:
    HH - - HH - - HH -
    SN - SN - - SN - -
    KD KD - - KD - - -
    CR - - - - - - -
    """

    lane = ["-"] * 16

    lines = text.strip().split("\n")

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 2:
            continue

        name = parts[0].upper()

        if name in ["KICK", "KD"]:
            name = "FT"

        if name not in ROWS:
            continue

        steps = parts[1:17]

        for i, s in enumerate(steps):
            if s != "-" and i < 16:
                lane[i] = name

    return lane


# --------------- HTTP SERVER ----------------
class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global PATTERN, BPM, target_step_time

        length = int(self.headers.get("Content-Length"))
        data = json.loads(self.rfile.read(length))

        # ---------- 1️⃣ DIRECT CONFIG (like before) ----------
        if "lane" in data or "bpm" in data:
            if "bpm" in data:
                BPM = int(data["bpm"])
                target_step_time = 60 / BPM / 4

            if "lane" in data:
                lane = data["lane"]

                def track(name):
                    return [1 if x == name else 0 for x in lane]

                PATTERN["HH"] = track("HH")
                PATTERN["SN"] = track("SN")
                PATTERN["FT"] = track("KD") or track("FT")
                PATTERN["CR"] = track("CR")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"UPDATED")
            return

        # ---------- 2️⃣ GENERATE USING OLLAMA ----------
        if "song_or_style" in data:

            song = data["song_or_style"]
            BPM = int(data.get("bpm", BPM))
            target_step_time = 60 / BPM / 4

            prompt = f"""
Create a simple 16-step drum pattern for {song}.
Return ONLY 4 lines in this exact format:

HH x - - x - - x - x - - x - - x
SN - - x - - - x - - - x - - - x -
KD x - - - x - - - x - - - x - - -
CR - - - - - - - - - - - - - - - -

Use HH SN KD CR only. Use - where silent.
"""

            res = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "llama3", "prompt": prompt}
            )

            text = res.json()["response"]

            lane = parse_lane_from_text(text)

            def track(name):
                return [1 if x == name else 0 for x in lane]

            PATTERN["HH"] = track("HH")
            PATTERN["SN"] = track("SN")
            PATTERN["FT"] = track("FT")
            PATTERN["CR"] = track("CR")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"GENERATED")
            return

        self.send_response(400)
        self.end_headers()
        self.wfile.write(b"INVALID REQUEST")


def start_server():
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()


threading.Thread(target=start_server, daemon=True).start()


# ---------------- MAIN LOOP -------------------------
t0 = time.time()

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    STEP_TIME += (target_step_time - STEP_TIME) * 0.15

    now = time.time()
    if now - t0 >= STEP_TIME:
        t0 = now
        current_step = (current_step + 1) % 16

        for r in ROWS:
            if PATTERN[r][current_step] == 1:
                current_hit = r

    screen.fill((12, 16, 22))

    bpm_text = font_med.render(f"{BPM} BPM", True, (140, 255, 255))
    screen.blit(bpm_text, (W//2 - 60, 40))

    x = W // 2 - 160
    for i in range(4):
        note = next_note(i)
        c = COLOR[note]
        pygame.draw.rect(screen, c, (x + i * 90, 150, 70, 70), border_radius=18)

    cx, cy = W // 2, H // 2 + 40
    glow_circle(cx, cy, 160, COLOR[current_hit])
    pygame.draw.circle(screen, COLOR[current_hit], (cx, cy), 160)

    text = font_big.render(current_hit, True, (0, 0, 0))
    screen.blit(text, (cx - 90, cy - 70))

    dots_x = W // 2 - 200
    for i in range(16):
        col = (100, 200, 120) if i == current_step else (70, 90, 70)
        pygame.draw.circle(screen, col, (dots_x + i * 25, H - 120), 7)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
