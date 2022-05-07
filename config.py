from typing import Final

import yaml
from dataclasses import dataclass


@dataclass
class Config:
    bot_token: str


with open('config.yaml') as file:
    data = yaml.safe_load(file)
    config = Config(**data)
