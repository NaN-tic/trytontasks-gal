#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import os
import xmltodict
import random
from decimal import Decimal
from proteus import Model
from .utils import *

def create_product_category(name):
    """
    Creates product category with the supplied name.
    """
    Category = Model.get('product.category')
    category = Category(name=name)
    category.save()

def create_product_categories(count=20):
    """
    Creates 'count' (20 by default) product categories.
    """
    Category = Model.get('product.category')
    for name in ('A', 'B', 'C', 'D', 'E'):
        category = Category(name=name)
        category.save()

def create_product(name, code="", template=None, cost_price=None,
        list_price=None, type='goods', unit=None, consumable=False):
    """
    Create product
    """
    ProductUom = Model.get('product.uom')
    Product = Model.get('product.product')
    ProductTemplate = Model.get('product.template')
    Category = Model.get('product.category')

    if module_installed('account'):
        Tax = Model.get('account.tax')

    categories = Category.find([])
    category = None
    if categories:
        category = random.choice(categories)

    product = Product.find([('name', '=', name), ('code', '=', code)])
    if product:
        return product[0]

    if not cost_price:
        cost_price = Decimal(random.randrange(1, 100))

    if not list_price:
        list_price = cost_price * (1 + Decimal(random.randrange(1, 100)) / 100)

    if unit is None:
        unit = ProductUom(1)

    if template is None:
        template = ProductTemplate()
        template.name = name
        template.default_uom = unit
        template.type = type
        template.consumable = consumable
        template.list_price = list_price
        template.cost_price = cost_price
        template.category = category
        if hasattr(template, 'salable'):
            template.salable = True
        if hasattr(template, 'purchasable'):
            template.purchasable = True

        if (hasattr(template, 'account_expense')
                or hasattr(template, 'account_revenue')):
            Company = Model.get('company.company')
            company = Company(1)
        if hasattr(template, 'account_expense'):
            Account = Model.get('account.account')
            expense = Account.find([
                ('kind', '=', 'expense'),
                ('company', '=', company.id),
                ])
            if expense:
                template.account_expense = expense[0]
        if hasattr(template, 'account_revenue'):
            Account = Model.get('account.account')
            revenue = Account.find([
                ('kind', '=', 'revenue'),
                ('company', '=', company.id),
                ])
            if revenue:
                template.account_revenue = revenue[0]
        if module_installed('account_es'):
            if hasattr(template, 'customer_taxes'):
                tax, = Tax.find([
                        ('template', '=',
                            get_object('account_es', 'iva_rep_21').id)
                        ])
                template.customer_taxes.append(tax)
            if hasattr(template, 'supplier_taxes'):
                tax, = Tax.find([
                        ('template', '=',
                            get_object('account_es', 'iva_sop_21').id)
                        ])
                template.supplier_taxes.append(tax)
        else:
            if hasattr(template, 'customer_taxes'):
                taxes = Tax.find([])
                if taxes:
                    template.customer_taxes.append(taxes[0])
            if hasattr(template, 'supplier_taxes'):
                taxes = Tax.find([])
                if taxes:
                    template.supplier_taxes.append(taxes[0])

        template.products[0].code = code
        template.save()
        product = template.products[0]
    else:
        product = Product()
        product.template = template
        product.code = code
        product.save()
    return product

def create_products(count=400):
    """
    Creates the 'count' first products from the icecat database in catalog.xml.
    """
    gal_dir = os.path.dirname(os.path.realpath(__file__))

    with open(gal_dir + '/product-catalog.xml', 'r') as f:
        xml = xmltodict.parse(f.read())
    i = 0
    for item in xml.get('ICECAT-interface').get('files.index').get('file'):
        name = item.get('@Model_Name')
        code = "PROD%05d" % i
        create_product(name, code)
        i += 1
        if i >= count:
            break

def create_price_lists(language='en_US', count=5, productcount=10, categorycount=2):
    """
    Creates 'count' pricelists using random products and quantities
    """
    PriceList = Model.get('product.price_list')
    PriceListLine = Model.get('product.price_list.line')
    Product = Model.get('product.product')
    Category = Model.get('product.category')
    category_module = module_installed('product_price_list_category')

    price_list_name = {
        'ca_ES': 'Tarifa',
        'en_US': 'Price List',
        'es_ES': 'Tarifa',
        }

    categories = Category.find()
    if module_installed('sale'):
        domain = [('salable', '=', True)]
    else:
        domain = []
    products = Product.find(domain)
    for c in xrange(count):
        price_list = PriceList()
        price_list.name = price_list_name[language] +" "+ str(c)

        sequence = 1
        for lc in xrange(random.randrange(1, productcount)):
            line = PriceListLine()
            price_list.lines.append(line)
            line.sequence = sequence
            line.product = random.choice(products)
            line.formula = 'unit_price * 0.90'
            sequence += 1

        if category_module:
            for lc in xrange(random.randrange(1, categorycount)):
                line = PriceListLine()
                price_list.lines.append(line)
                line.sequence = sequence
                line.category = random.choice(categories)
                line.formula = 'unit_price * 0.95'
                sequence += 1

        line = PriceListLine()
        price_list.lines.append(line)
        line.sequence = sequence
        line.formula = 'unit_price'

        price_list.save()
