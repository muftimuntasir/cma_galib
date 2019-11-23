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
        for loan_obj in self.browse(cr, uid, ids, context=context):
            # import pdb
            # pdb.set_trace()
            sales_vals={}
            sales_vals["origin"] = False
            sales_vals["incoterm"] = False
            sales_vals["date_order"] = loan_obj.loan_date
            sales_vals["user_id"] = 1
            sales_vals["partner_shipping_id"] = 7
            child_list=[]

            for product_items in loan_obj.product_lines:
                # import pdb
                # pdb.set_trace()
                order_tmp_dict = {}
                order_tmp_dict['product_uos_qty']= 1
                order_tmp_dict['product_id']= product_items.product_id.id
                order_tmp_dict['product_uom'] = 1
                order_tmp_dict['route_id']=False
                order_tmp_dict['price_unit']= product_items.unit_price
                order_tmp_dict['product_uom_qty']= 1
                order_tmp_dict['delay']= 7
                order_tmp_dict['product_uos']=False
                order_tmp_dict['th_weight']=0
                order_tmp_dict['product_packaging']=False
                order_tmp_dict['discount']=0
                order_tmp_dict['tax_id']=[]
                child_list.append([0,False,order_tmp_dict])

                    # 'product_uom': 5,
                    # 'date_planned': '2019-11-18',
                    # 'price_unit': calculated_unit_price,
                    # 'taxes_id': [[6, False, []]],
                    # 'product_qty': 1,
                    # 'account_analytic_id': False,
                    # 'name': 'Service'

            sales_vals["order_line"] =child_list
            # purchase_vals["order_line"] = [[0, False, order_tmp_dict]]
            sales_vals["picking_policy"] = 'direct'
            sales_vals["order_policy"] = 'manual'
            sales_vals["payment_term"] =  False
            sales_vals["section_id"] = False
            sales_vals["warehouse_id"] = 1
            sales_vals["note"] = False
            sales_vals["message_follower_ids"] = False
            sales_vals["fiscal_position"] = False
            sales_vals["client_order_ref"] = False
            sales_vals["partner_invoice_id"] = 7
            sales_vals["pricelist_id"] = 1
            sales_vals["project_id"] = 1
            sales_vals["partner_id"] = loan_obj.customer_id.id
            sales_vals["message_ids"] = False


           ## Update By Kazi
            #
            # po_vals ={}
            #
            sale_obj = self.pool.get('sale.order')
            purchase_id = sale_obj.create(cr, uid, vals=sales_vals, context=context)

            ###

            ## Link up with PO
            # cr.execute('update proforma_invoice set po_id=%s where id=%s',(purchase_id,pi_obj ))
            # cr.execute('update purchase_order set pi_id=%s where id=%s',(pi_obj.id,purchase_id ))
            # cr.commit()
            ## Ends He


        return purchase_id

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

    def create(self, cr, uid, vals, context=None):
        loan_id = super(loan, self).create(cr, uid, vals, context=context)
        # import pdb
        # pdb.set_trace()
        #
        #

        if loan_id is not None:
            sample_text = 'L-00' + str(loan_id)
            cr.execute('update loan set name=%s where id=%s', (sample_text, loan_id))
            cr.commit()

        return loan_id
    

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

    def onchange_product(self, cr, uid, ids, product_id, context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
        # pi_obj=self.pool.get('proforma.invoice').browse(cr, uid, pi_id, context=None)
        # import pdb
        # pdb.set_trace()
        abc = {'currency_price': dep_object.list_price, 'total_price': dep_object.list_price}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_quantity(self,cr,uid,ids,product_id,quantity,unit_price,context=None):
        # import pdb
        # pdb.set_trace()
        tests = {'values': {}}
        dep_object = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
        unit_prices= dep_object.list_price
        total=unit_prices*quantity
        abc = {'total_price': total}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests


class loan_service_line(osv.osv):
    _name = 'loan.service.line'
    _description = "PI service List"

    _columns = {
        'loan_id': fields.many2one('loan', 'Loan Ids', ondelete='cascade', select=True, readonly=True),
        'total_cost': fields.float('Service Cost'),
        'service_name': fields.char('Service name'),
        'add_service_id': fields.many2one('add.service')

    }


