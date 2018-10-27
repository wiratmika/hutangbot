import hashlib
import time


def beautify_amount(amount):
    return 'Rp ' + '{:,}'.format(int(amount))


def generate_transaction_id():
    sha1 = hashlib.sha1()
    sha1.update(str(time.time()).encode('utf-8'))
    return sha1.hexdigest()[:5]
