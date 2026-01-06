# AirJam: Real-time Air Drumming with Edge AI

AirJam is a real-time, dual-hand air drumming system that uses TinyML models on Arduino Nicla Vision boards and a local LLM tutor running on a laptop to teach and accompany drummers at the edge.

## Problem statement

Traditional drum kits are expensive, bulky, and fixed in one place, which makes them hard to access for many learners. Learning drums also usually requires a human instructor, which limits flexibility and increases cost. There is a need for a portable, low-cost, and intelligent drumming system that works offline and preserves user privacy.

## Project goal

The goal of **AirJam** is to build a portable, real-time air drumming system that:

- Uses IMU-equipped drumsticks and TinyML models to detect drum hits with low latency on-device.
- Provides an interactive **LLM-based** tutor that generates play-along beats.
- Runs entirely at the edge (microcontrollers + laptop) so that it works offline and keeps user data local.

## Dataset description

The dataset consists of IMU time-series data collected from two Arduino Nicla Vision boards mounted on drumsticks, one for each hand. Each board records accelerometer and gyroscope readings along the three axes: \(ax, ay, az, gx, gy, gz\).

- **Left drumstick**:
  - Trained to detect snare, hi-hat, and no-hit gestures (e.g., `leftdown`, `leftup`, `nothingleft`).
- **Right drumstick**:
  - Trained to detect floor tom, crash, and no-hit gestures.

Data was collected by repeatedly performing each gesture and recording labeled sequences, which are then used to train decision-tree TinyML classifiers. The dataset shows clear peaks in accelerometer/gyroscope channels around hit events and relatively flat segments for no-hit periods.

## Model pipeline and workflow

AirJam uses an edge-first pipeline that runs across two Nicla Vision boards and a laptop.

1. **Sensing and data acquisition**
   - Each Nicla Vision samples IMU data \((ax, ay, az, gx, gy, gz)\) from its attached drumstick.
   - Data is segmented into frames for further processing.

2. **Preprocessing**
   - Simple statistics (e.g., variance over a time window) are computed per frame to detect motion intensity.
   - Two approaches were explored:
     - Sliding-window variance (robust to small vibrations but stays high after peaks).
     - Single-frame variance (very precise at peaks but more sensitive to noise).

3. **TinyML classification on-device**
   - A 3-class decision-tree model runs on each Nicla Vision:
     - Left: snare, hi-hat, no-hit.
     - Right: floor tom, crash, no-hit.
   - The TinyML model is chosen for low memory footprint and fast inference on the microcontroller.
   - The classifier achieves around 97% accuracy on training and test data with moderate inference latency suitable for live drumming.

4. **Synchronization and sound generation**
   - The laptop receives predictions from both sticks in real time and synchronizes them.
   - Mapped drum sounds (snare, hi-hat, floor tom, crash) are triggered to produce the final audio output.

5. **LLM tutor loop**
   - A local LLM (e.g., llama3.2 latest) runs on the laptop as an edge device.
   - The user provides prompts such as “teach me a basic rock beat” or “give me a 4-bar fill”.
   - The LLM generates play-along beat sequences and textual guidance, which the user follows while the TinyML system detects hits and plays sounds.

## Deployment details

AirJam is designed as an edge-first system where all inference happens on-device.

- **Microcontroller side (Nicla Vision)**
  - Each Nicla Vision runs:
    - IMU sampling firmware.
    - Preprocessing (windowing and variance).
    - A decision-tree TinyML model compiled for the board.
  - Models run entirely on the microcontroller, avoiding cloud calls and enabling low-latency response.

- **Laptop side**
  - Receives class labels from both Nicla boards via serial or another communication channel.
  - Maps labels to audio samples and plays the corresponding drum sounds.
  - Hosts the local LLM (e.g., llama3.2) that:
    - Generates beat patterns and exercise prompts based on user input.
    - Optionally provides feedback or next-step suggestions.

- **Edge AI properties**
  - On-device inference on Nicla Vision keeps latency moderate and drumming responsive.
  - Since all data processing and tutoring run locally, the system is privacy-first and fully offline.

## Instructions to run the code

> Note: Adapt folder names and commands below to match your actual repository structure and scripts.

### 1. Hardware setup

1. Mount an Arduino Nicla Vision on each drumstick (left and right hand).
2. Connect both boards to your laptop for flashing and serial communication.
3. Ensure IMU orientation is consistent across data collection and deployment.

### 2. Flash TinyML models to Nicla boards

1. Open the left and right firmware projects.
2. In OpenMV IDE:
   - Connect the Nicla Vision board.
   - Move the required file to the drive and rename it as `main.py`.
   - Repeat for both Nicla Vision devices.

### 3. Start the laptop-side drum engine

`basic_drum_inferencenot.py`

# Acknowledgement

We thank the organizers for resources, equipment and guidance for developing this project during the **ACM India Winter School on Edge AI** hackathon (https://www.samy101.com/acm-winter-school-edge-ai/)

# Team
- [Bhavik Dodda](https://github.com/BhavikDodda)
- [Yamini Prabha](https://github.com/yaminiprabhab)
- [Shambhavi Sinha](https://github.com/Ssinha254)
- [Varsha Pillai](https://github.com/varsha-2024-snu)
- [Tejasri Pendota](https://github.com/Tejasri-Pendota)
