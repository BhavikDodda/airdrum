import socket
import csv
import os
from datetime import datetime
import time
 
# -----------------------------
# CONFIG
# -----------------------------
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
DATA_DIR = "imu_data"
# -----------------------------

os.makedirs(DATA_DIR, exist_ok=True)
activity = input("Enter activity label (e.g., sitting, walking, jogging, jumping, wrist curl): ")
filename = f"{activity}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
filepath = os.path.join(DATA_DIR, filename)
 
f = open(filepath, "w", newline="")
writer = csv.writer(f)
writer.writerow(["timestamp", "ax", "ay", "az", "gx", "gy", "gz", "activity"])
duration_seconds = 120
print('recording will start in 5 seconds')
for i in range(5):
    print(i)
    time.sleep(1)
start_time = time.time() 

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
 
print(f"Listening on UDP port {UDP_PORT}")
print(f"Saving to {filepath}")

print('recording start')

try:
    while (time.time() - start_time) < duration_seconds:
        data, addr = sock.recvfrom(1024)
        decoded = data.decode().strip()
        rowinit = decoded.split(",")
        if float(rowinit[1])==1.0:  # to filter only valid data rows
            row=[rowinit[0],rowinit[2],rowinit[3],rowinit[4],rowinit[5],rowinit[6],rowinit[7]]

            row.append(activity)
            writer.writerow(row)
            print(row)
except KeyboardInterrupt:
    print("\nStopped. File saved.")
 
sock.close()