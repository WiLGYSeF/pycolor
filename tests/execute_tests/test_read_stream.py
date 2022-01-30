from io import BytesIO
import os
import typing
import unittest

from src.pycolor.execute.execute import read_stream

class ReadStreamTest(unittest.TestCase):
    def test_empty(self):
        stream = StreamObj(b'')
        self.assertEqual([], stream.read_stream())
        self.assertEqual([], stream.read_stream(last=True))

    def test_oneline_last(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            ['abc\n'],
            stream.read_stream(last=True)
        )

    def test_oneline(self):
        stream = StreamObj(b'abc\n')
        self.assertEqual(
            ['abc\n'],
            stream.read_stream()
        )

    def test_oneline_last_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual(
            ['abc'],
            stream.read_stream(last=True)
        )

    def test_oneline_nolf(self):
        stream = StreamObj(b'abc')
        self.assertEqual([], stream.read_stream())

    def test_twoline_last(self):
        stream = StreamObj([
            b'abc\n123\n',
            b'123\n'
        ])

        callback_data = stream.read_stream(last=True)
        self.assertEqual('abc\n', callback_data[0])
        self.assertEqual('123\n', callback_data[1])

    def test_twoline(self):
        stream = StreamObj([
            b'abc\n123\n'
        ])

        callback_data = stream.read_stream()
        self.assertEqual('abc\n', callback_data[0])
        self.assertEqual('123\n', callback_data[1])

    def test_twoline_late_lf_one(self):
        stream = StreamObj([
            b'abc',
            b'\n123\n'
        ])

        self.assertEqual([], stream.read_stream())
        callback_data = stream.read_stream()
        self.assertEqual('abc\n', callback_data[0])
        self.assertEqual('123\n', callback_data[1])

    def test_twoline_late_lf_multi(self):
        stream = StreamObj([
            b'ab',
            b'c',
            b'\n1',
            b'23',
            b'',
            b'\n'
        ])

        self.assertEqual([], stream.read_stream())
        self.assertEqual([], stream.read_stream())
        self.assertEqual(
            ['abc\n'],
            stream.read_stream()
        )
        self.assertEqual([], stream.read_stream())
        self.assertEqual([], stream.read_stream())
        self.assertEqual(
            ['123\n'],
            stream.read_stream()
        )

    def test_twoline_last_nolf(self):
        stream = StreamObj([
            b'ab',
            b'c',
            b'\n123'
        ])

        self.assertEqual([], stream.read_stream())
        self.assertEqual([], stream.read_stream())
        self.assertEqual(
            ['abc\n'],
            stream.read_stream()
        )
        self.assertEqual(
            ['123'],
            stream.read_stream(last=True)
        )

class StreamObj:
    def __init__(self,
        data: typing.Union[typing.List[bytes], bytes],
        callback: typing.Optional[typing.Callable[[str], None]] = None
    ):
        self._stream: BytesIO
        self._data: typing.Union[typing.List[bytes], bytes]
        self._data_idx: typing.Optional[int] = None
        self.set_stream(data)

        self._callback_func: typing.Optional[typing.Callable[[str], None]] = callback

        self._callback_data: str = ''
        self._last_callback_data: typing.List[str] = []

    def set_stream(self, data: typing.Union[typing.List[bytes], bytes]) -> None:
        self._stream = BytesIO()
        self._data = data
        self._data_idx = None

        if isinstance(data, list):
            self._stream.write(data[0])
            self._data_idx = 1
        else:
            self._stream.write(data)
        self._stream.seek(0)

    def callback(self, data: str) -> None:
        self._callback_data += data
        self._last_callback_data.append(data)

        if callable(self._callback_func):
            self._callback_func(data)

    def read_stream(self, encoding: str = 'utf-8', last: bool = False) -> typing.List[str]:
        self._last_callback_data = []

        read_stream(
            self._stream,
            self.callback,
            self._stream.read(),
            encoding=encoding,
            last=last
        )

        if isinstance(self._data, list) and self._data_idx is not None:
            if self._data_idx < len(self._data):
                self._stream.write(self._data[self._data_idx])
                self._stream.seek(-len(self._data[self._data_idx]), os.SEEK_CUR)
                self._data_idx += 1

        return self._last_callback_data
