#!/usr/bin/python3
from dataclasses import dataclass
from typing import Optional

@dataclass
class ADUser:
    username: str
    roastable: bool = False
    hash_value: Optional[str] = None
    
    def get_hashcat_format(self) -> str:
        if self.hash_value:
            return self.hash_value
        return ""
