from openerp.osv import osv, fields

class loan(osv.osv):
    _name = 'loan'
    _description = "Loan"

    _columns = {
        'name': fields.char('Loan NO'),
        'loan_date': fields.datetime('Date', required=True),
        'exp_return_date': fields.datetime('Expected Return Date', required=True),
        'description': fields.char('Description'),
        'customer_id': fields.many2one('res.partner', 'Customer', select=True),
        'total': fields.float('Total Loan Amount'),

        'state': fields.selection([
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),

        ], 'Status', readonly=True, copy=False, help="Gives the status of the Proforma Invoices", select=True),

        'product_lines': fields.one2many('loan.product.line', 'loan_id', 'loan Product Lines', required=True),

    }

    _defaults = {
        'loan_date': fields.datetime.now,
        'state': 'pending',

    }
    

class loan_product_line(osv.osv):
    _name = 'loan.product.line'
    _description = "loan Product List"

    _columns = {
        'loan_id': fields.many2one('proforma.invoice', 'loan Ids', required=True, ondelete='cascade', select=True,readonly=True),
        'product_id': fields.many2one('product.product', 'Product Name', required=True),
        'unit_price':fields.float('Unit Price (BDT)'),
        'currency_price':fields.float('Currency Price'),
        'conversion_rate':fields.float('Conversion Rate'),
        'total_price':fields.float('Total Price'),
        'quantity':fields.float('Quantity'),

    }


