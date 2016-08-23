"""
Based on Demo platform: a platform that returns all data from dutch 'smart meters', returning power and gas consumtion.

Inspired by: https://github.com/OrangeTux/carrot/blob/master/telegram.go
"""
from homeassistant.helpers.entity import Entity

VOLUME_CUBIC_METRE = 'm3'
POWER_KILOWATT     = 'kW'
ENERGY_KILOWATTHOUR= 'kWh'

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensors."""
    add_devices([
		DemoSensor('Equipment Id'                  ,'TODO:ID'      ,''                 ), """ 0-0:96.1.1  """
		DemoSensor('Power used : low tariff'       ,0              ,ENERGY_KILOWATTHOUR), """ 1-0:1.8.1   """
		DemoSensor('Power used : normal tariff'    ,0              ,ENERGY_KILOWATTHOUR), """ 1-0:1.8.2   """
		DemoSensor('Power produced : low tariff'   ,0              ,ENERGY_KILOWATTHOUR), """ 1-0:2.8.1   """
		DemoSensor('Power produced : normal tariff',0              ,ENERGY_KILOWATTHOUR), """ 1-0:2.8.2   """
		DemoSensor('Current tariff'                ,'TODO:HIGH/LOW',''                 ), """ 0-0:96.14.0 """
		DemoSensor('Current power usage'           ,0              ,POWER_KILOWATT     ), """ 1-0:1.7.0   """
		DemoSensor('Current power produced'        ,0              ,POWER_KILOWATT     ), """ 1-0:2.7.0   """
		DemoSensor('Gas used'                      ,0              ,VOLUME_CUBIC_METRE ), """ 0-1:24.2.1  """
    ])


class SmartMeterSensor(Entity):
    """Representation of a sensor on a dutch smart meter."""

    def __init__(self, name, state, unit_of_measurement):
        """Initialize the sensor."""
        self._name = name
        self._state = state
        self._unit_of_measurement = unit_of_measurement

    @property
    def should_poll(self):
        """TODO: figure out how to implement polling"""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor. (total/current power consumption/production or total gas used)"""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return self._unit_of_measurement
