#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import random
from proteus import Model

def create_inventory(config, maxquantity=1000):
    """
    It randomly makes an inventory of 80% of existing products.

    The remaining 20% is left with existing stock (usually 0).

    A random value between 0 and maxquantity (1000 by default) will be used.
    """
    Inventory = Model.get('stock.inventory')
    InventoryLine = Model.get('stock.inventory.line')
    Location = Model.get('stock.location')
    Product = Model.get('product.product')

    location = Location.find([('type', '=', 'warehouse')])[0].storage_location

    inventory = Inventory()
    inventory.location = location
    inventory.save()
    products = Product.find([
            ('type', '=', 'goods'),
            ('consumable', '=', False),
            ])
    products = random.sample(products, int(0.8 * len(products)))

    for product in products:
        inventory_line = InventoryLine()
        inventory.lines.append(inventory_line)
        inventory_line.product = product
        inventory_line.quantity = random.randrange(maxquantity)
        inventory_line.expected_quantity = 0.0
    inventory.save()
    Inventory.confirm([inventory.id], config.context)

def process_customer_shipments(config):
    """
    It randomly processes waiting customer shipments.

    20% of existing waiting customer shipments are left in waiting state
    80% are tried to be assigned (may not be assigned if stock is not enough)
    90% of the assigned ones are packed
    90% of the packed ones are done
    """
    Shipment = Model.get('stock.shipment.out')
    shipments = Shipment.find([('state', '=', 'waiting')])
    shipments = [x.id for x in shipments]

    shipments = random.sample(shipments, int(0.8 * len(shipments)))
    for shipment in shipments:
        Shipment.assign_try([shipment], config.context)
    shipments = random.sample(shipments, int(0.9 * len(shipments)))
    Shipment.pack(shipments, config.context)
    shipments = random.sample(shipments, int(0.9 * len(shipments)))
    Shipment.done(shipments, config.context)

def process_supplier_shipments(config):
    """
    It randomly processes waiting supplier shipments.

    10% of existing purchase orders are left processing
    90% are added to a shipment and set as received
    90% of those shipments are set as done
    """
    Shipment = Model.get('stock.shipment.in')
    Purchase = Model.get('purchase.purchase')

    shipments = []
    purchases = Purchase.find([('state', '=', 'confirmed')])
    purchases = random.sample(purchases, int(0.9 * len(purchases)))
    for purchase in purchases:
        shipment = Shipment()
        shipment.supplier = purchase.party
        shipment.save()
        shipments.append(shipment)
        for line in purchase.lines:
            for move in line.moves:
                # TODO: Improve performance, but append crashes
                #shipment.incoming_moves.append(move)
                move.shipment = shipment
                move.save()

    Shipment.receive([x.id for x in shipments], config.context)
    shipments = random.sample(shipments, int(0.9 * len(shipments)))
    Shipment.done([x.id for x in shipments], config.context)
