#!/usr/bin/env python3

from aiohttp import web
import sys
import videomixer

class MixerApi:
    def __init__(self):
        self.videomixers = {}

        app = web.Application()
        print("Starting API server...")
        app.router.add_route('PUT',    '/stream/{stream_id}',                 self.create_handler)
        app.router.add_route('PUT',    '/stream/{stream_id}/{pip_id}',        self.add_stream_handler)
        # TODO: implement these.
        app.router.add_route('POST',   '/stream/{stream_id}/resize/{pip_id}', self.resize_handler)
        app.router.add_route('POST',   '/stream/{stream_id}/move/{pip_id}',   self.move_handler)
        app.router.add_route('DELETE', '/stream/{stream_id}/{pip_id}',        self.remove_handler)
        app.router.add_route('DELETE', '/stream/{stream_id}',                 self.delete_handler)
        self.app = app

    def get_handler(self):
        return self.app.make_handler()

    def add_stream_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        pip_id = request.match_info.get('pip_id')
        if stream_id in self.videomixers:
            print("Found stream {}".format(stream_id))
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')
        body = yield from request.json()
        stream_uri = body['stream_uri']
        # default to the origin (0, 0)
        xpos = body['x'] if 'x' in body else 0
        ypos = body['y'] if 'y' in body else 0
        # default to z=1 (background has z=0)
        zpos = body['z'] if 'z' in body else 1
        mixer = self.videomixers[stream_id]['mixer']
        mixer.add_rtmp_source(pip_id, stream_uri, xpos, ypos, zpos)
        # kick off the new source
        mixer.play()
        return web.Response(text='{"status": "OK"}')

    def resize_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Found stream")
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')
        return web.Response(text='{"status": "OK"}')

    def move_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Found stream")
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')
        return web.Response(text='{"status": "OK"}')

    def remove_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Found stream")
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')
        return web.Response(text='{"status": "OK"}')

    def delete_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Found stream")
        else:
            print("Could not find stream {}".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')
        return web.Response(text='{"status": "OK"}')

    def create_handler(self, request):
        stream_id = request.match_info.get('stream_id')
        if stream_id in self.videomixers:
            print("Stream {} already exists".format(stream_id))
            return web.Response(text='{"status": "FAIL"}')

        body = yield from request.json()
        print("Creating new stream {}".format(stream_id))
        output_uri = body['output_uri']
        bg_uri = body['bg_uri']
        print("Creating a videomixer for stream_id={} {} -> {}...".format(
              stream_id,
              bg_uri,
              output_uri))
        self.videomixers[stream_id] = {}
        mixer =  videomixer.VideoMixer(output_uri)
        self.videomixers[stream_id]['mixer'] = mixer
        self.videomixers[stream_id]['bg'] = mixer.add_rtmp_source('bg', bg_uri)
        mixer.play()
        return web.Response(text="{'status': 'OK'}")