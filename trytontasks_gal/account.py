# encoding: utf-8
#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
import datetime
import random
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from proteus import Model, Wizard
from .utils import *

TODAY = datetime.date.today()

def create_taxes():
    """
    Create Taxes
    """
    Tax = Model.get('account.tax')
    Account = Model.get('account.account')

    accounts = Account.find([
        ('kind', 'not in', ['view', 'receivable', 'payable'])])

    tax = Tax()
    tax.name = '21%'
    tax.description = '21%'
    tax.rate = Decimal('0.21')
    tax.invoice_account = accounts[0]
    tax.credit_note_account = accounts[0]
    tax.save()

    tax2 = Tax()
    tax2.name = '10%'
    tax2.description = '10%'
    tax2.rate = Decimal('0.10')
    tax2.invoice_account = accounts[0]
    tax2.credit_note_account = accounts[0]
    tax2.save()

    return tax, tax2

def create_account_chart(company=None, module=None, fs_id=None, digits=None):
    """
    Creates the chart of accounts defined by module and fs_id for the given
    company.

    If no 'module' and 'fs_id' are given, the last template chart created is
    used.
    """
    AccountTemplate = Model.get('account.account.template')
    Account = Model.get('account.account')
    Company = Model.get('company.company')
    ModelData = Model.get('ir.model.data')

    root_accounts = Account.find([('parent', '=', None)])
    if root_accounts:
        return

    if module and fs_id:
        data = ModelData.find([
                ('module', '=', module),
                ('fs_id', '=', fs_id),
                ], limit=1)

        assert len(data) == 1, ('Unexpected num of root templates '
            'with name "%s": %s' % (module, fs_id))
        template = data[0].db_id
        template = AccountTemplate(template)
    else:
        template, = AccountTemplate.find([('parent', '=', None)],
            order=[('id', 'DESC')], limit=1)

    if company:
        domain = [('party.name', '=', company),]
    else:
        domain =[]
    company, = Company.find(domain)

    create_chart = Wizard('account.create_chart')
    create_chart.execute('account')
    create_chart.form.account_template = template
    create_chart.form.company = company
    if digits:
        create_chart.form.account_code_digits = int(digits)
    create_chart.execute('create_account')

    receivable = Account.find([
            ('kind', '=', 'receivable'),
            ('company', '=', company.id),
            ])
    receivable = receivable[0]
    payable = Account.find([
            ('kind', '=', 'payable'),
            ('company', '=', company.id),
            ])[0]
    #revenue, = Account.find([
    #        ('kind', '=', 'revenue'),
    #        ('company', '=', company.id),
    #        ])
    #expense, = Account.find([
    #        ('kind', '=', 'expense'),
    #        ('company', '=', company.id),
    #        ])
    #cash, = Account.find([
    #        ('kind', '=', 'other'),
    #        ('company', '=', company.id),
    #        ('name', '=', 'Main Cash'),
    #        ])
    create_chart.form.account_receivable = receivable
    create_chart.form.account_payable = payable
    create_chart.execute('create_properties')

def create_fiscal_year(config, company=None, year=None):
    """
    Creates a new fiscal year with monthly periods and the appropriate
    invoice sequences for the given company.

    If no year is specified the current year is used.
    """
    FiscalYear = Model.get('account.fiscalyear')
    Module = Model.get('ir.module')
    Sequence = Model.get('ir.sequence')
    SequenceStrict = Model.get('ir.sequence.strict')
    Company = Model.get('company.company')

    if year is None:
        year = TODAY.year
    date = datetime.date(int(year), 1, 1)

    if company:
        domain = [('party.name', '=', company),]
    else:
        domain =[]
    company, = Company.find(domain)

    installed_modules = [m.name
        for m in Module.find([('state', '=', 'installed')])]

    post_move_sequence = Sequence.find([
            ('name', '=', '%s' % year),
            ('code', '=', 'account_move'),
            ('company', '=', company.id),
            ])
    if post_move_sequence:
        post_move_sequence = post_move_sequence[0]
    else:
        post_move_sequence = Sequence(name='%s' % year,
            code='account.move', company=company)
        post_move_sequence.save()

    fiscalyear = FiscalYear.find([
            ('name', '=', '%s' % year),
            ('company', '=', company.id),
            ])
    if fiscalyear:
        fiscalyear = fiscalyear[0]
    else:
        fiscalyear = FiscalYear(name='%s' % year)
        fiscalyear.start_date = date + relativedelta(month=1, day=1)
        fiscalyear.end_date = date + relativedelta(month=12, day=31)
        fiscalyear.company = company
        fiscalyear.post_move_sequence = post_move_sequence
        if 'account_invoice' in installed_modules:
            for attr, name in (('out_invoice_sequence', 'Customer Invoice'),
                    ('in_invoice_sequence', 'Supplier Invoice'),
                    ('out_credit_note_sequence', 'Customer Credit Note'),
                    ('in_credit_note_sequence', 'Supplier Credit Note')):
                sequence = SequenceStrict.find([
                        ('name', '=', '%s %s' % (name, year)),
                        ('code', '=', 'account.invoice'),
                        ('company', '=', company.id),
                        ])
                if sequence:
                    sequence = sequence[0]
                else:
                    sequence = SequenceStrict(
                        name='%s %s' % (name, year),
                        code='account.invoice',
                        company=company)
                    sequence.save()
                setattr(fiscalyear, attr, sequence)
        fiscalyear.save()

    if not fiscalyear.periods:
        FiscalYear.create_period([fiscalyear.id], config.context)

    return fiscalyear

