#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gi
import numpy as np
import matplotlib.pyplot as plt
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
from gi.repository.GdkPixbuf import InterpType
from PIL import Image

"""
FotochoPI, a free (as in draft beer) image editor
"""
__author__ = "Augusto Bennemann"
__license__ = "GPL"
__version__ = "2.0"
__email__ = "abennemann@inf.ufrgs.br"

class FPIWindow(Gtk.Window):
    temp_height = 0
    temp_width = 0
    number_of_tones = 255
    histogram = [0] * 256
    cumulative_histogram = [0] * 256
    histogram_calculated = False

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

        button = Gtk.Button.new_with_mnemonic("_Invert")
        button.connect("clicked", self.on_invert_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Show Histogram")
        button.connect("clicked", self.on_histogram_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Brightness")
        button.connect("clicked", self.on_brightness_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Contrast")
        button.connect("clicked", self.on_contrast_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Histogram _Equalization")
        button.connect("clicked", self.on_equalization_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Rotate -90º")
        button.connect("clicked", self.on_rotateleft_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Rotate 90º")
        button.connect("clicked", self.on_rotateright_clicked)
        hbox.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Save")
        button.connect("clicked", self.on_save_clicked)
        hbox.pack_start(button, True, True, 0)

        self.originalgtkimage = Gtk.Image()
        self.gtkimage = Gtk.Image()
        #TODO resize image on window resize
        #self.gtkimage.connect('draw', self.on_image_resize, window)
        imgbox.add(self.originalgtkimage)
        imgbox.add(self.gtkimage)

        # TODO show a loading image while processing the image?

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        dialog.set_current_folder(os.getcwd())
        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print "File selected: " + dialog.get_filename()
            self.img = Image.open(dialog.get_filename())
            self.pix = np.asarray(self.img)
            originalpixbuf = image2pixbuf(self.img)
            self.originalgtkimage.set_from_pixbuf(originalpixbuf)
            self.update_image()
            self.number_of_tones = 255
            self.histogram = [0] * 256
            self.cumulative_histogram = [0] * 256
            self.histogram_calculated = False


        dialog.destroy()

    def add_filters(self, dialog):
        filter_jpeg = Gtk.FileFilter()
        filter_jpeg.set_name("JPEG files")
        filter_jpeg.add_mime_type("image/jpeg")
        dialog.add_filter(filter_jpeg)

    def on_horizontal_clicked(self, button):
        self.pix = np.fliplr(self.pix)
        self.update_image()

    def on_vertical_clicked(self, button):
        self.pix = np.flipud(self.pix)
        self.update_image()

    def on_invert_clicked(self, button):
        self.pix = 255 - self.pix
        self.update_image()

    def on_histogram_clicked(self, button):
        if not self.histogram_calculated:
            self.calculate_histogram()

        self.show_histogram()

    def calculate_histogram(self):
        if not is_grayscale(self.img):
            self.apply_luminance()

        shape = self.pix.shape
        for i in np.ndindex(shape[0], shape[1], 1):
            color = self.pix[i[0]][i[1]][i[2]]
            self.histogram[color] += 1.0/(shape[0] * shape[1])

        self.histogram_calculated = True

    def calculate_cumulative_histogram(self):
        if not self.histogram_calculated:
            self.calculate_histogram()

        shape = self.pix.shape
        a = 255.0 / (shape[0] * shape[1])
        self.cumulative_histogram[0] = a * self.histogram[0]
        for i in range(1, 256):
            self.cumulative_histogram[i] = a * self.histogram[i] + self.cumulative_histogram[i-1]
            print(self.cumulative_histogram[i])

    def on_equalization_clicked(self, button):
        if not is_grayscale(self.img):
            self.apply_luminance()

        self.calculate_cumulative_histogram()
        self.show_histogram()

        shape = self.pix.shape
        self.pix.flags.writeable = True
        print(self.cumulative_histogram[0])
        for i in np.ndindex(shape[0], shape[1], 1):
            # TODO improve code and remove this '(shape[0] * shape[1])'
            self.pix[i[0]][i[1]][0] = self.cumulative_histogram[self.pix[i[0]][i[1]][0]] * (shape[0] * shape[1])
            self.pix[i[0]][i[1]][1] = self.cumulative_histogram[self.pix[i[0]][i[1]][1]] * (shape[0] * shape[1])
            self.pix[i[0]][i[1]][2] = self.cumulative_histogram[self.pix[i[0]][i[1]][2]] * (shape[0] * shape[1])

        self.show_histogram()
        self.update_image()

    def on_rotateleft_clicked(self, button):
        self.pix = zip(*self.pix)[::-1]
        self.update_image()

    def on_rotateright_clicked(self, button):
        self.pix = zip(*self.pix[::-1])
        self.update_image()

    def apply_luminance(self):
        x2 = np.array([0.299, 0.587, 0.114])
        pix_sum = np.multiply(self.pix, x2).sum(2, dtype=np.uint8)
        self.pix = np.dstack([pix_sum] * 3)

        self.update_image()

    def apply_quantization(self, tones):
        if not is_grayscale(self.img):
            self.apply_luminance()

        min_tone = self.pix.min()
        max_tone = self.pix.max()
        tones_range = (max_tone - min_tone) + 1
        self.number_of_tones = tones

        # Enhanced Quantization (discard extreme tones that are not used):
        def f(x):
            passo = tones_range / float(tones)
            pos = x / passo
            if (pos - int(pos)) >  passo/2:
                pos += 1
            result = clamp(int( int(pos) * passo + min_tone), 0, 255)
            return result
        f = np.vectorize(f)
        self.pix = f(self.pix)

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
            filename = dialog.get_filename()
            # TODO this is not the best solution. If the filename
            # already exists with ".jpg" and user enter the same name
            # without the extension, it will overwrite without the file any alert
            if not filename.endswith('.jpg'):
                filename += '.jpg'
            self.img.save(filename)
            print "File saved: " + filename

        dialog.destroy()

    def on_quantization_clicked(self, widget):
        dialog = DialogQuantization(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.apply_quantization(int(dialog.spinbutton.get_value()))

        dialog.destroy()

    def on_brightness_clicked(self, widget):
        dialog = DialogBrightness(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.pix = clamp(self.pix + dialog.spinbutton.get_value(), 0, 255)

        dialog.destroy()

    def on_contrast_clicked(self, widget):
        dialog = DialogContrast(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            self.pix = clamp(self.pix * dialog.spinbutton.get_value(), 0, 255)

        dialog.destroy()

    def update_image(self):
        self.img = Image.fromarray(np.uint8(self.pix))
        pixbuf = image2pixbuf(self.img)
        # TODO Resize if image is bigger than window
        #self.gtkimage.set_from_pixbuf(pixbuf.scale_simple(200, 200, InterpType.BILINEAR))
        self.gtkimage.set_from_pixbuf(pixbuf)

    def show_histogram(self):
        ind = np.arange(256)
        plt.xlim(0, 255)
        plt.bar(ind, self.histogram)
        plt.show()

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
        adjustment = Gtk.Adjustment(parent.number_of_tones, 2, 256, 1, 10, 0)
        self.spinbutton = Gtk.SpinButton()
        self.spinbutton.set_adjustment(adjustment)

        table.attach(label, 0, 1, 0, 1)
        table.attach(self.spinbutton, 1, 3, 0, 1)

        box = self.get_content_area()
        box.add(table)
        self.show_all()

class DialogBrightness(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Brightness", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(30, 70)

        table = Gtk.Table(1, 2, True)
        label = Gtk.Label("Add: ")
        adjustment = Gtk.Adjustment(parent.number_of_tones, -255, 255, 0.1, 5.0, 0)
        self.spinbutton = Gtk.SpinButton(digits=2)
        self.spinbutton.set_adjustment(adjustment)

        table.attach(label, 0, 1, 0, 1)
        table.attach(self.spinbutton, 1, 3, 0, 1)

        box = self.get_content_area()
        box.add(table)
        self.show_all()

class DialogContrast(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Contrast", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(30, 70)

        table = Gtk.Table(1, 2, True)
        label = Gtk.Label("Multiply by: ")
        adjustment = Gtk.Adjustment(parent.number_of_tones, 0.1, 255, 0.1, 5.0, 0)
        self.spinbutton = Gtk.SpinButton(digits=2)
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

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

win = FPIWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
