#!/usr/bin/python3
# note run ' export DISPLAY=:0.0 ' first in terminal if running from remote SSH session
# pylint: disable=no-member

import tkinter as tk
from gtasks import Gtasks
from datetime import datetime
import soco
import os

my_dark_green = "#162D32"
my_darker_green = "#122928"
my_dark_grey = "#202020"
my_white = "#AAAAAA"
my_yellow = "#AAAA00"
separator_v = ",\n"
backlight_timeout_start_time = -1
MS_IN_MINUTES = 1000*60
S_IN_MINUTES = 60
S_IN_HOURS = S_IN_MINUTES*60
BACKLIGHT_TIMEOUT_SHORT = 10 * S_IN_MINUTES
BACKLIGHT_TIMEOUT_LONG = 10*S_IN_HOURS
BACKLIGHT_DAYTIME_HOUR_START = 8
BACKLIGHT_DAYTIME_HOUR_END = 22

#tkinter root object and screen config
root = tk.Tk()

#comment this out to allow window to be moved / resized
root.overrideredirect(True)

# set size to match pi touchscreen resolution and location -
# top left (desktop) / full screen (on pi)
root.geometry("800x480+0+0")

# visual styling 

# make all widgets dark green
root.option_add("*Background", my_dark_green)
root.option_add("*Foreground", my_white)
root.option_add("*activeForeground", my_yellow)
root.option_add("*activeBackground", my_darker_green)
root.option_add("*highlightForeground", my_darker_green)
root.option_add("*highlightBackground", my_darker_green)

# GTasks object
gt=Gtasks()

# Sonos globals
bedroom = soco.SoCo('192.168.1.208')
kitchen = soco.SoCo('192.168.1.210')
current_spkr = bedroom # Current speaker to display info for and control
party_mode = True
volume_ramp_target = -1
volume_is_ramping = False
transport_state = ""
sonos_favorites_dict = {}

# Timed autoupdater for gtasks
def update_tasks():
  task_list=gt.get_tasks()
  task_names = "Tasks:\n\n"
  task_names += separator_v.join(task.title for task in task_list)
  tasksLabel.configure(text=task_names)
  root.after(1000, update_tasks)

# Timed autoupdater for sonos
def update_sonos():
    # Check if speakers are grouped and get list of speakers in group
    unique_zones=set()
    for player in current_spkr.group.members:
        unique_zones.add(player.player_name)
    separator_h = ", "
    zone_list = separator_h.join(unique_zones)
    global party_mode
    if (len(unique_zones) > 1) :
      party_mode = True
    else:
      party_mode = False
    update_sonosPartyModeButton()
    
    # Update Volume Scale
    sonosVolumeSlider.set(current_spkr.volume)
    
    # Update Now Playing info
    sonos_label_text = f"Playing on: {zone_list}\n"
    current_coordinator = current_spkr.group.coordinator
    global transport_state
    transport_state = current_coordinator.get_current_transport_info()\
      ["current_transport_state"]
    if transport_state == "PLAYING":
        sonosPlayPausebutton.configure(text="PAUSE")
        if current_coordinator.is_playing_radio:
          sonos_label_text+=("Playing Radio\n")
          sonosRWDbutton.configure(state=tk.DISABLED)
          sonosFWDbutton.configure(state=tk.DISABLED)
        else:
          sonosRWDbutton.configure(state=tk.NORMAL)
          sonosFWDbutton.configure(state=tk.NORMAL)
          track_info=current_coordinator.get_current_track_info()
          sonos_label_text+=(f"Current Track: {track_info['title']}\n")
          sonos_label_text+=(f"Artist: {track_info['artist']}\n")
          sonos_label_text+=(f"Album: {track_info['album']}\n")
    else:
      sonosPlayPausebutton.configure(text="PLAY")
      sonos_label_text+=(f"Current status: {transport_state}")
    
    sonosLabel.configure(text=sonos_label_text)
    root.after(1000, update_sonos)

# Timed autoupdater for sonos library favorites
def update_sonos_favorites():
  global sonos_favorites_dict
  sonos_favorites = bedroom.music_library.get_sonos_favorites()
  sonos_favorites_dict={}
  for fav in sonos_favorites:
    if "New Releases" in fav.title:
        sonos_favorites_dict[fav.title]="TBA"
    else:
        sonos_favorites_dict[fav.title]=fav.resources.pop().uri
  root.after(5*MS_IN_MINUTES, update_sonos_favorites)

def update_sonosPartyModeButton():
  global party_mode
  if party_mode == True:
    sonosPartyModeButton.configure(text="UNGROUP", relief=tk.SUNKEN)
  else:
    sonosPartyModeButton.configure(text="GROUP", relief=tk.RAISED)

