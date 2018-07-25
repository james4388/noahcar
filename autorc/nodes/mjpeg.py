import asyncio
from aiohttp import web

from autorc.nodes import Node


class MjpegStreamer(Node):
    ''' Stand alone mjpeg streamer '''
    def __init__(self, context, host='0.0.0.0', port=8888, **kwargs):
        super(MjpegStreamer, self).__init__(context, input_callback={
            'on_jpeg_frame': 'cam/image-jpeg'
        }, **kwargs)
        self.ctx = context
        self.host = host
        self.port = port
        self.is_run = True
        self.frame = None

    def start_up(self):
        # return
        loop = asyncio.get_event_loop()
        self.loop = loop
        app = web.Application(logger=self.logger)
        self.app = app
        app.router.add_route('GET', "/", self.index)
        app.router.add_route('GET', "/image", self.handler)
        print("Server ready!")
        # This will be hold until finish
        web.run_app(app, host=self.host, port=self.port)

    def shutdown(self):
        self.is_run = False
        self.app.shutdown()

    def on_jpeg_frame(self, jpeg_frame):
        print('New frame', len(self.context.get('cam/image-jpeg')))
        self.frame = jpeg_frame

    async def index(self, request):
        return web.Response(
            text='<img src="/image"/>', content_type='text/html')

    async def handler(self, request):
        self.logger.info('Client connected %s', request.raw_headers)
        boundary = "boundarydonotcross"
        response = web.StreamResponse(status=200, reason='OK', headers={
            'Content-Type': 'multipart/x-mixed-replace; '
                            'boundary=--%s' % boundary,
            'Cache-Control': 'no-cache'
        })
        try:
            await response.prepare(request)
            frame = None
            while self.is_run:
                while self.is_run and not self.input_updated('cam/image-jpeg'):
                    await asyncio.sleep(0.01)
                frame = self.ctx.get('cam/image-jpeg')
                if frame is not None:
                    try:
                        # Write header
                        await response.write(
                            '--{}\r\n'.format(boundary).encode('utf-8'))
                        await response.write(b'Content-Type: image/jpeg\r\n')
                        await response.write('Content-Length: {}\r\n'.format(
                                len(frame)).encode('utf-8'))
                        await response.write(b"\r\n")
                        # Write data
                        await response.write(frame)
                        await response.write(b"\r\n")
                        await response.drain()
                    except ConnectionResetError as ex:
                        print('Client connection closed')
                        break
                    except KeyboardInterrupt as ex:
                        print('Keyboard Interrupt')
                        break
                else:
                    print('Empty frame')
        except asyncio.CancelledError:
            print('Client connection closed')
        finally:
            if response is not None:
                await response.write_eof()
        return response
