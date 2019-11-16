from openerp.osv import osv, fields
from openerp import SUPERUSER_ID, api
from openerp.tools.translate import _
from datetime import datetime



class proforma_invoice(osv.osv):
    _name = 'proforma.invoice'
    _description = "Proforma Invoice"

    _columns = {
        'name': fields.char('PI NO'),
        'pi_date': fields.datetime('Date', required=True),
        'description': fields.char('Description'),
        'vendor_id': fields.many2one('res.partner', 'Vendor name', select=True),
        'total': fields.float('Grand Total'),

        'state': fields.selection([
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),

        ], 'Status', readonly=True, copy=False, help="Gives the status of the Proforma Invoices", select=True),

        'product_lines': fields.one2many('pi.product.line', 'pi_id', 'PI Product Lines', required=True),
        'service_lines': fields.one2many('pi.service.line', 'pi_id', 'PI Service Lines', required=True),
        'po_id': fields.many2one('purchase.order','Purchase Order')


    }

    _defaults = {
        'pi_date': fields.datetime.now,
        'state': 'pending',

    }


    def create(self, cr, uid, vals, context=None):
        pi_id = super(proforma_invoice, self).create(cr, uid, vals, context=context)



        if pi_id is not None:
            sample_text = 'PI-00' + str(pi_id)
            cr.execute('update proforma.invoice set name=%s where id=%s', (sample_text, pi_id))
            cr.commit()

        return True



class pi_product_line(osv.osv):
    _name = 'pi.product.line'
    _description = "PI Product List"

    _columns = {
        'pi_id': fields.many2one('proforma.invoice', 'PI Ids', required=True, ondelete='cascade', select=True,readonly=True),
        'product_id': fields.many2one('product.product', 'Product Name', required=True),
        'unit_price':fields.float('Unit Price (BDT)'),
        'currency_price':fields.float('Currency Price'),
        'conversion_rate':fields.float('Conversion Rate'),
        'total_price':fields.float('Total Price'),
        'quantity':fields.float('Quantity'),
        'calculated_unit_price':fields.float('Calculated Unit Price'),
        'calculated_total_price':fields.float('Calculated Total Price'),
    }



class pi_service_line(osv.osv):
    _name = 'pi.service.line'
    _description = "PI service List"

    _columns = {
        'pi_id': fields.many2one('proforma.invoice', 'PI Ids', ondelete='cascade', select=True, readonly=True),
        'service_cost': fields.float('Service Cost'),
        'total_cost': fields.float('Total Cost'),
        'service_name': fields.char('Service name'),

    }


