"""
Based on Demo platform: a platform that returns all data from dutch 'smart meters', returning power and gas consumtion.

Devices inspired by: https://github.com/OrangeTux/carrot/blob/master/telegram.go
"""
import serial
import logging
import voluptuous as vol

REQUIREMENTS = ['smeterd==2.5.0']

from smeterd.meter import SmartMeter
from smeterd.meter import P1Packet
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (CONF_PORT)
from homeassistant.helpers.config_validation import PLATFORM_SCHEMA


CONF_BAUDRATE = 'Baud rate'

VOLUME_CUBIC_METRE = 'm3'
POWER_KILOWATT = 'kW'
ENERGY_KILOWATTHOUR = 'kWh'

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_PORT, default='/dev/ttyUSB0'): cv.string,
    vol.Optional(CONF_BAUDRATE, default=9600): cv.positive_int
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensors."""

    meter = TimedMeter(config)

    add_devices([
        SmartMeterSensor(meter, 'Equipment Id'                  ,'TODO:ID'      ,''), #0-0:96.1.1
		SmartMeterSensor(meter, 'Power used : low tariff'       ,0              ,ENERGY_KILOWATTHOUR), #1-0:1.8.1
		SmartMeterSensor(meter, 'Power used : normal tariff'    ,0              ,ENERGY_KILOWATTHOUR), #1-0:1.8.2
		SmartMeterSensor(meter, 'Power produced : low tariff'   ,0              ,ENERGY_KILOWATTHOUR), #1-0:2.8.1
		SmartMeterSensor(meter, 'Power produced : normal tariff',0              ,ENERGY_KILOWATTHOUR), #1-0:2.8.2
		SmartMeterSensor(meter, 'Current tariff'                ,'TODO:HIGH/LOW',''), #0-0:96.14.0
		SmartMeterSensor(meter, 'Current power usage'           ,0              ,POWER_KILOWATT), #1-0:1.7.0
		SmartMeterSensor(meter, 'Current power produced'        ,0              ,POWER_KILOWATT), #1-0:2.7.0
		SmartMeterSensor(meter, 'Gas used'                      ,0              ,VOLUME_CUBIC_METRE) #0-1:24.2.1
    ])

    return True

class TimedMeter(object):
    def getPacket(self):
        meter = SmartMeter(self._port,baudrate=self._baudrate)
        
        try:
            self.lastpacket = meter.pythonread_one_packet()
        except serial.SerialException as e:
            _LOGGER.error('Failed read packet: %s', str(ex))
            return False
        finally:
            meter.disconnect()
        return None

    def __init__(self, config, **kwargs):
        self._port = config.get(CONF_PORT)
        self._baudrate = config.get(CONF_BAUDRATE)

        return None

    @property
    def lastpacket(self):
        return self.lastpacket

class SmartMeterSensor(Entity):
    """Representation of a sensor on a dutch smart meter."""

    def __init__(self, meter, name, state, unit_of_measurement):
        """Initialize the sensor."""
        self._meter = meter
        self._name = name
        self._state = state
        self._unit_of_measurement = unit_of_measurement

    @property
    def should_poll(self):
        """TODO: figure out how to implement push"""
        return False

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor. (total/current power consumption/production or total gas used)"""
        return self._meter.lastpacket
        #return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return self._unit_of_measurement

    def update(self):
        return self._meter.getPacket()