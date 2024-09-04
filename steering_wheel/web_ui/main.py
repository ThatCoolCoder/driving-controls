from fastapi import FastAPI

from steering_wheel.models import FFBProfile

app = FastAPI()

ACTIVE_CONFIG_NAME = 'active'

apply_settings_func: lambda: None

@app.get("/config/{name}")
async def get_config(name: str):
    if name == ACTIVE_CONFIG_NAME:
        pass
    return ''
    
@app.post("/config/{name}")
async def save_config(name: str):
    if name == ACTIVE_CONFIG_NAME:
        pass
    return