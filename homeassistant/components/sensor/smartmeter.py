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


CONF_BAUDRATE = 'baud_rate'

VOLUME_CUBIC_METRE = 'm³'
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
        SmartMeterSensor(meter, 'Equipment Id'                  ,'TODO:ID'      ,''                     ,'mdi:speedometer', lambda x: x['kwh']['eid']               ), #0-0:96.1.1
		SmartMeterSensor(meter, 'Power used : low tariff'       ,0              ,ENERGY_KILOWATTHOUR    ,'mdi:speedometer', lambda x: x['kwh']['low']['consumed']   ), #1-0:1.8.1
		SmartMeterSensor(meter, 'Power used : normal tariff'    ,0              ,ENERGY_KILOWATTHOUR    ,'mdi:speedometer', lambda x: x['kwh']['high']['consumed']  ), #1-0:1.8.2
		SmartMeterSensor(meter, 'Power produced : low tariff'   ,0              ,ENERGY_KILOWATTHOUR    ,'mdi:speedometer', lambda x: x['kwh']['low']['produced']   ), #1-0:2.8.1
		SmartMeterSensor(meter, 'Power produced : normal tariff',0              ,ENERGY_KILOWATTHOUR    ,'mdi:speedometer', lambda x: x['kwh']['high']['produced']  ), #1-0:2.8.2
		SmartMeterSensor(meter, 'Current tariff'                ,'TODO:HIGH/LOW',''                     ,'mdi:speedometer', lambda x: x['kwh']['tariff']            ), #0-0:96.14.0
		SmartMeterSensor(meter, 'Current power usage'           ,0              ,POWER_KILOWATT         ,'mdi:speedometer', lambda x: x['kwh']['current_consumed']  ), #1-0:1.7.0
		SmartMeterSensor(meter, 'Current power produced'        ,0              ,POWER_KILOWATT         ,'mdi:speedometer', lambda x: x['kwh']['current_produced']  ), #1-0:2.7.0
		SmartMeterSensor(meter, 'Gas used'                      ,0              ,VOLUME_CUBIC_METRE     ,'mdi:speedometer', lambda x: x['gas']['total']             )  #0-1:24.2.1
    ])

    return True

class TimedMeter(object):
    def getPacket(self):
        if self._reading:
            _LOGGER.info('P1 packet is already being read')
            return None

        self._reading = True;
        meter = SmartMeter(self._port,baudrate=self._baudrate)
        
        try:
            self._lastpacket = meter.read_one_packet()
        except serial.SerialException as ex:
            _LOGGER.error('Failed to read packet: %s', str(ex))
            return None
        except BaseException as ex:
            _LOGGER.error('Failed to read packet %s', str(ex))
            return None
        finally:
            meter.disconnect()
            _LOGGER.info('Done reading packet')
            self._reading = False;
        return None

    def __init__(self, config, **kwargs):
        self._lastpacket = None;
        self._reading = False;
        self._port = config.get(CONF_PORT)
        self._baudrate = config.get(CONF_BAUDRATE)

        return None

    @property
    def lastpacket(self):
        return self._lastpacket

class SmartMeterSensor(Entity):
    """Representation of a sensor on a dutch smart meter."""

    def __init__(self, meter, name, state, unit_of_measurement, icon, valueExpression):
        """Initialize the sensor."""
        self._meter = meter
        self._name = name
        self._state = state
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._valueExpression = valueExpression

    @property
    def should_poll(self):
        """TODO: figure out how to implement push"""
        return True

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor. (total/current power consumption/production or total gas used)"""
        #return self._meter.lastpacket
        #return self._state
        if self._meter.lastpacket is None:
            _LOGGER.warning('P1 packet has not been read yet.')
            return None

        try:
            return self._valueExpression(self._meter.lastpacket)
        except BaseException as ex:
            _LOGGER.error('Failed to read current power usage: %s', str(ex))
            return 42

    @property
    def unit_of_measurement(self):
        """Return the unit this state is expressed in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    def update(self):
        return self._meter.getPacket()