import unittest
from unittest import mock

from homeassistant.components.sensor import smartmeter
from tests.common import get_test_home_assistant

class TestSmartmeter(unittest.TestCase):
    """Tests the dutch smart meter."""

    def setUp(self):  # pylint: disable=invalid-name
        """Setup things to be run when tests are started."""
        self.hass = get_test_home_assistant()
        
        #self.assertTrue(thermostat.setup(self.hass, {'thermostat': {
        #    'platform': 'demo',
        #}}))

    def tearDown(self):  # pylint: disable=invalid-name
        """Stop down everything that was started."""
        self.hass.stop()

    def test_setup_platform(self):
        add_devices = mock.MagicMock();
        config = {
        };
        assert smartmeter.setup_platform(self.hass,config, add_devices) is True