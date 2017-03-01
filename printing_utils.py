
#!/usr/bin/env python3
import config
import subprocess
header = config.header
tail = config.tail
MAX_L = 34
def format_receipt(receipt, succ=True):
    res = header + "\n"
    res += "dic: " + config.dic + "\n"
    res += "Uctenka cislo " + str(receipt.number) + "\n"
    total = 0
    for item in receipt.items:
        name_l = len(item.name)
        total += item.price
        price_l = len("{:.2f}".format(item.price)) # format to 2 decimals here
        dots = (MAX_L -name_l-price_l) * "."
        res += "{}{}{:.2f}\n".format(item.name, dots, item.price)
    total_l = len("{:.2f}".format(total))
    res += "Celkove{}{:.2f}\n".format(((MAX_L -7 -total_l) * "."), total)
    res += "A ted EET zabava: \n"
    if succ:
        res += "fik: " +receipt.fik + "\n" #textwrap these
    else:
        res += "Nebylo navazano spojeni, tiskneme PKP\n"
        res += "PKP: " +receipt.pkp + "\n" 
    res += "bkp: " +receipt.bkp + "\n" 
    res += "datum: "+ receipt.date + "\n"
    res += tail
    print(res)
    return(res)

def print_POS(text):
    p = subprocess.Popen(['lp', '-d', 'POS58', '-o', 'cpi=18', '-o', 'lpi=10','-'], stdin=subprocess.PIPE)
    p.communicate(str.encode(text))

def main():
    from classes import Receipt
    from classes import ReceiptItem
    items = [ReceiptItem("666", 40, 'e', "syr"),
             ReceiptItem("666", 19.3333, 'e', "nepro"),ReceiptItem("666", 230, 'e', "dava"),ReceiptItem("666", 90, 'e', "me"),ReceiptItem("666", 40.00, 'e', "syr")]
    rec = Receipt(items)
    rec.number = 1
    rec.fik = "nejaky fik kod"
    rec.bkp = "nejaky bezpecnosti kod"
    format_receipt(rec)

if __name__ == "__main__":
    main()
