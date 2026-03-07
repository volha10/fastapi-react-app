import enum


class JwtTokenType(enum.StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
