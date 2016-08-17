#// TODO exibir botoes soh qndo a imagem ja tiver sido carregada
#// TODO carregar img e exibir na tela com gtk
#// TODO especificar dependencias e docuemntacao do codigo, dizer q suporta teclado. aceitar arrastar o mouse?
#// TODO git

import gi
import array
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from PIL import Image

class FPIWindow(Gtk.Window):
    img = 0; # TODO add Global here!

    def __init__(self):
        Gtk.Window.__init__(self, title="FPI Pt.1")
        self.set_border_width(10)

        hbox = Gtk.Box(spacing=6)
        self.add(hbox)

        button1 = Gtk.Button.new_with_mnemonic("_Open")
        button1.connect("clicked", self.on_file_clicked)
        hbox.add(button1)

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
            original_img = Image.open(dialog.get_filename())
            original_pix = original_img.load()
            img = Image.open(dialog.get_filename())
            pix = img.load();
            width, height = img.size

            # Flip Horizontally
            #for i in range(width):
            #    for j in range(height):
            #        pix[i,j] = original_pix[width-i-1,j]

            # Flip Vertically
            #for i in range(width):
            #    for j in range(height):
            #        pix[i,j] = original_pix[i,height-j-1]



            img.show()



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

    def on_vertical_clicked(self, button):
        print("\"Vertical\" button was clicked")

    def on_luminance_clicked(self, button):
        print("\"Luminance\" button was clicked")

    def on_quantization_clicked(self, button):
        print("\"Quantization\" button was clicked")

    def on_save_clicked(self, button):
        print("\"Save\" button was clicked")


def image2pixbuf(self,im):
    arr = array.array('B', im.tostring())
    width, height = im.size
    return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                          True, 8, width, height, width * 4)

win = FPIWindow()
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
