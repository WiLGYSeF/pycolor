from io import BytesIO
import os
import unittest

from src.pycolor.execute import read_stream


class ReadStreamTest(unittest.TestCase):
    def test_empty(self):
        stream = StreamObj(b'')
        self.assertEqual(stream.read_stream(), [])
        self.assertEqual(stream.read_stream(last=True), [])

    def test_oneline_last(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(last=True),
            ['abc\n']
        )

    def test_oneline(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(),
            ['abc\n']
        )

    def test_oneline_last_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(
            stream.read_stream(last=True),
            ['abc']
        )

    def test_oneline_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(stream.read_stream(), [])

    def test_twoline_last(self):
        stream = StreamObj([
            b'abc\n123\n',
            b'123\n'
        ])

        callback_data = stream.read_stream(last=True)
        self.assertEqual(
            callback_data[0],
            'abc\n'
        )
        self.assertEqual(
            callback_data[1],
            '123\n'
        )

    def test_twoline(self):
        stream = StreamObj([
            b'abc\n123\n'
        ])

        callback_data = stream.read_stream()
        self.assertEqual(
            callback_data[0],
            'abc\n'
        )
        self.assertEqual(
            callback_data[1],
            '123\n'
        )

    def test_twoline_late_lf_one(self):
        stream = StreamObj([
            b'abc',
            b'\n123\n'
        ])

        self.assertEqual(stream.read_stream(), [])
        callback_data = stream.read_stream()
        self.assertEqual(
            callback_data[0],
            'abc\n'
        )
        self.assertEqual(
            callback_data[1],
            '123\n'
        )

    def test_twoline_late_lf_multi(self):
        stream = StreamObj([
            b'ab',
            b'c',
            b'\n1',
            b'23',
            b'',
            b'\n'
        ])

        self.assertEqual(stream.read_stream(), [])
        self.assertEqual(stream.read_stream(), [])
        self.assertEqual(
            stream.read_stream(),
            ['abc\n']
        )
        self.assertEqual(stream.read_stream(), [])
        self.assertEqual(stream.read_stream(), [])
        self.assertEqual(
            stream.read_stream(),
            ['123\n']
        )

    def test_twoline_last_nolf(self):
        stream = StreamObj([
            b'ab',
            b'c',
            b'\n123'
        ])

        self.assertEqual(stream.read_stream(), [])
        self.assertEqual(stream.read_stream(), [])
        self.assertEqual(
            stream.read_stream(),
            ['abc\n']
        )
        self.assertEqual(
            stream.read_stream(last=True),
            ['123']
        )


class StreamObj:
    def __init__(self, data, callback=None):
        self.set_stream(data)
        self.callback_func = callback

        self.callback_data = ''
        self.last_callback_data = None

    def set_stream(self, data):
        self.stream = BytesIO()
        self.data = data
        self.data_idx = None

        if isinstance(data, list):
            self.stream.write(data[0])
            self.data_idx = 1
        else:
            self.stream.write(data)

        self.stream.seek(0)

    def callback(self, data):
        self.callback_data += data
        self.last_callback_data.append(data)

        if callable(self.callback_func):
            self.callback_func(data)

    def read_stream(self, encoding='utf-8', last=False):
        self.last_callback_data = []

        read_stream(
            self.stream,
            self.callback,
            self.stream.read(),
            encoding=encoding,
            last=last
        )

        if self.data_idx is not None and self.data_idx < len(self.data):
            self.stream.write(self.data[self.data_idx])
            self.stream.seek(-len(self.data[self.data_idx]), os.SEEK_CUR)
            self.data_idx += 1

        return self.last_callback_data
