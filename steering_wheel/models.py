from typing import TypeVar, Generic
from dataclasses import field

from pydantic.dataclasses import dataclass

@dataclass
class FFBProfile:
    '''
    As in a single profile, you may want to switch between these for different games/cars etc.
    '''

    name: str = '' # only used for api to remember what profile it is, ignored in settings file
    description: str = ''
    sensitivity: float = 1
    damping: float = 0.1

    # if your game supports applying steering lock forces for vehicles that have smaller rotations,
    # then set this nice and high and let the game handle it
    total_rotations: float = 4

@dataclass
class ODriveSettings:
    ignore_odrive_errors: bool = False
    print_ffb_debug: bool = False
    start_odrive_paused: bool = False

@dataclass
class WheelDriverSettings:
    '''
    Interface used by wheel driver module, separate from wheelsettings so it doesn't have to know about profiles
    and whatever jazz may be added in future.
    This possibly may get really duplicated with WheelSettings, in which case something new needs to be figured out
    '''

    ffb_profile: FFBProfile = field(default_factory=lambda: FFBProfile)
    odrive_settings: ODriveSettings = field(default_factory=lambda: ODriveSettings())

@dataclass
class WheelSettings:
    '''
    Entire settings for all modules of the wheel
    '''

    odrive_settings: ODriveSettings = field(default_factory=lambda: ODriveSettings())
    profiles: dict[str, FFBProfile] = field(default_factory=lambda: {})
    active_profile: FFBProfile = field(default_factory=lambda: FFBProfile)

WHEEL_SETTINGS_FILE = 'wheel_settings.json'

TValue = TypeVar("TValue")

class Box(Generic[TValue]):
    def __init__(self, value: TValue):
        self.value = value