""" Ubigraph does not play nicely with the OpenGL stuff in QT, so we switch to GTK """
import pygtk
pygtk.require('2.0')
import gtk

class ImageWindow:
    def __init__(self, pics):
        self.window = gtk.Window()
        self.event_box = gtk.EventBox()
        self.pics = pics
        self.image = gtk.Image()
        self.image.set_from_file(pics[1])
        self.event_box.add(self.image)
        self.window.add(self.event_box)
        self.window.show_all()

    def setPic(self, picNo):
        self.image.set_from_file(self.pics[picNo])

def gtk_run():
    gtk.gdk.threads_init()
    gtk.threads_enter()
    gtk.main()
    gtk.threads_leave()