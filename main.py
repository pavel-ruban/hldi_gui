#!/usr/bin/env python2.7

# HLDI - home laser device interface. Python version
# @author Pavel Ruban http://pavelruban.org

from multiprocessing import Process, Pipe
import time
from multiprocessing.queues import SimpleQueue

import pygtk
pygtk.require('2.0')
import gtk
import com
import re
import gobject

import glib

class Hldi:
    line_num = 0

    def x(self):
        self.textbuffer.set_text('das')

    # This is a callback function. The data arguments are ignored
    # in this example. More on callbacks below.
    def hello(self, widget, data=None):
        print "Hello World"

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

    def enter_callback(self, widget, entry):
        input = entry.get_text()
        com.uart_send(input)
        self.entry_text = input

        self.line_num += 1
        self.textbuffer.insert(self.textbuffer.get_end_iter(), '%d: < %s\r\n' % (self.line_num, input))

        self.textview.scroll_to_mark(self.textbuffer.get_insert(), 0);

    def click_callback(self, widget, data=None):
        input = self.entry.get_text()
        com.uart_send(input)

        self.line_num += 1
        self.textbuffer.insert(self.textbuffer.get_end_iter(), '%d: < %s\r\n' % (self.line_num, input))

        self.textview.scroll_to_mark(self.textbuffer.get_insert(), 0);

    def __init__(self):
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    
        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)
    
        # Here we connect the "destroy" event to a signal handler.  
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)
    
        # Sets the border width of the window.
        self.window.set_border_width(10)
        self.window.set_title('CoreXY HLDI (c) Pavel Ruban')
        self.window.set_resizable(True)
        self.window.resize(640, 480)

        self.box = gtk.VBox(False, 0)
        self.window.add(self.box)
        self.box.show()

        self.box2 = gtk.VBox(False, 10)
        self.box2.set_border_width(10)
        self.box.pack_start(self.box2, True, True, 0)
        self.box2.show()
        self.sw = gtk.ScrolledWindow()
        self.sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textview.set_editable(False)
        self.sw.add(self.textview)
        self.sw.show()
        self.textview.show()
        self.box2.pack_start(self.sw)
        # Creates a new button with the label "Hello World".
        self.button = gtk.Button('send')

        self.box3 = gtk.VBox(False, 10)
        self.box3.set_border_width(10)
        self.box.pack_start(self.box3, True, True, 0)
        self.box3.show()

        self.entry = gtk.Entry()
        self.entry.set_max_length(50)
        self.entry.connect("activate", self.enter_callback, self.entry)
        self.entry.set_text("hello")
        self.entry.insert_text(" world", len(self.entry.get_text()))
        self.entry.select_region(0, len(self.entry.get_text()))
        self.box.pack_start(self.entry, True, True, 0)
        self.entry.show()

        # When the button receives the "clicked" signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
        self.button.connect('clicked', self.click_callback, None)
        self.box.pack_end(self.button, True, True, 0)

        # This will cause the window to be destroyed by calling
        # gtk_widget_destroy(window) when "clicked".  Again, the destroy
        # signal could come from here, or the window manager.
        # self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
    
        # This packs the button into the window (a GTK container).
        self.window.add(self.button)
    
        # The final step is to display this newly created widget.
        self.button.show()
    
        # and the window
        self.window.show()

    # read values from the child
    def read_data(self, source, condition):
        self.line_num += 1

        assert parent_conn.poll()
        try:
            i = parent_conn.recv()
        except EOFError:
            return False  # stop reading
        # update text
        # self.textbuffer.set_text(self.textbuffer.get_text(*self.textbuffer.get_bounds()) + '%d: %s' % (self.line_num, i))
        self.textbuffer.insert(self.textbuffer.get_end_iter(), '%d: %s' % (self.line_num, i))

        self.textview.scroll_to_mark(self.textbuffer.get_insert(), 0);

        return True  # continue reading

    def main(self, parent_conn):
        # Process STDIN of the parnet process with read_data method.
        gobject.io_add_watch(parent_conn.fileno(), gobject.IO_IN, self.read_data)

        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

def application_thread(parent_conn):
    hldi = Hldi()
    hldi.main(parent_conn)

def com_thread(conn):
    com.listen_com(conn)

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    queue = SimpleQueue()

    # Create pipe Parent < Child.
    parent_conn, child_conn = Pipe(duplex = False)
    com_proc = Process(name = 'com', target = com_thread, args=[child_conn])
    com_proc.daemon = True
    com_proc.start()

    child_conn.close()

    application_thread(parent_conn)
