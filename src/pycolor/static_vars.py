# https://stackoverflow.com/a/279586
def static_vars(**kwargs):
    def decorate(func):
        for k, val in kwargs.items():
            setattr(func, k, val)
        return func
    return decorate
