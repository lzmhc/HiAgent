import json
import os
import tomllib
from pathlib import Path

from memory.message import PiMessage, CodexMessage


class BaseConfig:
    def __init__(self):
        self.timeout = None
        self.max_tokens = None
        self.temperature = None

    def set_timeout(self, timeout):
        self.timeout = timeout

    def set_max_tokens(self, max_tokens):
        self.max_tokens = max_tokens

    def set_temperature(self, temperature):
        self.temperature = temperature

class PiConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.path = os.path.expanduser('~') + "/.pi/agent"
        self.auth = self.path + "/auth.json"
        self.trust = self.path + "/trust.json"
        self.settings = self.path + "/settings.json"
        self.message = PiMessage()

    def read_trust(self):
        with open(self.trust) as f:
            return json.load(f)

    def read_auth(self):
        with open(self.auth) as f:
            return json.load(f)

    def read_settings(self):
        with open(self.settings) as f:
            return json.load(f)

    def get_provider(self):
        settings = self.read_settings()
        provider = settings["defaultProvider"]
        return provider

    def get_base_url(self):
        provider = self.get_provider()
        if provider == "xiaomi":
            return "https://api.xiaomimimo.com/v1"
        return None

    def get_model(self):
        settings = self.read_settings()
        model = settings["defaultModel"]
        return model

    def get_think_level(self):
        settings = self.read_settings()
        return settings["defaultThinkingLevel"]

    def get_api_key(self):
        auth = self.read_auth()
        provider = self.get_provider()
        if provider == "xiaomi":
            return auth["xiaomi"]["key"]
        return None

    def get_message(self):
        return self.message

    def get_timeout(self):
        return self.timeout

    def get_max_tokens(self):
        return self.max_tokens

    def get_temperature(self):
        return self.temperature

class CodexConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.path = os.path.expanduser('~') + "/.codex"
        self.auth = self.path + "/auth.json"
        self.config = self.path + "/config.toml"
        self.message = CodexMessage()

    def read_trust(self):
        with open(self.config, "rb") as f:
            projects = tomllib.load(f)["projects"]
        print(projects)

    def read_auth(self):
        with open(self.auth) as f:
            return json.load(f)

    def read_config(self):
        with open(self.config, "rb") as f:
            return tomllib.load(f)

    def get_provider(self):
        return self.read_config()["model_provider"]

    def get_base_url(self):
        provider = self.get_provider()
        return self.read_config()["model_providers"][provider]["base_url"]

    def get_model(self):
        return self.read_config()["model"]

    def get_think_level(self):
        return self.read_config()["model_reasoning_effort"]

    def get_api_key(self):
        provider = self.get_provider()
        return self.read_config()["model_providers"][provider]["api_key"]

    def get_message(self):
        return self.message

    def get_timeout(self):
        return self.timeout

    def get_max_tokens(self):
        return self.max_tokens

    def get_temperature(self):
        return self.temperature

class GlobalConfig:
    def __init__(self):
        base_dir = Path(__file__).parent
        with open(base_dir / "config.json") as f:
            self.json_config = json.load(f)
        self.Provider = None
        self.config = self.get_config()
        self.config.set_timeout(self.json_config.get("timeout", 60))
        self.config.set_max_tokens(self.json_config.get("max_tokens", 2048))
        self.config.set_temperature(self.json_config.get("temperature", 0.7))

    def get_config(self):
        agent_type = self.json_config["agent_type"]
        if agent_type == "pi":
            return PiConfig()
        if agent_type == "codex":
            return CodexConfig()
        return None

    def get_message(self):
        return self.config.get_message()


if __name__ == "__main__":
    config = GlobalConfig()
    print(config.get_config().get_base_url())
    print(config.get_config().get_model())
    print(config.get_config().get_think_level())
    print(config.get_config().get_api_key())
