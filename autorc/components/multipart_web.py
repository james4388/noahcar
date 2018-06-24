import asyncio
import cv2
from aiohttp import web, MultipartWriter
from camera import WebCam


async def mjpeg_handler(request):
    my_boundary = "boundarydonotcross"
    response = web.StreamResponse(status=200, reason='OK', headers={
        'Content-Type': 'multipart/x-mixed-replace; '
                        'boundary=--%s' % my_boundary,
    })
    await response.prepare(request)
    wc = WebCam()
    encode_param = (int(cv2.IMWRITE_JPEG_QUALITY), 90)

    while True:
        frame = wc.process()
        if frame is None:
            continue
        with MultipartWriter('image/jpeg', boundary=my_boundary) as mpwriter:
            result, encimg = cv2.imencode('.jpg', frame, encode_param)
            data = encimg.tostring()
            mpwriter.append(data, {
                'Content-Type': 'image/jpeg'
            })
            await mpwriter.write(response)
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
