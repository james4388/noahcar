import asyncio
import cv2
from aiohttp import web
from camera import WebCam
from concurrent.futures import ProcessPoolExecutor


class MjpegStreamer():
    def __init__(self, webcam, loop):
        self.wc = webcam
        self.loop = loop

    async def get_image_frame(self):
        frame = self.wc.process()
        if frame is not None:
            encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)
            # Should not spawn ProcessPoolExecutor everytime like this
            result, encimg = await loop.run_in_executor(
                ProcessPoolExecutor(),
                cv2.imencode, '.jpg', frame, encode_param)
            return encimg.tostring()
        return None

    async def handler(self, request):
        if not self.wc:
            return web.Response(status=404, text='Webcam not found')
        print('Client connected', request.raw_headers)
        boundary = "boundarydonotcross"
        response = web.StreamResponse(status=200, reason='OK', headers={
            'Content-Type': 'multipart/x-mixed-replace; '
                            'boundary=--%s' % boundary,
            'Cache-Control': 'no-cache'
        })
        try:
            await response.prepare(request)
            while True:
                data = await self.get_image_frame()
                if data is not None:
                    try:
                        # Write header
                        await response.write(
                            '--{}\r\n'.format(boundary).encode('utf-8'))
                        await response.write(b'Content-Type: image/jpeg\r\n')
                        await response.write('Content-Length: {}\r\n'.format(
                                len(data)).encode('utf-8'))
                        await response.write(b"\r\n")
                        # Write data
                        await response.write(data)
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


async def index(request):
    return web.Response(text='<img src="/image"/>', content_type='text/html')


async def start_server(loop, address, port, webcam):
    app = web.Application(loop=loop)
    mjpeg = MjpegStreamer(webcam, loop)
    app.router.add_route('GET', "/", index)
    app.router.add_route('GET', "/image", mjpeg.handler)
    return await loop.create_server(app.make_handler(), address, port)


if __name__ == '__main__':
    wc = WebCam()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server(loop, '0.0.0.0', 8888, wc))
    print("Server ready!")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting Down!")
        loop.close()
