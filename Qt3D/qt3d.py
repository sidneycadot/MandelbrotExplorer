#! /usr/bin/env python3
from PySide6.QtGui import QOpenGLContext
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtWidgets import QApplication, QMainWindow


class MyOpenGLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()

    def initializeGL(self):
        print("resizeGL()")

    def resizeGL(self, w, h):
        print("resizeGL(w={}, h={})".format(w, h))

    def paintGL(self):
        f = QOpenGLContext.currentContext().functions()
        print("paintGL()")
        f.glClearColor(1.0, 1.0, 1.0, 1.0)
        f.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


class MyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        central_widget = MyOpenGLWidget()
        self.setCentralWidget(central_widget)


class MyApplication(QApplication):
    def __init__(self):
        super().__init__()
        self._main_window = MyMainWindow()
        self._main_window.show()


def main():
    app = MyApplication()
    app.exec()
    print("bye!")


if __name__ == "__main__":
    main()
