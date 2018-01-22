#!/usr/bin/env python3

import sys
import rtmpsource
import videomixer
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gst, GstBase, Gtk, GObject


class Mix:
    input_test_url = 'rtmp://stream-0-stage.taggedvideo.com/live/mishatest1'
    input_testpattern_url = 'rtmp://stream-0-stage.taggedvideo.com/live/testpattern'
    output_test_url = 'rtmp://stream-0-stage.taggedvideo.com/live/rtmpsink'

    def __init__(self):
        Gst.init(sys.argv)

        print("Creating a videomixer...")
        videomix = videomixer.VideoMixer(self.output_test_url)
        videomix.add_rtmp_source(self.input_testpattern_url, 0, 0, 2)
        videomix.add_rtmp_source(self.input_test_url, 20, 20, 10)
        videomix.add_rtmp_source(self.input_test_url, 440, 20, 30)
        videomix.play()


start = Mix()
Gtk.main()
# asyncio -- preferred. transforms async event driven code into seq code.
#            explicit async boundaries. non-blocking i/o server.
# idle add (Gtk) -- post to main loop using g_idle_add ?
