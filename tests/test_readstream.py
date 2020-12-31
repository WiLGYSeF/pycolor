from io import BytesIO
import threading
import unittest

import pycolor


class ReadStreamTest(unittest.TestCase):
    def test_empty(self):
        stream = BytesIO()

        def callback(data):
            self.assertTrue(False)

        pycolor.read_stream(stream, callback, buffer_line=True, last=True)
        pycolor.read_stream(stream, callback, buffer_line=False, last=True)
        pycolor.read_stream(stream, callback, buffer_line=True, last=False)
        pycolor.read_stream(stream, callback, buffer_line=False, last=False)

    def test_oneline_buflf_last(self):
        stream = BytesIO()
        indata = b'abc\n'

        stream.write(indata)
        stream.seek(0)

        def callback(data):
            self.assertEqual(data, indata)

        pycolor.read_stream(stream, callback, buffer_line=True, last=True)

    def test_oneline_buflf_last_nolf(self):
        stream = BytesIO()
        indata = b'abc'

        stream.write(indata)
        stream.seek(0)

        def callback(data):
            self.assertEqual(data, indata)

        pycolor.read_stream(stream, callback, buffer_line=True, last=True)

    def test_oneline_buflf_nolf(self):
        stream = BytesIO()
        indata = b'abc'

        stream.write(indata)
        stream.seek(0)

        def callback(data):
            self.assertTrue(False)

        pycolor.read_stream(stream, callback, buffer_line=True, last=False)

    def test_oneline_nolf(self):
        stream = BytesIO()
        indata = b'abc'

        stream.write(indata)
        stream.seek(0)

        def callback(data):
            self.assertEqual(data, indata)

        pycolor.read_stream(stream, callback, buffer_line=False, last=False)

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

        pycolor.read_stream(stream, callback, buffer_line=True, last=True)
