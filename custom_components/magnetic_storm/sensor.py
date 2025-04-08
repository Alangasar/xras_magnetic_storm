import logging
from datetime import timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, BASE_URL, CITIES, FORECAST_URL
import aiohttp

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)  # Интервал обновления данных (5 минут)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the sensor platform."""
    city_key = config_entry.data["city"]
    sensors = [
        MagneticStormSensor(city_key, "today", 0),
        MagneticStormSensor(city_key, "yesterday", 1),
        MagneticStormSensor(city_key, "before_yesterday", 2),

        MagneticStormSensor(city_key, "forecast_today", 2),
        MagneticStormSensor(city_key, "forecast_tomorrow", 1),
        MagneticStormSensor(city_key, "forecast_after_tomorrow", 0),
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
    def icon(self):
        """Динамическая иконка в зависимости от уровня Kp-индекса."""
        if self._state is None:
            return "mdi:earth"
        try:
            kp = float(self._state)
            if kp < 3:
                return "mdi:earth"  # Спокойная геомагнитная обстановка
            elif 3 <= kp < 5:
                return "mdi:weather-cloudy-alert"  # Умеренная активность
            elif 5 <= kp < 7:
                return "mdi:weather-lightning"  # Геомагнитная буря
            else:
                return "mdi:shield-alert"  # Экстремальный шторм
        except ValueError:
            return "mdi:earth"

    @property
    def unique_id(self):
        return f"magnetic_storm_{self._city_key}_{self._type}"

    @property
    def extra_state_attributes(self):
        return self._attrs

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            is_forecast = self._type.startswith("forecast_")
            url = FORECAST_URL.format(city_key=self._city_key) if is_forecast else BASE_URL.format(city_key=self._city_key)

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    data = await response.json()

                    # Проверка наличия данных
                    if "data" not in data or len(data["data"]) <= self._data_index:
                        self._state = "No data"
                        self._attrs = {"error": "Data not available"}
                        return

                    sensor_data = data["data"][self._data_index]

                    _LOGGER.debug("Updating sensor: %s", self._type)

                    if self._type == "today":
                        # Поиск последнего заполненного значения для сенсора "today"
                        last_value = None
                        for key in ["h22", "h19", "h16", "h13", "h10", "h07", "h04", "h01", "h00"]:
                            value = sensor_data.get(key, "null")
                            if value != "null":
                                last_value = value.lstrip("-")
                                break

                        self._state = last_value if last_value else None
                    else:
                        # Для остальных сенсоров используем max_kp
                        self._state = sensor_data.get("max_kp", None)

                    # Формируем атрибуты
                    self._attrs = {
                        "time": sensor_data.get("time", "Unknown"),
                        "f10": sensor_data.get("f10", "Unknown"),
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

                    if is_forecast:
                        self._attrs.update({
                            "p4": sensor_data.get("p4", "Unknown"),
                            "p5": sensor_data.get("p5", "Unknown"),
                            "p6": sensor_data.get("p6", "Unknown"),
                            "p7": sensor_data.get("p7", "Unknown"),
                        })
                    else:
                        self._attrs["sn"] = sensor_data.get("sn", "Unknown")

        except Exception as e:
            _LOGGER.error(f"Error updating sensor: {e}")
            self._state = None
            self._attrs = {"error": str(e)}
