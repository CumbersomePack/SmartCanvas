import moderngl_window as mglw
from threading import Thread

# fyi :https://moderngl-window.readthedocs.io/en/latest/reference/context/windowconfig.html#moderngl_window.context.base.window.WindowConfig


class Window(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "SmartCanvas"
    window_size = (1280, 720)
    aspect_ratio = None
    resizable = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def run(cls):
        mglw.run_window_config(cls)
