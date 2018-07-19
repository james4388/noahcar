import asyncio
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


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONSTANTS = Config(config_file=os.path.join(BASE_DIR, 'constants.json'))


class Views:

    ''' Serve static views '''
    @aiohttp_jinja2.template('index.html')
    async def index(self, request):
        session = await get_session(request)
        if config.SESSION_KEY not in session:
            session[config.SESSION_KEY] = str(uuid.uuid4())
        logger.debug('Session KEY %s', session[config.SESSION_KEY])
        return {'key': session[config.SESSION_KEY]}


class SocketController:
    ''' Controll car via web socket controller '''

    USERS = 'ws_ctlr_user'
    _counter = 0    # Connection counter

    def __init__(self, app: web.Application):
        self.app = app
        if self.USERS not in app:
            app[self.USERS] = {}
            logger.debug('Socket started! Waiting for connection')
            app.on_shutdown.append(self.on_shutdown)

    async def on_shutdown(self, *args, **kwargs):
        logger.debug('Notify server closing to all sockets')
        for user in list(self.app[self.USERS].values()):
            await user['ws'].close(
                code=1012, message='Server is shutting down')

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


class WebController():
    def config_router(self, router, app):
        views = Views()
        sc = SocketController(app)
        router.add_static('/static/', os.path.join(BASE_DIR, 'static'))
        router.add_get('/', views.index)
        router.add_get('/ws', sc.handler)

    def create_server(self, ioloop=None):
        ioloop = ioloop or asyncio.get_event_loop()
        app = web.Application(loop=ioloop, logger=logger)

        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(
            os.path.join(BASE_DIR, 'templates')))

        self.config_router(app.router, app)
        secret = config.WEB_CONTROLLER_SECRET_KEY
        if isinstance(secret, str):
            secret = secret.encode('utf-8')
        setup_session(
            app, EncryptedCookieStorage(secret))

        self.app = app
        self.ioloop = ioloop
        return app

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

    def runserver(self):
        if config.WEB_CONTROLLER_COLLECT_STATIC:
            self.collect_static()
        web.run_app(self.create_server(), host=config.WEB_CONTROLLER_HOST,
                    port=config.WEB_CONTROLLER_PORT)


if __name__ == '__main__':
    wc = WebController()
    wc.runserver()
