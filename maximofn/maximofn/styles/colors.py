from enum import Enum

class Color(Enum):
    PRIMARY = "#bdc8f8"
    SECONDARY = "#d5defb"
    BACKGROUND = "#07090d"
    WHITE = "#f1f2f4"
    BLUE = "#718ef4"
    GREEN = "#0ca470"
    ORANGE = "#fc895a"
    PURPLE = "#cd3af8"
    DARK = "#0e121f"

class TextColor(Enum):
    HEADER = Color.WHITE.value
    BODY = Color.PRIMARY
    LINK = Color.WHITE.value
    FOOTER = Color.WHITE.value