#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO exibir botões só quando a imagem já tiver sido carregada?
# TODO limitar imagem ao tamanho da tela

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
from PIL import Image

class FPIWindow(Gtk.Window):
    img = "" # TODO how to initialize it correctly?
    pix = ""
    gtkimg = Gtk.Image

    def __init__(self):
        Gtk.Window.__init__(self, title="FotochoPI")
        self.set_border_width(10)

        hbox = Gtk.Box(spacing=6)
        self.add(hbox)

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
        hbox.add(self.gtkimage)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print "Open clicked"
            print "File selected: " + dialog.get_filename()
            self.img = Image.open(dialog.get_filename())
            self.pix = self.img.load()
            self.update_image()

        elif response == Gtk.ResponseType.CANCEL:
            print "Cancel clicked"

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
                r, g, b = original_pix[i, j]
                cinza = int(0.299*r + 0.587*g + 0.114*b)
                self.pix[i, j] = (cinza, cinza, cinza)

    def on_luminance_clicked(self, button):
        self.apply_luminance()
        self.update_image()

    def on_quantization_clicked(self, button):
        if not is_grayscale(self.img):
            self.apply_luminance()

        # TODO fazer otimizacao q manuel falou pra evitar que
        # os extremos sejam usados sem necessidade
        # TODO o extremo branco nao ta sendo usado! ajeitar isso
        # TODO colocar botao de range
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size

        ntons = 4
        for i in range(width):
            for j in range(height):
                color = int((original_pix[i, j][0]*ntons)/256 * 256/ntons)
                """print original_pix[i, j][0],
                print " => ",
                print color"""
                self.pix[i, j] = (color, color, color)
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

    def update_image(self):
        self.gtkimage.set_from_pixbuf(image2pixbuf(self.img))

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
