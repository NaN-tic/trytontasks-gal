#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import datetime
from dateutil.relativedelta import relativedelta
from proteus import Model
from .utils import *

TODAY = datetime.date.today()

def create_purchases(count=100, linecount=10):
    """
    It creates 'count' purchases using random products (linecount maximum)
    and parties.

    If 'count' is not specified 100 is used by default.
    If 'linecount' is not specified 10 is used by default.
    """
    Purchase = Model.get('purchase.purchase')
    PurchaseLine = Model.get('purchase.line')
    Party = Model.get('party.party')
    Product = Model.get('product.product')
    Term = Model.get('account.invoice.payment_term')

    parties = Party.find([])
    products = Product.find([('purchasable', '=', True)])
    if not products:
        print 'Not found purchasable products'
        return
    terms = Term.find([])

    for c in xrange(count):
        purchase = Purchase()
        purchase.party = random.choice(parties)
        if not purchase.payment_term:
            purchase.payment_term = random.choice(terms)

        for lc in xrange(random.randrange(1, linecount)):
            line = PurchaseLine()
            purchase.lines.append(line)
            line.product = random.choice(products)
            line.quantity = random.randrange(1, 20)
        purchase.save()

def process_purchases(config):
    """
    It randomly processes some purchases:

    10% of existing draft purchases are left in draft state
    10% of existing draft purchases are left in quotation state
    80% of existing draft purchases are left in confirmed state
    """
    Purchase = Model.get('purchase.purchase')

    purchases = Purchase.find([('state', '=', 'draft')])
    if not purchases:
        print 'Not found draft purchases'
        return
    # Change 90% to quotation state
    purchases = random.sample(purchases, int(0.9 * len(purchases)))
    Purchase.quote([x.id for x in purchases], config.context)

    # Change 90% to confirmed state
    purchases = random.sample(purchases, int(0.9 * len(purchases)))
    Purchase.confirm([x.id for x in purchases], config.context)
