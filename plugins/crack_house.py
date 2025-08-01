from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import pwnagotchi
import logging
import os
import subprocess
import requests
import time
from pwnagotchi.ai.reward import RewardFunction

READY = 0

#the list with hostname:password without duplicate for the plugin
CRACK_MENU = list()
BEST_RSSI = -1000
BEST_CRACK = ['']

class CrackHouse(plugins.Plugin):
    __author__ = '@V0rT3x, doki'
    __version__ = '1.0.1'
    __license__ = 'GPL3'
    __description__ = 'A plugin to display closest cracked network & its password'

    def on_loaded(self):
        global READY
        global CRACK_MENU
        tmp_line = ''
        tmp_list = list()
        crack_line = list()

#       loop to retreive all passwords of all files into a big list without dulicate
        for file_path in self.options['files']:
            with open(file_path) as f:
                for line in f:
                    tmp_line = str(line.rstrip().split(':',2)[-1:])[2:-2]
                    tmp_list.append(tmp_line)
        CRACK_MENU = list(set(tmp_list))
#       write all name:password inside a file as backup for the run
        with open(self.options['saving_path'], 'w') as f:
            for crack in CRACK_MENU:
                f.write(crack + '\n')
        READY = 1
        logging.info("[Crack House]: Plugin loaded.")
##        logging.info('[CRACK HOUSE] all paths: ' + str(self.options['files']))

    def on_ui_setup(self, ui):
        ui.add_element('crack_house', LabeledValue(color=BLACK, label='', value='',
                                                   position=(int(self.options["x_pos"]),
                                                             int(self.options["y_pos"])),
                                                   label_font=fonts.Bold, text_font=fonts.Medium))


    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('crack_house')

    def on_wifi_update(self, agent, access_points):
        global READY
        global CRACK_MENU
        global BEST_RSSI
        global BEST_CRACK
        tmp_crack = list()

        if READY == 1 and "Not-Associated" in os.popen('iwconfig wlan0').read():
            BEST_RSSI = -1000
            for network in access_points:
                hn = str(network['hostname'])
                ssi = network['rssi']
                for crack in CRACK_MENU:
                    tmp_crack = crack.rstrip().split(':')
                    tc = str(tmp_crack[0])
                    if hn == tc:
                        logging.info('[CRACK HOUSE] %s, pass: %s, RSSI: %d' % (tmp_crack[0], tmp_crack[1], ssi))
                        if ssi > BEST_RSSI:
                            BEST_RSSI = ssi
                            BEST_CRACK = tmp_crack
            logging.info('[CRACK HOUSE] %s, pass: %s, RSSI: %d' % (BEST_CRACK[0], BEST_CRACK[1], BEST_RSSI))

    def on_ui_update(self, ui):
        global CRACK_MENU
        global BEST_RSSI
        global BEST_CRACK
        near_rssi = str(BEST_RSSI)
		
		
        if BEST_RSSI != -1000:
            msg_ch = str(BEST_CRACK[0] + ':' + BEST_CRACK[1])
            ui.set('crack_house', '%s' % (msg_ch))
            logging.info('[CRACK HOUSE] %s, pass: %s, RSSI: %d' % (BEST_CRACK[0], BEST_CRACK[1], BEST_RSSI))
        else:
            last_line = 'tail -n 1 /root/handshakes/wpa-sec.cracked.potfile | awk -F: \'{printf $3 " - " $4}\''
            ui.set('crack_house', '%s' % (os.popen(last_line).read().rstrip()))



		