def select_spkr(spkr):
  global current_spkr
  current_spkr=spkr
  if spkr==bedroom:
    #other_spkr = kitchen
    sonosBedroomButton.config(relief=tk.SUNKEN)
    sonosKitchenButton.config(relief=tk.RAISED)
  else:
    #other_spkr = bedroom
    sonosBedroomButton.config(relief=tk.RAISED)
    sonosKitchenButton.config(relief=tk.SUNKEN)
  
def select_bedroom():
  select_spkr(bedroom)

def select_kitchen():
  select_spkr(kitchen)

def toggle_party_mode():
  global party_mode
  if party_mode == True:
    current_spkr.unjoin()
  else:
    if current_spkr == bedroom:
      bedroom.join(kitchen)
    else:
      kitchen.join(bedroom)

def update_sonosVolume(sliderPosition): 
  # called when slider is moved (either by user, or by update_sonos)
  # I did briefly look at using current_spkr.ramp_to_volume(sliderPosition),
  # but slider calls this function repeatedly and overrides target... 
  # Will maybe revisit this later, but it works well enough for now
  current_spkr.volume = sliderPosition

def sonos_action_rwd():
  try:
    current_spkr.group.coordinator.previous()
  except Exception as e:
    print("Uh-oh. Something went bad while trying to skip to previous track")
    print (e)

def sonos_action_play_pause():
  #do the thing
  if transport_state=="PLAYING":
    current_spkr.group.coordinator.pause()
  else:
    current_spkr.group.coordinator.play()
  
  

def sonos_action_fwd():
  try:
    current_spkr.group.coordinator.next()
  except Exception as e:
    print("Uh-oh. Something went bad while trying to skip to next track")
    print (e)

def sonos_play_radio_fav(channel_label):
  current_spkr.group.coordinator.play_uri(\
    uri=sonos_favorites_dict[channel_label], title=channel_label)

def sonos_action_fav_6music():
  sonos_play_radio_fav("BBC Radio 6 Music")

def sonos_action_fav_1btn():
  sonos_play_radio_fav("1BrightonFM")
  
def sonos_action_fav_radio2():
  sonos_play_radio_fav("BBC Radio 2")

def sonos_action_fav_lbc():
  sonos_play_radio_fav("LBC London")

def backlight_toggle(action="TOGGLE"):
  if action=="TOGGLE":
    stream = os.popen('cat /sys/class/backlight/rpi_backlight/bl_power')
    output = stream.read()
  elif action=="ON":
    output = "1" # pretend backlight was off
  elif action=="OFF":
    output = "0" # pretend backlight was on
  else:
    output = -1 # invalid action -> ignore
  if '0' in output: # then turn backlight off
    os.popen('sudo bash -c "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"')
  elif '1' in output: # then turn backlight on
    os.popen('sudo bash -c "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"')
    reset_backlight_timer()
  else:
    print(f"Invalid parameter sent to backlight_toggle(action): {action}")

def reset_backlight_timer():
  global backlight_timeout_start_time
  backlight_timeout_start_time = datetime.now()
  
def check_backlight_timer():
  global backlight_timeout_start_time
  current_datetime = datetime.now()
  if BACKLIGHT_DAYTIME_HOUR_START <= current_datetime.hour <= BACKLIGHT_DAYTIME_HOUR_END: # daytime - use longer timeout
    backlight_timeout=BACKLIGHT_TIMEOUT_LONG
  else: #nighttime - use shorter timeout
    backlight_timeout=BACKLIGHT_TIMEOUT_SHORT
  if backlight_timeout_start_time==-1: # Then we need to initialise it
    reset_backlight_timer()
    backlight_toggle("ON")
  else: # we can check against it
    elapsed_time = datetime.now()-backlight_timeout_start_time
    if elapsed_time.seconds >= (backlight_timeout):
      backlight_toggle("OFF")
  root.after(1*MS_IN_MINUTES, check_backlight_timer)


# Main window layout frames

# Top menu bar
menuFrame = tk.Frame(root, bg=my_dark_grey)
menuFrame.place(relwidth=1, relheight=0.05, relx=0, rely=0)

#LH gtasks frame
tasksFrame = tk.Frame(root)#, bg=my_dark_green)
tasksFrame.place(relwidth=0.5, relheight=0.95, relx=0, rely=0.05)

#RH sonos frame
sonosFrame = tk.Frame(root)#, bg=my_dark_green)
sonosFrame.place(relwidth=0.5, relheight=0.95, relx=0.5, rely=0.05)

# menuFrame widgets
quitButton = tk.Button(menuFrame, text="X", command=exit, bg=my_dark_grey,\
  highlightbackground=my_dark_grey, relief=tk.FLAT,\
  activebackground=my_white, activeforeground=my_dark_grey)
quitButton.pack(side=tk.RIGHT)

# tasksFrame widgets
tasksLabel = tk.Label(tasksFrame, text="loading")
tasksLabel.grid(sticky="new")
backlightToggleButton = tk.Button(tasksFrame, text="BACKLIGHT ON/OFF", height=3, command=backlight_toggle)
backlightToggleButton.grid(sticky="nsew")
tasksFrame.columnconfigure(0, weight=1)
tasksFrame.rowconfigure(0, weight=1)

