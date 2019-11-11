import paho.mqtt.client as mqtt
import json
import util
import constants as const
from machine_config import *

mqtt = mqtt.Client(transport="websockets")


def bridgeMQTTProduct(config, control):

    dataProduct = {
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

    dataMqtt = json.dumps(dataProduct)
    mqtt.publish(const.PRODUCT_PATH_MQTT, dataMqtt)


def bridgeMQTTError(config, error_stack, timer_error, timer_error_stack, addr):
    dataError = {
        "mc_id": config.getMcId(),
        "name": config.getName(),
        "ip": config.getIP(),
        "error": {
            "error_id": addr,
            "description_error": ERROR_DESCRIPTION[addr],
            "error_stack": error_stack,
            "time_error": timer_error,
            "time_error_stack": timer_error_stack
        }
    }
    dataMqtt = json.dumps(dataError)
    util.printMsg(
        'MC/ID : {0} Pareto Data: {1}'.format(config.getMcId(), dataMqtt))
    mqtt.publish(const.ERROR_PATH_MQTT, dataMqtt)


def bridgeMQTTAlarm(config, alarm, error_stack, time_errors, time_error_stacks):
    # print(alarm)
    for i in range(len(alarm)):

        dataAlarm = {
            "mc_id": config.getMcId(),
            "name": config.getName(),
            "ip": config.getIP(),
            "error_id": i,
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
                util.printMsg(
                    'MC/ID : {0} Alarm Data: {1}'.format(config.getMcId(), dataMqtt))
                mqtt.publish(const.ALARM_PATH_MQTT, dataMqtt)

                bridgeMQTTError(
                    config, error_stack[i], time_errors[i], time_error_stacks[i], i)


def bridgeMQTTErrorBad(config, bad_error):
    for i in range(len(bad_error)):
        dataErrorBad = {
            "mc_id": config.getMcId(),
            "name": config.getName(),
            "ip": config.getIP(),
            "error": {
                "error_id": i,
                "description_error": ERROR_DESCRIPTION[i],
                "error_stack": bad_error[i]
            }
        }

        if (bad_error[i] != config.getBadCheckDuplicate(i)):
            config.setBadCheckDuplicate(i, bad_error[i])
            dataMqtt = json.dumps(dataErrorBad)
            mqtt.publish(const.BAD_PATH_MQTT, dataMqtt)


def bridgeMQTTAuto(config, status):

    dataStatus = {
        "mc_id": config.getMcId(),
        "name": config.getName(),
        "ip": config.getIP(),
        "status_machine": status[0],
        "status_auto": status[1],
        "status_auto_stop": status[2]
    }

    util.printMsg('MC/ID: {0} Auto is {1}'.format(config.getMcId(), status))
    dataMqtt = json.dumps(dataStatus)
    mqtt.publish(const.AUTO_STATUS_PATH_MQTT, dataMqtt)


def initMqtt(on_connect):
    mqtt.on_connect = on_connect
    mqtt.connect(const.HOST_URL, const.PORT, 120)
    mqtt.loop_forever()
