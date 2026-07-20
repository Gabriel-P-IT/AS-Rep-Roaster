from dataclasses import dataclass
from typing import Optional

@dataclass
class ADUser:
    username: str
    roastable: bool = False
    hash_value: Optional[str] = None
    cracked_password: Optional[str] = None

    def get_hashcat_format(self) -> str:
        return self.hash_value or ""
