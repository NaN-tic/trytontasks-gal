#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import random
from datetime import timedelta
from functools32 import lru_cache
from proteus import Model

def random_datetime(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)

@lru_cache()
def module_installed(module):
    Module = Model.get('ir.module')
    return bool(Module.find([
            ('name', '=', module),
            ('state', '=', 'installed'),
            ]))

@lru_cache()
def get_account_payable():
    Payable = Model.get('account.account')
    return Payable.find([('kind', '=', 'payable')])

@lru_cache()
def get_account_receivable():
    Receivable = Model.get('account.account')
    return Receivable.find([('kind', '=', 'receivable')])

@lru_cache()
def get_payment_terms():
    Term = Model.get('account.invoice.payment_term')
    return Term.find([])

@lru_cache()
def get_payment_types(kind):
    Type = Model.get('account.payment.type')
    return Type.find([('kind', '=', kind)])

@lru_cache()
def get_languages():
    Lang = Model.get('ir.lang')
    return Lang.find([
            ('code', 'in', ['ca_ES', 'es_ES', 'en_US']),
            ])

@lru_cache()
def get_price_lists():
    PriceList = Model.get('product.price_list')
    return PriceList.find([])

@lru_cache()
def get_banks():
    if not module_installed('bank'):
        return
    Bank = Model.get('bank')
    return Bank.find([])

@lru_cache()
def get_company():
    Company = Model.get('company.company')
    companies = Company.find([])
    if companies:
        return companies[0]

@lru_cache()
def get_model_id(module, fs_id):
    ModelData = Model.get('ir.model.data')
    data, = ModelData.find([
            ('module', '=', module),
            ('fs_id', '=', fs_id),
            ])
    Class = Model.get(data.model)
    return data.model, data.db_id

def get_object(module, fs_id):
    model, id = get_model_id(module, fs_id)
    Class = Model.get(model)
    return Class(id)
