#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import os
import random
import datetime
from invoke import task, run
from blessings import Terminal
from proteus import Model, Wizard
from proteus import config as pconfig_
from trytond.protocols.dispatcher import create as tcreate
from trytond.config import config, parse_uri

from .utils import *
from .company import *
from .bank import *
from .country import *
from .account import *
from .party import *
from .product import *
from .sale import *
from .sale_opportunity import *
from .purchase import *
from .production import *
from .stock import *

t = Terminal()

TODAY = datetime.date.today()

def create_database(database, language, password):
    tcreate(database, password, language, password)

def set_config(database, password):
    os.environ['DB_NAME'] = database
    database = 'postgresql://%s' % database
    return pconfig_.set_trytond(database=database, user='admin', config_file='./trytond.conf')

def install_modules(config, modules):
    Module = Model.get('ir.module')
    modules = Module.find([
            ('name', 'in', modules),
            ])
    for module in modules:
        if module.state == 'installed':
            module.click('upgrade')
        else:
            module.click('install')
    modules = [x.name for x in Module.find([('state', '=', 'to install')])]
    Wizard('ir.module.install_upgrade').execute('upgrade')

    ConfigWizardItem = Model.get('ir.module.config_wizard.item')
    for item in ConfigWizardItem.find([('state', '!=', 'done')]):
        item.state = 'done'
        item.save()

    installed_modules = [m.name
        for m in Module.find([('state', '=', 'installed')])]
    return modules, installed_modules

@task()
def create(database, language='en_US', password='admin'):
    'Create new Gal Database (PostgreSQL)'
    config.update_etc('./trytond.conf')
    create_database(database, language, password)

@task()
def install(database, password='admin', modules=
        'company party product product_price_list account ' \
        'account_payment_type sale purchase'):
    'Install modules and create data'
    pconfig = set_config(database, password)
    context = pconfig.context
    language = context.get('language')

    # TODO modules args list parameters
    # https://github.com/pyinvoke/invoke/issues/132
    modules = modules.split(' ')
    print t.green("Modules to install: ") + ', '.join(modules)

    to_install, installed = install_modules(pconfig, modules)

    if 'bank_es' in to_install:
        print "Load Spanish Banks..."
        load_bank_es()
    if 'country_zip_es' in to_install:
        print "Load Spanish cities and subdivisions..."
        load_country_zip_es()

    if 'company' in to_install:
        print "Create company..."
        create_company(pconfig, 'TrytonERP')
    if 'account' in to_install:
        print "Create accounts..."
        last_year = TODAY.year -1
        create_fiscal_year(config=pconfig, year=last_year)
        create_fiscal_year(config=pconfig)
        create_payment_terms()
        if 'account_es' in to_install:
            module = 'account_es'
            fs_id = 'es'
        elif 'account_es_pyme' in to_install:
            module = 'account_es_pyme'
            fs_id = 'es_pyme'
        else:
            module = 'account'
            fs_id = 'account_template_root_%s' % language[:2]
        create_account_chart(module=module, fs_id=fs_id)
        create_taxes()
    if 'account_payment_type' in to_install:
        print "Create payment types..."
        create_payment_types()
    if 'party' in to_install:
        print "Create parties..."
        create_parties()
    if 'product' in to_install:
        print "Create products..."
        create_product_categories()
        create_products()
    #~ if 'product_price_list' in to_install:
        #~ print "Create price lists..."
        #~ create_price_lists(language=language)
    if 'sale' in to_install:
        print "Create sales..."
        create_sales()
        process_sales(config=pconfig)
    if 'sale_opportunity' in to_install:
        print "Create sale opportunities..."
        create_opportunities()
        process_opportunities()
    #~ if 'purchase' in to_install:
        #~ print "Create purchases..."
        #~ create_purchases()
        #~ process_purchases(config=pconfig)
    #~ if 'production' in to_install:
        #~ print "Create productions..."
        #~ create_boms()
        #~ create_production_requests()
    #~ if 'stock' in to_install:
        #~ print "Create Stock Inventory..."
        #~ create_inventory(config=pconfig)
        #~ print "Process Stock Shipments..."
        #~ process_customer_shipments(config=pconfig)
        #~ process_supplier_shipments(config=pconfig)
    if 'account_invoice' in to_install:
        print "Process Customer Invoices..."
        process_customer_invoices(config=pconfig)

@task()
def dump(database):
    'Dump PSQL Database to SQL file'
    config.update_etc('./trytond.conf')
    uri = config.get('database', 'uri')

    print "Dump PSQL database: " + t.green(database)

    command = 'pg_dump -d %(database)s -U %(username)s > ./psql_%(database)s.sql' % {
        'database': database,
        'username': parse_uri(uri).username,
        }
    run(command)

@task()
def dropdb(database):
    'Drop PSQL Database'
    config.update_etc('./trytond.conf')
    uri = config.get('database', 'uri')

    print "Drop PSQL database: " + t.green(database)

    command = 'dropdb %(database)s -U %(username)s' % {
        'database': database,
        'username': parse_uri(uri).username,
        }
    run(command)
