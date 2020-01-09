# sonos-frame.py
import tkinter as tk
import soco
import os

class SonosFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.auto_refresh_time_ms = 1000 # 1 second in ms
        self.bedroom = soco.SoCo('192.168.1.208')
        self.kitchen = soco.SoCo('192.168.1.210')
        self.current_spkr = self.bedroom # Current speaker to display info for and control
        self.party_mode = True
        self.transport_state = ""
        self.sonos_favorites_dict = {}

        # sonosFrame layout
        self.sonosRoomsFrame = tk.Frame(self)
        self.sonosRoomsFrame.grid(sticky="ew")
        self.sonosVolumeFrame = tk.Frame(self)
        self.sonosVolumeFrame.grid(sticky="ew")
        self.sonosPlayingFrame = tk.Frame(self)
        self.sonosPlayingFrame.grid(sticky="ew")
        self.sonosTransportFrame = tk.Frame(self)
        self.sonosTransportFrame.grid(sticky="ew")
        self.sonosFavouritesFrame = tk.Frame(self)
        self.sonosFavouritesFrame.grid(sticky="ew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # sonosRoomsFrame layout
        self.sonosRoomsLabel = tk.Label(self.sonosRoomsFrame, text="Room")
        self.sonosRoomsLabel.grid(columnspan=2, sticky="nsew")
        self.sonosPartyLabel = tk.Label(self.sonosRoomsFrame, text="Party Mode")
        self.sonosPartyLabel.grid(row=0, column=2, sticky="nsew")
        self.sonosBedroomButton = tk.Button(self.sonosRoomsFrame, text="Bedroom",\
        height=3, relief=tk.SUNKEN, command=self.select_bedroom)
        self.sonosBedroomButton.grid(row=1, column=0)
        self.sonosKitchenButton = tk.Button(self.sonosRoomsFrame, text="Kitchen",\
        height=3, command=self.select_kitchen)
        self.sonosKitchenButton.grid(row=1, column=1)
        self.sonosPartyModeButton = tk.Button(self.sonosRoomsFrame, text="ENABLE",\
        height=3, command=self.toggle_party_mode)
        self.sonosPartyModeButton.grid(row=1, column=2)
        self.sonosRoomsFrame.columnconfigure(0, weight=1)
        self.sonosRoomsFrame.columnconfigure(1, weight=1)
        self.sonosRoomsFrame.columnconfigure(2, weight=1)

        # sonosVolumeFrame layout
        self.sonosVolumeSlider = tk.Scale(self.sonosVolumeFrame, from_=0, to=100,\
        orient=tk.HORIZONTAL, length=350, \
        sliderlength=15, width=30, command=self.update_sonosVolume)
        self.sonosVolumeSlider.grid()
        self.sonosVolumeFrame.columnconfigure(0, weight=1)

        # sonosPlayingFrame layout
        self.nowPlayingLabel = tk.Label(self.sonosPlayingFrame, text="waiting for info")
        self.nowPlayingLabel.grid()
        self.sonosPlayingFrame.columnconfigure(0, weight=1)
        self.sonosPlayingFrame.rowconfigure(0, weight=1)


        # sonosTransportFrame layout
        self.sonosRWDbutton = tk.Button(self.sonosTransportFrame, text="RWD",\
        height=3, width=10, command=self.sonos_action_rwd)
        self.sonosRWDbutton.grid()
        self.sonosPlayPausebutton = tk.Button(self.sonosTransportFrame, text="Play",\
        height=3, width=10, command=self.sonos_action_play_pause)
        self.sonosPlayPausebutton.grid(row=0, column=1)
        self.sonosFWDbutton = tk.Button(self.sonosTransportFrame, text="FWD",\
        height=3, width=10, command=self.sonos_action_fwd)
        self.sonosFWDbutton.grid(row=0, column=2)
        self.sonosTransportFrame.columnconfigure(0, weight=1)
        self.sonosTransportFrame.columnconfigure(1, weight=1)
        self.sonosTransportFrame.columnconfigure(2, weight=1)


        # sonosFavoritesFrame layout
        self.sonos6MusicButton = tk.Button(self.sonosFavouritesFrame, text="6 Music",\
        height=3, command=self.sonos_action_fav_6music)
        self.sonos1BTNButton = tk.Button(self.sonosFavouritesFrame, text="1BTN",\
        height=3, command=self.sonos_action_fav_1btn)
        self.sonosRadio2Button = tk.Button(self.sonosFavouritesFrame, text="Radio 2",\
        height=3, command=self.sonos_action_fav_radio2)
        self.sonosLBCButton = tk.Button(self.sonosFavouritesFrame, text="LBC",\
        height=3, command=self.sonos_action_fav_lbc)
        self.sonos6MusicButton.grid(sticky="ew")
        self.sonos1BTNButton.grid(row=0, column=1, sticky="ew")
        self.sonosRadio2Button.grid(row=0, column=2, sticky="ew")
        self.sonosLBCButton.grid(row=0, column=3, sticky="ew")
        self.sonosFavouritesFrame.columnconfigure(0, weight=1)
        self.sonosFavouritesFrame.columnconfigure(1, weight=1)
        self.sonosFavouritesFrame.columnconfigure(2, weight=1)
        self.sonosFavouritesFrame.columnconfigure(3, weight=1)


        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.update_sonos()
        self.update_sonos_favorites()

    def cursor_is_visible(self):
        cursor = self.parent.cget('cursor')
        if cursor == 'none':
            return False
        else:
            return True
    
    # Timed autoupdater for sonos
    def update_sonos(self):
        # Check if speakers are grouped and get list of speakers in group
        unique_zones=set()
        for player in self.current_spkr.group.members:
            unique_zones.add(player.player_name)
        separator_h = ", "
        zone_list = separator_h.join(unique_zones)
        #global party_mode
        if (len(unique_zones) > 1) :
            self.party_mode = True
        else:
            self.party_mode = False
        self.update_sonosPartyModeButton()
        
        # Update Volume Scale
        if not self.cursor_is_visible():
            # Then volume change has definitely come from an external source
            # so we update the slider position to reflect current setting
            self.sonosVolumeSlider.set(self.current_spkr.volume)
            
        # Update Now Playing info
        now_playing_label_text = f"Playing on: {zone_list}\n"
        self.current_coordinator = self.current_spkr.group.coordinator
        #global transport_state
        self.transport_state = self.current_coordinator.get_current_transport_info()\
        ["current_transport_state"]
        if self.transport_state == "PLAYING":
            self.sonosPlayPausebutton.configure(text="PAUSE")
            if self.current_coordinator.is_playing_radio:
                now_playing_label_text+=("Playing Radio\n")
                self.sonosRWDbutton.configure(state=tk.DISABLED)
                self.sonosFWDbutton.configure(state=tk.DISABLED)
            else:
                self.sonosRWDbutton.configure(state=tk.NORMAL)
                self.sonosFWDbutton.configure(state=tk.NORMAL)
                track_info=self.current_coordinator.get_current_track_info()
                now_playing_label_text+=(f"Current Track: {track_info['title']}\n")
                now_playing_label_text+=(f"Artist: {track_info['artist']}\n")
                now_playing_label_text+=(f"Album: {track_info['album']}\n")
        else:
            self.sonosPlayPausebutton.configure(text="PLAY")
            now_playing_label_text+=(f"Current status: {self.transport_state}")

        self.nowPlayingLabel.configure(text=now_playing_label_text)
        self.after(1000, self.update_sonos)

    # Timed self.autoupdater for sonos library favorites
    def update_sonos_favorites(self):
        #global sonos_favorites_dict
        sonos_favorites = self.bedroom.music_library.get_sonos_favorites()
        self.sonos_favorites_dict={}
        for fav in sonos_favorites:
            if "New Releases" in fav.title:
                self.sonos_favorites_dict[fav.title]="TBA"
            else:
                self.sonos_favorites_dict[fav.title]=fav.resources.pop().uri
        #schedule to run again in 5 minutes
        self.after((5*1000*60), self.update_sonos_favorites)

    def update_sonosPartyModeButton(self):
        #global party_mode
        if self.party_mode == True:
            self.sonosPartyModeButton.configure(text="UNGROUP", relief=tk.SUNKEN)
        else:
            self.sonosPartyModeButton.configure(text="GROUP", relief=tk.RAISED)

    def select_spkr(self, spkr):
        #global current_spkr
        self.current_spkr=spkr
        if spkr==self.bedroom:
            self.sonosBedroomButton.config(relief=tk.SUNKEN)
            self.sonosKitchenButton.config(relief=tk.RAISED)
        else:
            #other_spkr = bedroom
            self.sonosBedroomButton.config(relief=tk.RAISED)
            self.sonosKitchenButton.config(relief=tk.SUNKEN)

    # Change focus to bedroom zone  
    def select_bedroom(self):
        self.select_spkr(self.bedroom)

    # Change focus to kitchen zone  
    def select_kitchen(self):
        self.select_spkr(self.kitchen)

    def toggle_party_mode(self):
        #global party_mode
        if self.party_mode == True:
            self.current_spkr.unjoin()
        else:
            if self.current_spkr == self.bedroom:
                self.bedroom.join(self.kitchen)
            else:
                self.kitchen.join(self.bedroom)

    def update_sonosVolume(self, sliderPosition): 
        if self.cursor_is_visible():
            # Then slider movements are probably local user-driven 
            # If we were to override volume every time slider move is
            # detected then alarms (or any volume ramp) won't work... 
            self.current_spkr.volume = sliderPosition

    def sonos_action_rwd(self):
        try:
            self.current_spkr.group.coordinator.previous()
        except Exception as e:
            print("Uh-oh. Something went bad while trying to skip to previous track")
            print (e)

    def sonos_action_play_pause(self):
        if self.transport_state=="PLAYING":
            self.current_spkr.group.coordinator.pause()
        else:
            self.current_spkr.group.coordinator.play()

    def sonos_action_fwd(self):
        try:
            self.current_spkr.group.coordinator.next()
        except Exception as e:
            print("Uh-oh. Something went bad while trying to skip to next track")
            print (e)

    def sonos_play_radio_fav(self, channel_label):
        self.current_spkr.group.coordinator.play_uri(\
        uri=self.sonos_favorites_dict[channel_label], title=channel_label)

    def sonos_action_fav_6music(self):
        self.sonos_play_radio_fav("BBC Radio 6 Music")

    def sonos_action_fav_1btn(self):
        self.sonos_play_radio_fav("1BrightonFM")
    
    def sonos_action_fav_radio2(self):
        self.sonos_play_radio_fav("BBC Radio 2")

    def sonos_action_fav_lbc(self):
        self.sonos_play_radio_fav("LBC London")



def main():
    # Removes requirement to run ' export DISPLAY=:0.0 ' first in
    # terminal if running from remote SSH session
    os.environ['DISPLAY'] = ':0.0' 

    # create tkinter root    
    root = tk.Tk()
    
    # add our Frame to the root
    SonosFrame(root).pack(side="top", fill="both", expand=True)

    # cede control to tkinter scheduler
    root.mainloop()

# Allow the module to run standalone for testing
if __name__ == "__main__":
    main()