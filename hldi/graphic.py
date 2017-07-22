import pygtk;
pygtk.require('2.0')
import gtk, gtk.gdk as gdk, gtk.gtkgl as gtkgl, gtk.gdkgl as gdkgl
from gtk import glade
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
from numpy import matrix

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders
import numpy as np
import gobject

class TestContext( BaseContext ):
    """Creates a simple vertex shader..."""

    def OnInit(self):
        VERTEX_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }""", GL_VERTEX_SHADER)

        FRAGMENT_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_FragColor = vec4( 0, 1, 0, 1 );
        }""", GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)

        self.vbo = vbo.VBO(
            array([
                [0, 1, 0],
                [-1, -1, 0],
                [1, -1, 0],
                [2, -1, 0],
                [4, -1, 0],
                [4, 1, 0],
                [2, -1, 0],
                [4, 1, 0],
                [2, 1, 0],
            ], 'f')
        )

    def Render(self, mode):
        """Render the geometry for the scene."""
        shaders.glUseProgram(self.shader)
        try:
            self.vbo.bind()
            try:
                glEnableClientState(GL_VERTEX_ARRAY);
                glVertexPointerf(self.vbo)
                glDrawArrays(GL_TRIANGLES, 0, 9)
            finally:
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY);

        finally:
            shaders.glUseProgram( 0 )



import time, threading


def hldiGlInit(self):
    # glutInit(sys.argv)
    # glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    # glutInitWindowSize(400, 400)
    # glutCreateWindow('xxx')
    #
    # glClearColor(0., 0., 0., 1.)
    # glShadeModel(GL_SMOOTH)
    # glEnable(GL_CULL_FACE)
    # glEnable(GL_DEPTH_TEST)
    # glEnable(GL_LIGHTING)
    # lightZeroPosition = [10., 4., 10., 1.]
    # lightZeroColor = [0.8, 1.0, 0.8, 1.0]  # green tinged
    # glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    # glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    # glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    # glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    # glEnable(GL_LIGHT0)
    # glutDisplayFunc(display)
    # glMatrixMode(GL_PROJECTION)
    # gluPerspective(40., 1., 1., 40.)
    # glMatrixMode(GL_MODELVIEW)
    # gluLookAt(0, 0, 10,
    #           0, 0, 0,
    #           0, 1, 0)
    # glPushMatrix()
    # glutMainLoop()

    # TestContext.ContextMainLoop()
    import sys

    # window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    # window.set_title("Zoom Pan Rotate")
    # window.set_size_request(640, 480)
    # window.connect("destroy", lambda event: gtk.main_quit())

    # vbox = gtk.VBox(False, 0)

    # window.add(vbox)

    # zpr = HldiGL()
    # zpr.draw = _demo_draw

    config = gdkgl.Config (
        mode = (
            gdkgl.MODE_RGBA |
            gdkgl.MODE_DOUBLE |
            gdkgl.MODE_DEPTH))

    area = gtkgl.DrawingArea (config)
    # area.set_size_request(
    #     width=200,
    #     height=200)

    # glClearColor(1., 0., 0., 1.)
    # glShadeModel(GL_SMOOTH)
    # glEnable(GL_CULL_FACE)
    # glEnable(GL_DEPTH_TEST)
    # glEnable(GL_LIGHTING)
    # lightZeroPosition = [10., 4., 10., 1.]
    # lightZeroColor = [0.8, 1.0, 0.8, 1.0]  # green tinged
    # glLightfv(GL_LIGHT0, GL_POSITION, lightZeroPosition)
    # glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor)
    # glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.1)
    # glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    # glEnable(GL_LIGHT0)
    # glMatrixMode(GL_PROJECTION)
    # gluPerspective(40., 1., 1., 40.)
    # glMatrixMode(GL_MODELVIEW)
    # gluLookAt(0, 0, 10,
    #           0, 0, 0,
    #           0, 1, 0)
    # glPushMatrix()
    area.connect('expose-event', on_draw)

    vbox = self.glade.get_object('glvbox')
    vbox.pack_start(area, True, True)
    area.show()

    def foo():
        # print(time.ctime())
        # on_draw(area, self)
        # threading.Timer(1, foo).start()
        # source_id = gobject.timeout_add(1000, foo)
        area.queue_draw()
        return True

    foo()

    source_id = gobject.timeout_add(1, foo)


    # window.show_all()

    # gtk.main()
    # self.glade.get_object("MainWindow").show_all()
