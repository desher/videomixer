#!/usr/bin/env python3

import rtmpsource
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
from gi.repository import GObject, Gst, GstBase, GObject  # noqa: E402


class VideoMixer:

    def __init__(self, output_url):
        self.sources = {}
        self.output_url = output_url
        self.initialize()

    def play(self):
        print("Playing...")
        self.pipeline.set_state(Gst.State.PLAYING)
        return

    def pause(self):
        print("Pausing...")
        self.pipeline.set_state(Gst.State.PAUSED)
        return

    def add_rtmp_source(self, pip_id, location, xpos=0, ypos=0, zorder=0,
                        width=None, height=None):
        self.sources[pip_id] = rtmpsource.RtmpSource(location,
                                                     self.pipeline,
                                                     self.videomixer,
                                                     self.audiomixer,
                                                     xpos, ypos, zorder,
                                                     width, height)
        return self.sources[pip_id]

    def resize_rtmp_source(self, pip_id, width, height):
        if pip_id not in self.sources:
            raise Exception("pip_id={} does not exist".format(pip_id))
        self.sources[pip_id].resize(width, height)

    def move_rtmp_source(self, pip_id, x, y, z):
        if pip_id not in self.sources:
            raise Exception("pip_id={} does not exist".format(pip_id))
        self.sources[pip_id].move(x, y, z)

    def get_info(self):
        ret = {'pip_streams': {}}
        for pip_id in self.sources.keys():
            ret['pip_streams'][pip_id] = self.sources[pip_id].get_info()
        return ret

    def initialize(self):
        print("Creating pipeline...")
        self.pipeline = Gst.Pipeline.new()

        if self.pipeline is None:
            print("Could not create pipeline. Bailing out!")
            raise Exception("Could not create pipeline in videomixer")

        print("Creating objects and adding to pipeline...")
        self.videomixer = Gst.ElementFactory.make("videomixer")
        self.pipeline.add(self.videomixer)

        self.audiomixer = Gst.ElementFactory.make("audiomixer")
        self.pipeline.add(self.audiomixer)

        self.faac = Gst.ElementFactory.make("avenc_aac")
        self.pipeline.add(self.faac)

        self.x264enc = Gst.ElementFactory.make("x264enc")
        self.x264enc.set_property("threads", 0)
        self.pipeline.add(self.x264enc)

        self.x264caps = Gst.ElementFactory.make("capsfilter")
        caps = Gst.Caps.from_string("video/x-h264, profile=baseline")
        self.x264caps.set_property("caps", caps)
        self.pipeline.add(self.x264caps)

        self.flvmux = Gst.ElementFactory.make("flvmux")
        self.flvmux.set_property("streamable", 1)
        self.pipeline.add(self.flvmux)

        self.rtmpsink = Gst.ElementFactory.make("rtmpsink")
        self.rtmpsink.set_property("location", self.output_url)
        self.pipeline.add(self.rtmpsink)

        print("Linking elements")
        # Encode the output of videomixer to H.264
        ret = self.videomixer.link(self.x264enc)
        ret = ret and self.x264enc.link(self.x264caps)
        # Put the H.264 into an FLV container
        ret = ret and self.x264caps.link(self.flvmux)
        # Send the FLV to an RTMP sink
        ret = ret and self.flvmux.link(self.rtmpsink)

        print("Linking audio pipeline")
        ret = ret and self.audiomixer.link(self.faac)
        # XXX: uncomment below to enable audio pipeline.
        # NOTE: this causes videomixer to freeze currently.
        # ret = ret and self.faac.link(self.flvmux)

        if not ret:
            print("ERROR: Elements could not be linked.")
            raise Exception("Could not link elements in videomixer")
