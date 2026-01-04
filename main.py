# This work is licensed under the MIT license.
# Copyright (c) 2013-2023 OpenMV LLC. All rights reserved.
# https://github.com/openmv/openmv/blob/master/LICENSE
#
# Connect Example
#
# This example shows how to connect to a WiFi network.
# and sends the imu data to the host network

import network, time, socket
from machine import Pin, SPI, LED
from lsm6dsox import LSM6DSOX

SSID = "Galaxy"  # Network SSID
KEY = "bhavik115"  # Network key

# Init wlan module and connect to network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, KEY)

red_led = LED("LED_RED"); green_led = LED('LED_GREEN')
timeout = 5
while not wlan.isconnected() and timeout > 0:
    print('Trying to connect to "{:s}"...'.format(SSID))
    time.sleep_ms(1000)
    timeout -= 1

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
PC_IP = "10.216.155.96"
PORT = 5005

def imu_data():
    print('Now collecting the IMU data')
    spi = SPI(5)
    cs = Pin("PF6", Pin.OUT_PP, Pin.PULL_UP)
    lsm = LSM6DSOX(spi, cs)

    print("Timestamp,Ax,Ay,Az,Gx,Gy,Gz")

    while(True):
        a = lsm.accel()  # Returns (x, y, z)
        g = lsm.gyro()   # Returns (x, y, z)
        ts = time.ticks_ms()

        # Format for terminal/Excel
        data = "%d, %f, %f, %f, %f, %f, %f, %f" % (ts,0,
        a[0], a[1], a[2],
        g[0], g[1], g[2])

        print(data)

        client.sendto(data.encode(), (PC_IP, PORT))
        time.sleep_ms(20)

if wlan.isconnected() == False:
    print('Failed to connect to Wi-Fi')
    red_led.on()
    while True:
        pass
else:
# We should have a valid IP now via DHCP
    print("WiFi Connected ", wlan.ifconfig())
    green_led.on()
    # time.sleep(1)
    # green_led.off()
    imu_data()
