#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import os
import random
from proteus import Model
from .utils import *

def create_party(name, street=None, streetbis=None, zip=None, city=None,
        subdivision_code=None, country_code='ES', phone=None, website=None,
        email=None, address_name=None):
    """
    Create party
    """
    Address = Model.get('party.address')
    ContactMechanism = Model.get('party.contact_mechanism')
    Country = Model.get('country.country')
    Party = Model.get('party.party')
    Subdivision = Model.get('country.subdivision')

    parties = Party.find([('name', '=', name)])
    if parties:
        return parties[0]

    country, = Country.find([('code', '=', country_code)])
    if subdivision_code:
        subdivision, = Subdivision.find([('code', '=', subdivision_code)])
    else:
        subdivision = None

    if zip is None:
        # Create a ZIP from Barcelona if none was provided
        zip = '08' + str(random.randrange(1000)).zfill(3)

    party = Party(name=name)
    party.addresses.pop()
    party.addresses.append(
        Address(
            name=address_name,
            street=street,
            streetbis=streetbis,
            zip=zip,
            city=city,
            country=country,
            subdivision=subdivision))
    if phone:
        party.contact_mechanisms.append(
            ContactMechanism(type='phone',
                value=phone))
    if website:
        party.contact_mechanisms.append(
            ContactMechanism(type='website',
                value=website))
    if email:
        party.contact_mechanisms.append(
            ContactMechanism(type='email',
                value=email))
    party.lang = random.choice(get_languages())

    if hasattr(party, 'account_payable'):
        payable = get_account_payable()
        if payable:
            party.account_payable = payable[0].id
    if hasattr(party, 'account_payable'):
        receivable = get_account_receivable()
        if receivable:
            party.account_receivable = receivable[0].id
    if hasattr(party, 'customer_payment_term'):
        terms = get_payment_terms()
        if terms:
            term = random.choice(terms)
            party.customer_payment_term = term
            party.supplier_payment_term = term
    if hasattr(party, 'customer_payment_type'):
        types = get_payment_types('receivable')
        if types:
            party.customer_payment_type = random.choice(types)
    if hasattr(party, 'customer_payment_type'):
        types = get_payment_types('payable')
        if types:
            party.supplier_payment_type = random.choice(types)
    if hasattr(party, 'sale_price_list'):
        price_lists = get_price_lists()
        if price_lists:
            party.sale_price_list = random.choice(price_lists)
    if hasattr(party, 'include_347'):
        party.include_347 = True

    party.save()
    return party

def create_parties(count=1000):
    """
    Create 'count' parties taking random information from the following files:
    - party-companies.txt
    - party-streets.txt
    - party-names.txt
    - party-surnames.txt
    """
    gal_dir = os.path.dirname(os.path.realpath(__file__))

    with open(gal_dir + '/party-companies.txt', 'r') as f:
        companies = f.read().split('\n')
    companies = [x.strip() for x in companies if x.strip()]
    companies = random.sample(companies, min(len(companies), count))
    with open(gal_dir + '/party-streets.txt', 'r') as f:
        streets = f.read().split('\n')
    streets = [x.strip() for x in streets if x.strip()]
    with open(gal_dir + '/party-names.txt', 'r') as f:
        names = f.read().split('\n')
    names = [x.strip() for x in names if x.strip()]
    with open(gal_dir + '/party-surnames.txt', 'r') as f:
        surnames = f.read().split('\n')
    surnames = [x.strip() for x in surnames if x.strip()]
    phones = ['93', '972', '973', '977', '6', '900']
    for company in companies:
        name = random.choice(names)
        surname1 = random.choice(surnames)
        surname2 = random.choice(surnames)
        street = random.choice(streets)
        name = '%s %s, %s' % (surname1, surname2, name)
        street = '%s, %d' % (street, random.randrange(1, 100))
        phone = random.choice(phones)
        while len(phone) < 9:
            phone += str(random.randrange(9))
        create_party(company, street=street, zip=None, city=None,
            subdivision_code=None, country_code='ES', phone=phone,
            website=None, address_name=name)
