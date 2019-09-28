# data class for store state of slave
class MachineConfig:
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


configs = [{
    "name": "assy1",
    "mc_id": 1432,
    "ip": "192.168.1.10",
    "port": 8501,
    "unitId": 1
}]

machineConfig = []
for i in range(len(configs)):
    machineConfig.append(MachineConfig())
    machineConfig[i].setName(configs[i]["name"])
    machineConfig[i].setIP(configs[i]["ip"])
    machineConfig[i].setMcId(configs[i]["mc_id"])
    machineConfig[i].setPort(configs[i]["port"])
    machineConfig[i].setUnitID(configs[i]["unitId"])

ERROR_DESCRIPTION = [
    "Load valve body",
    "Insert seal body",
    "Check seal body",
    "Insert Key",
    "Place key",
    "Insert ball",
    "Check ball",
    "Insert tail",
    "Test torque",
    "Check seal tail",
    "Glue",
    "Load tail",
    "Insert seal tail",
    "Table 1",
    "Unload key",
    "Load key",
    "O-ring 1",
    "O-ring 2",
    "Table 2"
]
