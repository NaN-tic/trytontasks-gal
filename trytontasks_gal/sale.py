#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import datetime
from dateutil.relativedelta import relativedelta
from proteus import Model
from .utils import *

TODAY = datetime.date.today()

def create_sales(count=100, linecount=10):
    """
    It creates 'count' sales using random products (linecount maximum)
    and parties.

    If 'count' is not specified 100 is used by default.
    If 'linecount' is not specified 10 is used by default.
    """
    Sale = Model.get('sale.sale')
    SaleLine = Model.get('sale.line')
    Party = Model.get('party.party')
    Product = Model.get('product.product')
    Term = Model.get('account.invoice.payment_term')

    parties = Party.find([])
    products = Product.find([('salable', '=', True)])
    if not products:
        print 'Not found salable products'
        return
    terms = Term.find([])

    for c in xrange(count):
        sale = Sale()
        sale.sale_date = random_datetime(TODAY + relativedelta(months=-12),
            TODAY)
        sale.party = random.choice(parties)
        if not sale.payment_term:
            sale.payment_term = random.choice(terms)

        for lc in xrange(random.randrange(1, linecount)):
            line = SaleLine()
            sale.lines.append(line)
            line.product = random.choice(products)
            line.quantity = random.randrange(1, 20)
        sale.save()

def process_sales(config):
    """
    It randomly processes some sales:

    10% of existing draft sales are left in draft state
    10% of existing draft sales are left in quotation state
    10% of existing draft sales are left in confirmed state
    70% of existing draft sales are left in processed state
    """
    Sale = Model.get('sale.sale')

    sales = Sale.find([('state', '=', 'draft')])
    if not sales:
        print 'Not found draft sales'
        return
    #TODO: Put random sale dates
    # sale.sale_date = random_datetime(TODAY + relativedelta(months=-12),
    #        TODAY)

    # Change 90% to quotation state
    sales = random.sample(sales, int(0.9 * len(sales)))
    Sale.quote([x.id for x in sales], config.context)

    # Change 90% to confirmed state
    sales = random.sample(sales, int(0.9 * len(sales)))
    Sale.confirm([x.id for x in sales], config.context)

    # Change 90% to processed state
    sales = random.sample(sales, int(0.9 * len(sales)))
    Sale.process([x.id for x in sales], config.context)
