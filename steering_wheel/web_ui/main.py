from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from steering_wheel.models import FFBProfile, Box, WheelSettings, ODriveSettings

app = FastAPI()

ACTIVE_PROFILE_NAME = 'active'

apply_settings_func = lambda: None
active_settings_box: Box[WheelSettings] = None

app.mount('/app/', StaticFiles(directory='steering_wheel/web_ui/static/', html=True), name='static')

@app.get('/profiles/{name}')
async def get_profile(name: str):
    if name == ACTIVE_PROFILE_NAME:
        profile = active_settings_box.value.active_profile
        profile.name = name
        return profile
    
    try:
        profile = active_settings_box.value.profiles[name]
        profile.name = name
        return profile
    except KeyError:
        raise HTTPException(404, f'Unknown profile: "{name}"')

@app.post('/profiles/{name}')
async def save_profile(name: str, profile: FFBProfile):
    if name == ACTIVE_PROFILE_NAME:
        profile.name = 'active'
        active_settings_box.value.active_profile = profile
    else:
        profile.name = name
        active_settings_box.value.profiles[name] = profile

    apply_settings_func()
    return profile

@app.get('/profilenames')
async def get_profile_names():
    return list(active_settings_box.value.profiles.keys())

@app.get('/odrivesettings')
async def get_odrive_settings():
    return active_settings_box.value.odrive_settings

@app.post('/odrivesettings')
async def save_odrive_settings(odrive_settings: ODriveSettings):
    active_settings_box.value.odrive_settings = odrive_settings

    apply_settings_func()