degree = 360
def on_draw (area, _):

    """ Handles an `expose-event` event. Draws in the test OpenGL drawing
        area.
    """

    drawable = area.get_gl_drawable ()
    context = area.get_gl_context ()

    if not drawable.gl_begin(context):
        return

    allocation = area.get_allocation()
    viewport_width = float (allocation.width)
    viewport_height = float (allocation.height)

    # gluPerspective does not accept named parameters.
    # Use variable instead, for readability.
    # Z negative forward oriented.

    aspect =  viewport_width / viewport_height
    fovy   =  35.0 # The one which looks to most natural.
    z_near =   2.0 # Enough for a moderately sized sample model.
    z_far  =  -2.0 # Idem.

    # glTranslate does not accept named parameters.
    # Use variable instead, for readability.
    # Z positive forward oriented.

    projection_dx =  0.0
    projection_dy =  0.0
    projection_dz = -3.0

    # Reset picture.
    glViewport (0, 0, int (viewport_width), int (viewport_height))
    glClearColor(1., 1., 1., 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Model defined in default coordinates.
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Projection using perspective and a few units backward.
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovy, aspect, z_near, z_far)
    glTranslate(projection_dx, projection_dy, projection_dz)

    # Use the line below instead of the two above, for non perspective view.
    # glOrtho (-aspect, +aspect, -1.0, +1.0, zNear, zFar)
    glColor3f(0.3, 0.3, 0.3)

    glPointSize(10.0)

    pi_degree = 2 * np.pi / 360
    global degree

    degree = degree + 1
    np.sin(degree * pi_degree)

    # print 'degress: %d' % degree

    if degree > 360:
        degree = -360

    x = degree / 360.

    # glEnable(GL_POINT_SPRITE)


    glEnable(GL_POINT_SMOOTH)
    # glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glPointSize(8.0)

    # glActiveTexture(GL_TEXTURE0);
    # glEnable(GL_TEXTURE_2D);
    # glTexEnv(GL_POINT_SPRITE, GL_COORD_REPLACE, GL_TRUE);
    # glTexEnv(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE);
    # glBindTexture(GL_TEXTURE_2D, texture_name);

    # print x
    # glVertex(1.0, 1.0, 0.0)
    # Draw a 1x1 square center on origin and on the x*y plan.
    # x*y*z, Z negative forward oriented.
    glBegin(GL_POINTS)
    for i in range(-360, 360, 1):
        xx = i / 360.
        y = np.sin((degree + i) * pi_degree)
        glColor3f(0., 0., 0.)

        glVertex(xx * 1.3, y / 2, 0.0)
        glColor3f(0., 1., 0.)
        glVertex(xx * 2, y / 2, 0.0)
        glColor3f(1., 1., 0.)
        glVertex(xx * 2.8, y / 2, 0.0)
    glEnd()

    drawable.swap_buffers ()

    drawable.gl_end()

    return True

