import os

import moderngl_window as mglw


class SetupScene(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Space Invaders"
    window_size = (1280, 720)
    aspect_ratio = 16 / 9
    resizable = True

    resource_dir = os.path.normpath(os.path.join(__file__, '../models'))
