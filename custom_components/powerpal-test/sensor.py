"""Sensor platform for powerpal."""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Final, cast, final

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
    StateType
)

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_ENERGY, POWER_KILO_WATT, DEVICE_CLASS_POWER, DEVICE_CLASS_MONETARY, CURRENCY_DOLLAR

from .const import NAME, DOMAIN, ICON, CONF_DEVICE_ID, ATTRIBUTION

async def async_setup_entry(hass, entry, async_add_devices):
    """Setup sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        PowerpalTotalConsumptionSensor(coordinator, entry),
        PowerpalLiveConsumptionSensor(coordinator, entry),
        PowerpalTotalCostSensor(coordinator, entry),
        PowerpalLastTimestampSensor(coordinator, entry),
        PowerpalTariffPeriodSensor(coordinator, entry),
    ]
    async_add_devices(entities)

class PowerpalSensor(CoordinatorEntity):
    """Powerpal Sensor class."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the native unit of measurement."""
        return None
    
    @property
    def device_class(self) -> str:
        """Return the device class."""
        return None
    
    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.config_entry.entry_id)},
            "name": NAME,
            "model": self.config_entry.data[CONF_DEVICE_ID],
            "manufacturer": NAME,
        }

    @property
    def extra_state_attributes(self):
        """Return the extra state attributes."""
        return {
            "attribution": ATTRIBUTION,
            "id": self.config_entry.data[CONF_DEVICE_ID],
            "integration": DOMAIN,
        }
    
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

class PowerpalTotalConsumptionSensor(PowerpalSensor, SensorEntity):
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Powerpal Total Consumption"

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"powerpal-total-{self.config_entry.entry_id}"

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return SensorStateClass.TOTAL_INCREASING
    
    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return self.coordinator.data.get("total_watt_hours") / 1000
    
    @property
    def device_class(self) -> str:
        """Return the device class."""
        return DEVICE_CLASS_ENERGY
    
    @property
    def native_unit_of_measurement(self) -> str:
        """Return the native unit of measurement."""
        return ENERGY_KILO_WATT_HOUR



class PowerpalLiveConsumptionSensor(PowerpalSensor, SensorEntity):
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Powerpal Live Consumption"

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"powerpal-live-{self.config_entry.entry_id}"
    
    @property
    def device_class(self) -> str:
        """Return the device class."""
        return SensorDeviceClass.POWER

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return (self.coordinator.data.get("last_reading_watt_hours") * 60) / 1000
    
    @property
    def native_unit_of_measurement(self) -> str:
        """Return the native unit of measurement."""
        return POWER_KILO_WATT

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:lightning-bolt-outline"
    
class PowerpalTotalCostSensor(PowerpalSensor, SensorEntity):
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Powerpal Total Cost"

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"powerpal-cost-{self.config_entry.entry_id}"

    @property
    def state_class(self) -> str:
        """Return the state class."""
        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return (self.coordinator.data.get("total_cost"))
            
    @property
    def device_class(self) -> str:
        """Return the device class."""
        return DEVICE_CLASS_MONETARY
    
    @property
    def native_unit_of_measurement(self) -> str:
        """Return the native unit of measurement."""
        return CURRENCY_DOLLAR
    
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:currency-usd"

class PowerpalTariffPeriodSensor(PowerpalSensor, SensorEntity):
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Powerpal Tariff Period"

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"powerpal-peak-{self.config_entry.entry_id}"
    
    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return (self.coordinator.data.get("is_peak"))
    
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:progress-clock"
    
class PowerpalLastTimestampSensor(PowerpalSensor, SensorEntity):
    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Powerpal Last Timestamp"

    @property
    def unique_id(self) -> str:
        """Return the unique id."""
        return f"powerpal-last-{self.config_entry.entry_id}"

    @property
    def native_value(self):
        """Return the native value of the sensor."""
        return (self.coordinator.data.get("last_reading_timestamp"))
    
    @property
    def icon(self):
        """Return the icon of the sensor."""
        return "mdi:clock-outline"

    @property
    def device_class(self) -> str:
        """Return the device class, if any."""
        return SensorDeviceClass.TIMESTAMP    
    
