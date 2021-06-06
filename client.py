from time import sleep
from serial import Serial
import json
import requests
mapped = dict()
import random

import sys
sys.path.append('/home/pi/tracer/python')
from tracer import Tracer, TracerSerial, QueryCommand

port1 = Serial('/dev/ttyACM0', 9600, timeout = 0)
port = Serial('/dev/ttyS0', 9600, timeout = 1) 
port.flushInput()
port.flushOutput()
tracer = Tracer(0x16)
t_ser= TracerSerial(tracer, port)
query = QueryCommand()

def getMedian(a):
    a_len = len(a)
    if(a_len == 0):return Node
    a_center = int(a_len/2)

    if(a_len%2==1):
        return a[a_center]
    else:
        return (a[a_center - 1] + a[a_center]) / 2.0

j=0
sensorIrradiation = [0 for i in range(100)]
panelIrradiation = [0 for i in range(100)]
temperature = [0 for i in range(100)]

sensor_sum = 0
panel_sum = 0
temperature_sum = 0
try:
    while 1:
        try:
            t_ser.send_command(query)
            data = t_ser.receive_result()
        except(IndexError, IOError) as e:
            print(e)
            port.flushInput()
            port.flushOutput()
            sleep(1)
            continue
        try:
            sensing_value = port1.readline()
            sensing_value = int(sensing_value[0:-2])
        except ValueError:
            pass	
	if j == 100:
		j=0
		sensorIrradiation.sort()
		panelIrradiation.sort()
		temperature.sort()
		
		sensor_value = (((((getMedian(sensorIrradiation))/352))*100) * 1.5) / 1.2
		panel_value = (getMedian(panelIrradiation)*120)+2
		temperature_value = getMedian(temperature)

		mapped["sensorIrradiation"] = sensor_value 
		mapped["panelIrradiation"] =  panel_value 
		mapped["temperature"] = temperature_value 
	
		url = "http://192.168.123.3:8080/api/panels/3/collectors"

		payload = str(json.dumps(mapped))
		print(mapped)
		headers = {'Content-Type': 'application/json'}

		response = requests.request("POST", url, data=payload, headers=headers)
		print(response.text)
		sleep(1)
	sensorIrradiation[j] = sensing_value
	panelIrradiation[j]  = data.charge_current 
	temperature[j] = 10 
	
	j+=1         
	
	sleep(0.1)
except KeyboardInterrupt:
    print("\nCtrl-C pressed.  Closing serial port and exiting...")
finally:
    port.close()
