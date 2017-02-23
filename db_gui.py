#!/usr/bin/env python
from __future__ import print_function
from classes import ReceiptItem
from dbutils import save_to_db, get_item
import pygtk
pygtk.require('2.0')
import gtk

class DbGui:

    def handle_input(self, barentry, nameentry, priceentry, dphentry):
        barcode = barentry.get_text()
        name = nameentry.get_text()
        dph = float(dphentry.get_text())
        try:
            price = float(priceentry.get_text())
        except ValueError:
            price = None
        for text in [barcode, name, price]:
            if text == "":
                print('not all fields were filled, waiting')
                return
        # we set the DPH to be 21 by default
        item = ReceiptItem(barcode, price, dph, name)
        print(item)
        print('saving to db')
        save_to_db(item)
        for entry in [barentry, priceentry]:
            entry.set_text('')
        barentry.grab_focus()

    def try_fill_fields(self, barentry, nameentry, priceentry, dphentry):
        barcode = barentry.get_text()
        item = get_item(barcode)
        print(item)
        if item == None:
	    priceentry.grab_focus()
            return
        else:
            nameentry.set_text(item.name)
            priceentry.set_text(str(item.price))
            dphentry.set_text(item.dph)
	priceentry.grab_focus()

    def __init__(self):
        # create a new window
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_size_request(400, 300)
        window.set_title("Pokladna")
        window.connect("delete_event", lambda w,e: gtk.main_quit())

        vbox = gtk.VBox(False, 0)
        window.add(vbox)
        vbox.show()

        barentry = gtk.Entry()
        bar_label = gtk.Label('Carovy kod')
        barentry.select_region(0, len(barentry.get_text()))
        vbox.pack_start(bar_label, False, True, 0)
        vbox.pack_start(barentry, True, True, 0)
        bar_label.show()
        barentry.show()

        name_entry = gtk.Entry()
        name_label = gtk.Label('Nazev zbozi')
        vbox.pack_start(name_label, True, True, 0)
        vbox.pack_start(name_entry, True, True, 0)
        name_label.show()
        name_entry.show()

        price_entry = gtk.Entry()
        price_label = gtk.Label('Cena')
        vbox.pack_start(price_label, True, True, 0)
        vbox.pack_start(price_entry, True, True, 0)
        price_label.show()
        price_entry.show()

        name_entry.connect("activate", lambda x: price_entry.grab_focus())
        
        dph_entry = gtk.Entry()
        dph_label = gtk.Label('DPH')
        dph_entry.set_text("15")
        vbox.pack_start(dph_label, True, True, 0)
        vbox.pack_start(dph_entry, True, True, 0)
        dph_label.show()
        dph_entry.show()

        barentry.connect("activate", lambda x : self.try_fill_fields(barentry, name_entry, price_entry, dph_entry))        
        hbox = gtk.HBox(False, 0)
        vbox.add(hbox)
        hbox.show()
                                  
        save_button = gtk.Button(stock=gtk.STOCK_SAVE)
        save_button.connect("clicked", lambda x: self.handle_input(barentry, name_entry,
            price_entry, dph_entry))
    
        price_entry.connect("activate", lambda x: save_button.grab_focus())
        vbox.pack_start(save_button, True, True, 0)
        button = gtk.Button(stock=gtk.STOCK_CLOSE)
        button.connect("clicked", lambda w: gtk.main_quit())
        vbox.pack_start(button, True, True, 0)
        save_button.set_flags(gtk.CAN_DEFAULT)
        save_button.grab_default()
        button.show()
        save_button.show()
        window.show()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    DbGui()
    main()
