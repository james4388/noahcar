import unittest
import time
from multiprocessing import Process, Manager, Event
from autorc.nodes import AsyncNode


class TestAsyncNode(AsyncNode):
    def __init__(self, context):
        super(TestAsyncNode, self).__init__(context, inputs={
            'on_key1_change': 'key1',
            'on_key23_change': ('key2', 'key3')
        }, outputs={
            'on_key1_change': 'test_result_key1',
            'on_key23_change': ('test_result_key23'),
            'process_loop': 'test_counter'
        })
        self.counter = 0

    async def on_key1_change(self, key1):
        self.logger.info('Got new key1 %s', key1)
        return key1 + 1

    async def on_key23_change(self, key2, key3):
        return key2 + key3

    async def process_loop(self):
        self.counter += 1
        return self.counter


class NodeTestCase(unittest.TestCase):
    def run(self, result=None):
        with Manager() as manager:
            context = manager.dict()
            stop_event = Event()
            p = Process(target=TestAsyncNode.start, args=(context, stop_event))
            p.daemon = True
            p.start()
            self.manager = manager
            self.context = context
            super(NodeTestCase, self).run(result)
            stop_event.set()

    def test_node_single_key(self):
        self.context['key1'] = 1
        self.context['key2'] = 3
        time.sleep(1)   # Wait for result
        self.assertEqual(self.context.get('test_result_key1'), 2)
        self.context['key1'] = 3
        self.context['key1__timestamp'] = time.time()
        time.sleep(1)   # Wait for result
        self.context['key3'] = 4
        self.assertEqual(self.context.get('test_result_key1'), 4)
        self.assertEqual(self.context.get('test_counter') > 5, True)
        time.sleep(1)
        self.assertEqual(self.context.get('test_result_key23'), 7)
        print('Total main loop', self.context.get('test_counter'))
