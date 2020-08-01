#!/usr/bin/env python3

import grovepi
from grovepi import *
from grove_rgb_lcd import *
from time import sleep
from math import isnan
import subprocess
from datetime import datetime

#
# DHT11 settings
#

dht_sensor_port = 7 # connect the DHt sensor to port 7
dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white-colored sensor

# set green as backlight color
# we need to do it just once
# setting the backlight color once reduces the amount of data transfer over the I2C line

setRGB(0,100,0)

#
# Light Sensor settings
#

# Connect the Grove Light Sensor to analog port A0
# SIG,NC,VCC,GND
light_sensor = 0

# Connect the LED to digital port D4
# SIG,NC,VCC,GND
led = 4

# Turn on LED once sensor exceeds threshold resistance
threshold = 100

grovepi.pinMode(light_sensor,"INPUT")
grovepi.pinMode(led,"OUTPUT")


while True:
    try:
        f = open("output.log", "a")
        # get the temperature and Humidity from the DHT sensor
        [ temp,hum ] = dht(dht_sensor_port,dht_sensor_type)
        # print("temp =", temp, "C\thumidity =", hum,"%")

        # check if we have nans
        # if so, then raise a type error exception
        if isnan(temp) is True or isnan(hum) is True:
            raise TypeError('nan error')

        t = str(temp)
        h = str(hum)


        # get the light sensor data
        sensor_value = grovepi.analogRead(light_sensor)

        # Calculate resistance of sensor in K
        resistance = (float)(1023 - sensor_value) * 10 / sensor_value

        if resistance > threshold:
            # Send HIGH to switch on LED
            grovepi.digitalWrite(led,1)
        else:
            # Send LOW to switch off LED
            grovepi.digitalWrite(led,0)

        # print("sensor_value = %d resistance = %.2f" %(sensor_value,  resistance))

        now = datetime.now()
        datestring = now.strftime("%m/%d/%YT%H:%M:%S")
        p = subprocess.Popen('cat /sys/class/thermal/thermal_zone0/temp', \
            shell=True, stdout=subprocess.PIPE, \
            stderr=subprocess.STDOUT)
        tempstring = 0
        for line in p.stdout.readlines():
            tempstring = round((int(line)/1000),0)


        # instead of inserting a bunch of whitespace, we can just insert a \n
        # we're ensuring that if we get some strange strings on one line, the 2nd one won't be affected
        setText_norefresh("T:" + t + "c," + "H:" + h + "%\n" \
                + "V:" + str(sensor_value) + ",R:" + str(resistance))
        f.write(\
            "temperature: %s, humidity: %s, sensor_value: %s, resistance: %s, \
cpu_temp: %s, datestring: %s EOL\n" \
            % (t, h, str(sensor_value), str(resistance), str(tempstring), datestring))
        f.close()

    except (IOError, TypeError) as e:
        print(str(e))
        # and since we got a type error
        # then reset the LCD's text
        setText("Error:\nIOError")
    except KeyboardInterrupt as e:
        print(str(e))
        # since we're exiting the program
        # it's better to leave the LCD with a blank text
        setText("Error:\nKeyboardInterrupt")
        break

    # wait some time before re-updating the LCD
    sleep(1)

