from enum import Enum

class Color(Enum):
    PRIMARY = "#f6f6f9"
    SECONDARY = "#d1d1d1"
    BACKGROUND = "#17181c"
    WHITE = "#ffffff"
    BLUE = "#60a4fa"
    DARK_BLUE = "#171d4f"
    GREEN = "#0ca470"
    DARK_GREEN = "#304e21"
    ORANGE = "#fc895a"
    DARK_ORANGE = "#4e4022"
    PURPLE = "#cd3af8"
    DARK_PURPLE = "#40224e"
    RED = "#853654"
    DARK_RED = "#4e2232"
    GRAY = "#24272f"
    DARK = "#0e121f"
    BLACK = "#000000"

class TextColor(Enum):
    HEADER = Color.WHITE.value
    BODY = Color.PRIMARY
    LINK = Color.WHITE.value
    FOOTER = Color.WHITE.value