import logging
import asyncio
import re
from datetime import timedelta

import aiohttp
import async_timeout

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, BASE_URL, CITIES, FORECAST_URL

_LOGGER = logging.getLogger(__name__)

# Интервал обновления данных — раз в 5 минут
SCAN_INTERVAL = timedelta(minutes=5)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Настройка платформы сенсоров."""
    city_key = config_entry.data["city"]
    
    sensors = [
        MagneticStormSensor(city_key, "today", 0),
        MagneticStormSensor(city_key, "forecast_today", 2),
        MagneticStormSensor(city_key, "forecast_tomorrow", 1),
        MagneticStormSensor(city_key, "forecast_after_tomorrow", 0),
    ]
    
    async_add_entities(sensors, update_before_add=True)

class MagneticStormSensor(SensorEntity):
    """Сущность для отображения геомагнитной активности."""

    def __init__(self, city_key, sensor_type, data_index):
        """Инициализация сенсора с привязкой к городу и типу данных."""
        self._city_key = city_key
        self._type = sensor_type
        self._data_index = data_index
        self._state = None
        self._attrs = {}

    @property
    def name(self):
        """Человекочитаемое название сенсора."""
        city_name = CITIES.get(self._city_key, 'Unknown')
        return f"Magnetic Storm {city_name} {self._type}"

    @property
    def state(self):
        """Возвращает текущее значение Kp-индекса (состояние)."""
        if self._state is None:
            return None
        try:
            value = float(self._state)
            # Валидный диапазон Kp-индекса от 0 до 9
            if 0 <= value <= 9:
                return value
            return self._state
        except (ValueError, TypeError):
            return self._state

    @property
    def native_unit_of_measurement(self):
        """Техническая единица измерения."""
        return "Kp"

    @property
    def state_class(self):
        """Класс измерения для корректной записи в долгосрочную статистику."""
        return "measurement"

    @property
    def icon(self):
        """Динамическая иконка, отражающая уровень угрозы."""
        if self._state is None:
            return "mdi:earth"
        try:
            kp = float(self._state)
            if kp < 4: return "mdi:earth"
            elif 4 <= kp <= 5: return "mdi:weather-cloudy-alert"
            elif 5 < kp <= 7: return "mdi:weather-lightning"
            else: return "mdi:shield-alert"
        except (ValueError, TypeError):
            return "mdi:earth"

    @property
    def unique_id(self):
        """Уникальный ID для интеграции в реестр Home Assistant."""
        return f"magnetic_storm_{self._city_key}_{self._type}"

    @property
    def extra_state_attributes(self):
        """Дополнительные атрибуты (почасовые данные, индексы)."""
        return self._attrs

    def _clean_value(self, val):
        """
        Удаляет любые лишние символы (минусы, тире, спецсимволы).
        Оставляет только цифры и десятичную точку.
        """
        if val is None or str(val).lower() == "null":
            return None
        
        # Регулярное выражение: удаляем всё, кроме цифр и точки
        cleaned = re.sub(r'[^0-9.]', '', str(val))
        
        if not cleaned:
            return None

        try:
            # Если есть точка, возвращаем float, иначе int
            return float(cleaned) if '.' in cleaned else int(cleaned)
        except ValueError:
            return cleaned

    async def async_update(self):
        """Запрос данных из API и обновление состояния сущности."""
        is_forecast = self._type.startswith("forecast_")
        url = FORECAST_URL.format(city_key=self._city_key) if is_forecast else BASE_URL.format(city_key=self._city_key)
        
        # Получаем сессию через HA, чтобы не плодить лишние подключения
        session = async_get_clientsession(self.hass)

        try:
            async with async_timeout.timeout(10):
                response = await session.get(url)
                data = await response.json()

            # Проверка наличия данных в ответе
            if not isinstance(data, dict) or "data" not in data or len(data["data"]) <= self._data_index:
                _LOGGER.warning("Данные для %s недоступны в ответе API", self.name)
                return

            sensor_data = data["data"][self._data_index]
            new_state_candidate = None

            # Логика определения основного значения сенсора
            if self._type == "today":
                # Берем последнее доступное измерение за сегодня
                for hour in reversed(range(24)):
                    key = f"h{hour:02d}"
                    val = sensor_data.get(key, "null")
                    if val != "null":
                        new_state_candidate = self._clean_value(val)
                        break
            else:
                # Берем максимальный индекс для прогнозных дат
                new_state_candidate = self._clean_value(sensor_data.get("max_kp"))

            # Обновляем состояние, только если данные валидны (не сбрасываем в Unknown)
            if new_state_candidate is not None:
                self._state = new_state_candidate

            # Обработка почасовой статистики в атрибутах
            hourly_attrs = {}
            for hour in range(24):
                key = f"h{hour:02d}"
                if key in sensor_data:
                    val = sensor_data[key]
                    if val != "null":
                        cleaned_val = self._clean_value(val)
                        if cleaned_val is not None:
                            hourly_attrs[key] = cleaned_val

            # Сборка общих атрибутов
            new_attrs = {
                "time": sensor_data.get("time", "Unknown"),
                "f10": self._clean_value(sensor_data.get("f10")),
                "ap": self._clean_value(sensor_data.get("ap")),
                **hourly_attrs
            }

            # Добавление специфичных для типа данных полей
            if is_forecast:
                for p in ["p4", "p5", "p6", "p7"]:
                    val = self._clean_value(sensor_data.get(p))
                    if val is not None:
                        new_attrs[p] = val
            else:
                new_attrs["sn"] = self._clean_value(sensor_data.get("sn"))

            self._attrs = new_attrs

        except Exception as e:
            # В случае ошибки логируем ее и оставляем старые данные
            _LOGGER.error("Ошибка при обновлении %s: %s", self.name, e)