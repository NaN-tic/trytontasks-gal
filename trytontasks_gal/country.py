#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from proteus import Wizard

def load_country_zip_es():
    'Loads zip codes from spain'
    load_zips = Wizard('load.country.zips')
    load_zips.execute('accept')
