# ------------------------------------
# NICLA EDGE RECEIVER (LAPTOP)
# ------------------------------------

import socket
import pygame
import time
from pathlib import Path

# -----------------------------
# UDP CONFIG
# -----------------------------
UDP_IP   = "0.0.0.0"
UDP_PORT = 5005

# -----------------------------
# AUDIO INIT (LOW LATENCY)
# -----------------------------
pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.init()

BASE_DIR = Path(__file__).resolve().parent

# -----------------------------
# LOAD SOUNDS
# -----------------------------
SNARE     = pygame.mixer.Sound(str(BASE_DIR / "sound" / "snare.mpeg"))
HIHAT     = pygame.mixer.Sound(str(BASE_DIR / "sound" / "hihat.mpeg"))
CRASH     = pygame.mixer.Sound(str(BASE_DIR / "sound" / "crash.mp3"))
FLOORTOM  = pygame.mixer.Sound(str(BASE_DIR / "sound" / "kick.mp3"))

# Optional: dedicated channels (cleaner overlaps)
pygame.mixer.set_num_channels(4)

# -----------------------------
# UDP SOCKET
# -----------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening for Nicla triggers on UDP", UDP_PORT)

# -----------------------------
# EVENT LOOP
# -----------------------------
try:
    while True:
        data, addr = sock.recvfrom(64)
        msg = data.decode().strip()

        try:
            side, cls = map(int, msg.split(","))
        except ValueError:
            continue  # ignore malformed packets

        # -------------------------
        # LEFT NICLA (0)
        # -------------------------
        if side == 0:
            # class mapping (as per your training)
            if cls == 2:
                SNARE.play()
                print("LEFT → SNARE")
            elif cls == 0:
                HIHAT.play()
                print("LEFT → HIHAT")

        # -------------------------
        # RIGHT NICLA (1)
        # -------------------------
        elif side == 1:
            if cls == 0:
                CRASH.play()
                print("RIGHT → CRASH")
            elif cls == 2:
                FLOORTOM.play()
                print("RIGHT → FLOORTOM")

except KeyboardInterrupt:
    print("\nStopping receiver...")

finally:
    sock.close()
    pygame.quit()
    print("Done.")
