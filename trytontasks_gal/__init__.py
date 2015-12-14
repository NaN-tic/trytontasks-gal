#This file is part of trytontasks_gal. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from invoke import task, run

@task()
def create(language=None, password=None):
    'Create Gal Database'
    print "Create Gal Database"
