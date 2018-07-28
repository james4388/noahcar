import unittest
import time
import numpy as np
import multiprocessing
from multiprocessing import Process, Manager, Event
from autorc.nodes import Node


class TestNode(Node):
    def __init__(self, context):
        super(TestNode, self).__init__(context, inputs={
            'on_key1_change': 'key1',
            'on_key23_change': ('key2', 'key3'),
            'on_np_arr': 'keynp'
        }, outputs={
            'on_key1_change': 'test_result_key1',
            'on_key23_change': (
                'test_result_key2', 'test_result_key3', 'test_result_key23'),
            'on_np_arr': 'np_arr_result'
        })
        print('TestNode init from', multiprocessing.current_process().name)
        for cb in self.input_output_mapping:
            print('Method', cb, id(cb))

    def __getstate__(self):
        print(multiprocessing.current_process().name, 'get my state')
        return True

    def __setstate__(self, *args, **kwargs):
        print(multiprocessing.current_process().name, 'set my state')
        return True

    def on_key1_change(self, key1):
        self.logger.info('Got new key1 %s, from %s', key1,
                         multiprocessing.current_process().name)
        time.sleep(0.5)
        return key1 + 1

    def start_up(self):
        print('Start up from', multiprocessing.current_process().name)

    def on_key23_change(self, key2, key3):
        key2 = key2 + 3
        key3 = key3 - 4
        self.logger.info('Got new key2, key3, %s, %s', key2, key3)
        return key2, key3, key2 * key3

    def on_np_arr(self, nparr):
        self.logger.info('Got new nparray %s', nparr)
        print('Np array id proc', id(nparr))
        result = nparr + 2
        return result


class NodeTestCase(unittest.TestCase):
    def run(self, result=None):
        with Manager() as manager:
            context = manager.dict()
            stop_event = Event()
            p = Process(target=TestNode.start, args=(context, stop_event, ))
            p.daemon = True
            p.start()
            self.manager = manager
            self.context = context
            super(NodeTestCase, self).run(result)
            stop_event.set()

    def test_node_single_key(self):
        self.context['key1'] = 1
        time.sleep(1)   # Wait for result
        self.assertEqual(self.context.get('test_result_key1'), 2)
        self.context['key1'] = 3
        self.context['key1__timestamp'] = time.time()
        time.sleep(1)   # Wait for result
        self.assertEqual(self.context.get('test_result_key1'), 4)

    def test_node_key_pair(self):
        self.context['key2'] = 3
        # Should not do anything
        time.sleep(1)
        self.assertEqual(self.context.get('test_result_key2'), None)
        self.context['key3'] = 5
        time.sleep(1)
        self.assertEqual(self.context.get('test_result_key2'), 6)
        self.assertEqual(self.context.get('test_result_key3'), 1)
        self.assertEqual(self.context.get('test_result_key23'), 6)

    def test_nparray(self):
        arr = np.array([1, 2, 3, 4, 5])
        print('Np array id main', id(arr))
        self.context['keynp'] = arr
        time.sleep(1)
        self.assertEqual(np.array_equal(
            self.context.get('np_arr_result'),
            arr + 2
        ), True)
