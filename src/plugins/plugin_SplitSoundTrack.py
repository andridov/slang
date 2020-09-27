import io
import sys
import time

from pydub import AudioSegment
from plugin_Base import PluginBase

from subtitles import SubTitle


class SplitSoundTrack(PluginBase):
    def __init__(self, env, name):
        super().__init__(env, name)


    def process(self, param_map=None):
        self.env.print_env()

        SubTitle

        sound = AudioSegment.from_mp3(
            "c:\\Home\\Download\\now_playing\\4.mp3")
            # self.env["sl_sst_sound_track_file"])

        # len() and slicing are in milliseconds
        halfway_point = len(sound) / 2
        second_half = sound[halfway_point:]

        # Concatenation is just adding
        second_half_3_times = second_half

        # writing mp3 files is a one liner
        second_half_3_times.export(
            "c:\\Home\\Download\\now_playing\\5.mp3", format="mp3")



