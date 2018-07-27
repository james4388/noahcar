import asyncio
import time
from aiohttp import web

from autorc.nodes import AsyncNode


class MjpegStreamer(AsyncNode):
    ''' Stand alone mjpeg streamer (for testing only) '''
    def __init__(self, context, *, inputs=('cam/image-jpeg', ), host='0.0.0.0',
                 port=8888, frame_rate=24, **kwargs):
        super(MjpegStreamer, self).__init__(context, inputs=inputs, **kwargs)
        if not inputs or len(inputs) < 1:
            raise Exception('Input key (jpeg stream) is required')
        self.host = host
        self.port = port
        self.is_run = True
        self.frame_rate = frame_rate

    async def start_up(self):
        app = web.Application(logger=self.logger)
        self.app = app
        app.router.add_route('GET', "/", self.index)
        app.router.add_route('GET', "/image", self.handler)
        # Blocking run
        # web.run_app(app, host=self.host, port=self.port)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host=self.host, port=self.port)
        await site.start()

    async def shutdown(self):
        super(MjpegStreamer, self).shutdown()
        self.is_run = False
        await self.app.shutdown()
        await self.runner.cleanup()

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
            max_sleep_time = 1.0 / self.frame_rate
            while self.is_run:
                start_time = time.time()
                frame = self.context.get(self.inputs[0])
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

                sleep_time = max_sleep_time - (time.time() - start_time)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
        except asyncio.CancelledError:
            print('Client connection closed')
        finally:
            if response is not None:
                await response.write_eof()
        return response
