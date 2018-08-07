from aiohttp import web, WSMsgType, WSCloseCode
import aiohttp_jinja2
import logging
import jinja2
import json
import os
import uuid
from aiohttp_session import get_session, setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage

from autorc.config import config, Config
from autorc.nodes import AsyncNode
from autorc.nodes.mjpeg import MjpegStreamer


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONSTANTS = Config(config_file=os.path.join(BASE_DIR, 'constants.json'))


class StaticViews(object):

    ''' Serve static views '''
    @aiohttp_jinja2.template('index.html')
    async def index(self, request):
        session = await get_session(request)
        if config.SESSION_KEY not in session:
            session[config.SESSION_KEY] = str(uuid.uuid4())
        logger.debug('Session KEY %s', session[config.SESSION_KEY])
        return {'key': session[config.SESSION_KEY]}


class SocketController(object):
    ''' Controll car via web socket controller '''

    USERS = 'ws_ctlr_user'
    _counter = 0    # Connection counter

    def __init__(self, app: web.Application, update_context: None,
                 logger=None):
        self.app = app
        self.logger = logger or logging.getLogger(__name__)
        if callable(update_context):
            self.update_context = update_context
        else:
            self.update_context = lambda x: x
        if self.USERS not in app:
            app[self.USERS] = {}
            logger.debug('Socket started! Waiting for connection')
            app.on_shutdown.append(self.on_shutdown)

    async def on_shutdown(self, *args, **kwargs):
        logger.debug('Notify server closing to all sockets')
        for user in list(self.app[self.USERS].values()):
            await user['ws'].close(
                code=1000, message='Server is shutting down')

    def user_json(self, user):
        ''' Return filtered user to json encoder '''
        return {k: user[k] for k in ['id', 'name']}

    async def send(self, socket: web.WebSocketResponse, data, *,
                   compress=None, dtype='json'):
        ''' Send data throw socket '''
        try:
            if dtype == WSMsgType.BINARY or isinstance(
                    data, (bytes, bytearray, memoryview)):
                await socket.send_bytes(data, compress=compress)
            elif dtype == 'json' or isinstance(data, (dict, list)):
                await socket.send_json(data, compress=compress)
        except Exception as ex:
            logger.debug('Exception on socket send: %s', str(ex))

    async def broadcast(self, data, *, compress=None, dtype='json'):
        users = self.app[self.USERS].values()
        logger.debug('Broadcasting message to %d sockets', len(users))
        for user in users:
            await self.send(user['ws'], data, compress=compress, dtype=dtype)

    async def disconnect(self, user, reconnect=False):
        # Close connection
        logger.debug('%s (%s) has %s', user['name'], user['id'],
                     'reconnect' if reconnect else 'disconnect')
        if user['id'] in self.app[self.USERS]:
            try:
                await self.app[self.USERS][user['id']]['ws'].close()
            except Exception:
                pass
            del self.app[self.USERS][user['id']]

        if not reconnect:
            # Broadcast goodbye message
            await self.broadcast({
                'action': CONSTANTS.USER_DISCONNECT,
                'user': self.user_json(user),
                'users': [
                    self.user_json(user)
                    for user in self.app[self.USERS].values()
                ]
            })

    async def add_user(self, ws: web.WebSocketResponse, _id):
        self._counter += 1
        display_name = 'User %d' % self._counter
        logger.debug('%s (%s) has connected', display_name, _id)

        # Register connection
        user = {
            'ws': ws,
            'id': _id,
            'name': display_name
        }
        # Disconnect previous user if any
        if _id in self.app[self.USERS]:
            try:
                await self.disconnect(user, reconnect=True)
            except Exception:
                pass
        self.app[self.USERS][_id] = user

        # Broadcast welcome message
        await self.broadcast({
            'action': CONSTANTS.USER_CONNECT,
            'user': self.user_json(user),
            'users': [
                self.user_json(user) for user in self.app[self.USERS].values()
            ]
        })
        return user

    async def on_message(self, user, msg):
        # TODO rewrite this to call Node's method to controll inputs, outputs
        if msg.type == WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
            except (ValueError, TypeError):
                logger.debug('Message is an invalid JSON')
                print(data)
                return
            action = data.get('action')
            if action == CONSTANTS.SEND_MESSAGE_REQUEST:
                await self.broadcast({
                    'action': CONSTANTS.SEND_MESSAGE_RESPONSE,
                    'user': self.user_json(user),
                    'message': data.get('message')
                })
            elif action == CONSTANTS.RENAME_REQUEST:
                user['name'] = data.get('value')
                await self.broadcast({
                    'action': CONSTANTS.RENAME_RESPONSE,
                    'user': self.user_json(user),
                    'users': [
                        self.user_json(user)
                        for user in self.app[self.USERS].values()
                    ]
                })
            elif action == CONSTANTS.USER_LIST_REQUEST:
                await self.send({
                    'action': CONSTANTS.USER_LIST_RESPONSE,
                    'users': [
                        self.user_json(user)
                        for user in self.app[self.USERS].values()
                    ]
                })
            elif action == CONSTANTS.VEHICLE_STATS_REQUEST:
                ''' Current vehicle params '''
                await self.send({
                    'action': CONSTANTS.VEHICLE_STATS_RESPONSE,
                    'vehicle_stats': {
                        'MAX_SPEED': config.MAX_SPEED
                    }
                })
            elif action == CONSTANTS.VEHICLE_STEER:
                steering_percent = data.get('value', 0)
                self.update_context('user/steering', steering_percent)
            elif action == CONSTANTS.VEHICLE_THROTTLE:
                throttle_percent = data.get('value', 0)
                self.update_context('user/throttle', throttle_percent)
            elif action == CONSTANTS.TRAINING_RECORD_START:
                self.logger.info('You are on cam. smile')
                self.update_context('training/record', True)
            elif action == CONSTANTS.TRAINING_RECORD_END:
                self.logger.info('Done')
                self.update_context('training/record', False)
            elif action == CONSTANTS.PILOT_ENGAGE_START:
                self.logger.info('Auto pilot is on')
                self.update_context('pilot/engage', True)
            elif action == CONSTANTS.PILOT_ENGAGE_END:
                self.logger.info('Auto pilot is off')
                self.update_context('pilot/engage', False)

    async def handler(self, request):
        ws = web.WebSocketResponse(heartbeat=1.0, timeout=1.0, autoping=True,
                                   autoclose=True)
        ws_ready = ws.can_prepare(request)
        if not ws_ready.ok:
            logger.debug('Cannot prepare ws connection')
            raise web.HTTPFound('/')
        await ws.prepare(request)

        # Get session
        session = await get_session(request)
        if config.SESSION_KEY not in session:
            await ws.close(code=WSCloseCode.POLICY_VIOLATION,
                           message=b'Please access using index page')
            raise web.HTTPFound('/')
        _id = session[config.SESSION_KEY]

        user = await self.add_user(ws, _id)

        # Wait for messages
        async for msg in ws:
            if msg.type == WSMsgType.ERROR:
                logger.error('WS connection closed with exception %s',
                             ws.exception())
            else:
                await self.on_message(user, msg)

        await self.disconnect(user)
        return ws


