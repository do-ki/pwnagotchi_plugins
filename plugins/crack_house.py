from pwnagotchi.ui.components import LabeledValue
from pwnagotchi.ui.view import BLACK
import pwnagotchi.ui.fonts as fonts
import pwnagotchi.plugins as plugins
import logging
import os
import time

class CrackHouse(plugins.Plugin):
    __author__ = '@V0rT3x, doki'
    __version__ = '1.0.2'
    __license__ = 'GPL3'
    __description__ = 'A plugin to display closest cracked network & its password'

    def __init__(self):
        self.ready = False
        self.crack_menu = []
        self.best_rssi = -1000
        self.best_crack = ['', '']

    def on_loaded(self):
        tmp_set = set()

        for file_path in self.options.get('files', []):
            try:
                with open(file_path) as f:
                    for line in f:
                        parts = line.strip().split(':', 1)
                        if len(parts) == 2:
                            tmp_set.add(line.strip())
            except Exception as e:
                logging.warning(f"[Crack House] Failed to read {file_path}: {e}")

        self.crack_menu = list(tmp_set)

        try:
            with open(self.options.get('saving_path', '/tmp/crackhouse_backup.txt'), 'w') as f:
                for entry in self.crack_menu:
                    f.write(entry + '\n')
        except Exception as e:
            logging.warning(f"[Crack House] Failed to write backup: {e}")

        self.ready = True
        logging.info("[Crack House]: Plugin loaded with %d entries." % len(self.crack_menu))

    def on_ui_setup(self, ui):
        ui.add_element(
            'crack_house',
            LabeledValue(
                color=BLACK,
                label='',
                value='',
                position=(int(self.options.get("x_pos", 0)), int(self.options.get("y_pos", 95))),
                label_font=fonts.Bold,
                text_font=fonts.Medium
            )
        )

    def on_unload(self, ui):
        with ui._lock:
            ui.remove_element('crack_house')

    def on_wifi_update(self, agent, access_points):
        if not self.ready:
            return

        if "Not-Associated" not in os.popen('iwconfig wlan0').read():
            return

        self.best_rssi = -1000
        self.best_crack = ['', '']

        for ap in access_points:
            hn = str(ap.get('hostname', ''))
            rssi = ap.get('rssi', -1000)
            for entry in self.crack_menu:
                parts = entry.split(':', 1)
                if len(parts) == 2 and hn == parts[0]:
                    if rssi > self.best_rssi:
                        self.best_rssi = rssi
                        self.best_crack = parts

    def on_ui_update(self, ui):
        if self.best_crack[0] and self.best_crack[1]:
            msg_ch = f"{self.best_crack[0]}:{self.best_crack[1]}"
        else:
            msg_ch = os.popen("tail -n 1 /root/handshakes/wpa-sec.cracked.potfile | awk -F: '{printf $3\":\"$4}'").read().strip()

        ui.set('crack_house', msg_ch)
