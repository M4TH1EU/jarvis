import json

import homeassistant.homeassistant
from homeassistant.homeassistant import callService


def turnOn(entity_id):
    """
    Turn on a light

    Parameters
    ----------
    entity_id : str
    """

    callService('{"entity_id": "' + entity_id + '" }', "light/turn_on")


def turnOff(entity_id):
    """
    Turn off a light

    Parameters
    ----------
    entity_id : str
    """
    callService('{"entity_id": "' + entity_id + '" }', "light/turn_off")


def is_on(entity_id):
    return json.loads(homeassistant.homeassistant.getState(entity_id))['state'] == 'on'


def changeColorWithName(entity_id, color):
    """
    Change the color of a specified light with human readable color

    Parameters
    ----------
    entity_id : str
    color : str
    """
    callService('{"entity_id": "' + entity_id +
                '", "color_name": "' + color + '" }', "light/turn_on")


def changeColorWithRGB(entity_id, r, g, b):
    """
    Change the color of a specified light with RGB code

    Parameters
    ----------
    entity_id : str
    r : int
    g : int
    b : int

    """
    callService('{"entity_id": "' + entity_id +
                '", "rgb_color": "[' + r + ',' + g + ',' + b + ']" }', "light/turn_on")


def changeBrightness(entity_id, brightness):
    """
    Change the brightness of a specified light

    Parameters
    ----------
    entity_id : str
    brightness : int

    """
    callService('{"entity_id": "' + entity_id +
                '", "brightness": "' + brightness + '" }', "light/turn_on")
