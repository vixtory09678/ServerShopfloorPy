configs = [{
    "name": "assy1",
    "mc_id": 1432,
    "ip": "192.168.43.249",
    "port": 5002,
    "unitId": 1
}, {
    "name": "assy2",
    "mc_id": 1424,
    "ip": "192.168.43.87",
    "port": 5002,
    "unitId": 2
}]

# data class for store state of slave


class SlaveConfig:
    def __init__(self):
        self.name = ""
        self.mc_id = 0
        self.ip = ""
        self.port = 5002
        self.unitId = 0
        self.stateCheckDuplicate = [False, False, False, False, False,
                                    False, False, False, False, False, False, False, False]

    def setName(self, name):
        self.name = name

    def setMcId(self, mc_id):
        self.mc_id = mc_id

    def setIP(self, ip):
        self.ip = ip

    def setPort(self, port):
        self.port = port

    def setUnitID(self, unitId):
        self.unitId = unitId

    def setStateCheckDuplicate(self, index, value):
        self.stateCheckDuplicate[index] = value

    def getName(self):
        return self.name

    def getMcId(self):
        return self.mc_id

    def getIP(self):
        return self.ip

    def getPort(self):
        return self.port

    def getUnitID(self):
        return self.unitId

    def getStateCheckDuplicate(self, index):
        return self.stateCheckDuplicate[index]


slaveConfig = []

for i in range(2):
    slaveConfig.append(SlaveConfig())
    slaveConfig[i].setName(configs[i]["name"])
    slaveConfig[i].setIP(configs[i]["ip"])
    slaveConfig[i].setMcId(configs[i]["mc_id"])
    slaveConfig[i].setPort(configs[i]["port"])
    slaveConfig[i].setUnitID(configs[i]["unitId"])

ERROR_DESCRIPTION = [
    "Load valve body",
    "Insert seal body",
    "Check seal body",
    "Insert Key",
    "Place key",
    "Insert ball",
    "Check ball",
    "Insert seal tail",
    "Check seal tail",
    "Load tail",
    "Insert tail",
    "Glue",
    "Test torque"
]
