#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf, InterpType
from PIL import Image

"""
FotochoPI, a free (as in draft beer) image editor
"""
__author__ = "Augusto Bennemann"
__license__ = "GPL"
__version__ = "1.0"
__email__ = "abennemann@inf.ufrgs.br"

# TODO add a loading image while processing the image?

class FPIWindow(Gtk.Window):
    temp_height = 0
    temp_width = 0

    def __init__(self):
        Gtk.Window.__init__(self, title="FotochoPI")
        self.set_border_width(10)

        grid = Gtk.Grid()
        self.add(grid)

        hbox = Gtk.Box(spacing=6)
        imgbox = Gtk.Box()
        imgbox.set_border_width(0)
        grid.add(hbox)
        grid.attach_next_to(imgbox, hbox, Gtk.PositionType.BOTTOM, 1, 2)

        button = Gtk.Button.new_with_mnemonic("_Open")
        button.connect("clicked", self.on_file_clicked)
        hbox.add(button)

        button = Gtk.Button.new_with_mnemonic("Flip _Horizontally")
        button.connect("clicked", self.on_horizontal_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Flip _Vertically")
        button.connect("clicked", self.on_vertical_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Luminance")
        button.connect("clicked", self.on_luminance_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Quantization")
        button.connect("clicked", self.on_quantization_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Save")
        button.connect("clicked", self.on_save_clicked)
        hbox.pack_start(button, True, True, 0)

        self.gtkimage = Gtk.Image()
        #TODO resize image on window resize
        #self.gtkimage.connect('draw', self.on_image_resize, window)
        imgbox.add(self.gtkimage)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print "File selected: " + dialog.get_filename()
            self.img = Image.open(dialog.get_filename())
            self.pix = self.img.load()
            self.update_image()

        dialog.destroy()

    def add_filters(self, dialog):
        filter_jpeg = Gtk.FileFilter()
        filter_jpeg.set_name("JPEG files")
        filter_jpeg.add_mime_type("image/jpeg")
        dialog.add_filter(filter_jpeg)

    def on_horizontal_clicked(self, button):
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size
        for i in range(width):
            for j in range(height):
                self.pix[i, j] = original_pix[width-i-1, j]

        self.update_image()

    def on_vertical_clicked(self, button):
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size

        for i in range(width):
            for j in range(height):
                self.pix[i, j] = original_pix[i, height-j-1]

        self.update_image()

    def apply_luminance(self):
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size

        for i in range(width):
            for j in range(height):
                red, green, blue = original_pix[i, j]
                cinza = int(0.299*red + 0.587*green + 0.114*blue)
                self.pix[i, j] = (cinza, cinza, cinza)

    def apply_quantization(self, tones):
        if not is_grayscale(self.img):
            self.apply_luminance()

        # TODO fazer otimizacao q manuel falou pra evitar que
        # os extremos sejam usados sem necessidade
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size

        for i in range(width):
            for j in range(height):
                color = int((original_pix[i, j][0]*tones)/256 * 256/(tones-1))
                self.pix[i, j] = (color, color, color)
        self.update_image()

    def on_luminance_clicked(self, button):
        self.apply_luminance()
        self.update_image()

    def on_save_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print "Save clicked"
            filename = dialog.get_filename()
            # TODO this is not the best solution. If the filename
            # already exists with ".jpg" and user enter the same name
            # without the extension, it will overwrite without the file any alert
            if not filename.endswith('.jpg'):
                filename += '.jpg'
            self.img.save(filename)
            print "File saved: " + filename

        elif response == Gtk.ResponseType.CANCEL:
            print "Cancel clicked"

        dialog.destroy()

    def on_quantization_clicked(self, widget):
        dialog = DialogQuantization(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.apply_quantization(int(dialog.spinbutton.get_value()))

        dialog.destroy()

    def update_image(self):
        # TODO Resize if image is bigger than window
        pixbuf = image2pixbuf(self.img)
        #self.gtkimage.set_from_pixbuf(pixbuf.scale_simple(200, 200, InterpType.BILINEAR))
        self.gtkimage.set_from_pixbuf(pixbuf)

    def on_image_resize(self, widget, event, window):
        allocation = widget.get_allocation()
        if self.temp_height != allocation.height or self.temp_width != allocation.width:
            self.temp_height = allocation.height
            self.temp_width = allocation.width
            pixbuf = image2pixbuf(self.img).scale_simple(allocation.width,
                                                         allocation.height,
                                                         InterpType.BILINEAR)
            widget.set_from_pixbuf(pixbuf)


class DialogQuantization(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Quantization", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(30, 70)

        table = Gtk.Table(1, 2, True)
        label = Gtk.Label("Tones: ")
        # TODO set default value the number of tones the photo currently have
        adjustment = Gtk.Adjustment(256, 2, 256, 1, 10, 0)
        self.spinbutton = Gtk.SpinButton()
        self.spinbutton.set_adjustment(adjustment)

        table.attach(label, 0, 1, 0, 1)
        table.attach(self.spinbutton, 1, 3, 0, 1)

        box = self.get_content_area()
        box.add(table)
        self.show_all()


def image2pixbuf(im): # From https://gist.github.com/mozbugbox/10cd35b2872628246140
    """Convert Pillow image to GdkPixbuf"""
    data = im.tobytes()
    w, h = im.size
    data = GLib.Bytes.new(data)
    pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
                                          False, 8, w, h, w * 3)
    return pix

def pixbuf2Image(pb):
    width, height = pb.get_width(), pb.get_height()
    return Image.fromstring("RGB", (width, height), pb.get_pixels())

def is_grayscale(im):
    pix = im.load()
    width, height = im.size
    for i in range(width):
        for j in range(height):
            if len(set(pix[i, j])) != 1: # if red, green and blue aren't equal
                return False

    return True

win = FPIWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
