#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from proteus import Model, Wizard
from .utils import *

def create_opportunities(count=100, linecount=10):
    """
    It randomly creates leads and opportunities

    It creates 'count' leads.
    - It converts 80% of the converted leads into opportunities
    - It converts 40% of the opportunities as lost
    - It sets 80% of the remaining opportunities are converted.
    """
    Opportunity = Model.get('sale.opportunity')
    OpportunityLine = Model.get('sale.opportunity.line')
    Product = Model.get('product.product')
    Party = Model.get('party.party')
    Term = Model.get('account.invoice.payment_term')

    parties = Party.find([])
    products = Product.find([('salable', '=', True)])
    terms = Term.find([])

    for x in xrange(count):
        opp = Opportunity()
        party = random.choice(parties)
        product = random.choice(products)
        opp.description = '%s - %s' % (party.rec_name, product.rec_name)
        opp.party = party
        if party.addresses:
            opp.address = party.addresses[0]
        opp.start_date = random_datetime(TODAY + relativedelta(months=-12),
            TODAY)
        if not opp.payment_term:
            opp.payment_term = random.choice(terms)
        opp.probability = random.randrange(1, 9) * 10
        opp.amount = random.randrange(1, 10) * 1000

        for lc in xrange(random.randrange(1, linecount)):
            line = OpportunityLine()
            opp.lines.append(line)
            line.product = random.choice(products)
            line.quantity = random.randrange(1, 20)
        opp.save()

def process_opportunities():
    """
    It randomly processes leads

    - It converts 80% of the leads into opportunities
    - It converts 40% of the opportunities as lost
    - It sets 80% of the remaining opportunities as converted (sale created)
    """
    Opportunity = Model.get('sale.opportunity')
    opps = Opportunity.find([('state', '=', 'lead')])
    opps = [x.id for x in opps]
    opps = random.sample(opps, int(0.8 * len(opps)))
    if opps:
        Opportunity.opportunity(opps, config.context)

    lost = random.sample(opps, int(0.4 * len(opps)))
    if lost:
        Opportunity.lost(lost, config.context)

    # Only convert non-lost opportunities
    nopps = []
    for opp in opps:
        if opp in lost:
            continue
        nopps.append(opp)
    opps = nopps
    opps = random.sample(opps, int(0.8 * len(opps)))
    opps = [Opportunity(x) for x in opps]
    if opps:
        Wizard('sale.opportunity.convert_opportunity', opps)
