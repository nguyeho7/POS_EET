#!/usr/bin/env python3
from datetime import date

class Receipt(object):

    def __init__(self, items):
        self.items = []
        self.date = date.today()
        for item in items:
            self.items.append(item)
    def __str__(self):
	    res = ""
	    for item in self.items:
		    res += str(item) + "\n"

class ReceiptItem(object):
    
    def __init__(self, barcode, price, dph_bracket, name):
        self.barcode = barcode
        self.price = price
        self.dph = dph_bracket
        self.name = name

    def __str__(self):
        res = "Name: {}\n price: {}\n dph_bracket: {}\n barcode: {}".format(self.name,self.price,self.dph, self.barcode)
        return res
