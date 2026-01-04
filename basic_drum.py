import socket
import time
import pygame
from collections import deque
from pathlib import Path

# -----------------------------
# CONFIG
# -----------------------------
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
DURATION_SECONDS = 120

WINDOW_SIZE = 50
FEATURES_PER_ROW = 6
# -----------------------------

# -----------------------------
# AUDIO INIT (LOW LATENCY)
# -----------------------------
pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.init()

BASE_DIR = Path(__file__).resolve().parent

CRASH = pygame.mixer.Sound(str(BASE_DIR / "sound" / "crash.mp3"))
FLOORTOM = pygame.mixer.Sound(str(BASE_DIR / "sound" / "kick.mp3"))
SNARE = pygame.mixer.Sound(str(BASE_DIR / "sound" / "snare.mpeg"))
HIHAT = pygame.mixer.Sound(str(BASE_DIR / "sound" / "hihat.mpeg"))

SNARE_PATH = BASE_DIR / "sound" / "snare.mpeg"

SNARE = pygame.mixer.Sound(str(SNARE_PATH))
# -----------------------------

# -----------------------------
# SLIDING WINDOW
# -----------------------------
window_L = deque(maxlen=WINDOW_SIZE)
window_R = deque(maxlen=WINDOW_SIZE)
# -----------------------------

# -----------------------------
# MODEL
# -----------------------------
def score_L(input):
    if input[146] <= -0.5661009848117828:
        if input[32] <= -0.4818115085363388:
            var0 = [0.0, 1.0, 0.0]
        else:
            var0 = [0.0, 0.4, 0.6]
    else:
        if input[187] <= -0.6529539823532104:
            if input[247] <= -0.6609494984149933:
                if input[98] <= -0.28472900390625:
                    if input[296] <= -0.28155550360679626:
                        var0 = [0.0, 1.0, 0.0]
                    else:
                        var0 = [1.0, 0.0, 0.0]
                else:
                    if input[110] <= 0.021667500026524067:
                        var0 = [1.0, 0.0, 0.0]
                    else:
                        var0 = [0.4, 0.6, 0.0]
            else:
                if input[217] <= -0.6558839976787567:
                    if input[77] <= 44.58618927001953:
                        var0 = [1.0, 0.0, 0.0]
                    else:
                        var0 = [0.2, 0.0, 0.8]
                else:
                    if input[195] <= 3.6621105074882507:
                        var0 = [0.0, 0.0, 1.0]
                    else:
                        var0 = [0.2, 0.2, 0.6]
        else:
            if input[157] <= -0.6719360053539276:
                if input[197] <= 39.794921875:
                    if input[38] <= -0.2765499949455261:
                        var0 = [0.8, 0.2, 0.0]
                    else:
                        var0 = [1.0, 0.0, 0.0]
                else:
                    var0 = [0.0, 0.0, 1.0]
            else:
                if input[149] <= 14.404300689697266:
                    if input[221] <= 21.026615142822266:
                        if input[278] <= -0.16418449580669403:
                            var0 = [0.0, 1.0, 0.0]
                        else:
                            if input[153] <= -2.777100592851639:
                                var0 = [0.0, 0.0, 1.0]
                            else:
                                var0 = [0.0, 0.6, 0.4]
                    else:
                        var0 = [0.0, 0.0, 1.0]
                else:
                    var0 = [0.0, 0.0, 1.0]
    return var0
# -----------------------------
def score_R(input):
    if input[19] <= -0.5087279975414276:
        if input[264] <= 0.2947999984025955:
            if input[164] <= 0.11511199921369553:
                if input[171] <= -24.29199981689453:
                    var0 = [0.0, 0.4, 0.6]
                else:
                    var0 = [0.0, 1.0, 0.0]
            else:
                if input[266] <= -0.19079599529504776:
                    var0 = [1.0, 0.0, 0.0]
                else:
                    var0 = [0.0, 0.0, 1.0]
        else:
            if input[233] <= -58.89893341064453:
                var0 = [0.0, 1.0, 0.0]
            else:
                if input[259] <= -0.5972900092601776:
                    var0 = [0.0, 0.0, 1.0]
                else:
                    var0 = [0.2, 0.0, 0.8]
    else:
        if input[175] <= -0.8533934950828552:
            var0 = [0.0, 0.8333333333333334, 0.16666666666666666]
        else:
            if input[265] <= -0.6979369819164276:
                var0 = [0.6, 0.0, 0.4]
            else:
                var0 = [1.0, 0.0, 0.0]
    return var0
