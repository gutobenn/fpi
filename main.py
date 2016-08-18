#!/usr/bin/env python
# -*- coding: utf-8 -*-

# TODO melhorar interface:
# TODO- exibir botões só quando a imagem já tiver sido carregada
# TODO - colocar extensao automatica ao salvar se n estiver especificada
# TODO - especificar dependencias e docuemntacao do codigo, dizer q suporta teclado. aceitar arrastar o mouse?

import gi
import array
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, GdkPixbuf
from PIL import Image

class FPIWindow(Gtk.Window):
    img = "" # TODO how to initialize it correct?
    pix = ""
    gtkimg = Gtk.Image

    def __init__(self):
        Gtk.Window.__init__(self, title="FPI Pt.1")
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
        self.gtkimage.set_from_file("pb.jpg")
        hbox.add(self.gtkimage)

    def on_file_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            print("File selected: " + dialog.get_filename())
            self.img = Image.open(dialog.get_filename())
            self.pix = self.img.load();
            self.gtkimage.set_from_pixbuf(image2pixbuf(self.img))

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()

    def add_filters(self, dialog):
        filter_jpeg = Gtk.FileFilter()
        filter_jpeg.set_name("JPEG files")
        filter_jpeg.add_mime_type("image/jpeg")
        dialog.add_filter(filter_jpeg)

    def on_click_me_clicked(self, button):
        print("\"Click me\" button was clicked")

    def on_horizontal_clicked(self, button):
        print("\"Horizontal\" button was clicked")
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size
        for i in range(width):
            for j in range(height):
                self.pix[i,j] = original_pix[width-i-1,j]

        self.gtkimage.set_from_pixbuf(image2pixbuf(self.img))

    def on_vertical_clicked(self, button):
        print("\"Vertical\" button was clicked")
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size

        for i in range(width):
            for j in range(height):
                self.pix[i,j] = original_pix[i,height-j-1]

        self.gtkimage.set_from_pixbuf(image2pixbuf(self.img))

    def on_luminance_clicked(self, button):
        print("\"Luminance\" button was clicked")
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size

        for i in range(width):
            for j in range(height):
                r, g, b = original_pix[i,j]
                cinza = int(0.299*r + 0.587*g + 0.114*b)
                self.pix[i,j] = (cinza, cinza, cinza)

        self.gtkimage.set_from_pixbuf(image2pixbuf(self.img))

    def on_quantization_clicked(self, button):
        # TODO só deve funcionar com fotografia preto e branca? dar erro se n for preto e branca? ou aplicar luminanscia?
        # TODO fazer otimizacao q manuel falou pra evitar que os extremos sejam usados sem necessidade
        # TODO colocar botao de range
        print("\"Quantization\" button was clicked")
        original_img = self.img.copy()
        original_pix = original_img.load()
        width, height = self.img.size

        ntons = 30

        for i in range(width):
            for j in range(height):
                color = int((original_pix[i,j][0]*100 / 256) * (256/ntons) )
                print color
                self.pix[i,j] = (color, color, color)

        self.gtkimage.set_from_pixbuf(image2pixbuf(self.img))

    def on_save_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Save clicked")
            self.img.save(dialog.get_filename())
            print("File saved: " + dialog.get_filename())

        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()


def image2pixbuf(im): # From https://gist.github.com/mozbugbox/10cd35b2872628246140
    """Convert Pillow image to GdkPixbuf"""
    data = im.tobytes()
    w, h = im.size
    data = GLib.Bytes.new(data)
    pix = GdkPixbuf.Pixbuf.new_from_bytes(data, GdkPixbuf.Colorspace.RGB,
            False, 8, w, h, w * 3)
    return pix

def pixbuf2Image(pb):
    width,height = pb.get_width(),pb.get_height()
    return Image.fromstring("RGB",(width,height),pb.get_pixels() )

win = FPIWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
