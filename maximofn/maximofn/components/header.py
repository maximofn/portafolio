import reflex as rx

from maximofn.components.link_icon import link_icon
import maximofn.components.constants as constants
from maximofn.components.logo import logo_long

from maximofn.styles.colors import Color
from maximofn.styles.sizes import Size
from maximofn.styles.fonts import Font, FontWeight

LANGUAJES = True
DARK_LIGHT_MODE = True

def logo() -> rx.Component:
    return logo_long()

def icons() -> rx.Component:
    return rx.responsive_grid(
        link_icon("icons/linkedin-dark_mode.svg", constants.LINKEDIN, "linkedin"),
        link_icon("icons/huggingface-dark_mode.svg", constants.HUGGINGFACE, "huggingface", icon_width=Size.LARGE.value),
        link_icon("icons/kaggle-dark_mode.svg", constants.KAGGLE, "kaggle", icon_width=Size.KAGLE_ICON_SIZE.value, icon_margin_x=Size.XXSMALL.value),
        link_icon("icons/x-dark_mode.svg", constants.TWITTER, "x/twitter"),
        link_icon("icons/facebook-dark_mode.svg", constants.FACEBOOK, "facebook"),
        link_icon("icons/instagram-dark_mode.svg", constants.INSTAGRAM, "instagram"),
        link_icon("icons/tiktok-dark_mode.svg", constants.TIKTOK, "tiktok"),
        link_icon("icons/twitch-dark_mode.svg", constants.TWITCH, "twitch"),
        link_icon("icons/youtube-dark_mode.svg", constants.YOUTUBE, "youtube"),
        link_icon("icons/threads-dark_mode.svg", constants.THREADS, "threads"),
        link_icon("icons/github-dark_mode.svg", constants.GITHUB, "github"),
        spacing = Size.XSMALL.value,
        columns=[4, 6, 11],
        margin_right=Size.XLARGE.value,
        align_items="flex-end",
    )

def languajes() -> rx.Component:
    return rx.flex(
        rx.image(
            src="languajes/english.svg",
            width=Size.LARGE.value,
            alt="English",
            margin_right=Size.XSMALL.value,
        ),
        rx.image(
            src="languajes/portuguese.svg",
            width=Size.LARGE.value,
            alt="Portuguese",
        ),
        margin_right=Size.XLARGE.value,
    )

def dark_light_mode() -> rx.Component:
    return rx.flex(
        rx.image(
            src="icons/dark_mode.svg",
            alt="Dark mode",
        ),
    )

def header() -> rx.Component:
    width = "100%"
    background_color = Color.BACKGROUND.value
    padding = "10px 20px"
    height = "auto"
    position = "sticky"
    top = "0px"
    left = "0px"
    align = "center"

    if LANGUAJES and DARK_LIGHT_MODE:
        header_component = rx.flex(
            logo(),
            rx.spacer(),
            rx.flex(
                icons(),
                languajes() ,
                dark_light_mode(),
            ),
            width=width,
            background_color=background_color,
            padding=padding,
            height=height,
            position=position,
            top=top,
            left=left,
            align=align,
        )
    elif LANGUAJES:
        header_component = rx.flex(
            logo(),
            rx.spacer(),
            rx.flex(
                icons(),
                # languajes() ,
                dark_light_mode(),
            ),
            width=width,
            background_color=background_color,
            padding=padding,
            height=height,
            position=position,
            top=top,
            left=left,
            align=align,
        )
    elif DARK_LIGHT_MODE:
        header_component = rx.flex(
            logo(),
            rx.spacer(),
            rx.flex(
                icons(),
                languajes() ,
                # dark_light_mode(),
            ),
            width=width,
            background_color=background_color,
            padding=padding,
            height=height,
            position=position,
            top=top,
            left=left,
            align=align,
        )
    else:
        header_component = rx.flex(
            logo(),
            rx.spacer(),
            rx.flex(
                icons(),
                # languajes() ,
                # dark_light_mode(),
            ),
            width=width,
            background_color=background_color,
            padding=padding,
            height=height,
            position=position,
            top=top,
            left=left,
            align=align,
        )

    return header_component