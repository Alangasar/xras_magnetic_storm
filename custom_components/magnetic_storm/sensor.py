import logging
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, BASE_URL, CITIES
import aiohttp

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)  # Интервал обновления данных (5 минут)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    city_key = config_entry.data["city"]
    sensors = [
        MagneticStormSensor(city_key, "today", 0),
        MagneticStormSensor(city_key, "yesterday", 1),
        MagneticStormSensor(city_key, "before_yesterday", 2)
    ]
    async_add_entities(sensors, update_before_add=True)  # Обновляем данные перед добавлением

class MagneticStormSensor(SensorEntity):
    def __init__(self, city_key, sensor_type, data_index):
        self._city_key = city_key
        self._type = sensor_type
        self._data_index = data_index
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        return f"Magnetic Storm {CITIES.get(self._city_key, 'Unknown')} {self._type}"

    @property
    def state(self):
        try:
            value = float(self._state) if self._state is not None else None
            if value is not None and 0 <= value <= 9:
                return value
            return None  # Если значение вне диапазона, сбрасываем его
        except ValueError:
            return None

    @property
    def native_unit_of_measurement(self):
        return "Kp"

    @property
    def device_class(self):
        return None  # Нет подходящего класса

    @property
    def state_class(self):
        return "measurement"

    @property
    def unique_id(self):
        return f"magnetic_storm_{self._city_key}_{self._type}"

    @property
    def extra_state_attributes(self):
        return self._attrs

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            url = BASE_URL.format(city_key=self._city_key)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    data = await response.json()

                    # Проверка наличия данных
                    if "data" not in data or len(data["data"]) <= self._data_index:
                        self._state = "No data"
                        self._attrs = {"error": "Data not available"}
                        return

                    # Получение данных для текущего сенсора
                    sensor_data = data["data"][self._data_index]

                    _LOGGER.info("Xras Ready!")
                    _LOGGER.info(self._type)
                    # Поиск последнего заполненного значения для сенсора "today"
                    if self._type == "today":
                        last_value = None
                        for key in ["h22", "h19", "h16", "h13", "h10", "h07", "h04", "h01", "h00"]:
                            value = sensor_data.get(key, "null")
                            if value != "null":
                                last_value = value.lstrip("-")  # Удаляем минус, если он есть
                                break

                        # Если найдено значение, используем его
                        if last_value:
                            self._state = last_value
                        else:
                            # Иначе используем значение по умолчанию
                            self._state = None
                    else:
                        # Для других сенсоров используем max_kp
                        self._state = sensor_data.get("max_kp", None)

                    # Добавление атрибутов
                    self._attrs = {
                        "time": sensor_data.get("time", "Unknown"),
                        "f10": sensor_data.get("f10", "Unknown"),
                        "sn": sensor_data.get("sn", "Unknown"),
                        "ap": sensor_data.get("ap", "Unknown"),
                        "h00": sensor_data.get("h00", "Unknown"),
                        "h01": sensor_data.get("h01", "Unknown"),
                        "h04": sensor_data.get("h04", "Unknown"),
                        "h07": sensor_data.get("h07", "Unknown"),
                        "h10": sensor_data.get("h10", "Unknown"),
                        "h13": sensor_data.get("h13", "Unknown"),
                        "h16": sensor_data.get("h16", "Unknown"),
                        "h19": sensor_data.get("h19", "Unknown"),
                        "h22": sensor_data.get("h22", "Unknown")
                    }

        except Exception as e:
            _LOGGER.error(f"Error updating sensor: {e}")
            self._state = None
            self._attrs = {"error": str(e)}