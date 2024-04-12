import json
import os

class Settings:
    def __init__(self) -> None:
        self.username = ""
        self.load_settings()

    def set_username(self, username: str) -> None:
        self.username = username
        self.save_settings()
    
    def load_settings(self) -> None:
        if "settings" not in os.listdir():
            with open("settings", "w") as file:
                json.dump({"username": ""}, file)
                
        settings = open("settings", "r")
        settings = json.load(settings)
        self.username = settings["username"]
    
    def save_settings(self) -> None:
        with open("settings", "w") as file:
            json.dump({"username": self.username}, file)


settings: Settings = None
def init_settings() -> None:
    global settings
    settings = Settings()