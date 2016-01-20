#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from proteus import Wizard

def load_bank_es():
    'Loads all banks from spain'
    load_banks = Wizard('load.banks')
    load_banks.execute('accept')
