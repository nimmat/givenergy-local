"""Home Assistant sensor descriptions."""
from __future__ import annotations

from enum import Enum

from homeassistant.components.sensor import (
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_FREQUENCY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    ELECTRIC_POTENTIAL_VOLT,
    ENERGY_KILO_WATT_HOUR,
    FREQUENCY_HERTZ,
    POWER_WATT,
    TEMP_CELSIUS,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import GivEnergyUpdateCoordinator
from .const import DOMAIN
from .entity import GivEnergyEntity


class Icon(str, Enum):
    """Icon styles."""

    PV = "mdi:solar-power"
    AC = "mdi:power-plug-outline"
    Battery = "mdi:battery-high"
    Inverter = "mdi:flash"
    GridImport = "mdi:transmission-tower-export"
    GridExport = "mdi:transmission-tower-import"
    Temperature = "mdi:thermometer"


_BASIC_SENSORS = [
    SensorEntityDescription(
        key="e_pv_total",
        name="PV Energy Total",
        icon=Icon.PV,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="e_grid_in_day",
        name="Grid Import Today",
        icon=Icon.GridImport,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="e_grid_out_day",
        name="Grid Export Today",
        icon=Icon.GridExport,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="e_inverter_out_day",
        name="Inverter Output Today",
        icon=Icon.Inverter,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="e_inverter_out_total",
        name="Inverter Output Total",
        icon=Icon.Inverter,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
        native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
    ),
    SensorEntityDescription(
        key="p_load_demand",
        name="Consumption Power",
        icon=Icon.AC,
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=POWER_WATT,
    ),
    SensorEntityDescription(
        key="p_grid_out",
        name="Grid Export Power",
        icon=Icon.GridExport,
        device_class=DEVICE_CLASS_POWER,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=POWER_WATT,
    ),
    SensorEntityDescription(
        key="v_ac1",
        name="AC Voltage",
        icon=Icon.AC,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=ELECTRIC_POTENTIAL_VOLT,
    ),
    SensorEntityDescription(
        key="f_ac1",
        name="AC Frequency",
        icon=Icon.AC,
        device_class=DEVICE_CLASS_FREQUENCY,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=FREQUENCY_HERTZ,
    ),
    SensorEntityDescription(
        key="temp_inverter_heatsink",
        name="Heatsink Temperature",
        icon=Icon.Temperature,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
    SensorEntityDescription(
        key="temp_charger",
        name="Charger Temperature",
        icon=Icon.Temperature,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
        native_unit_of_measurement=TEMP_CELSIUS,
    ),
]

_PV_ENERGY_TODAY_SENSOR = SensorEntityDescription(
    key="e_pv_day",
    name="PV Energy Today",
    icon=Icon.PV,
    device_class=DEVICE_CLASS_ENERGY,
    state_class=STATE_CLASS_TOTAL_INCREASING,
    native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
)

_PV_POWER_SENSOR = SensorEntityDescription(
    key="p_pv",
    name="PV Power",
    icon=Icon.PV,
    device_class=DEVICE_CLASS_POWER,
    state_class=STATE_CLASS_MEASUREMENT,
    native_unit_of_measurement=POWER_WATT,
)

_CONSUMPTION_TODAY_SENSOR = SensorEntityDescription(
    key="e_consumption_today",
    name="Consumption Today",
    icon=Icon.AC,
    device_class=DEVICE_CLASS_ENERGY,
    state_class=STATE_CLASS_TOTAL_INCREASING,
    native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
)

_CONSUMPTION_TOTAL_SENSOR = SensorEntityDescription(
    key="e_consumption_consumption",
    name="Consumption Total",
    icon=Icon.AC,
    device_class=DEVICE_CLASS_ENERGY,
    state_class=STATE_CLASS_TOTAL_INCREASING,
    native_unit_of_measurement=ENERGY_KILO_WATT_HOUR,
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add sensors for passed config_entry in HA."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    # Add basic sensors that map directly to registers.
    async_add_entities(
        InverterBasicSensor(coordinator, config_entry, entity_description)
        for entity_description in _BASIC_SENSORS
    )

    # Add other sensors that require more customization
    # (e.g. sensors that derive values from several registers).
    async_add_entities(
        [
            PVEnergyTodaySensor(
                coordinator, config_entry, entity_description=_PV_ENERGY_TODAY_SENSOR
            ),
            PVPowerSensor(
                coordinator, config_entry, entity_description=_PV_POWER_SENSOR
            ),
            ConsumptionTodaySensor(
                coordinator, config_entry, entity_description=_CONSUMPTION_TODAY_SENSOR
            ),
            ConsumptionTotalSensor(
                coordinator, config_entry, entity_description=_CONSUMPTION_TOTAL_SENSOR
            ),
        ]
    )


class InverterBasicSensor(GivEnergyEntity, SensorEntity):
    """A sensor that derives its value from the register values fetched from the inverter."""

    def __init__(
        self,
        coordinator: GivEnergyUpdateCoordinator,
        config_entry: ConfigEntry,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize a sensor based on an entity description."""
        super().__init__(coordinator, config_entry)
        self._attr_unique_id = f"{self.coordinator.data.inverter.inverter_serial_number}_{entity_description.key}"
        self.entity_description = entity_description

    @property
    def native_value(self) -> StateType:
        """Return the register value as referenced by the 'key' property of the associated entity description."""
        return self.coordinator.data.inverter.dict().get(self.entity_description.key)


class PVEnergyTodaySensor(InverterBasicSensor):
    """Total PV Energy sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the sum of energy generated across both PV strings."""
        return (
            self.coordinator.data.inverter.e_pv1_day
            + self.coordinator.data.inverter.e_pv2_day
        )


class PVPowerSensor(InverterBasicSensor):
    """Total PV Power sensor."""

    @property
    def native_value(self) -> StateType:
        """Return the sum of power generated across both PV strings."""
        return (
            self.coordinator.data.inverter.p_pv1 + self.coordinator.data.inverter.p_pv2
        )


class ConsumptionTodaySensor(InverterBasicSensor):
    """Consumption Today sensor."""

    @property
    def native_value(self) -> StateType:
        """Calculate consumption based on the inverter output plus net grid import."""
        return (
            self.coordinator.data.inverter.e_inverter_out_day
            + self.coordinator.data.inverter.e_grid_in_day
            - self.coordinator.data.inverter.e_grid_out_day
        )


class ConsumptionTotalSensor(InverterBasicSensor):
    """Consumption Total sensor."""

    @property
    def native_value(self) -> StateType:
        """Calculate consumption based on the inverter output plus net grid import."""
        return (
            self.coordinator.data.inverter.e_inverter_out_total
            + self.coordinator.data.inverter.e_grid_in_total
            - self.coordinator.data.inverter.e_grid_out_total
        )