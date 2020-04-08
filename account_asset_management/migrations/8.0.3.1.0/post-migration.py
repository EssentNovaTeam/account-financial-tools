# coding: utf-8
import logging
from openerp import api, fields, SUPERUSER_ID


def migrate(cr, version):
    """ Set asset purchase date to start date. """
    env = api.Environment(cr, SUPERUSER_ID, {})
    assets = env['account.asset'].search([
        ('purchase_date', '<=', fields.Datetime.now())
    ])

    for asset in assets:
        asset.purchase_date = asset.date_start

    logging.info('Set asset purchase date to start date')
