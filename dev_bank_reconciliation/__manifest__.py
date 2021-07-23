# -*- coding: utf-8 -*-

{
	'name': 'Bank Reconciliation & Bank Statement',
	'version': '14.0.0.1',
	'sequence':1,
	'description': """
	Apps will allow Bank Reconciliation Manually to reconcile with Bank Statement
	""",
	"category":'Account',
	'summary': 'Apps will allow Bank Reconciliation Manually to reconcile with Bank Statement',
	'author': 'DevIntelle Consulting Service Pvt.Ltd',
	'website': 'http://www.devintellecs.com/',
	'images': ['images/main_screenshot.jpg'],
	'depends': ['base','account'],
	'data': [
		'security/ir.model.access.csv',
		'views/bank_reconciliation_view.xml',
		'views/report_bank_reconcile.xml',
		'views/account_view.xml',
	],
	'demo': [],
	'test':[],
	'appli cation':True,
	'installable': True,
	'auto_install': False,
	'price':45.0,
	'currency':'EUR', 
}
