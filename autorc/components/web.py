import asyncio
import cv2
import numpy as np
from aiohttp import web, MultipartWriter
from camera import WebCam
from PIL import Image
from io import BytesIO


async def mjpeg_handler(request):
    boundary = "boundarydonotcross"
    response = web.StreamResponse(status=200, reason='OK', headers={
        'Content-Type': 'multipart/x-mixed-replace; '
                        'boundary=--%s' % boundary,
        'Cache-Control': 'no-cache'
    })
    await response.prepare(request)
    wc = WebCam()
    # encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)

    while True:
        frame = wc.process()
        '''
        arr = np.uint8(frame)
        img = Image.fromarray(arr)
        imgfile = BytesIO()
        img.save(imgfile, format='jpeg')
        data = imgfile.getvalue()
        '''
        if frame is not None:
            result, encimg = cv2.imencode('.jpg', frame)
            data = encimg.tostring()

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

    wc.shutdown()
    return response


async def index(request):
    return web.Response(text='<img src="/image"/>', content_type='text/html')


async def start_server(loop, address, port):
    app = web.Application(loop=loop)
    app.router.add_route('GET', "/", index)
    app.router.add_route('GET', "/image", mjpeg_handler)
    return await loop.create_server(app.make_handler(), address, port)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server(loop, '0.0.0.0', 8888))
    print("Server ready!")

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting Down!")
        loop.close()