# ----------------------------------

def score_L_stick(input):
    if input[278] <= -0.1757199987769127:
        if input[188] <= 0.15112300217151642:
            var0 = [0.0, 1.0, 0.0]
        else:
            var0 = [1.0, 0.0, 0.0]
    else:
        if input[108] <= 0.6574095189571381:
            if input[80] <= 0.08630399778485298:
                var0 = [0.0, 0.4, 0.6]
            else:
                var0 = [0.0, 0.0, 1.0]
        else:
            if input[12] <= 0.6967165172100067:
                var0 = [0.0, 0.2857142857142857, 0.7142857142857143]
            else:
                if input[67] <= -0.3919675052165985:
                    var0 = [0.4, 0.6, 0.0]
                else:
                    var0 = [1.0, 0.0, 0.0]
    return var0
#-------
def score_R_2(input):
    if input[36] <= 0.5671384930610657:
        if input[93] <= -8.453370094299316:
            var0 = [0.0, 0.0, 1.0]
        else:
            if input[21] <= -7.904052972793579:
                if input[144] <= 0.3271484971046448:
                    var0 = [0.0, 0.0, 1.0]
                else:
                    var0 = [0.0, 0.4, 0.6]
            else:
                if input[266] <= 0.9555664956569672:
                    var0 = [0.0, 1.0, 0.0]
                else:
                    var0 = [0.0, 0.8, 0.2]
    else:
        if input[202] <= -14.831546783447266:
            var0 = [1.0, 0.0, 0.0]
        else:
            if input[298] <= -19.4091796875:
                var0 = [1.0, 0.0, 0.0]
            else:
                if input[40] <= 12.695316314697266:
                    var0 = [0.0, 1.0, 0.0]
                else:
                    var0 = [0.4, 0.6, 0.0]
    return var0
# -----------------------------
# AUDIO TRIGGER
# -----------------------------
def play_snare():
    base_dir = Path(__file__).resolve().parent.parent   # project root
    sound_path = base_dir / "sound" / "snare.wav"

    if not pygame.mixer.get_init():
        pygame.mixer.pre_init(44100, -16, 2, 256)
        pygame.init()

    snare = pygame.mixer.Sound(str(sound_path))
    snare.play()
    time.sleep(snare.get_length())
    

# -----------------------------
# UDP SOCKET
# -----------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
# -----------------------------
def window_variation(window):
    total_var = 0.0

    # for each of the 6 features
    for c in range(6):
        for t in range(1, len(window)):
            total_var += abs(window[t][c] - window[t-1][c])

    return total_var

def row_variation(row):
    total_var = 0.0
    for t in range(1, len(row)):
        total_var += abs(row[t] - row[t-1])

    return total_var
# -----------------------------
# START
# -----------------------------
print("Recording will start in 5 seconds...")
for i in range(3, 0, -1):
    print(i)
    time.sleep(1)

start_time = time.time()
print("Listening...")
VARTHRESHOLD=60
try:
    while (time.time() - start_time) < DURATION_SECONDS:
        data, _ = sock.recvfrom(1024)
        decoded = data.decode().strip()
        mainrow=list(map(float, decoded.split(",")))[1:]
        row = mainrow[1:]
        print("row",mainrow)
        if mainrow[0]==0:
            window_L.append(row)
            print("L",row_variation(row))
            if len(window_L) == WINDOW_SIZE:
                # flatten 50 x 6 → 300
                input_vector = [x for r in window_L for x in r]

                output_L = score_L_stick(input_vector)
                if row_variation(row) > VARTHRESHOLD:
                    if output_L[2] == 1.0:
                        HIHAT.stop()
                        SNARE.play()
                        print("Played Snare")
                    elif output_L[0]==1.0:
                        SNARE.stop()
                        HIHAT.play()
                        print("Played HiHat")
        else:
            window_R.append(row)
            print("R",row_variation(row))
            if len(window_R) == WINDOW_SIZE:
                # flatten 50 x 6 → 300
                input_vector = [x for r in window_R for x in r]

                output_R = score_L_stick(input_vector)
                if row_variation(row) > VARTHRESHOLD:
                    predicted = output_R.index(max(output_R))
                    if predicted == 0:      # crash
                        FLOORTOM.stop()
                        CRASH.play()
                        print("Played Crash")
                    elif predicted == 2:    # floortom
                        CRASH.stop()
                        FLOORTOM.play()
                        print("Played FloorTom")
                    

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    sock.close()
    pygame.quit()
    print("Done.")