# sonosFrame layout
sonosRoomsFrame = tk.Frame(sonosFrame)
sonosRoomsFrame.grid(sticky="ew")
sonosVolumeFrame = tk.Frame(sonosFrame)
sonosVolumeFrame.grid(sticky="ew")
sonosPlayingFrame = tk.Frame(sonosFrame)
sonosPlayingFrame.grid(sticky="ew")
sonosTransportFrame = tk.Frame(sonosFrame)
sonosTransportFrame.grid(sticky="ew")
sonosFavouritesFrame = tk.Frame(sonosFrame)
sonosFavouritesFrame.grid(sticky="ew")
sonosFrame.columnconfigure(0, weight=1)
sonosFrame.rowconfigure(2, weight=1)

# sonosRoomsFrame layout
sonosRoomsLabel = tk.Label(sonosRoomsFrame, text="Room")
sonosRoomsLabel.grid(columnspan=2, sticky="nsew")
sonosPartyLabel = tk.Label(sonosRoomsFrame, text="Party Mode")
sonosPartyLabel.grid(row=0, column=2, sticky="nsew")
sonosBedroomButton = tk.Button(sonosRoomsFrame, text="Bedroom",\
  height=3, relief=tk.SUNKEN, command=select_bedroom)
sonosBedroomButton.grid(row=1, column=0)
sonosKitchenButton = tk.Button(sonosRoomsFrame, text="Kitchen",\
  height=3, command=select_kitchen)
sonosKitchenButton.grid(row=1, column=1)
sonosPartyModeButton = tk.Button(sonosRoomsFrame, text="ENABLE",\
  height=3, command=toggle_party_mode)
sonosPartyModeButton.grid(row=1, column=2)
sonosRoomsFrame.columnconfigure(0, weight=1)
sonosRoomsFrame.columnconfigure(1, weight=1)
sonosRoomsFrame.columnconfigure(2, weight=1)

# sonosVolumeFrame layout
sonosVolumeSlider = tk.Scale(sonosVolumeFrame, from_=0, to=100,\
  orient=tk.HORIZONTAL, length=350, highlightbackground=my_dark_green,\
  sliderlength=15, width=30, command=update_sonosVolume)
sonosVolumeSlider.grid()
sonosVolumeFrame.columnconfigure(0, weight=1)

# sonosPlayingFrame layout
sonosLabel = tk.Label(sonosPlayingFrame, text="waiting for info")
sonosLabel.grid()
sonosPlayingFrame.columnconfigure(0, weight=1)
sonosPlayingFrame.rowconfigure(0, weight=1)


# sonosTransportFrame layout
sonosRWDbutton = tk.Button(sonosTransportFrame, text="RWD",\
  height=3, width=10, command=sonos_action_rwd)
sonosRWDbutton.grid()
sonosPlayPausebutton = tk.Button(sonosTransportFrame, text="Play",\
  height=3, width=10, command=sonos_action_play_pause)
sonosPlayPausebutton.grid(row=0, column=1)
sonosFWDbutton = tk.Button(sonosTransportFrame, text="FWD",\
  height=3, width=10, command=sonos_action_fwd)
sonosFWDbutton.grid(row=0, column=2)
sonosTransportFrame.columnconfigure(0, weight=1)
sonosTransportFrame.columnconfigure(1, weight=1)
sonosTransportFrame.columnconfigure(2, weight=1)


# sonosFavoritesFrame layout
sonos6MusicButton = tk.Button(sonosFavouritesFrame, text="6 Music",\
  height=3, command=sonos_action_fav_6music)
sonos1BTNButton = tk.Button(sonosFavouritesFrame, text="1BTN",\
  height=3, command=sonos_action_fav_1btn)
sonosRadio2Button = tk.Button(sonosFavouritesFrame, text="Radio 2",\
  height=3, command=sonos_action_fav_radio2)
sonosLBCButton = tk.Button(sonosFavouritesFrame, text="LBC",\
  height=3, command=sonos_action_fav_lbc)
sonos6MusicButton.grid(sticky="ew")
sonos1BTNButton.grid(row=0, column=1, sticky="ew")
sonosRadio2Button.grid(row=0, column=2, sticky="ew")
sonosLBCButton.grid(row=0, column=3, sticky="ew")
sonosFavouritesFrame.columnconfigure(0, weight=1)
sonosFavouritesFrame.columnconfigure(1, weight=1)
sonosFavouritesFrame.columnconfigure(2, weight=1)
sonosFavouritesFrame.columnconfigure(3, weight=1)

# Trigger recurring autoupdate methods
update_tasks()
update_sonos()
update_sonos_favorites()
check_backlight_timer()
root.mainloop()
