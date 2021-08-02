import time


class ThreadWait:
    def __init__(self):
        self.flags = set()

    def get_flag(self):
        flag = Flag()
        self.flags.add(flag)
        return flag

    def free_flag(self, flag):
        self.flags.remove(flag)

    def wait(self, timeout=0):
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

class Flag:
    def __init__(self):
        self.value = None

    def set(self, value=1):
        self.value = value

    def unset(self):
        value = self.value
        self.value = None
        return value

    def is_set(self):
        return self.value is not None