def _demo_draw(event):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glScalef(0.25, 0.25, 0.25)
    glPushMatrix()  # No name for grey sphere
    glColor3f(0.3, 0.3, 0.3)
    glutSolidSphere(0.7, 20, 20)
    glPopMatrix()
    glPushMatrix()
    glPushName(1)  # Red cone is 3
    glColor3f(1, 0, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCone(0.6, 4.0, 20, 20)
    glPopName()
    glPopMatrix()
    glPushMatrix()
    glPushName(2)  # Green cone is 2
    glColor3f(0, 1, 0)
    glRotatef(-90, 1, 0, 0)
    glutSolidCone(0.6, 4.0, 20, 20)
    glPopName()
    glPopMatrix()
    glPushMatrix()
    glColor3f(0, 0, 1)  # Blue cone is 3
    glPushName(3)
    glutSolidCone(0.6, 4.0, 20, 20)
    glPopName()
    glPopMatrix()


class HldiGL(gtkgl.DrawingArea):

    def __init__(self, w=200, h=150):
        try:
            glconfig = gdkgl.Config(mode=(gdkgl.MODE_RGB | gdkgl.MODE_DOUBLE | gdkgl.MODE_DEPTH))
        except gtk.gdkgl.NoMatches:
            glconfig = gdkgl.Config(mode=(gdkgl.MODE_RGB | gdkgl.MODE_DEPTH))

        gtkgl.DrawingArea.__init__(self, glconfig)
        self.set_size_request(w, h)
        self.connect_after("realize", self._init)
        self.connect("configure_event", self._reshape)
        self.connect("expose_event", self._draw)
        # self.connect("button_press_event", self._mouseButton)
        # self.connect("button_release_event", self._mouseButton)
        # self.connect("motion_notify_event", self._mouseMotion)
        # self.connect("scroll_event", self._mouseScroll)
        # self.set_events(self.get_events() |
        # gdk.BUTTON_PRESS_MASK | gdk.BUTTON_RELEASE_MASK |
        # gdk.POINTER_MOTION_MASK | gdk.POINTER_MOTION_HINT_MASK)
        self._zNear, self._zFar = -10.0, 10.0
        self._zprReferencePoint = [0., 0., 0., 0.]
        self._mouseX = self._mouseY = 0
        self._dragPosX = self._dragPosY = self._dragPosZ = 0.
        self._mouseRotate = self._mouseZoom = self._mousePan = False

    class _Context:
        def __init__(self, widget):
            self._widget = widget
            self._count = 0
            self._modelview = self._projection = None
            self._persist = False

        def __enter__(self):
            assert (self._count == 0)
            self.ctx = gtkgl.widget_get_gl_context(self._widget)
            self.surface = gtkgl.widget_get_gl_drawable(self._widget)
            self._begin = self.surface.gl_begin(self.ctx)

            if self._begin:
                self._count += 1

            if self._projection is not None:
                glMatrixMode(GL_PROJECTION)
                glLoadMatrixd(self._projection)

            if self._modelview is not None:
                glMatrixMode(GL_MODELVIEW)

                glLoadMatrixd(self._modelview)
                return self
            return

        def __exit__(self, exc_type, exc_value, exc_traceback):
            if self._begin:
                self._count -= 1
                if self._persist and (exc_type is None):
                    self._modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
                    self._projection = glGetDoublev(GL_PROJECTION_MATRIX)
                self.surface.gl_end()

            del self.ctx
            del self.surface

            self._persist = False
            if exc_type is not None:
                import traceback
                traceback.print_exception(exc_type, exc_value, exc_traceback)

            return True  # suppress

    def open_context(self, persist_matrix_changes=False):
        if not hasattr(self, "_context"):
            self._context = self._Context(self)

        assert (self._context._count == 0)
        self._context._persist = persist_matrix_changes
        return self._context

    def get_open_context(self):
        if hasattr(self, "_context") and (self._context._count > 0):
            return self._context

    def _init(self, widget):
        assert (widget == self)
        self.init()  ### optionally overriden by subclasses
        return True

    def reset(self):
        with self.open_context(True):
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

    def init(self):
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0., 0., 0., 1.))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT0, GL_SPECULAR, (1., 1., 1., 1.))
        glLightfv(GL_LIGHT0, GL_POSITION, (1., 1., 1., 0.))
        glMaterialfv(GL_FRONT, GL_AMBIENT, (.7, .7, .7, 1.))
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (.8, .8, .8, 1.))
        glMaterialfv(GL_FRONT, GL_SPECULAR, (1., 1., 1., 1.))
        glMaterialfv(GL_FRONT, GL_SHININESS, 100.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glEnable(GL_COLOR_MATERIAL)

    def _reshape(self, widget, event):
        assert (self == widget)

        with self.open_context(True):
            x, y, width, height = self.get_allocation()
            glViewport(0, 0, width, height);
            self._top = 1.0
            self._bottom = -1.0
            self._left = -float(width) / float(height)
            self._right = -self._left
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glOrtho(self._left, self._right, self._bottom, self._top, self._zNear, self._zFar)

        if hasattr(self, "reshape"):
            self.reshape(event, x, y, width, height)  ### optionally implemented by subclasses

        return True

    def _mouseMotion(self, widget, event):
        assert (widget == self)

        if event.is_hint:
            x, y, state = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.state

        dx = x - self._mouseX
        dy = y - self._mouseY

        if (dx == 0 and dy == 0): return

        self._mouseX, self._mouseY = x, y

        with self.open_context(True):
            changed = False

            if self._mouseZoom:
                s = math.exp(float(dy) * 0.01)
                self._apply(glScalef, s, s, s)
                changed = True

            elif self._mouseRotate:
                ax, ay, az = dy, dx, 0.

                viewport = glGetIntegerv(GL_VIEWPORT)
                angle = math.sqrt(ax ** 2 + ay ** 2 + az ** 2) / float(viewport[2] + 1) * 180.0

                inv = matrix(glGetDoublev(GL_MODELVIEW_MATRIX)).I

                bx = inv[0, 0] * ax + inv[1, 0] * ay + inv[2, 0] * az
                by = inv[0, 1] * ax + inv[1, 1] * ay + inv[2, 1] * az
                bz = inv[0, 2] * ax + inv[1, 2] * ay + inv[2, 2] * az

                self._apply(glRotatef, angle, bx, by, bz)

                changed = True

            elif self._mousePan:
                px, py, pz = self._pos(x, y);
                modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
                glLoadIdentity()
                glTranslatef(px - self._dragPosX, py - self._dragPosY, pz - self._dragPosZ)
                glMultMatrixd(modelview)
                self._dragPosX = px
                self._dragPosY = py
                self._dragPosZ = pz
                changed = True
            if changed:
                self.queue_draw()

    def _apply(self, func, *args):
        glTranslatef(*self._zprReferencePoint[0:3])
        func(*args)
        glTranslatef(*map(lambda x: -x, self._zprReferencePoint[0:3]))

    def _mouseScroll(self, widget, event):
        assert (self == widget)
        s = 4. if (event.direction == gdk.SCROLL_UP) else -4.
        s = math.exp(s * 0.01)
        with self.open_context(True):
            self._apply(glScalef, s, s, s)
            self.queue_draw()

    @classmethod
    def event_masked(cls, event, mask):
        return (event.state & mask) == mask

    @classmethod
    def _button_check(cls, event, button, mask):
        # this shouldn't be so crazy complicated
        if event.button == button:
            return (event.type == gdk.BUTTON_PRESS)
        return cls.event_masked(event, mask)

    @classmethod
    def get_left_button_down(cls, event):
        return cls._button_check(event, 1, gdk.BUTTON1_MASK)

    @classmethod
    def get_middle_button_down(cls, event):
        return cls._button_check(event, 2, gdk.BUTTON2_MASK)

    @classmethod
    def get_right_button_down(cls, event):
        return cls._button_check(event, 3, gdk.BUTTON3_MASK)

    def _mouseButton(self, widget, event):
        left = self.get_left_button_down(event)
        middle = self.get_middle_button_down(event)
        right = self.get_right_button_down(event)
        self._mouseRotate = left and not (middle or right)
        self._mouseZoom = middle or (left and right)
        self._mousePan = right and self.event_masked(event, gdk.CONTROL_MASK)
        x = self._mouseX = event.x
        y = self._mouseY = event.y
        self._dragPosX, self._dragPosY, self._dragPosZ = self._pos(x, y)
        if (left and not self.event_masked(event, gdk.CONTROL_MASK)) and \
            hasattr(self, "pick"):
            with self.open_context():
                nearest, hits = \
                    self._pick(x, self.get_allocation().height - 1 - y, 3, 3, event)
                self.pick(event, nearest, hits)  # None if nothing hit

        self.queue_draw()

    def pick(self, event, nearest, hits):
        print "picked", nearest
        for hit in hits:
            print hit.near, hit.far, hit.names

    def _pos(self, x, y):
        """
        Use the ortho projection and viewport information
        to map from mouse co-ordinates back into world
        co-ordinates
        """
        viewport = glGetIntegerv(GL_VIEWPORT)
        px = float(x - viewport[0]) / float(viewport[2])
        py = float(y - viewport[1]) / float(viewport[3])
        px = self._left + px * (self._right - self._left)
        py = self._top + py * (self._bottom - self._top)
        pz = self._zNear
        return (px, py, pz)

    def _pick(self, x, y, dx, dy, event):
        buf = glSelectBuffer(256)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()  # remember projection matrix
        viewport = glGetIntegerv(GL_VIEWPORT)
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        glLoadIdentity()
        gluPickMatrix(x, y, dx, dy, viewport)
        glMultMatrixd(projection)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        self.draw(event)
        glPopMatrix()
        hits = glRenderMode(GL_RENDER)
        nearest = []
        minZ = None
        for hit in hits:
            if (len(hit.names) > 0) and \
            ((minZ is None) or (hit.near < minZ)):
                minZ = hit.near
                nearest = hit.names

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()  # restore projection matrix
        glMatrixMode(GL_MODELVIEW)

        return (nearest, hits)

    def _draw(self, widget, event):
        assert (self == widget)

        with self.open_context() as ctx:
            glMatrixMode(GL_MODELVIEW)
            self.draw(event)  ### implemented by subclasses
            if ctx.surface.is_double_buffered():
                ctx.surface.swap_buffers()
            else:
                glFlush()

        return True
