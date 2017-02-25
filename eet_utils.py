import eet
import config
# read number from file
# instead of db, append 
# handle errors here
# FUCKING DB JESUS FUCKKKKKKKK
# pickle failed payments?
def send_receipt(receipt, testing=True):
    testing = config.testing
    amount = 0
    for item in receipt.items:
        amount += item.price
    if testing:
        eet_client = eet.EET(config.t_cert_path, config.t_cert_pass, provozovna=config.provozovna_number,
                pokladna='pokladna001', testing=False)
    else:
        eet_client = eet.EET(config.cert_path, config.cert_pass, provozovna=config.provozovna_number,
                pokladna='pokladna001', testing=False, eet_url=config.eet_url)
    payment = eet_client.create_payment(receipt.number, amount, test=False)
    result = eet_client.send_payment(payment)
    print(result)
    return result
