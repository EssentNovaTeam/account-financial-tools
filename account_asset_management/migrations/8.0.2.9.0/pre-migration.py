# coding: utf-8
# Copyright (C) 2020 Essent <http://www.essent.be>
# @author Stefan Rijnhart <stefan.rijnhart@dynapps.be>
# @author Robin Conjour <r.conjour@essent.be>
# @author Pieter Paulussen <pieter.paulussen@dynapps.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import _
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)


def table_empty(cr, table):
    """ Check whether a certain table exists and is empty """
    cr.execute('SELECT 1 FROM pg_class WHERE relname = %s', (table,))
    if cr.fetchone():
        cr.execute("SELECT 1 FROM %s" % table)
        if cr.fetchone():
            _logger.info('%s is not empty', table)
            raise Warning(_('Table %s is not empty', table))
    return True


def migrate(cr, version):
    """ Cleanup failed migration from account_asset_management. """
    if not version:
        return

    cr.execute("SELECT 1 FROM pg_class WHERE relname = 'account_asset'")
    if not cr.fetchone():
        _logger.info("Skipping migration, new tables aren't available")
        return

    _logger.info('Start cleaning up failed migration account_asset_management')

    if table_empty(cr, 'account_asset'):
        cr.execute('DROP TABLE IF EXISTS account_asset CASCADE;')

    if table_empty(cr, 'account_asset_profile'):
        cr.execute('DROP TABLE IF EXISTS account_asset_profile CASCADE;')
        cr.execute("""
            ALTER TABLE account_account DROP COLUMN IF EXISTS asset_profile_id;
            """)
        cr.execute("""
            ALTER TABLE account_invoice_line
            DROP COLUMN IF EXISTS asset_profile_id;
            """)
        cr.execute("""
            ALTER TABLE account_move_line
            DROP COLUMN IF EXISTS asset_profile_id;
            """)

    if table_empty(cr, 'account_asset_line'):
        cr.execute('DROP TABLE IF EXISTS account_asset_line CASCADE;')

    models = [
        'account.asset',
        'account.asset.profile',
        'account.asset.line',
    ]
    cr.execute("""
            DELETE FROM ir_model_constraint WHERE model IN (
                SELECT id FROM ir_model WHERE model IN %(models)s);
            DELETE FROM ir_model_data WHERE model='ir.model' AND res_id IN (
                SELECT id FROM ir_model WHERE model IN %(models)s);
            DELETE FROM ir_model_fields WHERE model_id IN (
                SELECT id FROM ir_model WHERE model IN %(models)s);
            DELETE FROM ir_model WHERE model IN %(models)s;
        """, {
        'models': tuple(models)
    })
    _logger.info('Fully cleaned failed migration account_asset_management')
