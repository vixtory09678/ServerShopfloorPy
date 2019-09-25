# import win_inet_pton
from pyModbusTCP.client import ModbusClient
from slave_config import *
from rounting import *
import paho.mqtt.client as mqtt
import time
import json

# all client for send comand
clients = []
mqtt = mqtt.Client(transport="websockets")


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


def initSlave():
    for slave in slaveConfig:
        try:
            clients.append(
                ModbusClient(
                    host=slave.getIP(),
                    port=slave.getPort(),
                    unit_id=slave.getUnitID()))
        except ValueError:
            print("Error with host or port params")


def initMqtt():
    mqtt.on_connect = on_connect
    # mqtt.connect("127.0.0.1", 9001, 60)
    mqtt.connect("192.168.43.70", 9001, 60)


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
    mqtt.publish(CONTROL_PATH_MQTT, dataMqtt)


def bridgeMQTTPareto(config, errors_inform, addr):
    dataPareto = {
        "name": config.getName(),
        "ip": config.getIP(),
        "error": {
            "error_id": addr,
            "description_error": ERROR_DESCRIPTION[addr],
            "error_stack": errors_inform[addr],
            "time_error": errors_inform[addr + 13]
        }
    }
    dataMqtt = json.dumps(dataPareto)
    print('MC/ID : {0} Pareto Data: {1}'.format(config.getMcId(), dataMqtt))
    mqtt.publish(PARETO_PATH_MQTT, dataMqtt)


def bridgeMQTTAlarm(config, alarm, errors_inform):

    for i in range(13):

        dataAlarm = {
            "mc_id": config.getMcId(),
            "name": config.getName(),
            "ip": config.getIP(),
            "id_error": i,
            "description_error": ERROR_DESCRIPTION[i]
        }

        state = (alarm[0] >> i)
        if (state & 0x01) == True:
            if (config.getStateCheckDuplicate(i) == False):

                dataMqtt = json.dumps(dataAlarm)
                mqtt.publish(ALARM_PATH_MQTT, dataMqtt)
        else:
            if (config.getStateCheckDuplicate(i) == True):
                config.setStateCheckDuplicate(i, False)

                dataAlarm["description_error"] = "clear"
                dataMqtt = json.dumps(dataAlarm)
                print(
                    'MC/ID : {0} Alarm Data: {1}'.format(config.getMcId(), dataMqtt))
                mqtt.publish(ALARM_PATH_MQTT, dataMqtt)

                bridgeMQTTPareto(config, errors_inform, i)


if __name__ == "__main__":
    initMqtt()
    initSlave()

    while True:
        for i in range(len(slaveConfig)):
            if clients[i].open():
                control = clients[i].read_holding_registers(0, 4)
                alarm = clients[i].read_holding_registers(4, 1)
                errors_inform = clients[i].read_holding_registers(5, 26)

                bridgeMQTTControl(slaveConfig[i], control)
                bridgeMQTTAlarm(slaveConfig[i], alarm, errors_inform)

                clients[i].close()
        time.sleep(4)
