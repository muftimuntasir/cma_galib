from openerp.osv import osv, fields
from openerp.tools.translate import _

class loan(osv.osv):
    _name = 'loan'
    _description = "Loan"

    def calculate_product_cost(self, cr, uid, ids, field_names, args, context=None):
        product_cost={}
        sum=0
        for items in self.pool.get("loan").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.product_lines:
                total_list.append(amount.bdttotal_price)

            for item in total_list:
                sum=item+sum
                # import pdb
                # pdb.ser_trace()
        product_cost[ids[0]]=sum
        return product_cost

    def calculate_service_cost(self, cr, uid, ids, field_names, args, context=None):
        service_cost={}
        sum=0
        for items in self.pool.get("loan").browse(cr,uid,ids,context=None):
            total_list=[]
            for amount in items.service_lines:
                total_list.append(amount.total_cost)

            for item in total_list:
                sum=item+sum
        service_cost[ids[0]]=sum
        return service_cost

    def calculate_total(self, cr, uid, ids, field_names, args, context=None):
        service_cost={}
        sum=0
        items=self.pool.get("loan").browse(cr,uid,ids,context=None)

        sum=items.ptotal+items.stotal
        # import pdb
        # pdb.set_trace()


        service_cost[ids[0]]=sum
        return service_cost

    _columns = {

        'name': fields.char('Loan NO'),
        'loan_date': fields.datetime('Date', required=True),
        'exp_return_date': fields.datetime('Expected Return Date'),
        'description': fields.char('Description'),
        'customer_id': fields.many2one('res.partner', 'Customer', select=True),
        'total': fields.function(calculate_total, type='float', string='Total', store=True),
        'ptotal': fields.function(calculate_product_cost, type='float', string='Product Total', store=True),
        'stotal': fields.function(calculate_service_cost, type='float', string='Service Total', store=True),

        'state': fields.selection([
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('return', 'Return'),
            ('cancel', 'Cancelled'),

        ], 'Status', readonly=True, copy=False, help="Gives the status of the Proforma Invoices", select=True),
        'pi_id':fields.many2one('proforma.invoice','PI'),

        'product_lines': fields.one2many('loan.product.line', 'loan_id', 'loan Product Lines', required=True),
        'service_lines': fields.one2many('loan.service.line', 'loan_id', 'Loan Service Lines', required=False),
        'receipt_lines': fields.one2many('loan.receipt.line', 'loan_id', 'Loan receipt Lines')

    }

    def onchange_pi(self,cr,uid,ids,pi_id,vals,context=None):

        values={}
        if not pi_id:
            return {}
        # import pdb
        # pdb.set_trace()
        abc={'service_lines':[]}
        service_id = self.pool.get('pi.service.line').search(cr, uid, [('pi_id', '=', pi_id)], context=None)
        service_object=self.pool.get('pi.service.line').browse(cr,uid,service_id,context)
        # import pdb
        # pdb.set_trace()
        for item in service_object:
            s_name=item.service_name
            s_cost=item.service_cost
            s_quantity=item.quantity
            s_total=item.total_cost

            abc['service_lines'].append([0, False, {'service_name':s_name, 'service_cost': s_cost,'quantity':s_quantity,'total_cost':s_total}])

        # abc={'bill_register_line_id':[[0, False, {'discount': 0, 'price': 400, 'name': 2, 'total_amount': 400}]]}
        # abc['bill_register_line_id'].append([0, False, {'discount': 0, 'price': 400, 'name': 2, 'total_amount': 400}])
        values['value']=abc

        return values

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

    def make_return(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update loan set state='return' where id=%s", (ids))
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
                'loan_id':ids[0]
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


    def add_receipt(self,cr,uid,ids,context=None):
        # import pdb
        # pdb.set_trace()
        if not ids: return []

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cma_galib', 'loan_receipt_form_view')
        #
        inv = self.browse(cr, uid, ids[0], context=context)
        # import pdb
        # pdb.set_trace()
        return {
            'name': _("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'loan.receipt',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'loan_id':ids[0]
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

    def write(self, cr, uid, ids, vals, context=None):
        cr.execute("select state from  loan where id=%s", (ids))
        result_list = cr.fetchall()
        # import pdb
        # pdb.set_trace()

        for item in result_list:
            if str(item[0]) == 'done' or str(item[0]) == 'cancel' or str(item[0]) == 'return':
                raise osv.except_osv(_('Message'), _("Sorry You Can not Edit it. Because it is already confirmed/Cancelled/Returned."))
        if isinstance(ids, (int, long)):
            ids = [ids]
            # import pdb
            # pdb.set_trace()
        res = super(proforma_invoice, self).write(cr, uid, ids, vals, context=context)
        return res
    

class loan_product_line(osv.osv):
    _name = 'loan.product.line'
    _description = "loan Product List"

    _columns = {
        'loan_id': fields.many2one('loan', 'Loan Ids', ondelete='cascade', select=True, readonly=True),
        'product_id': fields.many2one('product.product', 'Product Name', required=True),
        'uom': fields.selection([('kg', 'KG'), ('pound', 'Pound')], 'UoM'),
        'quantity': fields.float('Quantity/KG'),
        'currencyunit_price':fields.float('Foreign Price/kg'),
        'currencytotal_price': fields.float('Foreign Price(TOTAL)'),
        'bdt_rates': fields.float('Conversion Rate'),
        'bdtunit_price': fields.float('unit price bdt'),
        'bdttotal_price':fields.float('Total Price (BDT)'),

    }
    def onchange_unit(self,cr,uid,ids,product_id,quantity,currencyunit_price,context=None):
        tests = {'values': {}}
        total_currency=currencyunit_price*quantity
        abc = {'currencytotal_price': total_currency,}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_quantity(self,cr,uid,ids,product_id,quantity,currencyunit_price,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
        cunit_prices=currencyunit_price
        total=cunit_prices*quantity
        abc = {'currencytotal_price': total}
        tests['value'] = abc

        return tests

    def onchange_conversion(self,cr,uid,ids,product_id,currencytotal_price,quantity,bdt_rates,currencyunit_price,context=None):
        tests = {'values': {}}
        bdtunit_price=bdt_rates*currencyunit_price
        total_bdt_price=currencytotal_price*bdt_rates
        # import pdb
        # pdb.set_trace()
        abc = {'bdtunit_price': bdtunit_price,'bdttotal_price':total_bdt_price}
        tests['value'] = abc


        return tests

    # def onchange_product(self, cr, uid, ids, product_id, context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
    #     # pi_obj=self.pool.get('proforma.invoice').browse(cr, uid, pi_id, context=None)
    #     # import pdb
    #     # pdb.set_trace()
    #     abc = {'currency_price': dep_object.list_price, 'total_price': dep_object.list_price}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests
    #
    # def onchange_quantity(self,cr,uid,ids,product_id,quantity,unit_price,context=None):
    #     # import pdb
    #     # pdb.set_trace()
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
    #     unit_prices= dep_object.list_price
    #     total=unit_prices*quantity
    #     abc = {'total_price': total}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests


class loan_service_line(osv.osv):
    _name = 'loan.service.line'
    _description = "PI service List"

    _columns = {
        'loan_id': fields.many2one('loan', 'Loan Ids', ondelete='cascade', select=True, readonly=True),
        'service_name': fields.char('Service name'),
        'service_cost': fields.float('Service cost/KG'),
        'quantity': fields.float('Quantity'),
        'total_cost':fields.float('Total Cost'),
        'add_service_id': fields.many2one('add.service')

    }


class loan_receipt(osv.osv):
    _name = 'loan.receipt.line'
    _description = "Loan Payment"


    _columns = {
        'loan_id': fields.many2one('loan','Loan ID'),
        'amount': fields.float('Amount', required=True),
        'date': fields.datetime('Date'),
        'type': fields.char('Type'),
        'usd_amount': fields.float('Amount(USD)'),
        'con_rate': fields.float('Conversion Rate')
    }
    # def create(self,cr,uid,vals,context=None):
    #     import pdb
    #     pdb.set_trace()


