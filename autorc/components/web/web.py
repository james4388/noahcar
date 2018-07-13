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


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_KEY = 'session_key'


class Views:

    ''' Serve static views '''
    @aiohttp_jinja2.template('index.html')
    async def index(self, request):
        session = await get_session(request)
        if SESSION_KEY not in session:
            session[SESSION_KEY] = str(uuid.uuid4())
        logger.debug('Session KEY %s', session[SESSION_KEY])
        return {'key': session[SESSION_KEY]}


class SocketController:
    ''' Controll car via web socket controller '''

    USERS = 'ws_ctlr_user'
    _counter = 0    # Connection counter

    def __init__(self, app: web.Application):
        self.app = app
        if self.USERS not in app:
            app[self.USERS] = {}
            logger.debug('Socket started! Waiting for connection')

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
        except Exception:
            logger.debug('Exception on socket send')

    async def broadcast(self, data, *, compress=None, dtype='json'):
        users = self.app[self.USERS].values()
        logger.debug('Broadcasting message to %d sockets', len(users))
        for user in users:
            await self.send(user['ws'], data, compress=compress, dtype=dtype)

    async def disconnect(self, user):
        # Close connection
        logger.debug('%s (%s) has disconnected', user['name'], user['id'])
        if user['id'] in self.app[self.USERS]:
            del self.app[self.USERS][user['id']]

        # Broadcast goodbye message
        await self.broadcast({
            'action': 'disconnect',
            'user': self.user_json(user),
            'users': [
                self.user_json(user) for user in self.app[self.USERS].values()
            ]
        })

    async def on_message(self, user, msg):
        if msg.type == WSMsgType.TEXT:
            try:
                data = json.loads(msg.data)
                if data.get('action') == 'chat':
                    await self.broadcast({
                        'action': 'chat',
                        'user': self.user_json(user),
                        'message': data.get('message')
                    })
                elif data.get('action') == 'rename':
                    user['name'] = data.get('value')
                    await self.broadcast({
                        'action': 'rename',
                        'user': self.user_json(user),
                        'users': [
                            self.user_json(user)
                            for user in self.app[self.USERS].values()
                        ]
                    })
            except (ValueError, TypeError):
                logger.debug('Message is an invalid JSON')

    async def handler(self, request):
        app = self.app
        ws = web.WebSocketResponse(heartbeat=1.0)
        ws_ready = ws.can_prepare(request)
        if not ws_ready.ok:
            logger.debug('Cannot prepare ws connection')
            return web.HTTPFound('/')
        await ws.prepare(request)

        # Get session
        session = await get_session(request)
        if SESSION_KEY not in session:
            await ws.close(code=WSCloseCode.POLICY_VIOLATION,
                           message=b'Please access using index page')
            return
        _id = session[SESSION_KEY]
        self._counter += 1
        display_name = 'User %d' % self._counter
        logger.debug('%s (%s) has connected', display_name, _id)

        # Register connection
        user = {
            'ws': ws,
            'id': _id,
            'name': display_name
        }
        app[self.USERS][_id] = user

        # Broadcast welcome message
        await self.broadcast({
            'action': 'connect',
            'user': self.user_json(user),
            'users': [
                self.user_json(user) for user in app[self.USERS].values()
            ]
        })

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
    SECRET_KEY = b'Very secret KEY, keep safe !@#%*'

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
        setup_session(app, EncryptedCookieStorage(self.SECRET_KEY))

        self.app = app
        self.ioloop = ioloop
        return app

    def runserver(self):
        web.run_app(self.create_server())
