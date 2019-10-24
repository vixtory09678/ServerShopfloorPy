from machine_config import *
from HostLinkProtocol import HostLinkProtocol
import paho.mqtt.client as mqtt
import threading
import constants as const
import time
import datetime
import json

# all client for send comand
clients = []
mqtt = mqtt.Client(transport="websockets")


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
    # print('MC/ID : {0} Control Data: {1}'.format(config.getMcId(), dataMqtt))
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
    printMsg('MC/ID : {0} Pareto Data: {1}'.format(config.getMcId(), dataMqtt))
    mqtt.publish(const.PARETO_PATH_MQTT, dataMqtt)


def bridgeMQTTAlarm(config, alarm, error_stack, time_errors):
    # print(alarm)
    for i in range(len(alarm)):

        dataAlarm = {
            "mc_id": config.getMcId(),
            "name": config.getName(),
            "ip": config.getIP(),
            "id_error": i,
            "description_error": ERROR_DESCRIPTION[i]
        }
        if alarm[i] == True:
            if (config.getStateCheckDuplicate(i) == False):
                config.setStateCheckDuplicate(i, True)
                dataMqtt = json.dumps(dataAlarm)
                mqtt.publish(const.ALARM_PATH_MQTT, dataMqtt)
        else:
            if (config.getStateCheckDuplicate(i) == True):
                config.setStateCheckDuplicate(i, False)

                dataAlarm["description_error"] = "clear"
                dataMqtt = json.dumps(dataAlarm)
                printMsg(
                    'MC/ID : {0} Alarm Data: {1}'.format(config.getMcId(), dataMqtt))
                mqtt.publish(const.ALARM_PATH_MQTT, dataMqtt)

                bridgeMQTTPareto(config, error_stack[i], time_errors[i], i)


def bridgeMQTTAuto(config, status):

    autoJson = {
        "name": config.getName(),
        "ip": config.getIP(),
        "status_auto": status[0],
        "status_auto_stop": status[1]
    }
    printMsg('MC/ID: {0} Auto is {1}'.format(config.getMcId(), status))
    dataMqtt = json.dumps(autoJson)
    mqtt.publish(const.AUTO_STATUS_PATH_MQTT, dataMqtt)


def printMsg(string):
    x = datetime.datetime.now()
    print('{0}: {1}'.format(x, string))


def initMachineSync():
    for machine in machineConfig:
        try:
            data = HostLinkProtocol(machine.getIP(), machine.getPort())
            clients.append(data)
        except ValueError:
            printMsg("Error with host or port params")


def initMqtt():
    mqtt.on_connect = on_connect
    mqtt.connect(const.HOST_URL, const.PORT, 120)
    mqtt.loop_forever()
    # mqtt.connect("192.168.43.70", 9001, 60)


def on_connect(client, userdata, flags, rc):
    printMsg("Connected with result code "+str(rc))
    initThread()


def initThread():
    printMsg("init threading")

    threadMain = threading.Thread(target=mainProgram, args=(1,))
    threadMain.daemon = True
    threadMain.start()


def mainProgram(test):
    printMsg("Connecting PLC..")
    initMachineSync()
    printMsg("Connected")
    while True:
        for i in range(len(machineConfig)):
            if clients[i].open():

                isAutoRun = clients[i].requestContinuousDataRead("MR10", 1)
                isAutoRunStop = clients[i].requestContinuousDataRead(
                    "MR2710", 1)

                bridgeMQTTAuto(machineConfig[i], [
                               isAutoRun[0], isAutoRunStop[0]])

                if (isAutoRun[0] == 0):
                    clients[i].close()
                    printMsg("machine stop")
                    continue

                # read machine alarm
                alarm = clients[i].requestContinuousDataRead("MR6001", 19)
                # read machine error stact each station
                error_stack = clients[i].requestContinuousDataRead(
                    "D201.U", 19)
                # read machine time error each station
                time_errors = clients[i].requestContinuousDataRead(
                    "DM410.D", 19)
                # read machine data of product
                control = clients[i].requestContinuousDataRead("DM400.D", 4)

                if control is None:
                    continue
                if alarm is None:
                    continue
                if error_stack is None:
                    continue
                if time_errors is None:
                    continue

                printMsg("Send..")

                bridgeMQTTControl(machineConfig[i], control)
                bridgeMQTTAlarm(machineConfig[i],
                                alarm, error_stack, time_errors)

                clients[i].close()
            else:
                printMsg("can't connect")
        time.sleep(4)


# main program here
if __name__ == "__main__":
    TIME_WAIT_START = 20
    printMsg('Wait for connection in {0}'.format(TIME_WAIT_START))
    time.sleep(TIME_WAIT_START)
    initMqtt()
