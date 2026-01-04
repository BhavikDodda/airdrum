# -------------------------------------------------
# NICLA VISION – LEFT STICK
# MICRO PYTHON SAFE EDGE INFERENCE
# -------------------------------------------------

import network, time, socket
from machine import Pin, SPI, LED
from lsm6dsox import LSM6DSOX
from collections import deque

# -----------------------------
# WIFI CONFIG
# -----------------------------
SSID = "Galaxy"
KEY  = "bhavik115"

PC_IP = "10.216.155.96"
PORT  = 5005

# -----------------------------
# MODEL / WINDOW CONFIG
# -----------------------------
WINDOW_SIZE   = 50
FEATURES      = 6
VAR_THRESHOLD = 60
COOLDOWN_MS   = 80

# -----------------------------
# LEDS
# -----------------------------
red_led   = LED("LED_RED")
green_led = LED("LED_GREEN")

# -----------------------------
# WIFI INIT
# -----------------------------
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

timeout = 5
while not wlan.isconnected() and timeout > 0:
    print('Trying to connect to "{}"...'.format(SSID))
    time.sleep(1)
    timeout -= 1

# -----------------------------
# UDP SOCKET
# -----------------------------
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# -----------------------------
# HELPERS
# -----------------------------
def row_variation(row):
    total = 0.0
    i = 1
    while i < FEATURES:
        total += abs(row[i] - row[i-1])
        i += 1
    return total

# -----------------------------
# DECISION TREE (LEFT)
# -----------------------------
def score_L_stick(input):
    if input[278] <= -0.1757199987769127:
        if input[188] <= 0.15112300217151642:
            return [0.0, 1.0, 0.0]
        else:
            return [1.0, 0.0, 0.0]
    else:
        if input[108] <= 0.6574095189571381:
            if input[80] <= 0.08630399778485298:
                return [0.0, 0.4, 0.6]
            else:
                return [0.0, 0.0, 1.0]
        else:
            if input[12] <= 0.6967165172100067:
                return [0.0, 0.2857142857142857, 0.7142857142857143]
            else:
                if input[67] <= -0.3919675052165985:
                    return [0.4, 0.6, 0.0]
                else:
                    return [1.0, 0.0, 0.0]

# -----------------------------
# MAIN IMU + INFERENCE LOOP
# -----------------------------
def imu_data():
    print("Starting LEFT edge inference")

    spi = SPI(5)
    cs  = Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)
    lsm = LSM6DSOX(spi, cs)

    window = deque([], WINDOW_SIZE)

    # Preallocate flat input vector (300)
    input_vector = [0.0] * (WINDOW_SIZE * FEATURES)

    last_sent = 0

    while True:
        ax, ay, az = lsm.accel()
        gx, gy, gz = lsm.gyro()
        row = [ax, ay, az, gx, gy, gz]

        window.append(row)

        # Only proceed once window is full
        if len(window) == WINDOW_SIZE:

            # ---- flatten 50 x 6 → 300 ----
            k = 0
            for r in window:
                for v in r:
                    input_vector[k] = v
                    k += 1

            # ---- model inference ----
            output = score_L_stick(input_vector)

            # ---- motion gate AFTER inference ----
            if row_variation(row) > VAR_THRESHOLD:

                # argmax (MicroPython-safe)
                predicted = 0
                best = output[0]
                i = 1
                while i < 3:
                    if output[i] > best:
                        best = output[i]
                        predicted = i
                    i += 1

                # cooldown gate
                now = time.ticks_ms()
                if time.ticks_diff(now, last_sent) > COOLDOWN_MS:
                    packet = "0,%d" % predicted
                    client.sendto(packet.encode(), (PC_IP, PORT))
                    last_sent = now
                    print("Sent:", packet)

        time.sleep_ms(20)
# -----------------------------
# WIFI CHECK (ORIGINAL STYLE)
# -----------------------------
if wlan.isconnected() == False:
    print("Failed to connect to Wi-Fi")
    red_led.on()
    while True:
        pass
else:
    print("WiFi Connected", wlan.ifconfig())
    green_led.on()
    imu_data()
