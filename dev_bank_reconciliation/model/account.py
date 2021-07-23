# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import osv
from datetime import datetime as dt
import time
from odoo.exceptions import Warning
from datetime import date

class sale_order(models.Model):
    _inherit = "account.account"

    account_bool=fields.Boolean(string='Is_Bank')
