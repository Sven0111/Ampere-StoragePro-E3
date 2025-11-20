from homeassistant.components.sensor import SensorDeviceClass

SENSOR_DEFINITIONS = [
    # ----------------- Table 3-1 Inverter model defenition table -----------------

    # ----------------- Table 3-2 Inverter version defenition table -----------------
    ("Master Version", 36001, 1, 1, "", "uint16", None, None, True, True), #4
    ("Slave Version", 36002, 1, 1, "", "uint16", None, None, True, True), #5
    ("Manager Version", 36003, 1, 1, "", "uint16", None, None, True, True), #6
    ("Meter1 SN", 36100, 16, 1, "", "str", None, None, True, True), #7
    ("Meter1 MFG ID", 36116, 16, 1, "", "str", None, None, True, True), #8
    ("Meter1 Type", 36132, 16, 1, "", "str", None, None, True, True), #9
    ("Meter1 Version", 36148, 1, 1, "", "str", None, None, True, True), #10
    ("Meter2 SN", 36200, 16, 1, "", "str", None, None, False, True), #11
    ("Meter2 MFG ID", 36216, 16, 1, "", "str", None, None, False, True), #12
    ("Meter2 Type", 36232, 16, 1, "", "str", None, None, False, True), #13
    ("Meter2 Version", 36248, 1, 1, "", "str", None, None, False, True), #14

    # ----------------- Table 3-3 Battery Version defenition table -----------------
    # ----------------- BMS1 -----------------
    ("BMS1 Connected", 37002, 1, 1, "", "uint16", None, None, True, True), #15
    ("BMS1 Master Version", 37003, 1, 1, "", "uint16", None, None, False, True), #16
    ("BMS1 ?", 37004, 1, 1, "", "uint16", None, None, False, True), #17
    ("BMS1 SN", 37005, 16, 1, "", "str", None, None, False, True), #18
    ("BMS1 ??", 37032, 1, 1, "", "uint16", None, None, False, True), #19
    ("BMS1 Slave 1 version", 37033, 1, 1, "", "uint16", None, None, False, True), #20
    ("BMS1 Slave 2 version", 37034, 1, 1, "", "uint16", None, None, False, True), #21
    ("BMS1 Slave 1 SN", 37097, 16, 1, "", "str", None, None, False, True), #22
    ("BMS1 Slave 2 SN", 37113, 16, 1, "", "str", None, None, False, True), #23
    ("BMS1 Voltage", 37609, 1, 0.1, "V", "uint16", None, SensorDeviceClass.VOLTAGE, True, True),#24
    ("BMS1 Current", 37610, 1, 0.1, "A", "int16", None, SensorDeviceClass.CURRENT, True, True),#25
    ("BMS1 Ambient Temperature", 37611, 1, 0.1, "°C", "int16", None, SensorDeviceClass.TEMPERATURE, True, True), #26
    ("BMS1 SoC", 37612, 1, 1, "%", "uint16", None, SensorDeviceClass.BATTERY, True, True), #27
    ("BMS1 MAX Temperature", 37617, 1, 0.1, "°C", "int16", None, SensorDeviceClass.TEMPERATURE, False, True), #28
    ("BMS1 MIN Temperature", 37618, 1, 0.1, "°C", "int16", None, SensorDeviceClass.TEMPERATURE, False, True), #29
    ("BMS1 MAX Cell Voltage", 37619, 1, 1, "mV", "uint16", None, SensorDeviceClass.VOLTAGE, False, True),#30
    ("BMS1 MIN Cell Voltage", 37620, 1, 1, "mV", "uint16", None, SensorDeviceClass.VOLTAGE, False, True),#31
    ("BMS1 SOH", 37624, 1, 1, "%", "uint16", None, SensorDeviceClass.BATTERY, True, True), #32
    ("BMS1 Fault1", 37626, 1, 1, "", "bit16", None, None, False, True), #33
    ("BMS1 Fault2", 37627, 1, 1, "", "bit16", None, None, False, True), #34
    ("BMS1 Fault3", 37628, 1, 1, "", "bit16", None, None, False, True), #35
    ("BMS1 Fault4", 37629, 1, 1, "", "bit16", None, None, False, True), #36
    ("BMS1 Fault5", 37630, 1, 1, "", "bit16", None, None, False, True), #37
    ("BMS1 Fault6", 37631, 1, 1, "", "bit16", None, None, False, True), #38
    ("BMS1 Remain Energy", 37632, 1, 0.1, "Wh", "uint16", None, SensorDeviceClass.ENERGY, True, True), #39
    ("BMS1 FCC Capacity", 37633, 1, 0.1, "Ah", "uint16", None, None, True, True), #40
    ("BMS1 reserve", 37634, 1, 1, "", "uint16", None, None, False, False), #41
    ("BMS1 Design Energy", 37635, 1, 0.1, "Wh", "uint16", None, SensorDeviceClass.ENERGY, True, True), #42
    ("BMS1 Force to Change battery Flag", 37636, 1, 1, "", "uint16", None, None, False, True), #43
    # ----------------- BMS2 -----------------
    ("BMS2 Connected", 37700, 1, 1, "", "uint16", None, None, True, True), #44
    ("BMS2 Master Version", 37701, 1, 1, "", "uint16", None, None, False, True), #45
    ("BMS2 ?", 37702, 1, 1, "", "uint16", None, None, False, True), #46
    ("BMS2 SN", 37703, 16, 1, "", "str", None, None, False, True), #47
    ("BMS2 ??", 37730, 1, 1, "", "uint16", None, None, False, True), #48
    ("BMS2 Slave 1 version", 37731, 1, 1, "", "uint16", None, None, False, True), #49
    ("BMS2 Slave 2 version", 37732, 1, 1, "", "uint16", None, None, False, True), #50
    ("BMS2 Slave 1 SN", 37795, 16, 1, "", "str", None, None, False, True), #51
    ("BMS2 Slave 2 SN", 37811, 16, 1, "", "str", None, None, False, True), #52
    ("BMS2 Voltage", 38307, 1, 0.1, "V", "uint16", None, SensorDeviceClass.VOLTAGE, False, True),#53
    ("BMS2 Current", 38308, 1, 0.1, "A", "int16", None, SensorDeviceClass.CURRENT, False, True),#54
    ("BMS2 Ambient Temperature", 38309, 1, 0.1, "°C", "int16", None, SensorDeviceClass.TEMPERATURE, False, True), #55
    ("BMS2 SoC", 38310, 1, 1, "%", "uint16", None, SensorDeviceClass.BATTERY, False, True), #56
    ("BMS2 MAX Temperature", 38315, 1, 0.1, "°C", "int16", None, SensorDeviceClass.TEMPERATURE, False, True), #57
    ("BMS2 MIN Temperature", 38316, 1, 0.1, "°C", "int16", None, SensorDeviceClass.TEMPERATURE, False, True), #58
    ("BMS2 MAX Cell Voltage", 38317, 1, 1, "mV", "uint16", None, SensorDeviceClass.VOLTAGE, False, True),#59
    ("BMS2 MIN Cell Voltage", 38318, 1, 1, "mV", "uint16", None, SensorDeviceClass.VOLTAGE, False, True),#60
    ("BMS2 SOH", 38322, 1, 1, "%", "uint16", None, SensorDeviceClass.BATTERY, False, True), #61
    ("BMS2 Fault1", 38324, 1, 1, "", "bit16", None, None, False, True), #62
    ("BMS2 Fault2", 38325, 1, 1, "", "bit16", None, None, False, True), #63
    ("BMS2 Fault3", 38326, 1, 1, "", "bit16", None, None, False, True), #64
    ("BMS2 Fault4", 38327, 1, 1, "", "bit16", None, None, False, True), #65
    ("BMS2 Fault5", 38328, 1, 1, "", "bit16", None, None, False, True), #66
    ("BMS2 Fault6", 38329, 1, 1, "", "bit16", None, None, False, True), #67
    ("BMS2 Remain Energy", 38330, 1, 0.1, "Wh", "uint16", None, SensorDeviceClass.ENERGY, False, True), #68
    ("BMS2 FCC Capacity", 38331, 1, 0.1, "Ah", "uint16", None, None, False, True), #69
    ("BMS2 reserve", 38332, 1, 1, "", "uint16", None, None, False, False), #70
    ("BMS2 Design Energy", 38333, 1, 0.1, "Wh", "uint16", None, SensorDeviceClass.ENERGY, False, True), #71
    ("BMS2 Force to Change battery Flag", 38334, 1, 1, "", "uint16", None, None, False, True), #72

    # ----------------- Table 3-4 Register defenition table -----------------
    # ----------------- Meter1 -----------------
    ("Meter1 Connect State", 38801, 1, 1, "", "uint16", None, None, True, True), #73
    ("Meter1 R Phase Voltage", 38802, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, True, True), #74
    ("Meter1 S Phase Voltage", 38804, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, True, True), #75
    ("Meter1 T Phase Voltage", 38806, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, True, True), #76
    ("Meter1 R Phase Current", 38808, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, True, True), #77
    ("Meter1 S Phase Current", 38810, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, True, True), #78
    ("Meter1 T Phase Current", 38812, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, True, True), #79
    ("Meter1 Combined Active Power", 38814, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True, True), #80
    ("Meter1 R Phase Active Power", 38816, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True, True), #81
    ("Meter1 S Phase Active Power", 38818, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True, True), #82
    ("Meter1 T Phase Active Power", 38820, 2, 0.1, "W", "int32", None, SensorDeviceClass.POWER, True, True), #83
    ("Meter1 Combined Reactive Power", 38822, 2, 0.1, "Var", "int32", None, None, True, True), #84
    ("Meter1 R Phase Reactive Power", 38824, 2, 0.1, "Var", "int32", None, None, True, True), #85
    ("Meter1 S Phase Reactive Power", 38826, 2, 0.1, "Var", "int32", None, None, True, True), #86
    ("Meter1 T Phase Reactive Power", 38828, 2, 0.1, "Var", "int32", None, None, True, True), #87
    ("Meter1 Combined Apparent Power", 38830, 2, 0.1, "VA", "int32", None, None, True, True), #88
    ("Meter1 R Phase Apparent Power", 38832, 2, 0.1, "VA", "int32", None, None, True, True), #89
    ("Meter1 S Phase Apparent Power", 38834, 2, 0.1, "VA", "int32", None, None, True, True), #90
    ("Meter1 T Phase Apparent Power", 38836, 2, 0.1, "VA", "int32", None, None, True, True), #91
    ("Meter1 Combined Power Factor", 38838, 2, 0.001, "", "int32", None, None, True, True), #92
    ("Meter1 R Phase Power Factor", 38840, 2, 0.001, "", "int32", None, None, True, True), #93
    ("Meter1 S Phase Power Factor", 38842, 2, 0.001, "", "int32", None, None, True, True), #94
    ("Meter1 T Phase Power Factor", 38844, 2, 0.001, "", "int32", None, None, True, True), #95
    ("Meter1 Frequency", 38846, 2, 0.01, "Hz", "int32", None, SensorDeviceClass.FREQUENCY, True, True), #96
    # ----------------- Meter2 -----------------
    ("Meter2 Connect State", 38901, 1, 1, "", "", None, None, True, True), #97
    ("Meter2 R Phase Voltage", 38902, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, False, True), #98
    ("Meter2 S Phase Voltage", 38904, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, False, True), #99
    ("Meter2 T Phase Voltage", 38906, 2, 0.1, "V", "int32", None, SensorDeviceClass.VOLTAGE, False, True), #100
    ("Meter2 R Phase Current", 38908, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #101
    ("Meter2 S Phase Current", 38910, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #102
    ("Meter2 T Phase Current", 38912, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #103
    ("Meter2 Combined Active Power", 38914, 2, 0.1, "W", "int32", None, None, False, True), #104
    ("Meter2 R Phase Active Power", 38916, 2, 0.1, "W", "int32", None, None, False, True), #105
    ("Meter2 S Phase Active Power", 38918, 2, 0.1, "W", "int32", None, None, False, True), #106
    ("Meter2 T Phase Active Power", 38920, 2, 0.1, "W", "int32", None, None, False, True), #107
    ("Meter2 Combined Reactive Power", 38922, 2, 0.1, "Var", "int32", None, None, False, True), #108
    ("Meter2 R Phase Reactive Power", 38924, 2, 0.1, "Var", "int32", None, None, False, True), #109
    ("Meter2 S Phase Reactive Power", 38926, 2, 0.1, "Var", "int32", None, None, False, True), #110
    ("Meter2 T Phase Reactive Power", 38928, 2, 0.1, "Var", "int32", None, None, False, True), #111
    ("Meter2 Combined Apparent Power", 38930, 2, 0.1, "VA", "int32", None, None, False, True), #112
    ("Meter2 R Phase Apparent Power", 38932, 2, 0.1, "VA", "int32", None, None, False, True), #113
    ("Meter2 S Phase Apparent Power", 38934, 2, 0.1, "VA", "int32", None, None, False, True), #114
    ("Meter2 T Phase Apparent Power", 38936, 2, 0.1, "VA", "int32", None, None, False, True), #115
    ("Meter2 Combined Power Factor", 38938, 2, 0.001, "", "int32", None, None, False, True), #116
    ("Meter2 R Phase Power Factor", 38940, 2, 0.001, "", "int32", None, None, False, True), #117
    ("Meter2 S Phase Power Factor", 38942, 2, 0.001, "", "int32", None, None, False, True), #118
    ("Meter2 T Phase Power Factor", 38944, 2, 0.001, "", "int32", None, None, False, True), #119
    ("Meter2 Frequency", 38946, 2, 0.01, "Hz", "int32", None, SensorDeviceClass.FREQUENCY, False, True), #120
    # ----------------- Protocol -----------------
    ("Protocol Version", 39000, 2, 1, "", "uint32", None, None, True, True), #121
    # ----------------- INFO -----------------
    ("Model name", 39002, 16, 1, "", "str", None, None, True, True), #122
    ("SN", 39018, 16, 1, "", "str", None, None, True, True), #123
    ("PN", 39034, 16, 1, "", "str", None, None, True, True),  #124
    ("Model ID", 39050, 1, 1, "", "uint16", None, None, True, True), #125
    ("Number of strings", 39051, 1, 1, "", "uint16", None, None, True, True), #126
    ("Number of MPPT's", 39052, 1, 1, "", "uint16", None, None, True, True), #127
    # ----------------- Leistungswerte -----------------
    ("Rated Power (Pn)", 39053, 2, 0.001, "kW", "int32", None, SensorDeviceClass.POWER, True, True), #128
    ("Maximum active power (Pmax)", 39055, 2, 0.001, "kW", "int32", None, SensorDeviceClass.POWER, True, True), #129
    ("Maximum apparent power (Smax)", 39057, 2, 0.001, "kVA", "int32", None, None, True, True), #130
    ("Maximum reactive power (Qmax, fed into the grid)", 39059, 2, 0.001, "kVar", "uint32", None, None, True, True), #131
    ("Maximum reactive power (Qmax, absorbed from the grid)", 39061, 2, 0.001, "kVar", "uint32", None, None, True, True), #132
    ("Status 1", 39063, 1, 1, "", "bit6", None, None, False, True), #133 bit0: Standby, bit1: reserved, bit2: Operation, bit3: reserved, bit4: reserved, bit5: reserved, bit6: Fault, bit7: reserved
    #("Status 2 reserved", 39064, 1, 1, "", "bit6", None, None, False), #134
    ("Status 3", 39065, 1, 1, "", "bit6", None, None, False, True), #135 0: Not off-grid, 1: Off-grid
    ("Alarm 1", 39067, 1, 1, "", "bit6", None, None, False, True), #136 # see list of alarms
    ("Alarm 2", 39068, 1, 1, "", "bit6", None, None, False, True), #137 # see list of alarms
    ("Alarm 3", 39069, 1, 1, "", "bit6", None, None, False, True), #138 # see list of alarms
    # ----------------- PV Eingänge -----------------
    ("PV1 Voltage", 39070, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #139
    ("PV1 Current", 39071, 1, 0.01, "A", "int16", None, SensorDeviceClass.CURRENT, False, True), #140
    ("PV2 Voltage", 39072, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #141
    ("PV2 Current", 39073, 1, 0.01, "A", "int16", None, SensorDeviceClass.CURRENT, False, True), #142
    ("PV3 Voltage", 39074, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #143
    ("PV3 Current", 39075, 1, 0.01, "A", "int16", None, SensorDeviceClass.CURRENT, False, True), #144
    ("PV4 Voltage", 39076, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #145
    ("PV4 Current", 39077, 1, 0.01, "A", "int16", None, SensorDeviceClass.CURRENT, False, True), #146
    ("Total PV input Power", 39118, 2, 0.001, "kW", "int32", None, SensorDeviceClass.POWER, True, True), #147
    ("reserve", 39120, 1, 1, "", "", None, None, False, False), #148
    ("reserve", 39121, 1, 1, "", "", None, None, False, False), #149
    ("reserve", 39122, 1, 1, "", "", None, None, False, False), #150
    ("Grid R Phase Voltage", 39123, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #151
    ("Grid S Phase Voltage", 39124, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #152
    ("Grid T Phase Voltage", 39125, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #153
    ("Inverter R Phase Current", 39126, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #154
    ("Inverter S Phase Current", 39128, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #155
    ("Inverter T Phase Current", 39130, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #156
    ("reserve", 39132, 1, 1, "", "uint32", None, None, False, False), #157
    ("Active Power", 39134, 2, 0.001, "kW", "int32", None, SensorDeviceClass.POWER, False, True), #158
    ("Reactive Power", 39136, 2, 0.001, "kVar", "int32", None, SensorDeviceClass.POWER, False, True), #159
    ("Power Factor", 39138, 1, 0.001, "", "int16", None, None, False, True), #160
    ("Grid Frequency", 39139, 1, 0.1, "Hz", "int16", None, SensorDeviceClass.FREQUENCY, False, True), #161
    ("reserve", 39140, 1, 1, "", "", None, None, False, False), #162
    ("Internal Temperature", 39141, 1, 1, "°C", "int16", None, SensorDeviceClass.TEMPERATURE, False, True), #163
    ("reserve", 39142, 1, 1, "", "uint16", None, None, False, False), #164
    ("reserve", 39143, 1, 1, "", "uint16", None, None, False, False), #165
    ("reserve", 39144, 1, 1, "", "uint16", None, None, False, False), #166
    ("reserve", 39145, 2, 1, "", "uint32", None, None, False, False), #167
    ("reserve", 39147, 2, 1, "", "uint32", None, None, False, False), #168
    ("Cumulative Power Generation", 39149, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #169
    ("Power Generation Today", 39151, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #170
    ("reserve", 39153, 1, 1, "", "uint16", None, None, False, False), #171
    ("reserve", 39154, 2, 1, "", "uint32", None, None, False, False), #172
    ("reserve", 39156, 1, 1, "", "uint16", None, None, False, False), #173
    ("reserve", 39157, 1, 1, "", "uint16", None, None, False, False), #174
    ("reserve", 39158, 2, 1, "", "uint32", None, None, False, False), #175
    ("reserve", 39160, 1, 1, "", "uint16", None, None, False, False), #176
    ("reserve", 39161, 1, 1, "", "uint16", None, None, False, False), #177
    ("[Energy Storage module 1] Charge/Discharge Power", 39162, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #178
    ("reserve", 39164, 2, 1, "", "uint32", None, None, False, False), #179
    ("reserve", 39166, 2, 1, "", "uint32", None, None, False, False), #180
    ("[Meter collection] Active Power", 39168, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #181
    ("reserve", 39170, 1, 1, "", "uint16", None, None, False, False), #182
    ("reserve", 39171, 1, 1, "", "uint16", None, None, False, False), #183
    ("reserve", 39172, 1, 1, "", "uint16", None, None, False, False), #184
    ("reserve", 39200, 1, 1, "", "uint16", None, None, False, False), #185
    ("EPS R Phase Voltage", 39201, 1, 0.1, "V", "uint16", None, SensorDeviceClass.VOLTAGE, False, True), #186
    ("EPS S Phase Voltage", 39202, 1, 0.1, "V", "uint16", None, SensorDeviceClass.VOLTAGE, False, True), #187
    ("EPS T Phase Voltage", 39203, 1, 0.1, "V", "uint16", None, SensorDeviceClass.VOLTAGE, False, True), #188
    ("EPS R Phase Current", 39204, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #189
    ("EPS S Phase Current", 39206, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #190
    ("EPS T Phase Current", 39208, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #191
    ("EPS R Phase Power", 39210, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #192
    ("EPS S Phase Power", 39212, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #193
    ("EPS T Phase Power", 39214, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #194
    ("ESP Combined Power", 39216, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #195
    ("EPS Frequency", 39218, 1, 0.1, "Hz", "int16", None, SensorDeviceClass.FREQUENCY, False, True), #196
    ("Load R Phase Power", 39219, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #197
    ("Load S Phase Power", 39221, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #198
    ("Load T Phase Power", 39223, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #199
    ("Load Combined Power", 39225, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #200
    ("Battery 1 Voltage_", 39227, 1, 0.1, "V", "uint16", None, SensorDeviceClass.VOLTAGE, False, True), #201
    ("Battery 1 Current_", 39228, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #202
    ("Battery Power_", 39230, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #203
    ("Battery 2 Voltage_", 39232, 1, 0.1, "V", "uint16", None, SensorDeviceClass.VOLTAGE, False, True), #204
    ("Battery 2 Current_", 39233, 2, 0.001, "A", "int32", None, SensorDeviceClass.CURRENT, False, True), #205
    ("Battery 2 Power_", 39235, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #206
    ("Battery Combined Power_", 39237, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #207
    ("reserve", 39239, 1, 1, "", "int16", None, None, False, False), #208
    ("reserve", 39240, 1, 1, "", "int16", None, None, False, False), #209
    ("reserve", 39241, 1, 1, "", "int16", None, None, False, False), #210
    ("reserve", 39242, 2, 1, "", "int32", None, None, False, False), #211
    ("reserve", 39244, 2, 1, "", "int32", None, None, False, False), #212
    ("reserve", 39246, 2, 1, "", "int32", None, None, False, False), #213
    ("INV R Phase Active Power", 39248, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #214
    ("INV S Phase Active Power", 39250, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #215
    ("INV T Phase Active Power", 39252, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #216
    ("reserve", 39254, 2, 1, "", "int32", None, None, False, False), #217
    ("INV R Phase Reactive Power", 39256, 2, 1, "Var", "int32", None, None, False, True), #218
    ("INV S Phase Reactive Power", 39258, 2, 1, "Var", "int32", None, None, False, True), #219
    ("INV T Phase Reactive Power", 39260, 2, 1, "Var", "int32", None, None, False, True), #220
    ("reserve", 39262, 2, 1, "", "int32", None, None, False, False), #221
    ("INV R Phase A Transparent Power", 39264, 2, 1, "VA", "int32", None, None, False, True), #222
    ("INV S Phase A Transparent Power", 39266, 2, 1, "VA", "int32", None, None, False, True), #222
    ("INV T Phase A Transparent Power", 39268, 2, 1, "VA", "int32", None, None, False, True), #224
    ("INV Combined A Parent Power", 39270, 2, 1, "VA", "int32", None, None, False, True), #225
    ("INV Frequency R", 39272, 1, 0.1, "Hz", "int16", None, SensorDeviceClass.FREQUENCY, False, True), #226
    ("INV Frequency S", 39273, 1, 0.1, "Hz", "int16", None, SensorDeviceClass.FREQUENCY, False, True), #227
    ("INV Frequency T", 39274, 1, 0.1, "Hz", "int16", None, SensorDeviceClass.FREQUENCY, False, True), #228
    ("Available Import Power", 39275, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, True, True), #229
    ("Available Export Power", 39277, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, True, True), #230
    ("PV 1 Power", 39279, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #231
    ("PV 2 Power", 39281, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #232
    ("PV 3 Power", 39283, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #233
    ("PV 4 Power", 39285, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #234
    ("MPPT 1 Voltage", 39327, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #235
    ("MPPT 1 Current", 39328, 1, 0.01, "A", "int16", None, SensorDeviceClass.CURRENT, False, True), #236
    ("MPPT 1 Power", 39329, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #237
    ("MPPT 2 Voltage", 39331, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #238
    ("MPPT 2 Current", 39332, 1, 0.01, "A", "int16", None, SensorDeviceClass.CURRENT, False, True), #239
    ("MPPT 2 Power", 39333, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #240
    ("MPPT 3 Voltage", 39335, 1, 0.1, "V", "int16", None, SensorDeviceClass.VOLTAGE, False, True), #241
    ("MPPT 3 Current", 39336, 1, 0.01, "A", "int16", None, SensorDeviceClass.CURRENT, False, True), #242
    ("MPPT 3 Power", 39337, 2, 1, "W", "int32", None, SensorDeviceClass.POWER, False, True), #243

    # ----------------- PV- und Energie-Werte -----------------
    ("reserve",39600, 1, 1, "", "uint16", None, None, False, False), #244
    ("PV Power Total", 39601, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True, True), #245
    ("PV Power Today", 39603, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #246
    ("Total Charging Capacity", 39605, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True, True), #247
    ("Charging Capacity Today", 39607, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #248
    ("Total Discharge Power", 39609, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True, True), #249
    ("Discharge Power Today", 39611, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #250
    ("Total Feeder Network Power", 39613, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True, True), #251
    ("Feeder Power Today", 39615, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #252
    ("Total Power Taken", 39617, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True, True), #253
    ("Electricity Consumption Today", 39619, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #254
    ("Output Total Power", 39621, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True, True), #255
    ("Output Power Today", 39623, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #256
    ("Enter Total Power", 39625, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True, True), #257
    ("Enter Power Today", 39627, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #258
    ("Total Load Power", 39629, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, True, True), #259
    ("Load Power Today", 39631, 2, 0.01, "kWh", "uint32", None, SensorDeviceClass.ENERGY, False, True), #260
]