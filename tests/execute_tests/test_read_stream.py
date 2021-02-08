from io import BytesIO
import unittest

from execute import read_stream


class ReadStreamTest(unittest.TestCase):
    def test_empty(self):
        stream = StreamObj(b'')
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=True),
            []
        )
        self.assertEqual(
            stream.read_stream(buffer_line=False, last=True),
            []
        )
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=False),
            []
        )
        self.assertEqual(
            stream.read_stream(buffer_line=False, last=False),
            []
        )

    def test_oneline_buflf_last(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=True),
            ['abc\n']
        )

    def test_oneline_buflf(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=False),
            ['abc\n']
        )

    def test_oneline(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            stream.read_stream(buffer_line=False, last=False),
            ['abc\n']
        )

    def test_oneline_buflf_last_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=True),
            ['abc']
        )

    def test_oneline_buflf_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(
            stream.read_stream(buffer_line=True, last=False),
            []
        )

    def test_oneline_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(
            stream.read_stream(buffer_line=False, last=False),
            ['abc']
        )

    def test_twoline_buflf_last(self):
        stream = StreamObj([
            b'abc\n',
            b'123\n'
        ])

        callback_data = stream.read_stream(buffer_line=True, last=True)
        for i in range(len(stream.data)):
            self.assertEqual(
                callback_data[i],
                stream.data[i].decode('utf-8')
            )

    def test_twoline_buflf(self):
        stream = StreamObj([
            b'abc\n',
            b'123\n'
        ])

        callback_data = stream.read_stream(buffer_line=True, last=False)
        for i in range(len(stream.data)):
            self.assertEqual(
                callback_data[i],
                stream.data[i].decode('utf-8')
            )


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
        self.last_callback_data.append(data)

        if callable(self.callback_func):
            self.callback_func(data)

    def read_stream(self, buffer_line=True, encoding='utf-8', last=False):
        self.last_callback_data = []
        read_stream(
            self.stream,
            self.callback,
            buffer_line=buffer_line,
            encoding=encoding,
            last=last
        )
        return self.last_callback_data
