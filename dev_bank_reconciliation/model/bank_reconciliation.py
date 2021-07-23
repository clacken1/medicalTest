# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.osv import osv
from datetime import datetime as dt
import time
from odoo.exceptions import Warning
from datetime import date

class bank_reconciliation(models.Model):
    _name="bank.reconciliation"
    _description = "Bank Reconciliation"

    name=fields.Char(string='Reference',required="1",default="/")
    account_rec_id=fields.Many2one('account.account',string='Account')
    journal_id=fields.Many2one('account.journal',string='Journal')
    journal_op_id=fields.Many2one('account.journal',string='2nd Journal')
    start_balance=fields.Float(string='Starting Balance')
    end_balance=fields.Float(string='Ending Balance',required="1")
    journal_entry_ids = fields.Many2many('account.move.line', 'account_move_line_rel','journal_ids','move_ids',string="Journal Entries")
    state=fields.Selection([('draft','Draft'),('close','Close')],string='State',default="draft")
    start_date = fields.Date(string='Start Date',required="1",default=date(date.today().year, 1, 1))
    end_date = fields.Date(string='End Date',required="1")
    user_id = fields.Many2one('res.users', string='Responsible', required=False, default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', required=True, readonly=True, default=lambda self: self.env.company)
    bank_statement=fields.Float(string='Balance as per bank statement', compute='_compute_differance', store=True)
    bank_account=fields.Float(string='Balance as per bank account',compute='_compute_bank_account', store=True)
    bank_gl=fields.Float(string='Balance as per GL',compute='_compute_bank_account', store=True)
    less_unrepresented_amount=fields.Float(string='Unpresented amount', compute='_compute_bank_account', store=True)
    deposit_not_credited_bank=fields.Float(string='Add deposit not credited by bank',compute='_compute_bank_account', store=True)
    differance =fields.Float(string='difference' , compute='_compute_differance', store=True)


    def action_confirm(self):
        for move in self:
            move.state='close'


    @api.depends('bank_statement', 'bank_account', 'less_unrepresented_amount', 'deposit_not_credited_bank')
    def _compute_differance(self):
        for move in self:
            bank_statement = 0.0

            if move.end_balance:
                bank_statement = move.end_balance

            differance = move.bank_statement - move.bank_account

            if differance == 0.00 or differance == -4.18367562815547e-11 or differance == -1.1641532182693481e-10:
                differance = abs(differance)

            move.update({
                'differance' : differance,
                'bank_statement' : bank_statement
            })
        return True


    @api.depends('journal_entry_ids', 'start_balance', 'journal_entry_ids.is_bank_reconcile')
    def _compute_bank_account(self):
        for move in self:
            bank_account = 0.0
            less_unrepresented_amount = 0.0
            deposit_not_credited_bank = 0.0
            if move.journal_entry_ids:
                total_debit = abs(sum(journal_entry.debit for journal_entry in move.journal_entry_ids.filtered(lambda x : x.is_bank_reconcile)))
                total_credit =abs(sum(journal_entry.credit for journal_entry in move.journal_entry_ids.filtered(lambda x : x.is_bank_reconcile)))

                bank_account = move.start_balance + total_debit - total_credit

                less_unrepresented_amount = sum(abs(journal_entry.credit) for journal_entry in move.journal_entry_ids.filtered(lambda x : not x.is_bank_reconcile))

                deposit_not_credited_bank = sum(abs(journal_entry.debit) for journal_entry in move.journal_entry_ids.filtered(lambda x : not x.is_bank_reconcile))

                bank_gl = bank_account + deposit_not_credited_bank - less_unrepresented_amount

            move.update({
                'bank_account' : bank_account,
                'less_unrepresented_amount' : -less_unrepresented_amount,
                'deposit_not_credited_bank' : deposit_not_credited_bank,
                'bank_gl' : bank_gl
            }) 


    def get_total_debit_reconcile(self):
        for move in self:
            less_unrepresented_amount = sum(journal_entry.debit for journal_entry in move.journal_entry_ids.filtered(lambda x : x.is_bank_reconcile))
            return less_unrepresented_amount


    def get_total_credit_reconcile(self):
        for move in self:
            less_unrepresented_amount = sum(journal_entry.credit for journal_entry in move.journal_entry_ids.filtered(lambda x : x.is_bank_reconcile))
            return less_unrepresented_amount


    def get_total_debit_unreconcile(self):
        for move in self:
            less_unrepresented_amount = sum(journal_entry.debit for journal_entry in move.journal_entry_ids.filtered(lambda x : not x.is_bank_reconcile))
            return less_unrepresented_amount


    def get_total_credit_unreconcile(self):
        for move in self:
            less_unrepresented_amount = sum(journal_entry.credit for journal_entry in move.journal_entry_ids.filtered(lambda x : not x.is_bank_reconcile))
            return less_unrepresented_amount


    def button_dummy(self):
        self._compute_differance()
        self._compute_bank_account()



class account_move_line(models.Model):
    _inherit = 'account.move.line'

    is_bank_reconcile = fields.Boolean(string="IS Reconcile")
    is_not_confirm = fields.Boolean(string="Is Not Confirm")

    def action_make_confirm(self):
        for move in self:
            if self._context.get('state') == 'close':
                raise Warning(_('You can not reconcile the line in close state'))
            else:    
                move.write({
                    'is_bank_reconcile' : True
                })

    def action_cancle_confirm(self):
        for move in self:
            if self._context.get('state') == 'close':
                raise Warning(_('You can not un-reconcile the line in close state'))
            else:
                move.write({
                    'is_bank_reconcile' : False
                })