def create_payment_term(name, type='remainder', percentage=None, divisor=None,
        amount=None, day=None, month=None, weekday=None, months=0, weeks=0,
        days=0):
    """
    Creates a payment term with the supplied values.
    Default values are to create a Cash payment term
    """
    Term = Model.get('account.invoice.payment_term')
    TermLine = Model.get('account.invoice.payment_term.line')

    term = Term()
    term.name = name
    term.active = True
    line = TermLine()
    line.type = type
    if percentage is not None:
        line.percentage = percentage
    if divisor is not None:
        line.divisor = divisor
    if amount is not None:
        line.amount = amount
    line.day = day
    line.month = month
    line.weekday = weekday
    line.months = months
    line.weeks = weeks
    line.days = days
    term.lines.append(line)
    term.save()

    return term

def create_payment_terms():
    """
    Creates 3 payment terms:
    - 30 days
    - 60 days
    - 90 days
    """
    Term = Model.get('account.invoice.payment_term')
    TermLine = Model.get('account.invoice.payment_term.line')

    term = Term()
    term.name = '30 D'
    term.active = True
    line = TermLine()
    line.months = 1
    term.lines.append(line)
    term.save()

    term = Term()
    term.name = '60 D'
    line = TermLine()
    line.months = 2
    term.lines.append(line)
    term.save()

    term = Term()
    term.name = '90 D'
    line = TermLine()
    line.months = 3
    term.lines.append(line)
    term.save()

def create_payment_types(language='en_US'):
    """
    Creates payment types:
    - Bank Transfer
    - Direct Debit
    - Cash
    - Credit Card
    """
    Type = Model.get('account.payment.type')

    names = {
        'bank-transfer': {
            'ca_ES': 'Transferència Bancària',
            'en_US': 'Bank Transfer',
            'es_ES': 'Transferencia Bancaria',
            },
        'direct-debit': {
            'ca_ES': 'Domiciliació bancària',
            'en_US': 'Direct Debit',
            'es_ES': 'Domiciliación bancaria',
            },
        'cash': {
            'ca_ES': 'Efectiu',
            'en_US': 'Cash',
            'es_ES': 'Efectivo',
            },
        'credit-card': {
            'ca_ES': 'Targeta de crèdit',
            'en_US': 'Credit Card',
            'es_ES': 'Tarjeta de crédito',
            },
        }

    t = Type()
    t.name = names['bank-transfer'][language]
    t.kind = 'receivable'
    if hasattr(t, 'account_bank'):
        t.account_bank = 'company'
    t.save()

    t = Type()
    t.name = names['direct-debit'][language]
    t.kind = 'receivable'
    if hasattr(t, 'account_bank'):
        t.account_bank = 'party'
    t.save()

    t = Type()
    t.name = names['cash'][language]
    t.kind = 'receivable'
    if hasattr(t, 'account_bank'):
        t.account_bank = 'none'
    t.save()

    t = Type()
    t.name = names['bank-transfer'][language]
    t.kind = 'payable'
    if hasattr(t, 'account_bank'):
        t.account_bank = 'party'
    t.save()

    t = Type()
    t.name = names['direct-debit'][language]
    t.kind = 'payable'
    if hasattr(t, 'account_bank'):
        t.account_bank = 'company'
    t.save()

    t = Type()
    t.name = names['cash'][language]
    t.kind = 'payable'
    if hasattr(t, 'account_bank'):
        t.account_bank = 'none'
    t.save()

def process_customer_invoices(config):
    """
    It randomly confirms customer invoices.

    90% of customer invoices are confirmed.
    """
    Invoice = Model.get('account.invoice')

    payment_types = get_payment_types('receivable')

    invoices = Invoice.find([
            ('type', '=', 'out_invoice'),
            ('state', '=', 'draft'),
            ])
    invoices = random.sample(invoices, int(0.9 * len(invoices)))
    for invoice in invoices:
        # TODO: For consistency, better use the date of the maximum
        # date of the # sales composing the lines of the invoice
        invoice.invoice_date = random_datetime(
            TODAY + relativedelta(months=-12), TODAY)
        if hasattr(invoice, 'payment_type') and not invoice.payment_type:
            if invoice.party.customer_payment_type:
                invoice.payment_type = invoice.party.customer_payment_type
            else:
                if payment_types:
                    invoice.payment_type = random.choice(payment_types)
        invoice.save()

    Invoice.post([x.id for x in invoices], config.context)
