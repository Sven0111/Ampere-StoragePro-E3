from homeassistant.components.sensor import SensorDeviceClass
# Numerische Sensoren (alle ohne Diagnostic)
SENSOR_DEFINITIONS  = [
    # Versionsnummern
    ("Master Version", 36001, 1, 1, "", "uint16", None, None, True),
    ("Slave Version", 36002, 1, 1, "", "uint16", None, None, True),
    ("Manager Version", 36003, 1, 1, "", "uint16", None, None, True),  

    # Batterie SoC → battery device_class
    ("BMS1 Connceted", 37002, 1, 1, "", "uint16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 Master Version", 37003, 1, 1, "", "uint16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 Voltage", 37609, 1, 0.1, "V", "uint16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 Current", 37610, 1, 0.1, "A", "int16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 Ambient Temperature", 37611, 1, 0.1, "A", "int16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 SoC", 37612, 1, 1, "%", "uint16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 SOH", 37624, 1, 1, "%", "uint16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 Remain Energy", 37632, 1, 0.1, "Wh", "uint16", None, SensorDeviceClass.ENERGY, True),
    ("BMS1 FCC Capacity", 37633, 1, 0.1, "Ah", "uint16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 Design Capacity", 37635, 1, 0.1, "Wh", "uint16", None, SensorDeviceClass.BATTERY, True),
    ("BMS1 Force to Change battery Flag", 37636, 1, 1, "", "uint16", None, SensorDeviceClass.BATTERY, True),

    # Meter1/CT1 Werte → energy device_class
    ("Meter1 Connected", 38801, 1, 1, "", "uint16", None, SensorDeviceClass.ENERGY, True),
    ("Meter1 R Phase Voltage", 38802, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, True),
    ("Meter1 S Phase Voltage", 38804, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, True),
    ("Meter1 T Phase Voltage", 38808, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, True),
    ("Meter1 R Phase Current", 38808, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, True),
    ("Meter1 S Phase Current", 38810, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, True),
    ("Meter1 T Phase Current", 38812, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, True),
    ("Meter1 Combined Active Power", 38814, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 R Phase Active Power", 38816, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 S Phase Active Power", 38818, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 T Phase Active Power", 38820, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 Combined Reactive Power", 38822, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 R Phase Reactive Power", 38824, 2, 0.1, "Var", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 S Phase Reactive Power", 38826, 2, 0.1, "Var", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 T Phase Reactive Power", 38828, 2, 0.1, "Var", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 Combined Apparent Power", 38830, 2, 0.1, "VA", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 R Phase Apparent Power", 38832, 2, 0.1, "VA", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 S Phase Apparent Power", 38834, 2, 0.1, "VA", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 T Phase Apparent Power", 38836, 2, 0.1, "VA", "int32", None, SensorDeviceClass.POWER, True),
    ("Meter1 Combined Power Factor", 38838, 2, 0.001, "", "int32", None, SensorDeviceClass.POWER_FACTOR, True),
    ("Meter1 R Phase Power Factor", 38840, 2, 0.001, "", "int32", None, SensorDeviceClass.POWER_FACTOR, True),
    ("Meter1 S Phase Power Factor", 38842, 2, 0.001, "", "int32", None, SensorDeviceClass.POWER_FACTOR, True),
    ("Meter1 T Phase Power Factor", 38844, 2, 0.001, "", "int32", None, SensorDeviceClass.POWER_FACTOR, True),
    ("Meter1 Frequency", 38846, 2, 0.01, "Hz", "int32", None, SensorDeviceClass.FREQUENCY, True),

    #Protucol Version
    ("Protocol Version", 39000, 2, 1, "", "uint32", None, None, True),

    #INFO-Werte
    ("Model name", 39002, 16, 1, "", "str", None, None, True),
    ("SN", 39018, 16, 1, "", "str", None, None, True),
    ("PN", 39034, 16, 1, "", "str", None, None, True),
    ("Model ID", 39050, 1, 1, "", "uint16", None, None, True),
    ("Number of strings", 39051, 1, 1, "", "uint16", None, None, True),
    ("Number of MPPT's", 39052, 1, 1, "V", "uint16", None, None, True),
    ("Rated Power (Pn)", 39053, 2, 0.001, "Kw", "int32", None, SensorDeviceClass.POWER, True),
    ("Maximum active power (Pmax)", 39055, 2, 0.001, "Kw", "int32", None, SensorDeviceClass.POWER, True),
    ("Maximum apparent power (Smax)", 39057, 2, 0.001, "kVA", "int32", None, None, True),
    ("Maximum reactive power (Qmax, fed into the grid)", 39059, 2, 0.001, "kVar", "unt32", None, None, True),
    ("Maximum reactive power (Qmax, absorbed from the grid)", 39061, 2, 0.001, "kVar", "uint32", None, None, True),

    # PV- und Energie-Werte
    ("PV Power Total", 39601, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True),
    ("PV Power Today", 39603, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False),  # standardmäßig deaktiviert
    ("Total Charging Capacity", 39605, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True),
    ("Charging Capacity Today", 39607, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False),
    ("Total Discharge Power", 39609, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True),
    ("Discharge Power Today", 39611, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False),
    ("Total Feeder Network Power", 39613, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True),
    ("Feeder Power Today", 39615, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False),
    ("Total Power Taken", 39617, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True),
    ("Electricity Consumption Today", 39619, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False),

    # Normale Energie-Werte
    ("Output Total Power", 39621, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True),
    ("Output Power Today", 39623, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False),
    ("Enter Total Power", 39625, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True),
    ("Enter Power Today", 39627, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False),
    ("Total Load Power", 39629, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True),
    ("Load Power Today", 39631, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False),
]
