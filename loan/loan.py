from openerp.osv import osv, fields
from openerp.tools.translate import _

class loan(osv.osv):
    _name = 'loan'
    _description = "Loan"

    _columns = {
        'name': fields.char('Loan NO'),
        'loan_date': fields.datetime('Date', required=True),
        'exp_return_date': fields.datetime('Expected Return Date'),
        'description': fields.char('Description'),
        'customer_id': fields.many2one('res.partner', 'Customer', select=True),
        'total': fields.float('Total Loan Amount'),

        'state': fields.selection([
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('return', 'Return'),
            ('cancel', 'Cancelled'),

        ], 'Status', readonly=True, copy=False, help="Gives the status of the Proforma Invoices", select=True),

        'product_lines': fields.one2many('loan.product.line', 'loan_id', 'loan Product Lines', required=True),
        'service_lines': fields.one2many('loan.service.line', 'loan_id', 'Loan Service Lines', required=False),

    }

    def confirm(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update loan set state='done' where id=%s", (ids))
            cr.commit()
        return True
    def cancel_loan(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update loan set state='cancel' where id=%s", (ids))
            cr.commit()
        return True


    def convert_to_so(self,cr,uid,ids,context=None):
        return True

    def add_service(self,cr,uid,ids,context=None):
        # import pdb
        # pdb.set_trace()
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cma_galib', 'add_service_loan_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Add service"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'add.service.loan',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                # 'pi_id':ids[0]
                # 'default_price': 500,
                # # 'default_name':context.get('name', False),
                # 'default_total_amount': 200,
                # 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                # 'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                # 'default_reference': inv.name,
                # 'close_after_process': True,
                # 'invoice_type': inv.type,
                # 'invoice_id': inv.id,
                # 'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                # 'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))

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
        'currency_price':fields.float('Unit Price ($/RMB)'),
        'conversion_rate':fields.float('Conversion Rate'),
        'total_price':fields.float('Total Price'),
        'quantity':fields.float('Quantity'),

    }

class loan_service_line(osv.osv):
    _name = 'loan.service.line'
    _description = "PI service List"

    _columns = {
        'loan_id': fields.many2one('loan', 'Loan Ids', ondelete='cascade', select=True, readonly=True),
        'total_cost': fields.float('Service Cost'),
        'service_name': fields.char('Service name'),
        'add_service_id': fields.many2one('add.service')

    }


