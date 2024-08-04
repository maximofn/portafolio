import colors

###################### BACKGROUND ######################
dark_background = (
    f'background-color: {colors.colors["950"]};'
    'width: 100%; height: 100%;'
    'z-index: -2;'
)

dark_background_grid = (
    "position: fixed; bottom: 0; left: 0; right: 0; top: 0;"
    f"background-image: linear-gradient(to right, {colors.color_grid_dark} 1px, transparent 1px), "
    f"linear-gradient(to bottom, {colors.color_grid_dark} 1px, transparent 1px);"
    "background-size: 14px 24px;"
    "-webkit-mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, #000 70%, transparent 100%);"
    "mask-image: radial-gradient(ellipse 60% 50% at 50% 0%, #000 70%, transparent 100%);"
    "z-index: -1;"
)

light_background = (
    f'background-color: {colors.color_white};'
    'width: 100%; height: 100%;'
    'z-index: -2;'
)

light_background_grid = (
    "position: fixed; bottom: 0; left: 0; right: 0; top: 0;"
    f"background-image: linear-gradient(to right, {colors.color_grid_light} 1px, transparent 1px), "
    f"linear-gradient(to bottom, {colors.color_grid_light} 1px, transparent 1px);"
    "background-size: 14px 24px;"
    "-webkit-mask-image: radial-gradient(ellipse 80% 50% at 50% 0%, #000 70%, transparent 110%);"
    "mask-image: radial-gradient(ellipse 80% 50% at 50% 0%, #000 70%, transparent 110%);"
    "z-index: -1;"
)
#####################################################

###################### FONT ######################
cascadia_font = (
    "@font-face {"
    "   font-family: 'Cascadia Code';"
    "   src: url('fonts/CascadiaCode-2404.23/ttf/CascadiaCodeItalic.ttf');"
    "}"
)

font = (
    "font-family: 'Cascadia code', Ubuntu, sans-serif;"
    "color: white;"    # font color
)
#####################################################