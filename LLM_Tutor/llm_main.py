import time
import threading
from typing import List, Literal, Optional

import instructor
from openai import OpenAI
from pydantic import BaseModel, conint
import requests


# -----------------------------
# 1) CONFIG
# -----------------------------
SELECTED_MODEL = "llama3.2:latest"
OLLAMA_API_URL = "http://localhost:11434/v1"

UI_ENDPOINT = "http://localhost:8000"

MAIN_LOOP_SLEEP = 0.005


# -----------------------------
# 2) OUTPUT SCHEMA
# -----------------------------
Hit = Literal["HH", "SN", "KD", "CR", "-"]


class DrumPattern(BaseModel):
    title: str
    song_or_style: str

    bpm: conint(ge=40, le=220)
    bpm_source: Literal["estimated_from_song", "default", "user_provided"] = "default"
    confidence: conint(ge=0, le=100) = 50

    time_signature: Literal["4/4"] = "4/4"
    resolution: Literal["16th"] = "16th"

    steps: List[str]
    lane: List[Hit]

    loop_bars: conint(ge=1, le=4) = 1
    sections: List[str]
    tips: List[str]


# -----------------------------
# 3) PROMPT
# -----------------------------
TASK_PROMPT = (
    "You are an offline drum tutor for a MONOPHONIC air-drum.\n"
    "User has ONLY 4 drum sounds: HH, SN, KD, CR.\n"
    "CRITICAL: each step must be exactly one of these or '-'.\n"
    "Never output more than one drum per step.\n\n"
    "steps MUST be exactly this literal list:\n"
    "['1','e','&','a','2','e','&','a','3','e','&','a','4','e','&','a']\n"
    "Lane MUST contain exactly 16 elements.\n"
    "Tips must be exactly 3.\n\n"
    "User request:\n"
    "{input_text}\n"
)


# -----------------------------
# 4) CLIENT SETUP
# -----------------------------
client = instructor.patch(
    OpenAI(base_url=OLLAMA_API_URL, api_key="ollama"),
    mode=instructor.Mode.JSON,
)


def generate_pattern(user_text: str) -> DrumPattern:
    prompt = TASK_PROMPT.format(input_text=user_text.strip())
    return client.chat.completions.create(
        model=SELECTED_MODEL,
        messages=[
            {"role": "system", "content": "Return ONLY valid JSON."},
            {"role": "user", "content": prompt},
        ],
        response_model=DrumPattern,
        temperature=0.2,
    )


# -----------------------------
# 5) VALIDATION
# -----------------------------
EXPECTED_STEPS_16 = [
    '1','e','&','a','2','e','&','a','3','e','&','a','4','e','&','a'
]


def validate_pattern(p: DrumPattern) -> None:
    if p.steps != EXPECTED_STEPS_16:
        raise ValueError("steps must match")
    if len(p.lane) != 16:
        raise ValueError("lane must have 16")
    if len(p.tips) != 3:
        raise ValueError("tips must be 3")


def step_delay_seconds(bpm: int) -> float:
    return 60.0 / (float(bpm) * 4.0)


# -----------------------------
# 6) STATE
# -----------------------------
state = {
    "pattern": None,
    "playing": False,
    "step_idx": 0,
    "last_step_time": 0.0,
    "quit": False,
}


def reset_playhead():
    state["step_idx"] = 0
    state["last_step_time"] = time.time()
    print("PLAY: reset")


def start_play():
    if state["pattern"] is None:
        print("No pattern loaded. Type 'gen' first.")
        return
    state["playing"] = True
    reset_playhead()
    print("PLAY: started")


def stop_play():
    state["playing"] = False
    print("PLAY: stopped")


# -----------------------------
# 7) PLAYER LOOP
# -----------------------------
def player_loop():
    while not state["quit"]:
        pat: Optional[DrumPattern] = state["pattern"]

        if state["playing"] and pat is not None:
            dt = step_delay_seconds(pat.bpm)
            now = time.time()

            if now - state["last_step_time"] >= dt:
                state["last_step_time"] = now

                hit = pat.lane[state["step_idx"]]
                step_label = pat.steps[state["step_idx"]]

                print(f"[{pat.song_or_style}] BPM={pat.bpm} "
                      f"| step {state['step_idx']:02d} ({step_label}) -> {hit}")

                state["step_idx"] = (state["step_idx"] + 1) % 16

                if state["step_idx"] == 0:
                    print("---- BAR ----")
        else:
            time.sleep(MAIN_LOOP_SLEEP)


# -----------------------------
# 8) SEND TO UI
# -----------------------------
def send_to_ui(p: DrumPattern):
    try:
        payload = {"bpm": p.bpm, "lane": p.lane}
        print("Sending pattern to UI...")
        r = requests.post(UI_ENDPOINT, json=payload, timeout=5)
        print("UI response:", r.text)
    except Exception as e:
        print("WARNING: Could not send to UI:", e)


# -----------------------------
# 9) CLI
# -----------------------------
HELP_TEXT = """
Commands:
  gen
  start
  stop
  reset
  show
  quit
"""


def main():
    print("Edge LLM Drum Teacher")
    print(f"Model: {SELECTED_MODEL}")
    print(HELP_TEXT)

    threading.Thread(target=player_loop, daemon=True).start()

    while True:
        cmd = input("> ").strip().lower()

        if cmd == "gen":
            user_text = input("Enter song name OR style:\n> ").strip()
            if not user_text:
                print("Empty input.")
                continue

            print("Generating pattern...")

            try:
                pat = generate_pattern(user_text)

                # --- FORCE BPM = 60 ALWAYS ---
                pat.bpm = 40
                pat.bpm_source = "user_provided"
                pat.confidence = 100

                # --- FORCE CORRECT STEPS ---
                pat.steps = EXPECTED_STEPS_16

                # --- AUTO-FIX LANE TO 16 ---
                if len(pat.lane) < 16:
                    pat.lane += ["-"] * (16 - len(pat.lane))
                elif len(pat.lane) > 16:
                    pat.lane = pat.lane[:16]

                validate_pattern(pat)

            except Exception as e:
                print("LLM/Validation error:", e)
                continue

            state["pattern"] = pat
            stop_play()
            reset_playhead()

            print("\nPattern ready:")
            print(f"Song/Style: {pat.song_or_style}")
            print(f"BPM: {pat.bpm} ({pat.bpm_source}, conf={pat.confidence})")
            print("Lane:", pat.lane)
            print("Tips:", pat.tips)

            send_to_ui(pat)

            print("Type 'start' to begin.\n")

        elif cmd == "start":
            start_play()

        elif cmd == "stop":
            stop_play()

        elif cmd == "reset":
            reset_playhead()

        elif cmd == "show":
            if state["pattern"]:
                print(state["pattern"].model_dump_json(indent=2))
            else:
                print("No pattern loaded.")

        elif cmd == "quit":
            state["quit"] = True
            stop_play()
            time.sleep(0.2)
            print("Bye.")
            break

        else:
            print("Unknown command.")


if __name__ == "__main__":
    main()
