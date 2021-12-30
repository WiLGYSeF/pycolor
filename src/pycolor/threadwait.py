import time
import typing

class Flag:
    def __init__(self):
        self.value: typing.Any = None

    def set(self, value: typing.Any = 1) -> None:
        self.value = value

    def unset(self) -> typing.Any:
        value = self.value
        self.value = None
        return value

    def is_set(self) -> bool:
        return self.value is not None

class ThreadWait:
    def __init__(self):
        self.flags = set()

    def get_flag(self) -> Flag:
        flag = Flag()
        self.flags.add(flag)
        return flag

    def free_flag(self, flag: Flag) -> None:
        self.flags.remove(flag)

    def wait(self, timeout: float = 0) -> None:
        remove = set()
        timers = {}
        for flag in self.flags:
            timers[flag] = time.perf_counter()

        while len(self.flags) != 0:
            for flag in self.flags:
                if not flag.is_set():
                    flag.set()
                    timers[flag] = time.perf_counter()
                else:
                    if time.perf_counter() - timers[flag] >= timeout:
                        remove.add(flag)
                        del timers[flag]
            self.flags -= remove
            remove.clear()
            time.sleep(0.0001)
