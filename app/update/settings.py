"""Manages a TinyPilot update settings file.

TinyPilot currently manages some of its settings in a database and some of its
settings in a YAML settings file. This module is a wrapper around the YAML
settings file that allows TinyPilot code to modify it cleanly.

Typical usage example:

    settings = update_settings.load()
    settings.ustreamer_desired_fps = 15
    update_settings.save(settings)
"""

import yaml

import env
import video_service

_SETTINGS_FILE_PATH = env.abs_path_in_home_dir('settings.yml')

# To create a new EDID:
#  1. Convert the existing EDID to binary using "edid2bin".
#  2. Edit the binary using "AW EDID Editor v.02.00.13".
#  3. Save the new EDID in binary format.
#  4. Convert the binary EDID to a hex EDID using "make-edid".
#    - Use the "--yaml" option if required.

# Note: You may need to perform a few extra steps in order for the EDID
# to conform to edid-decode's check - but only if the "Display Range Limits"
# block changes. This is due to a bug in AW EDID Editor v.02.00.13 that doesn't
# set the correct bytes.
# To work around this:
#  1. Open the new EDID in "AW EDID Editor v.3.0.10".
#  2. Save the EDID to set correct bytes in the "Display Range Limits" block
#  3. Re-open the EDID in "AW EDID Editor v.02.00.13" and re-set
#     the screen size dimensions to 0 (both vertical and horizontal)
_DEFAULT_TC358743_EDID = """
00ffffffffffff005262769800888888
2d1e0103800000781aee91a3544c9926
0f50547fef8081c08140810081809500
a9c081406140271f80f07138164038c0
350000000000001eec2c80a070381a40
3020350000000000001e000000fc0054
696e7950696c6f740a202020000000fd
00185a125010000a20202020202001aa
02031ef14b010204131f2021223c3d3e
2309070766030c00300080e2007f0000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
00000000000000000000000000000000
0000000000000000000000000000008e
""".strip()

# Define default values for user-configurable TinyPilot settings. The YAML data
# in _SETTINGS_FILE_PATH take precedence over these defaults.
_DEFAULTS = {
    'tinypilot_keyboard_interface': '/dev/hidg0',
    'tinypilot_mouse_interface': '/dev/hidg1',
    'tinypilot_external_port': 80,
    'ustreamer_desired_fps': video_service.DEFAULT_FRAME_RATE,
    'ustreamer_edid': _DEFAULT_TC358743_EDID,
    'ustreamer_quality': video_service.DEFAULT_MJPEG_QUALITY,
    'ustreamer_h264_bitrate': video_service.DEFAULT_H264_BITRATE,
    'ustreamer_streaming_mode': video_service.DEFAULT_STREAMING_MODE,
}


class Error(Exception):
    pass


class LoadSettingsError(Error):
    pass


class SaveSettingsError(Error):
    pass


class Settings:
    """Manages the parameters for the update process in a YAML file.

    For historical/compatibility reasons, the naming of the uStreamer properties
    is not in line with the naming conventions in the code.
    """

    def __init__(self, data):
        # Merge the defaults with data, with data taking precedence.
        self._data = {**_DEFAULTS, **(data if data else {})}

    def as_dict(self):
        return self._data

    @property
    def ustreamer_desired_fps(self):
        return self._data['ustreamer_desired_fps']

    @ustreamer_desired_fps.setter
    def ustreamer_desired_fps(self, value):
        self._data['ustreamer_desired_fps'] = value

    @property
    def ustreamer_quality(self):
        return self._data['ustreamer_quality']

    @ustreamer_quality.setter
    def ustreamer_quality(self, value):
        self._data['ustreamer_quality'] = value

    @property
    def ustreamer_h264_bitrate(self):
        return self._data['ustreamer_h264_bitrate']

    @ustreamer_h264_bitrate.setter
    def ustreamer_h264_bitrate(self, value):
        self._data['ustreamer_h264_bitrate'] = value

    @property
    def ustreamer_streaming_mode(self):
        return self._data['ustreamer_streaming_mode']

    @ustreamer_streaming_mode.setter
    def ustreamer_streaming_mode(self, value):
        self._data['ustreamer_streaming_mode'] = value


def load():
    """Retrieves the current TinyPilot update settings.

    Parses the contents of settings file and generates a settings object that
    represents the values in the settings file.

    Args:
        None

    Returns:
        A Settings instance of the current update settings.
    """
    try:
        with open(_SETTINGS_FILE_PATH, encoding='utf-8') as settings_file:
            return _from_file(settings_file)
    except FileNotFoundError:
        return Settings(data=None)
    except IOError as e:
        raise LoadSettingsError(
            'Failed to load settings from settings file') from e


def save(settings):
    """Saves a Settings object to the settings file."""
    try:
        with open(_SETTINGS_FILE_PATH, 'w', encoding='utf-8') as settings_file:
            _to_file(settings, settings_file)
    except IOError as e:
        raise SaveSettingsError(
            'Failed to save settings to settings file') from e


def _from_file(settings_file):
    return Settings(yaml.safe_load(settings_file))


def _to_file(settings, settings_file):
    """Writes a Settings object to a file, excluding any default values."""
    # To avoid polluting the settings file with unnecessary default values, we
    # exclude them instead of hard-coding the defaults in the file.
    settings_without_defaults = {}
    for key, value in settings.as_dict().items():
        if (key not in _DEFAULTS) or (value != _DEFAULTS[key]):
            settings_without_defaults[key] = value

    if settings_without_defaults:
        yaml.safe_dump(settings_without_defaults, settings_file)
