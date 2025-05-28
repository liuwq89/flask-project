from dataclasses import dataclass
from typing import Optional, Union, Literal


@dataclass
class ArgsConfig:
    name: str
    type: type = str
    required: bool = False
    default: Optional[Union[str, int, float, bool]] = None
    help: Optional[str] = None
    action: str = "store"
    location: Literal["json", "args", "values", "headers", "form"] = "values"
    choices: Optional[Union[list, tuple]] = None
        
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "required": self.required,
            "help": self.help,
            "default": self.default,
            "action": self.action,
            "choices": self.choices,
            "location": self.location,
        }



