#!/usr/bin/env python3
from classes import *
from datetime import datetime
import sqlite3 as lite
import config

def add_to_pay():
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''create TABLE toPay (id integer PRIMARY KEY,
    Date TEXT, 
    receipt_id integer, 
    pkp text,
    bkp text,
    total_paid float
    ''')
    con.commit()
    con.close()

def create_table():
    con = None
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''CREATE TABLE Items
            (id integer PRIMARY KEY, barcode text, name text, price float, dph float, unique(barcode))''')
    cur.execute('''CREATE TABLE Receipts
            (id integer PRIMARY KEY, Date TEXT, total_paid float, fik TEXT, bkp TEXT)''')
    cur.execute('''CREATE TABLE RecHasItems
            (id integer,
            item_id integer,
            amount integer,
            receipt_id integer,
            foreign key(item_id) references Items(id),
            foreign key(receipt_id) references Receipts(id)) ''')
    con.commit()
    con.close()

def get_item(barcode):
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''select name, price from Items where barcode = ?''', (barcode,))
    res = cur.fetchone()
    con.close()
    print(res)
    if res:
        return ReceiptItem(barcode, res[1], 21, res[0])
    else:
        return None

def save_to_db(item):
    barcode = item.barcode
    name = item.name
    price = item.price
    dph = item.dph
    con = lite.connect(config.dbname)
    cur = con.cursor()
    # INSERT OR REPLACE
    cur.execute('''REPLACE into Items(barcode, name, price, dph) values(?,?,?,?)''', 
            (barcode, name, price, dph))
    con.commit()

def save_toSend(receipt):
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''Insert into toPay(Date, receipt_id, pkp, bkp, total_paid)) values(?,?,?,?,?)''', 
            (receipt.date, receipt.number, receipt.pkp, receipt.bkp, receipt.total_paid))
    con.commit()
    con.close()

def get_toSend():
    receipts = []
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''select * from toPay''')
    res = cur.fetchall()
    for rec_candidate in res:
        tmp_receipt = Receipt([])
        tmp_receipt.date = rec_candidate[1]
        tmp_receipt.number = rec_dandidate[2]
        tmp_receipt.pkp = rec_candidate[3]
        tmp_receipt.bkp = rec_dandidate[4]
        tmp_receipt.total_paid = rec_candidate[5]
        receipts.add(tmp_receipt)
    con.close()
    return receipts

def delete_toSend(receipt):
    receipt_id = receipt.number
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''delete from toPay where receipt_id = ?''', (receipt_id,))
    con.commit()
    con.close()

def save_receipt(receipt):
    con = lite.connect(config.dbname)
    cur = con.cursor()
    total_paid = 0
    item_ids = []
    for item in receipt.items:
        total_paid +=item.price
    con = lite.connect(config.dbname)
    cur = con.cursor()
    # INSERT OR REPLACE
    cur.execute('''Insert into Receipts(Date, total_paid, fik, bkp) values(?,?,?,?)''', 
            (receipt.date, total_paid, receipt.fik, receipt.bkp))
    con.commit()
    con.close()

def get_latest_receipt_id():
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''select MAX(id) from Receipts''')
    res = cur.fetchone()
    con.close()
    print("latest receipt id:", res)
    return res[0]

def show_db_content():
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''select * from Items''')
    res = cur.fetchall()
    for item in res:
        print(item)
    print("receipts")
    cur.execute('''select * from Receipts''')
    res = cur.fetchall()
    for item in res:
        print(item)

def get_total():
    con = lite.connect(config.dbname)
    cur = con.cursor()
    cur.execute('''select * from Receipts''')
    res = cur.fetchall()
    value = 0
    for item in res:
        value += item[2]
    return value

if __name__ == '__main__':
   # create_table()
   show_db_content()
   print(get_latest_receipt_id())

