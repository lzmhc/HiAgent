import json
import os
import tomllib
from abc import abstractmethod, ABC
from pathlib import Path

class BaseConfig(ABC):
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

    def get_timeout(self):
        return self.timeout

    def get_max_tokens(self):
        return self.max_tokens

    def get_temperature(self):
        return self.temperature

    @abstractmethod
    def get_provider(self):
        return None

    @abstractmethod
    def get_think_level(self):
        return None

    @abstractmethod
    def get_base_url(self):
        return None

    @abstractmethod
    def get_models(self):
        return None

    @abstractmethod
    def get_model(self):
        return None

    @abstractmethod
    def get_api_key(self):
        return None

class PiConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.path = os.path.expanduser('~') + "/.pi/agent"
        self.auth = self.path + "/auth.json"
        self.settings = self.path + "/settings.json"
        self.models = self.path + "/models.json"

    def read_auth(self):
        with open(self.auth) as f:
            return json.load(f)

    def read_settings(self):
        with open(self.settings) as f:
            return json.load(f)

    def read_models(self):
        with open(self.models) as f:
            return json.load(f)

    def get_provider(self):
        settings = self.read_settings()
        provider = settings["defaultProvider"]
        return provider

    def get_think_level(self):
        settings = self.read_settings()
        return settings["defaultThinkingLevel"]

    def get_base_url(self):
        provider = self.read_models()["providers"][self.get_provider()]
        return provider["baseUrl"]

    def get_models(self):
        models_list = []
        provider = self.read_models()["providers"][self.get_provider()]
        models = provider["models"]
        for model in models:
            models_list.append(model["id"])
        return models_list

    def get_model(self):
        return self.get_models()[0]

    def get_api_key(self):
        return self.read_auth()[self.get_provider()]["key"]

class CodexConfig(BaseConfig):
    def __init__(self):
        super().__init__()
        self.path = os.path.expanduser('~') + "/.codex"
        self.auth = self.path + "/auth.json"
        self.config = self.path + "/config.toml"

    def read_auth(self):
        with open(self.auth) as f:
            return json.load(f)

    def read_config(self):
        with open(self.config, "rb") as f:
            return tomllib.load(f)

    def get_provider(self):
        return self.read_config()["model_provider"]

    def get_think_level(self):
        return self.read_config()["model_reasoning_effort"]

    def get_base_url(self):
        return self.read_config()["model_providers"][self.get_provider()]["base_url"]

    def get_models(self):
        models_list = []
        models_list.append(self.read_config()["model"])
        return models_list

    def get_model(self):
        return self.read_config()["model"]

    def get_api_key(self):
        return self.read_auth()["OPENAI_API_KEY"]

class GlobalConfig:
    def __init__(self):
        base_dir = Path(__file__).parent
        with open(base_dir / "config.json") as f:
            self.json_config = json.load(f)
        self.provider = {
            "pi": PiConfig(),
            "codex": CodexConfig(),
        }
        self.config = self.provider.get(self.json_config["defaultProvider"])
        self.config.set_timeout(self.json_config.get("timeout", 60))
        self.config.set_max_tokens(self.json_config.get("max_tokens", 2048))
        self.config.set_temperature(self.json_config.get("temperature", 0.7))

    def get_provider(self):
        return self.json_config["defaultProvider"]

    def get_config(self):
        return self.config

if __name__ == "__main__":
    config = GlobalConfig()
    print(config.get_config().get_base_url())
    print(config.get_config().get_models())
    print(config.get_config().get_model())
    print(config.get_config().get_think_level())
    print(config.get_config().get_api_key())
    print(config.get_config().get_provider())
    print(config.get_config().get_timeout())
    print(config.get_config().get_max_tokens())
    print(config.get_config().get_temperature())
