#!/usr/bin/env python
from __future__ import print_function
import random
from classes import ReceiptItem, Receipt
from dbutils import save_toSend, get_item, get_latest_receipt_id, save_receipt
from eet_utils import send_receipt 
from printing_utils import *
from eet import utils
import pygtk
pygtk.require('2.0')
import gtk

class DbGui:
    def print_to_file(text, filename = "logs.tmp"):
        with open(filename, 'a') as f:
            f.write(text)
            f.write('\n')
 
    def handle_input(self, nameentry, priceentry):
        name = nameentry.get_text()
        price = float(priceentry.get_text())
        self.add_and_update(name, price, "15", barcode="Custom") 

    def custom_entry(self, widget=None, data=None):
        answerwin = gtk.Window()
        answerwin.set_position(gtk.WIN_POS_CENTER)
        answerwin.set_size_request(400, 200)
        answerwin.set_title("Zadejte vlastni polozku")
        vbox = gtk.VBox()
        name_entry = gtk.Entry()
        name_label = gtk.Label('Nazev zbozi')
        vbox.pack_start(name_label, True, True, 0)
        vbox.pack_start(name_entry, True, True, 0)
        price_entry = gtk.Entry()
        price_label = gtk.Label('Cena')
        vbox.pack_start(price_label, True, True, 0)
        vbox.pack_start(price_entry, True, True, 0)
        price_label.show()
        price_entry.show()
        name_label.show()
        name_entry.show()
        vbox.show()
        hbox = gtk.HBox()
        save_button = gtk.Button("pridat")
        save_button.connect("clicked", lambda x: self.handle_input(name_entry, price_entry))
        done_button = gtk.Button("hotovo")
        done_button.connect("clicked", lambda x: answerwin.destroy())
        save_button.show()
        done_button.show()
        hbox.show()
        hbox.pack_start(save_button)
        hbox.pack_start(done_button)
        vbox.pack_start(hbox)
        answerwin.add(vbox)
        answerwin.show()   

   
    def create_receipt_view(self):
        self.treeView = gtk.TreeView(self.store)
        for i, column_title in enumerate(["Polozka", "Cena", "DPH"]):
            cellRender = gtk.CellRendererText()
            column = gtk.TreeViewColumn(column_title, cellRender, text=i)
            self.treeView.append_column(column)
        self.treeView.show()
        return self.treeView 
    
    def remove_from_view(self):
        result = self.treeView.get_selection().get_selected()
        if result:
            model, treeiter = result
            price = model.get_value(treeiter, 1)
            print(price)
            self.current_value -= price
            self.textbuffer.set_text(str(self.current_value))
            model.remove(treeiter)

    def add_to_store(self):
        barcode = self.barentry.get_text()
        item = get_item(barcode)
        if item == None:
            return
        else:
            self.current_value += item.price
            self.store.append([item.name, item.price, item.dph, barcode])
            self.textbuffer.set_text(str(self.current_value))
            self.barentry.set_text("")
    
            self.barentry.grab_focus()

    def create_receipt(self, eet=True):
        items = []
        for item in self.store:
            items.append(ReceiptItem(item[3], item[1], item[2], item[0]))
            print(items[-1])
        receipt = Receipt(items)
        num = get_latest_receipt_id()
        if num == None:
            num = 1
        receipt.number = num + 1 # next ID
        eet_result = send_receipt(receipt, testing=eet)
        
        if eet_result['fik'] == None:
            print(eet_result['message'])
            date = eet_result['date_rejected']
            receipt.fik = "None"
            receipt.bkp = eet_result['bkp']
            amount = 0
            for item in receipt.items:
                amount += item.price
            receipt.pkp = eet_result['pkp']
            receipt.fik = "None"
            print_POS(format_receipt(receipt, succ=False))
            # save to tmp
            if eet:
                save_receipt(receipt)
                save_toSend(receipt)
                print_to_file(str(receipt))
        else:
            date = eet_result['date_received']
            fik = eet_result['fik']
            bkp = eet_result['bkp']
            receipt.fik = fik
            receipt.bkp = bkp
            receipt.date = date
            print_POS(format_receipt(receipt, succ=True))
            if eet :
                save_receipt(receipt)
            self.current_value = 0
            self.store.clear()
            self.textbuffer.set_text(str(self.current_value))
            self.barentry.grab_focus()

    def try_resend(self):
        pass
    def add_and_update(self, name, price, dph, barcode):
        self.current_value += price
        self.store.append([name, price, dph, barcode])
        self.textbuffer.set_text(str(self.current_value))
        self.barentry.set_text("")
        self.barentry.grab_focus()

    def create_upper_hbox(self):
        self.upper_hbox = gtk.HBox(False, 0)
        # barcode with label
        self.label_box = gtk.VBox(False, 0)
        self.barentry = gtk.Entry()
        self.bar_label = gtk.Label('Carovy kod')
        self.barentry.show()
        self.barentry.grab_focus()
        self.barentry.connect("activate", lambda x: self.add_to_store())
        self.bar_label.show()
        self.barentry.select_region(0, len(self.barentry.get_text()))
        self.label_box.pack_start(self.bar_label, False, True, 0)
        self.label_box.pack_start(self.barentry, True, True, 0)
        self.label_box.show()
        # add custom button
        custom_button = gtk.Button("vlastni polozka")
        custom_button.connect("clicked", lambda w: self.custom_entry())
        self.upper_hbox.pack_start(self.label_box, True)
        self.upper_hbox.pack_start(custom_button)
        custom_button.show()
        self.upper_hbox.show()
        return self.upper_hbox 

    def __init__(self):
        # create a new window
        self.current_value = 0.0;
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_size_request(600, 700)
        window.set_title("Pokladna")
        window.connect("delete_event", lambda w,e: gtk.main_quit())

        hbox = gtk.HBox(False,0)
        window.add(hbox)
        self.textview = gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textview.set_editable(False)
        self.textview.show()

        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self.textview, False, False, 0)
        vbox.pack_start(self.create_upper_hbox(), False, False, 0)
                                  #name, price, dph, barcode
        self.store = gtk.ListStore(str, float, str, str)
        self.textbuffer.set_text(str(self.current_value))
        self.scrollable_treelist = gtk.ScrolledWindow()
        self.create_receipt_view()
        self.scrollable_treelist.add(self.treeView)
        self.scrollable_treelist.set_usize(600,460)
        self.treeView.connect("row-activated", lambda x,y,z: self.remove_from_view())
        vbox.pack_start(self.scrollable_treelist)
        self.scrollable_treelist.show()
        hbox.pack_start(vbox)
        vbox.show()
        hbox.show()

        receipt_button = gtk.Button("Poslat EET")
        receipt_button.connect("clicked", lambda x: self.create_receipt())
        self.barentry.grab_focus()
        vbox.pack_start(receipt_button, True, True, 0)
        receipt_button.show()
        window.show()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    DbGui()
    main()
