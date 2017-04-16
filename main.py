#!/usr/bin/env python
from __future__ import print_function
import random
from classes import ReceiptItem, Receipt
from dbutils import *
from eet_utils import *
from printing_utils import *
from eet import utils
import pygtk
pygtk.require('2.0')
import gtk

class DbGui:
    def print_to_file(self, to_print, filename = "logs.tmp"):
        with open(filename, 'a') as f:
            f.write(to_print)
            f.write('\n')
 
    def handle_input(self, nameentry, priceentry):
        name = nameentry.get_text()
        price = float(priceentry.get_text())
        count_text = self.item_count.get_text()
        if str.isdigit(count_text):
            count = int(count_text)
        else:
            count = 1
        for x in range(count):
            self.add_and_update(name, price, "15", barcode="Custom") 
        self.item_count.set_text("1")

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
            self.current_value -= price
            self.textbuffer.set_text(str(self.current_value))
            model.remove(treeiter)

    def add_to_store(self):
        barcode = self.barentry.get_text()
        item = get_item(barcode)
        count_text = self.item_count.get_text()
        if str.isdigit(count_text):
            count = int(count_text)
        else:
            count = 1
        if item == None:
            return
        else:
            for x in range(count):
                self.current_value += item.price
                self.store.append([item.name, item.price, item.dph, barcode])
                self.textbuffer.set_text(str(self.current_value))
            self.item_count.set_text("1")
            self.barentry.set_text("")
            self.barentry.grab_focus()

    def try_send_failed_receipts(self):
        receipts = get_toSend()
        num_of_receipts = len(receipts)
        print("trying to send {} receipts".format(num_of_receipts))
        for receipt in receipts:
            eet_result = resend_receipt(receipt)
            if eet_result['fik'] != None:
                print("sent " + str(receipt) + " successfully")
                delete_toSend(receipt)
            else:
                print("sending failed, will try later")

    def create_receipt(self, eet=True):
        items = []
        self.try_send_failed_receipts()
        for item in self.store:
            items.append(ReceiptItem(item[3], item[1], item[2], item[0]))
            print(items[-1])
        receipt = Receipt(items)
        num = get_latest_receipt_id()
        if num == None:
            num = 1
        receipt.number = num + 1 # next ID
        eet_result = send_receipt(receipt, testing=eet)
        amount = 0
        for item in receipt.items:
            amount += item.price
        if eet_result['fik'] == None:
            receipt.fik = "None"
            receipt.bkp = "None"
            receipt.total_paid = amount
            receipt.pkp = eet_result['pkp']
            receipt.amount = amount
            print_POS(format_receipt(receipt, succ=False))
            print("failed to send receipt")
            # save to tmp
            if eet:
                save_receipt(receipt)
                save_toSend(receipt)
                self.print_to_file(str(receipt))
                self.current_value = 0
                self.store.clear()
                self.textbuffer.set_text(str(self.current_value))
                self.barentry.grab_focus()
        else:
            date = eet_result['date_received']
            fik = eet_result['fik']
            bkp = eet_result['bkp']
            receipt.fik = fik
            receipt.bkp = bkp
            receipt.date = date
            receipt.total_paid = amount
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

    def print_earnings(self):
        val = get_total()
        print_POS(format_total(val))
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
        self.print_all_button = gtk.Button("Vytisknout trzby")
        self.print_all_button.connect('clicked', lambda x: self.print_earnings())
        self.print_all_button.show()
        self.upper_hbox.pack_start(self.label_box, True)
        self.upper_hbox.pack_start(custom_button)
        self.upper_hbox.pack_start(self.print_all_button, True)
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

        self.item_count = gtk.Entry()
        self.item_count.set_text("1")
        self.item_count_label = gtk.Label('Pocet kusu')

        self.item_count.connect("activate", lambda x: self.barentry.grab_focus())
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
        vbox.pack_start(self.item_count_label, True, True, 0)
        vbox.pack_start(self.item_count, True, True, 0)
        vbox.pack_start(receipt_button, True, True, 0)
        self.item_count.show()
        self.item_count_label.show()
        receipt_button.show()
        window.show()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    DbGui()
    main()
