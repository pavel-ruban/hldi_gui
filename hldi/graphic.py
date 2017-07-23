import pygtk;
pygtk.require('2.0')
import gtk, gtk.gdk as gdk, gtk.gtkgl as gtkgl, gtk.gdkgl as gdkgl
from gtk import glade
from OpenGL.GLU import *

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
from OpenGL.GL import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders
import numpy as np
import gobject
import time

class TestContext(BaseContext):
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

def render_loop(area):
    # print(time.ctime())
    # on_draw(area, self)
    # threading.Timer(1, foo).start()
    # source_id = gobject.timeout_add(1000, foo)
    area.queue_draw()
    return True

def hldiGlInit(self):
    config = gdkgl.Config(
        mode = (
            gdkgl.MODE_RGBA |
            gdkgl.MODE_DOUBLE |
            gdkgl.MODE_DEPTH))

    area = gtkgl.DrawingArea(config)
    area.set_size_request(
        width=200,
        height=150)

    area.connect('expose-event', on_draw)

    vbox = self.glade.get_object('glvbox')
    vbox.pack_start(area, True, True)
    vbox.show()
    area.show()

    source_id = gobject.timeout_add(10, render_loop, area)

degree = 360

def on_draw (area, _):

    """ Handles an `expose-event` event. Draws in the test OpenGL drawing
        area.
    """

    drawable = area.get_gl_drawable()
    context = area.get_gl_context()

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

    glEnable(GL_POINT_SMOOTH)
    glPointSize(8.0)

    try:
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
    except:
        pass

    return True
