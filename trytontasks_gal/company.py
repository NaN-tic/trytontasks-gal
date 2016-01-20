#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from proteus import Model, Wizard
from .party import create_party

def create_company(config, name, street=None, streetbis=None, zip=None, city=None,
        subdivision_code=None, country_code='ES', currency_code='EUR',
        phone=None, website=None, email=None):
    """
    Creates a company in current gal database.

    Based on tryton_demo.py in tryton-tools repo:
    http://hg.tryton.org/tryton-tools
    """
    Company = Model.get('company.company')
    Currency = Model.get('currency.currency')

    party = create_party(name, street=street, streetbis=streetbis, zip=zip,
        city=city, subdivision_code=subdivision_code, country_code=country_code,
        phone=phone, website=website, email=email)

    companies = Company.find([('party', '=', party.id)])
    if companies:
        return companies[0]

    currency, = Currency.find([('code', '=', currency_code)])

    company_config = Wizard('company.company.config')
    company_config.execute('company')
    company = company_config.form
    company.party = party
    company.currency = currency
    company_config.execute('add')

    # Reload context
    User = Model.get('res.user')
    config._context = User.get_preferences(True, config.context)

    company, = Company.find([('party', '=', party.id)])

    return company

def create_employee(name, company=None, user=None):
    """
    Creates the employee with the given name in the given company and links
    it with the given user.

    If company is not set the first company found on the system is used.
    If user is not set, 'admin' user is used.
    """
    Company = Model.get('company.company')
    Employee = Model.get('company.employee')
    Party = Model.get('party.party')
    User = Model.get('res.user')

    if user is None:
        user = 'admin'
    if company:
        company, = Company.find([('name', '=', company)])
    else:
        company, = Company.find([], limit=1)

    party = Party()
    party.name = name
    party.save()

    employee = Employee()
    employee.party = party
    employee.company = company
    employee.save()

    user, = User.find([('login', '=', user)], limit=1)
    user.employees.append(employee)
    user.employee = employee
    user.save()
