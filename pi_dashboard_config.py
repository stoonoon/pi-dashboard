import datetime
# General UI config

width=800
height=480
relx=0
rely=0
prevent_move_resize=True

# Colour scheme
background_colour = "#162D32" # dark green
highlight_background_colour = "#122928" # darker green
title_background_colour = "#202020" # dark grey
foreground_colour = "#AAAAAA" # light grey
active_foreground_colour = "#AAAA00" # yellow

# Convenience time conversions
MS_IN_SECONDS = 1000
MS_IN_MINUTES = MS_IN_SECONDS * 60
S_IN_MINUTES = 60
S_IN_HOURS = S_IN_MINUTES * 60

# gtasks_frame config
gtasks_auto_refresh_time = 10 * MS_IN_MINUTES

# sonos_frame config
sonos_auto_refresh_time = 1 * MS_IN_SECONDS
sonos_bedroom_ip = '192.168.1.208'
sonos_kitchen_ip = '192.168.1.210'

# backlight config
BACKLIGHT_TIMEOUT_SHORT = datetime.timedelta(minutes=10)
BACKLIGHT_TIMEOUT_LONG = datetime.timedelta(hours=10)
BACKLIGHT_DAYTIME_HOUR_START = 8
BACKLIGHT_DAYTIME_HOUR_END = 22
backlight_auto_refresh_time = 1 * MS_IN_MINUTES

# mouse config
mouse_idle_timeout = 1 # (seconds)
pointer_home=(799,239)
mouse_watcher_refresh_time = 100 # (ms)