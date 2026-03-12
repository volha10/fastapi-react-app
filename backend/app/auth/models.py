import enum
from dataclasses import dataclass
from datetime import datetime


class JwtTokenType(enum.StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class UserPayload:
    email: str
    exp: datetime
    type: JwtTokenType
