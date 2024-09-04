import dataclasses
import json
import argparse
import webbrowser
import threading
import time

from pydantic import TypeAdapter

from steering_wheel.models import WheelSettings, WheelDriverSettings, FFBProfile, Box

def try_load_wheel_settings(create_on_missing=True) -> WheelSettings:
    try:
        with open('settings.json', 'r') as f:
            return TypeAdapter(WheelSettings).validate_json(f.read())
    except FileNotFoundError:
        if not create_on_missing:
            raise
        with open('config.json', 'w+') as f:
            print('Config file config.json not found, writing template config to there')

            settings = create_default_settings()
            f.write(json.dumps(dataclasses.asdict(settings), indent=4))
            return settings

def create_default_settings() -> WheelSettings:
    settings = WheelSettings()
    profile = FFBProfile()
    settings.profiles['Profile 1'] = profile
    settings.active_profile = dataclasses.replace(profile)

    return settings
    
# def reread_config_loop(profile_box: Box[WheelProfile]):
#     while running:
#         profile_box.value = try_load_wheel_settings(create_on_missing=False)
#         time.sleep(5)
    
def parse_args():
    parser = argparse.ArgumentParser(
        prog='FFB Wheel Driver',
        description='Driver and configuration program for force feedback wheel created by ThatCoolCoder',
        epilog='')
    # parser.add_argument('-v', '--version', action='store_true', help='Display version of the program') # actually we dont have version numbers yet so dont need this lol
    parser.add_argument('-t', '--terminal-only', action='store_true', help='Run the program without running the web configuration UI')
    parser.add_argument('-s', '--suppress-browser', action='store_true', help='Prevent the program from opening a browser when launching the config ')
    parser.add_argument('-u', '--ui-only', action='store_true', help='Don\'t actually run the wheel, just launch the browser UI')
    parser.add_argument('-x', '--no-init-config', action='store_true', help='Prevent the program from intializing default settings if it can\'t read the settings file')
    parser.add_argument('-p', '--port', default=9190)

    return parser.parse_args()

def main():
    args = parse_args()

    if args.ui_only and args.terminal_only:
        print('Why are you trying to disable both UI and wheel driver? There\'s no point in running the program like this lol')
        return
    
    settings = try_load_wheel_settings(create_on_missing=not args.no_init_config)

    wheel_driver_box = Box(WheelDriverSettings())

    if not args.ui_only:
        start_wheel_driver(args, wheel_driver_box)

    if not args.terminal_only:
        def apply_settings(new_settings: WheelSettings):
            wheel_driver_box.value.odrive_settings = new_settings.odrive_settings
            wheel_driver_box.value.ffb_profile = new_settings.active_profile
        start_web_ui(args, apply_settings)

    while True:
        # todo: uuh should probably do something better and handle shutdown elegantly and all
        time.sleep(0.5)

def start_wheel_driver(args, apply_settings_func):
    from steering_wheel.wheel_driver import main

    t = threading.Thread(target=lambda: main())
    t.start()

def start_web_ui(args):
    from steering_wheel.web_ui import app
    import uvicorn

    t = threading.Thread(target=lambda: uvicorn.run(app, host='localhost', port=args.port))
    t.start()
    
    if not args.suppress_browser:
        webbrowser.open(f'http://localhost:{args.port}/')

if __name__ == '__main__':
    main()