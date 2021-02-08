from io import BytesIO
import unittest

from execute import read_stream


class ReadStreamTest(unittest.TestCase):
    def test_empty(self):
        stream = StreamObj(b'')
        self.assertIsNone(stream.read_stream(buffer_line=True, last=True))
        self.assertIsNone(stream.read_stream(buffer_line=False, last=True))
        self.assertIsNone(stream.read_stream(buffer_line=True, last=False))
        self.assertIsNone(stream.read_stream(buffer_line=False, last=False))

    def test_oneline_buflf_last(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=True),
            'abc\n'
        )

    def test_oneline_buflf(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=False),
            'abc\n'
        )

    def test_oneline_last(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(buffer_line=False, last=True),
            'abc\n'
        )

    def test_oneline(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(buffer_line=False, last=False),
            'abc\n'
        )

    def test_oneline_buflf_last_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=True),
            'abc'
        )

    def test_oneline_buflf_nolf(self):
        stream = StreamObj(b'abc')
        self.assertIsNone(stream.read_stream(buffer_line=True, last=False))

    def test_oneline_last_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(
            stream.read_stream(buffer_line=False, last=True),
            'abc'
        )

    def test_oneline_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(
            stream.read_stream(buffer_line=False, last=False),
            'abc'
        )

    @unittest.skip
    def test_twoline_buflf_last(self):
        stream = BytesIO()
        indata = [
            b'abc\n',
            b'123\n'
        ]

        for line in indata:
            stream.write(line)
        stream.seek(0)

        counter = 0

        def callback(data):
            nonlocal counter
            self.assertEqual(data, indata[counter])
            counter += 1

        read_stream(stream, callback, buffer_line=True, last=True)


class StreamObj:
    def __init__(self, data, callback=None):
        self.data = data
        self.callback_func = callback

        self.set_stream(data)
        self.callback_data = ''

        self.last_callback_data = None

    def set_stream(self, data):
        self.stream = BytesIO()

        if isinstance(data, list):
            for segm in data:
                self.stream.write(segm)
        else:
            self.stream.write(data)

        self.stream.seek(0)

    def callback(self, data):
        self.callback_data += data
        self.last_callback_data = data

        if callable(self.callback_func):
            self.callback_func(data)

    def read_stream(self, buffer_line=True, encoding='utf-8', last=False):
        result = read_stream(
            self.stream,
            self.callback,
            buffer_line=buffer_line,
            encoding=encoding,
            last=last
        )
        if result is None or not result:
            self.last_callback_data = None
        return self.last_callback_data
