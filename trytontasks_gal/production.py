#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import random
from proteus import Model, Wizard

def create_boms(name='pc', inputcount=10, inputquantity=10):
    """
    Creates boms for all products that contain the word 'name' in their name.

    It creates between 1 and inputcount inputs with quantity between 1 and
    inputquantity.

    If name is empty it creates boms for 20% of the products available in the
    database.
    """

    Product = Model.get('product.product')
    BOM = Model.get('production.bom')
    Input = Model.get('production.bom.input')
    Output = Model.get('production.bom.output')
    ProductBOM = Model.get('product.product-production.bom')

    products = Product.find([])
    products = [x.id for x in products]
    if name:
        to_produce = Product.find([('name', 'ilike', '%' + name + '%')])
    else:
        to_produce = random.sample(products, int(0.2 * len(products)))
        to_produce = Product.find([('id', 'in', to_produce)])
    to_purchase = Product.find([('id', 'not in', [x.id for x in to_produce])])
    for product in to_produce:
        product.purchasable = False

        bom = BOM()
        bom.name = ''
        if product.code:
            bom.name = '[%s] ' % product.code
        bom.name += product.template.name

        # Use sample because product must be unique per BOM
        for input_product in random.sample(to_purchase, random.randrange(1, inputcount)):
            input_ = Input()
            bom.inputs.append(input_)
            input_.product = input_product
            input_.quantity = random.randrange(1, inputquantity)

        output = Output()
        bom.outputs.append(output)
        output.product = product
        output.quantity = 1
        bom.save()

        pb = ProductBOM()
        pb.bom = bom
        product.boms.append(pb)
        product.save()

def create_production_requests():
    Wizard('production.create_request').execute('create_')