class WebController(AsyncNode):
    def __init__(self, context, *, host='0.0.0.0', port=8080,
                 mjpeg_frame_rate=24, **kwargs):
        super(WebController, self).__init__(context, inputs={
            'update_stats': ('pilot/steering', 'pilot/throttle')
        }, **kwargs)
        self.host = host
        self.port = port
        self.mjpeg_frame_rate = mjpeg_frame_rate

    def config_router(self, router, app):
        views = StaticViews()
        sc = SocketController(app, update_context=self.update,
                              logger=self.logger)
        self.socket = sc
        mjpeg = MjpegStreamer(self.context, frame_rate=self.mjpeg_frame_rate)
        self.sc = sc
        self.mjpeg = mjpeg
        router.add_static('/static/', os.path.join(BASE_DIR, 'static'))
        router.add_get('/', views.index)
        router.add_get('/ws', sc.handler)
        router.add_get('/mjpeg_stream', mjpeg.handler)

    async def update_stats(self, *args):
        try:
            await self.socket.broadcast({
                'action': CONSTANTS.VEHICLE_STATS_RESPONSE,
                'vehicle_stats': {
                    'throttle': 0,
                    'steering': 0,
                    'pilot/throttle': self.context.get('pilot/throttle'),
                    'pilot/steering': self.context.get('pilot/steering'),
                }
            })
        except Exception:
            pass

    async def shutdown(self):
        await self.socket.on_shutdown()
        await super(WebController, self).shutdown()

    async def start_up(self):
        app = web.Application(logger=self.logger)
        self.app = app

        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(
            os.path.join(BASE_DIR, 'templates')))

        self.config_router(app.router, app)

        secret = config.WEB_CONTROLLER_SECRET_KEY
        if isinstance(secret, str):
            secret = secret.encode('utf-8')
        setup_session(
            app, EncryptedCookieStorage(secret))

        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, host=self.host, port=self.port)
        await site.start()
        print('=======================')
        print('Web controller start!')
        print('Navigate to:', 'http://%s:%s' % (self.host, self.port))
        print('=======================')

    def collect_static(self):
        ''' Build static files for ui application (React) '''
        import subprocess
        UI_BASE = os.path.join(BASE_DIR, 'ui')
        if not os.path.isdir(os.path.join(UI_BASE, 'node_modules/')):
            # Install node dependencies
            logger.info('Install UI dependencies')
            subprocess.run(["npm", "install", "--prefix", UI_BASE])
        if not os.path.isdir(os.path.join(UI_BASE, 'node_modules/')):
            logger.error('Could not install ui dependencies. Please cd to %s'
                         'and run `npm install`', UI_BASE)
            return False
        logger.info('Building UI')
        subprocess.run(["npm", "run", "build", "--prefix", UI_BASE])


if __name__ == '__main__':
    from multiprocessing import Process, Manager, Event
    from autorc.nodes.camera import CVWebCam, PGWebCam
    # from autorc.nodes.engine import Engine
    import time
    with Manager() as manager:
        context = manager.dict()
        stop_event = Event()

        p_wc = Process(target=WebController.start,
                       args=(context, stop_event, ))
        p_wc.daemon = True
        p_wc.start()

        p_cam = Process(target=CVWebCam.start,
                        args=(context, stop_event, ))
        p_cam.daemon = True
        p_cam.start()

        '''
        p_eng = Process(target=Engine.start, args=(context, stop_event, ))
        p_eng.daemon = True
        p_eng.start()'''

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print('Force shutdown server')
            stop_event.set()
        time.sleep(2)
