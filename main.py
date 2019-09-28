# import win_inet_pton
from pyModbusTCP.client import ModbusClient
from machine_config import *
from HostLinkProtocol import HostLinkProtocol
import paho.mqtt.client as mqtt
import threading
import constants as const
import time
import json

# all client for send comand
clients = []
mqtt = mqtt.Client(transport="websockets")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def initMachineSync():
    for machine in machineConfig:
        try:
            data = HostLinkProtocol(machine.getIP(), machine.getPort())
            clients.append(data)
        except ValueError:
            print("Error with host or port params")


def initMqtt():
    mqtt.on_connect = on_connect
    mqtt.connect(const.HOST_URL, 9001, 60)
    # mqtt.connect("192.168.43.70", 9001, 60)


def bridgeMQTTControl(config, control):
    dataConfig = {
        "name": config.getName(),
        "ip": config.getIP(),
        "mc_id": config.getMcId(),
        "data": {
            "good": control[0],
            "bad": control[1],
            "total": control[0] + control[1],
            "totalTime": control[2],
            "timeError": control[3]
        }
    }
    dataMqtt = json.dumps(dataConfig)
    print('MC/ID : {0} Control Data: {1}'.format(config.getMcId(), dataMqtt))
    mqtt.publish(const.CONTROL_PATH_MQTT, dataMqtt)


def bridgeMQTTPareto(config, error_stack, timer_error, addr):
    dataPareto = {
        "name": config.getName(),
        "ip": config.getIP(),
        "error": {
            "error_id": addr,
            "description_error": ERROR_DESCRIPTION[addr],
            "error_stack": error_stack,
            "time_error": timer_error
        }
    }
    dataMqtt = json.dumps(dataPareto)
    print('MC/ID : {0} Pareto Data: {1}'.format(config.getMcId(), dataMqtt))
    mqtt.publish(const.PARETO_PATH_MQTT, dataMqtt)


def bridgeMQTTAlarm(config, alarm, error_stack, time_errors):

    for i in range(len(error_stack)):

        dataAlarm = {
            "mc_id": config.getMcId(),
            "name": config.getName(),
            "ip": config.getIP(),
            "id_error": i,
            "description_error": ERROR_DESCRIPTION[i]
        }

        if error_stack[i] == True:
            if (config.getStateCheckDuplicate(i) == False):

                dataMqtt = json.dumps(dataAlarm)
                mqtt.publish(const.ALARM_PATH_MQTT, dataMqtt)
        else:
            if (config.getStateCheckDuplicate(i) == True):
                config.setStateCheckDuplicate(i, False)

                dataAlarm["description_error"] = "clear"
                dataMqtt = json.dumps(dataAlarm)
                print(
                    'MC/ID : {0} Alarm Data: {1}'.format(config.getMcId(), dataMqtt))
                mqtt.publish(const.ALARM_PATH_MQTT, dataMqtt)

                bridgeMQTTPareto(config, error_stack[i], time_errors[i], i)


def runRequestControl():
    while True:
        for i in range(len(machineConfig)):
            if clients[i].open():
                control = clients[i].requestContinuousDataRead("DM400.D", 4)
                bridgeMQTTControl(machineConfig[i], control)
                print(control)
                clients[i].close()
            else:
                print("can't connect")
        time.sleep(4)


def runRequestAlarm():
    while True:
        for i in range(len(machineConfig)):
            if clients[i].open():
                alarm = clients[i].requestContinuousDataRead("MR4001", 19)
                error_stack = clients[i].requestContinuousDataRead(
                    "D201.U", 19)
                time_errors = clients[i].requestContinuousDataRead(
                    "DM410.D", 19)
                bridgeMQTTAlarm(machineConfig[i],
                                alarm, error_stack, time_errors)
                print(control)
                clients[i].close()
            else:
                print("can't connect")
        time.sleep(4)


# main program here
if __name__ == "__main__":
    initMqtt()
    initMachineSync()

    thread1 = threading.Thread(target=runRequestControl)
    thread2 = threading.Thread(target=runRequestControl)

    thread1.daemon = True
    thread2.daemon = True

    thread1.start()
    thread2.start()

    # thread1.join()
    # thread2.join()

    while True:
        pass
