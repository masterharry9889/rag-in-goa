from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import dotenv
import os

router = APIRouter()
# backend/.env is at the root of backend directory
ENV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")

class ConfigUpdate(BaseModel):
    keys: Dict[str, str]

@router.get("/config")
def get_config():
    try:
        # If the file doesn't exist, dotenv_values returns {}
        if not os.path.exists(ENV_FILE_PATH):
            open(ENV_FILE_PATH, 'a').close()
            
        config = dotenv.dotenv_values(ENV_FILE_PATH)
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/config")
def update_config(update: ConfigUpdate):
    try:
        if not os.path.exists(ENV_FILE_PATH):
            open(ENV_FILE_PATH, 'a').close()
            
        for key, value in update.keys.items():
            # Update the key in the .env file
            dotenv.set_key(ENV_FILE_PATH, key, value)
            
        return {"status": "success", "message": "Configuration updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/config/{key}")
def delete_config(key: str):
    try:
        if not os.path.exists(ENV_FILE_PATH):
            return {"status": "success", "message": "Nothing to delete."}
            
        dotenv.unset_key(ENV_FILE_PATH, key)
        return {"status": "success", "message": f"Key {key} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
