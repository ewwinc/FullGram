"""Full Gram `android_utils` on the Full Gram iOS runtime."""
import _fullgram_bridge
import _fullgram_java


class R:
    """Wraps a callable as a Java Runnable."""

    def __init__(self, fn):
        self.fn = fn

    def run(self):
        self.fn()

    def __call__(self):
        self.fn()


class OnClickListener:
    def __init__(self, fn):
        self.fn = fn
        _fullgram_java.note("unsupportedSdk", "android_utils.OnClickListener")

    def onClick(self, view):
        self.fn(view)


class OnLongClickListener:
    def __init__(self, fn):
        self.fn = fn
        _fullgram_java.note("unsupportedSdk", "android_utils.OnLongClickListener")

    def onLongClick(self, view):
        return bool(self.fn(view))


def run_on_ui_thread(func, delay=0):
    """There is no Python on the iOS main thread. The callable runs on a
    worker thread; UI calls it makes are forwarded to the main thread by the
    host."""
    _fullgram_java._run_later(func, delay)


def log(data):
    _fullgram_bridge.log("debug", _fullgram_java.current_plugin(), data)


def copy_to_clipboard(text):
    _fullgram_bridge.call("clipboard.set", text=str(text), showBulletin=True)
    return True
