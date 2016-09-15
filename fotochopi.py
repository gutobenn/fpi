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
        hbox2 = Gtk.Box(spacing=6)
        imgbox = Gtk.Box()
        imgbox.set_border_width(0)
        grid.add(hbox)
        grid.attach_next_to(hbox2, hbox, Gtk.PositionType.BOTTOM, 1, 2)
        grid.attach_next_to(imgbox, hbox2, Gtk.PositionType.BOTTOM, 1, 2)

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
        hbox2.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Brightness")
        button.connect("clicked", self.on_brightness_clicked)
        hbox2.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Contrast")
        button.connect("clicked", self.on_contrast_clicked)
        hbox2.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Histogram _Equalization")
        button.connect("clicked", self.on_equalization_clicked)
        hbox2.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Rotate -90º")
        button.connect("clicked", self.on_rotateleft_clicked)
        hbox2.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Rotate 90º")
        button.connect("clicked", self.on_rotateright_clicked)
        hbox2.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Zoom _In")
        button.connect("clicked", self.on_zoom_in_clicked)
        hbox2.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("Zoom _Out")
        button.connect("clicked", self.on_zoom_out_clicked)
        hbox2.pack_start(button, True, True, 0)

        button = Gtk.Button.new_with_mnemonic("_Convolution")
        button.connect("clicked", self.on_convolution_clicked)
        hbox2.pack_start(button, True, True, 0)

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
        plt.show()

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

    def on_equalization_clicked(self, button):
        if not is_grayscale(self.img):
            self.apply_luminance()

        self.calculate_cumulative_histogram()
        self.show_histogram()

        shape = self.pix.shape
        self.pix.flags.writeable = True
        for i in np.ndindex(shape[0], shape[1], 1):
            # TODO improve code and remove this '(shape[0] * shape[1])'
            self.pix[i[0]][i[1]][0] = self.cumulative_histogram[self.pix[i[0]][i[1]][0]] * (shape[0] * shape[1])
            self.pix[i[0]][i[1]][1] = self.cumulative_histogram[self.pix[i[0]][i[1]][1]] * (shape[0] * shape[1])
            self.pix[i[0]][i[1]][2] = self.cumulative_histogram[self.pix[i[0]][i[1]][2]] * (shape[0] * shape[1])
        self.calculate_histogram()

        self.show_histogram()
        plt.show()

        self.update_image()

    def on_rotateleft_clicked(self, button):
        self.pix = zip(*self.pix)[::-1]
        self.update_image()

    def on_rotateright_clicked(self, button):
        self.pix = zip(*self.pix[::-1])
        self.update_image()

    def on_zoom_in_clicked(self, button):
        pix_old = self.pix.copy()
        height, width, rgb = pix_old.shape
        self.pix = np.zeros((height*2-1, width*2-1, rgb), dtype=np.int8)
        self.pix.flags.writeable = True

        for i in range(height):
            for j in range(1,width):
                #self.pix[2*i][j] = pix_old[i][j]
                #self.pix[2*i-1][j] = pix_old[i][j]
                self.pix[i][2*j] = pix_old[i][j]
                self.pix[i][2*j-1] = np.array((np.array(pix_old[i][j]) + np.array(pix_old[i][j-1])) / 2, dtype=np.uint8)
                #self.pix[i][2*j-1] = [int((x + y)/2) for x, y in zip(pix_old[i][j], pix_old[i][j-1])]
                #if self.pix[i][2*j][0] < 0:
                #    print(self.pix[i][2*j], pix_old[i][j], pix_old[i][j-1], self.pix[i][2*j-1])

        pix_old = self.pix.copy()
        self.pix = np.zeros((height*2-1, width*2-1, rgb))
        for i in range(1,height):
            for j in range(width*2-1):
                self.pix[2*i][j] = pix_old[i][j]
                self.pix[2*i-1][j] = np.array((np.array(pix_old[i][j]) + np.array(pix_old[i-1][j])) / 2, dtype=np.uint8)

        """
        for i in range(height-1):
            for j in range(width-1):
                self.pix[i][2*j] = pix_old[i][j]
                #self.pix[i][2*j+1] = (np.array(pix_old[i][j]) + np.array(pix_old[i][j+1])) / 2
                #self.pix[2*i+1][j] = (np.array(pix_old[i][j]) + np.array(pix_old[i+1][j])) / 2
                #self.pix[2*i+1][2*j+1] = (np.array(pix_old[i][j]) + np.array(pix_old[i][j+1]) + np.array(pix_old[i+1][j]) + np.array(pix_old[i+1][j+1])) / 4
        """

        self.update_image()

    def on_zoom_out_clicked(self, button):
        dialog = DialogZoomOut(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            pix_old = self.pix.copy()
            old_height, old_width, old_rgb = self.pix.shape
            sx, sy = dialog.sx.get_value(), dialog.sy.get_value()
            self.pix = np.zeros((int(old_height/sy), int(old_width/sx), old_rgb), dtype=np.int8)
            height, width, rgb = self.pix.shape
            self.pix.flags.writeable = True

            for i in range(height):
                for j in range(1,width):
                    self.pix[i][j] = pix_old[int(i*sy),int(j*sx)]

            self.update_image()

        dialog.destroy()

    def on_convolution_clicked(self, button):
        dialog = DialogConvolution(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if not is_grayscale(self.img):
                self.apply_luminance()

            pix_old = self.pix.copy()

            kernel = np.array([[dialog.s_a.get_value(), dialog.s_b.get_value(), dialog.s_c.get_value()],
                                    [dialog.s_d.get_value(), dialog.s_e.get_value(), dialog.s_f.get_value()],
                                    [dialog.s_g.get_value(), dialog.s_h.get_value(), dialog.s_i.get_value()]])
            kernel = np.rot90(kernel,2) # rotate kernel 180º

            height, width, rgb = self.pix.shape
            self.pix.flags.writeable = True

            for i in range(1,height-1):
                for j in range(1,width-1):
                    sum = 0.
                    neighbors = pix_old[i-1:i+2,j-1:j+2,0]

                    resultado = np.zeros((3,3))
                    for (rr,cc), value in np.ndenumerate(neighbors):
                        sum += neighbors[rr,cc] * kernel[rr,cc]
                        resultado[rr,cc] = neighbors[rr,cc] * kernel[rr,cc]

                    if dialog.add_127 is True:
                        sum += 127

                    new_value = clamp(int(sum), 0, 255)
                    self.pix[i][j] = (new_value, new_value, new_value)

        dialog.destroy()

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
            def f(x):
                return clamp(x + dialog.spinbutton.get_value(), 0, 255)
            f = np.vectorize(f)
            self.pix = f(self.pix)
            self.update_image()

        dialog.destroy()

    def on_contrast_clicked(self, widget):
        dialog = DialogContrast(self)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            def f(x):
                return clamp(x * dialog.spinbutton.get_value(), 0, 255)
            f = np.vectorize(f)
            self.pix = f(self.pix)
            self.update_image()

        dialog.destroy()


    def update_image(self):
        self.img = Image.fromarray(np.uint8(self.pix))
        pixbuf = image2pixbuf(self.img)
        # TODO Resize if image is bigger than window
        #self.gtkimage.set_from_pixbuf(pixbuf.scale_simple(200, 200, InterpType.BILINEAR))
        self.gtkimage.set_from_pixbuf(pixbuf)

    def show_histogram(self):
        ind = np.arange(256)
        plt.figure()
        plt.xlim(0, 255)
        plt.bar(ind, self.histogram)

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
        adjustment = Gtk.Adjustment(0, -255, 255, 0.1, 5.0, 0)
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
        adjustment = Gtk.Adjustment(1, 0.1, 255, 0.1, 5.0, 0)
        self.spinbutton = Gtk.SpinButton(digits=2)
        self.spinbutton.set_adjustment(adjustment)

        table.attach(label, 0, 1, 0, 1)
        table.attach(self.spinbutton, 1, 3, 0, 1)

        box = self.get_content_area()
        box.add(table)
        self.show_all()


class DialogConvolution(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Convolution", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(30, 200)

        table = Gtk.Table(7, 3, True)
        adjustment_a = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        adjustment_b = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        adjustment_c = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        adjustment_d = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        adjustment_e = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        adjustment_f = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        adjustment_g = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        adjustment_h = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        adjustment_i = Gtk.Adjustment(0, -255.0, 255.0, 0.1, 1.0, 0)
        self.s_a = Gtk.SpinButton(digits=4)
        self.s_a.set_adjustment(adjustment_a)
        self.s_b = Gtk.SpinButton(digits=4)
        self.s_b.set_adjustment(adjustment_b)
        self.s_c = Gtk.SpinButton(digits=4)
        self.s_c.set_adjustment(adjustment_c)
        self.s_d = Gtk.SpinButton(digits=4)
        self.s_d.set_adjustment(adjustment_d)
        self.s_e = Gtk.SpinButton(digits=4)
        self.s_e.set_adjustment(adjustment_e)
        self.s_f = Gtk.SpinButton(digits=4)
        self.s_f.set_adjustment(adjustment_f)
        self.s_g = Gtk.SpinButton(digits=4)
        self.s_g.set_adjustment(adjustment_g)
        self.s_h = Gtk.SpinButton(digits=4)
        self.s_h.set_adjustment(adjustment_h)
        self.s_i = Gtk.SpinButton(digits=4)
        self.s_i.set_adjustment(adjustment_i)

        self.add_127 = False

        table.attach(self.s_a, 0, 1, 0, 1)
        table.attach(self.s_b, 1, 2, 0, 1)
        table.attach(self.s_c, 2, 3, 0, 1)
        table.attach(self.s_d, 0, 1, 1, 2)
        table.attach(self.s_e, 1, 2, 1, 2)
        table.attach(self.s_f, 2, 3, 1, 2)
        table.attach(self.s_g, 0, 1, 2, 3)
        table.attach(self.s_h, 1, 2, 2, 3)
        table.attach(self.s_i, 2, 3, 2, 3)

        button = Gtk.CheckButton("Add 127")
        button.connect("toggled", self.on_add127_toggled)
        table.attach(button, 0, 2, 3, 4)

        box = self.get_content_area()
        box.add(table)

        button = Gtk.Button.new_with_label("Gaussian")
        button.connect("clicked", self.set_kernel, "g")
        table.attach(button, 0, 1, 4, 5)
        button = Gtk.Button.new_with_label("Laplacian")
        button.connect("clicked", self.set_kernel, "lp")
        table.attach(button, 1, 2, 4, 5)
        button = Gtk.Button.new_with_label("High Pass")
        button.connect("clicked", self.set_kernel, "hp")
        table.attach(button, 2, 3, 4, 5)
        button = Gtk.Button.new_with_label("Prewitt Hx")
        button.connect("clicked", self.set_kernel, "px")
        table.attach(button, 0, 1, 5, 6)
        button = Gtk.Button.new_with_label("Prewitt Hx Hy")
        button.connect("clicked", self.set_kernel, "pxy")
        table.attach(button, 1, 2, 5, 6)
        button = Gtk.Button.new_with_label("Sobel Hx")
        button.connect("clicked", self.set_kernel, "shx")
        table.attach(button, 2, 3, 5, 6)
        button = Gtk.Button.new_with_label("Sobel Hy")
        button.connect("clicked", self.set_kernel, "shy")
        table.attach(button, 0, 1, 6, 7)

        self.show_all()

    def set_kernel(self, button, label):
        kernel = np.zeros((3,3))

        if label is 'g':
            kernel = np.array([[0.0625,0.125,0.0625],
                                [0.125,0.25,0.125],
                                [0.0625,0.125,0.0625]])
        elif label is 'lp':
            kernel = np.array([[0., -1., 0.],
                                [-1., 4., -1.],
                                [0., -1., 0.]])
        elif label is 'hp':
            kernel = np.array([[-1., -1., -1.],
                                [-1., 8., -1.],
                                [-1., -1., -1.]])
        elif label is 'px':
            kernel = np.array([[-1., 0., 1.],
                                [-1., 0., 1.],
                                [-1., 0., 1.]])
        elif label is 'pxy':
            kernel = np.array([[-1., -1., -1.],
                                [0., 0., 0.],
                                [1., 1., 1.]])
        elif label is 'shx':
            kernel = np.array([[-1., 0., 1.],
                                [-2., 0., 2.],
                                [-1., 0., 1.]])
        elif label is 'shy':
            kernel = np.array([[-1., -2., -1.],
                                [0., 0., 0.],
                                [1., 2., 1.]])

        fields = (self.s_a, self.s_b, self.s_c, self.s_d, self.s_e, self.s_f, self.s_g, self.s_h, self.s_i)

        for i, v in enumerate(kernel.flat):
            fields[i].set_value(v)

    def on_add127_toggled(self, button):
        if button.get_active():
            self.add_127 = True
        else:
            self.add_127 = False

class DialogZoomOut(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Zoom Out", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(30, 100)

        table = Gtk.Table(1, 3, True)
        label_sx = Gtk.Label("Sx: ")
        label_sy = Gtk.Label("Sy: ")
        adjustment_sx = Gtk.Adjustment(2, 1, 10, 1, 2, 0)
        adjustment_sy = Gtk.Adjustment(2, 1, 10, 1, 2, 0)
        self.sx = Gtk.SpinButton()
        self.sx.set_adjustment(adjustment_sx)
        self.sy = Gtk.SpinButton()
        self.sy.set_adjustment(adjustment_sy)

        table.attach(label_sx, 0, 1, 0, 1)
        table.attach(self.sx, 1, 3, 0, 1)
        table.attach(label_sy, 0, 1, 1, 2)
        table.attach(self.sy, 1, 3, 1, 2)



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
    # TODO this method could use an variable to save current state. If already checked image colors, then doesn't need to check again.
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
