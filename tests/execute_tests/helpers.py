from contextlib import contextmanager

from tests.testutils import patch

from execute import read_stream


@contextmanager
def execute_patch(obj, stdout_stream, stderr_stream, stdout_cb, stderr_cb):
    def execute(cmd, stdout_callback, stderr_callback, buffer_line=True):
        print('PATCH')

        while True:
            result_stdout = None
            result_stderr = None

            if stdout_stream is not None:
                result_stdout = read_stream(stdout_stream, stdout_cb, buffer_line=buffer_line)
            if stderr_stream is not None:
                result_stderr = read_stream(stderr_stream, stderr_cb, buffer_line=buffer_line)

            if result_stdout is None and result_stderr is None:
                break

        if stdout_stream is not None:
            read_stream(stdout_stream, stdout_cb, buffer_line=buffer_line, last=True)
        if stderr_stream is not None:
            read_stream(stderr_stream, stderr_cb, buffer_line=buffer_line, last=True)
        return 0

    with patch(obj, 'execute', execute):
        yield
