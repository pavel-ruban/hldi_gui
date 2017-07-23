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
import ast
import gobject

from hldi.communication.uart import Uart
from hldi.profile import Profile
from hldi import graphic
hldi = None

from hldi import commands as cmd
import pickle

class Hldi:
    cmd_history = []
    cmd_entry_substring = ''
    cmd_history_filename = 'cmd_history.txt'
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

        # Load cmd history.
        try:
            with open(self.cmd_history_filename, 'r') as f:
                self.cmd_history = [line.rstrip('\n') for line in f]
        except:
            pass

        try:
            self.profile = pickle.load(open('profiles.txt', 'r'))
        except:
            self.profile = Profile()

        print self.cmd_history

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

        # Update history file.
        with open(self.cmd_history_filename, 'w') as f:
            for s in self.cmd_history:
                f.write(s + '\n')

        self.profile.device = self.glade.get_object('serial_device_entry').get_text()
        self.profile.baudrate = self.glade.get_object('serial_baudrate_entry').get_text()

        pickle.dump(self.profile, open('profiles.txt', 'w'))

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        print "destroy signal occurred"
        gtk.main_quit()

    def com_cmd_on_key_release(self, widget, ev, data=None):
        name = gtk.gdk.keyval_name(ev.keyval)

        if name != 'Up' and name != 'Down' and name != 'Return':
            self.cmd_entry_substring = self.glade.get_object("communication_cmd_entry").get_text()
            print 'cmd substring: %s' % self.cmd_entry_substring

        return True

    # Search entry in cmd history if entry is not empty or list all previously typed commands.
    def com_cmd_on_key_press(self, widget, ev, data=None):
        input = self.glade.get_object("communication_cmd_entry")

        name = gtk.gdk.keyval_name(ev.keyval)

        if name != 'Up' and name != 'Down':
            return

        if not hasattr(self, 'cmd_hist_index'):
            self.cmd_hist_index = -1

        cmd_hist_len = len(self.cmd_history)

        # If cmd entry is not empty search by substring.
        if self.cmd_entry_substring != '':
            origin_index = self.cmd_hist_index

            if name == 'Up':
                self.cmd_hist_index = self.cmd_hist_index - 1

                # Loop through all elements from.
                while origin_index != self.cmd_hist_index:
                    if cmd_hist_len < abs(self.cmd_hist_index):
                        self.cmd_hist_index = -1

                    if re.search(re.escape(self.cmd_entry_substring), self.cmd_history[self.cmd_hist_index]):
                        input.set_text(self.cmd_history[self.cmd_hist_index])
                        return  True

                    self.cmd_hist_index = self.cmd_hist_index - 1

            elif name == 'Down':
                self.cmd_hist_index = self.cmd_hist_index + 1

                # Loop through all elements from.
                while origin_index != self.cmd_hist_index:
                    if cmd_hist_len - 1 < abs(self.cmd_hist_index):
                        self.cmd_hist_index = 0

                    if re.search(re.escape(self.cmd_entry_substring), self.cmd_history[self.cmd_hist_index]):
                        input.set_text(self.cmd_history[self.cmd_hist_index])
                        return True

                    self.cmd_hist_index = self.cmd_hist_index + 1

        # Otherwise just use prev / next cmd.
        else:
            if name == 'Up':
                self.cmd_hist_index = self.cmd_hist_index - 1
                if cmd_hist_len < abs(self.cmd_hist_index):
                    self.cmd_hist_index = -1

                input.set_text(self.cmd_history[self.cmd_hist_index])
                self.cmd_entry_substring = ''
            elif name == 'Down':
                self.cmd_hist_index = self.cmd_hist_index + 1

                if cmd_hist_len - 1 < abs(self.cmd_hist_index):
                    self.cmd_hist_index = 0

                input.set_text(self.cmd_history[self.cmd_hist_index])
                self.cmd_entry_substring = ''

        return True

    def comm_send(self, input):
        self.com.send(input)

        # Update status bar message.
        statusbar = self.glade.get_object('statusbar')
        context_id = statusbar.get_context_id('last_event')
        statusbar.push(context_id, 'uart: "%s" have been sent' % input)

    def comm_cmd_send(self, input):
        self.comm_send(input)

        textview = self.glade.get_object("communication_output_textview")
        textbuffer = textview.get_buffer()

        self.line_num += 1

        textbuffer.insert(textbuffer.get_end_iter(), '%d: < %s\r\n' % (self.line_num, input))
        textview.scroll_to_mark(textbuffer.get_insert(), 0);

    def comm_cmd_entry_send(self, widget, entry):
        input = self.glade.get_object("communication_cmd_entry").get_text()

        self.comm_send(input)

        textview = self.glade.get_object("communication_output_textview")
        textbuffer = textview.get_buffer()

        self.line_num += 1

        textbuffer.insert(textbuffer.get_end_iter(), '%d: < %s\r\n' % (self.line_num, input))
        textview.scroll_to_mark(textbuffer.get_insert(), 0);

        print '\nbefore\n'
        print self.cmd_history
        # Make list unique.
        if input in self.cmd_history:
            self.cmd_history.remove(input)

        # Make repeated value most recent in cmd history.
        self.cmd_history.append(input)

        self.cmd_hist_index = -1

        print '\nbefore\n'
        print self.cmd_history

        # Avoid further searching if we already entered new string.
        self.cmd_entry_substring = ''
        print 'cmd substring: %s' % self.cmd_entry_substring

    def communication_cmd_enter_callback(self, widget, entry):
        self.comm_cmd_entry_send(widget, entry)

    def communication_send_click_callback(self, widget, data = None):
        self.comm_cmd_entry_send(widget, data)

    def set_speed_btn_on_click(self, widget, data = None):
        if (not self.com.isOpen()):
            self.log('Uart connection is not available', 'error')
            return 

        pwm = self.glade.get_object("speed_scale").get_value()

        self.comm_cmd_send(cmd.MOTOR_SET_PWM % pwm)

        # @todo implement true speed once servo & quadrature encoder are done.
        self.glade.get_object('speed_label').set_text('Speed: %d pwm' % pwm)

    def motor_dir_btn_on_click(self, widget, data = None):
        if (not self.com.isOpen()):
            self.log('Uart connection is not available', 'error')
            return 
        
        btn = self.glade.get_object('motor_dir_btn')

        if btn.get_label() == 'CW':
            btn.set_label('CCW')
            self.comm_cmd_send(cmd.MOTOR_CCW)
        else:
            btn.set_label('CW')
            self.comm_cmd_send(cmd.MOTOR_CW)

    def log(self, msg, type = 'status'):
        # Update status bar message.
        statusbar = self.glade.get_object('statusbar')
        context_id = statusbar.get_context_id('last_event')
        statusbar.push(context_id, '%s: %s' % (type, msg))
        
    def motor_on_btn_on_click(self, widget, data = None):
        if (not self.com.isOpen()):
            self.log('Uart connection is not available', 'error')
            return 
        
        btn = self.glade.get_object('motor_on_btn')
        spinner = self.glade.get_object('cmd_spinner')

        if btn.get_label() == 'Motor ON':
            btn.set_label('Motor OFF')
            self.comm_cmd_send(cmd.MOTOR_OFF)
            spinner.stop()
        else:
            btn.set_label('Motor ON')
            self.comm_cmd_send(cmd.MOTOR_ON)
            spinner.start()

    def frame_expander_eventbox_click_callback(self, widget, data = None, prefix = ''):
        frame_state = '%s_frame_state' % prefix
        origin_viewport_height = '%s_origin_viewport_height' % prefix

        if not hasattr(self, frame_state):
            setattr(self, frame_state, True)

        alignment = self.glade.get_object('%s_alignment' % prefix)
        frame = self.glade.get_object('%s_frame' % prefix)
        viewport = self.glade.get_object('%s_viewport' % prefix)

        if not hasattr(self, origin_viewport_height):
            setattr(self, origin_viewport_height, viewport.get_allocation().height)

        icon = self.glade.get_object('%s_icon' % prefix)

        if getattr(self, frame_state):
            alignment.hide()
            viewport.set_size_request(-1, 40)
            frame.set_shadow_type(gtk.SHADOW_NONE)
            icon.set_from_stock(gtk.STOCK_GO_DOWN, gtk.ICON_SIZE_BUTTON)
        else:
            viewport.set_size_request(-1, getattr(self, origin_viewport_height))
            alignment.show()
            frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
            icon.set_from_stock(gtk.STOCK_GO_UP, gtk.ICON_SIZE_BUTTON)

        setattr(self, frame_state, getattr(self, frame_state) ^ 1)

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
        self.glade.get_object('connection_eventbox').connect('button-press-event', self.frame_expander_eventbox_click_callback, 'connection')
        self.glade.get_object('movectrl_eventbox').connect('button-press-event', self.frame_expander_eventbox_click_callback, 'movectrl')
        self.glade.get_object('communication_cmd_entry').connect('activate', self.communication_cmd_enter_callback, None)
        self.glade.get_object('communication_cmd_entry').connect('key-release-event', self.com_cmd_on_key_release)
        self.glade.get_object('communication_cmd_entry').connect('key-press-event', self.com_cmd_on_key_press)
        self.glade.get_object('serial_connect_button').connect('clicked', self.communication_connect_on_click,
                                                               None)
        self.glade.get_object('motor_on_btn').connect('clicked', self.motor_on_btn_on_click, None)
        self.glade.get_object('motor_dir_btn').connect('clicked', self.motor_dir_btn_on_click, None)
        self.glade.get_object('set_speed_btn').connect('clicked', self.set_speed_btn_on_click, None)

        # configure the serial connections (the parameters differs on the device you are connecting to)

        try:
            self.glade.get_object('serial_device_entry').set_text(self.profile.device)
            self.glade.get_object('serial_baudrate_entry').set_text(self.profile.baudrate)
            self.glade.get_object('profile_entry').set_text(self.profile.name)
        except:
            self.glade.get_object('serial_device_entry').set_text('/dev/ttyUSB0')
            self.glade.get_object('serial_baudrate_entry').set_text('115200')
            self.glade.get_object('profile_entry').set_text('photoresist')

        self.glade.get_object("speed_scale").set_range(0, 255)

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

    def communication_connect_on_click(self, widget, entry):

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
