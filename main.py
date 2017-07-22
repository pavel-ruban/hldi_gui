#!/usr/bin/env python2.7

# HLDI - home laser device interface. Python version
# @author Pavel Ruban http://pavelruban.org

from multiprocessing import Process, Pipe
from multiprocessing.queues import Queue

import pygtk
pygtk.require('2.0')

import gtk
import gtk.glade

import time
import re
import gobject

from hldi.communication.uart import Uart
from hldi.profile import Profile
from hldi import graphic

import glib

hldi = None

class Hldi:
    # Communication layer.
    com = None
    # Profile is used to manage application settings.
    profile = None
    # All application available profile
    profiles = []

    line_num = 0

    def __init__(self):
        self.bootstrap()

        self.gui_init()

    def bootstrap(self):
        self.com = Uart()
        self.profile = Profile()

    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def communication_cmd_enter_callback(self, widget, entry):
        # communication_cmd_entry = self.glade.get_object("communication_cmd_entry").get_text()
        input = self.glade.get_object("communication_cmd_entry").get_text()
        # input = entry.get_text()

        self.com.send(input)

        textview = self.glade.get_object("communication_output_textview")
        textbuffer = textview.get_buffer()

        self.line_num += 1

        textbuffer.insert(textbuffer.get_end_iter(), '%d: < %s\r\n' % (self.line_num, input))

        textview.scroll_to_mark(textbuffer.get_insert(), 0);

    def communication_send_click_callback(self, widget, data = None):
        # input = self.entry.get_text()
        input = self.glade.get_object("communication_cmd_entry").get_text()
        self.com.send(input)

        textview = self.glade.get_object("communication_output_textview")
        textbuffer = textview.get_buffer()

        self.line_num += 1

        textbuffer.insert(textbuffer.get_end_iter(), '%d: < %s\r\n' % (self.line_num, input))

        textview.scroll_to_mark(textbuffer.get_insert(), 0)

    def gui_init(self):
        # Set the Glade file
        self.gladefile = "hldi.glade"
        self.glade = gtk.Builder()

        self.glade.add_from_file(self.gladefile)
        self.glade.connect_signals(self)

        window = self.glade.get_object("MainWindow")
    
        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        window.connect("delete_event", self.delete_event)
    
        # Here we connect the "destroy" event to a signal handler.  
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        window.connect("destroy", self.destroy)
    
        # Sets the border width of the window.
        # window.set_border_width(10)
        window.set_title('CoreXY HLDI (c) Pavel Ruban')

        # When the button receives the "clicked" signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
        self.glade.get_object('communication_send_button').connect('clicked', self.communication_send_click_callback, None)
        self.glade.get_object('communication_cmd_entry').connect('activate', self.communication_cmd_enter_callback, None)
        self.glade.get_object('serial_connect_button').connect('clicked', self.communication_connect_click_callback, None)

        # configure the serial connections (the parameters differs on the device you are connecting to)
        self.glade.get_object('serial_device_entry').set_text('/dev/ttyUSB0')
        self.glade.get_object('serial_baudrate_entry').set_text('115200')
        self.glade.get_object('profile_entry').set_text('photoresist')

        # and the window
        window.show_all()

    def communication_connect(self):
        self.com.connect(self.glade)

        time.sleep(1)

        # Create pipe Parent < Child.
        self.parent_conn, self.child_conn = Pipe(duplex=False)

        self.communication_proc = Process(name= 'self.com', target = communication_thread, args = [self.child_conn, queue])
        self.communication_proc.daemon = True
        self.communication_proc.start()

        self.child_conn.close()

    def communication_connect_click_callback(self, widget, entry):

        if self.com.isOpen():
            self.com.close()

            self.glade.get_object('serial_connect_button').set_label('connect')

            if hasattr(self, 'communication_proc') and hasattr(self.communication_proc, 'terminate'):
                self.communication_proc.terminate()
        else:
            self.communication_connect()

            if self.com.isOpen():
                self.glade.get_object('serial_connect_button').set_label('disconnect')

            # Process STDIN of the parnet process with read_data method.
            gobject.io_add_watch(self.parent_conn.fileno(), gobject.IO_IN, self.communication_read_data)

            self.glade.get_object('serial_connect_button').set_label('disconnect')

    # read values from the child process
    def communication_read_data(self, source, condition):
        self.line_num += 1

        assert self.parent_conn.poll()

        try:
            i = self.parent_conn.recv()
        except EOFError:
            return False  # stop reading

        # Update text
        textview = self.glade.get_object("communication_output_textview")

        textbuffer = textview.get_buffer()
        textbuffer.insert(textbuffer.get_end_iter(), '%d: %s' % (self.line_num, i))

        textview.scroll_to_mark(textbuffer.get_insert(), 0)

        return True  # continue reading

    def on_MainWindow_delete_event(self, widget, event):
        gtk.main_quit()

def application_thread():
    global hldi

    hldi = Hldi()
    graphic.hldiGlInit(hldi)
    hldi.main()

def communication_thread(conn, queue):
    if hldi.com.isOpen():
        hldi.com.listen(conn, queue)

def gl_thread(queue):
    pass

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    # graphic.hldiGlInit(hldi)

    queue = Queue()

    application_thread()
