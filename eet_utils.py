import eet
import config
# read number from file
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
    try:
        result = eet_client.send_payment(payment)
    except:
        result = {}
        result['fik'] = None
    trzba = payment.xml(eet_client._signing)
    pkp = trzba[2][0].text
    result.update({"pkp": pkp})
    print(result)
    return result

def resend_receipt(receipt):
    amount = receipt.total_paid
    eet_client = eet.EET(config.cert_path, config.cert_pass, provozovna=config.provozovna_number,
            pokladna='pokladna001', testing=False, eet_url=config.eet_url)
    payment = eet_client.create_payment(receipt.number, amount, first=False, test=False)
    try:
        result = eet_client.send_payment(payment)
    except:
        result = {}
        result['fik'] = None
    return result
