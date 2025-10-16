async def async_setup_entry(hass, entry, async_add_devices: AddEntitiesCallback):
    """Setup über UI (Config Flow)."""
    host = entry.data.get("host")
    port = entry.data.get("port")
    slave_id = entry.data.get("slave_id")

    # Gemeinsamer Modbus-Client für alle Sensoren
    device = ModbusDevice(host, port, slave_id)

    # Sensoren erstellen
    sensors = [
        ModbusSensor(device, "kWh Gesamt", 39607, count=2, scale=0.01, unit="kWh"),
    ]

    # HA die Sensoren registrieren
    async_add_devices(sensors)
    return True