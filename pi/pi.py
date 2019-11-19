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
        'curency': fields.selection([('usd', 'USD$'), ('bdt', 'BDT'), ('others', 'Others')], string='Curency', default='usd'),
        'equivalant': fields.float('Conversion Rate BDT'),
        'ptotal': fields.float('Total'),
        'stotal': fields.float('Total'),

        'state': fields.selection([
            ('pending', 'Pending'),
            ('done', 'Done'),

            ('cancel', 'Cancelled'),

        ], 'Status', readonly=True, copy=False, help="Gives the status of the Proforma Invoices", select=True),

        'product_lines': fields.one2many('pi.product.line', 'pi_id', 'PI Product Lines', required=True),
        'service_lines': fields.one2many('pi.service.line', 'pi_id', 'PI Service Lines', required=False),
        'po_id': fields.many2one('purchase.order','Purchase Order')


    }

    def convert_to_po(self,cr,uid,ids,context=None):

        for pi_obj in self.browse(cr, uid, ids, context=context):
            # import pdb
            # pdb.set_trace()

            total_service_value = 0
            total_product_value = 0

            for s_items in pi_obj.service_lines:
                total_service_value += s_items.total_cost


            for p_items in pi_obj.product_lines:
                total_product_value += p_items.total_price

            tmp_list =[]
            fraction = 0
            quantity=0
            for p_items in pi_obj.product_lines:
                fraction = 0

                fraction = p_items.total_price/total_product_value
                calculated_total_cost = p_items.total_price + (total_service_value * fraction)
                quantity=p_items.quantity


                if p_items.quantity > 0:
                    calculated_unit_price = calculated_total_cost / p_items.quantity
                else:
                    calculated_unit_price = 0

                tmp_list.append(
                    {
                        'product_id':p_items.product_id.id,
                        'calculated_unit_price':calculated_unit_price,
                        'calculated_total_cost':calculated_total_cost,
                        'id':p_items.id
                    }
                )
            for item in tmp_list:
                cr.execute('update pi_product_line set calculated_unit_price=%s where id=%s', (item.get("calculated_unit_price"),item.get("id")))
                cr.execute('update pi_product_line set calculated_total_price=%s where id=%s', (item.get("calculated_total_cost"),item.get("id")))
                cr.commit()


            purchase_vals={}
            purchase_vals["origin"] = False
            purchase_vals["message_follower_ids"] = False
            child_list=[]

            for product_items in pi_obj.product_lines:
                order_tmp_dict = {}
                order_tmp_dict['product_id']= product_items.product_id.id
                order_tmp_dict['product_uom']= 5
                order_tmp_dict['date_planned'] = '2019-11-18'
                order_tmp_dict['price_unit']=product_items.calculated_unit_price
                order_tmp_dict['taxes_id']= []
                order_tmp_dict['product_qty']= product_items.quantity
                order_tmp_dict['account_analytic_id']= False
                order_tmp_dict['name']=product_items.product_id.name
                child_list.append([0,False,order_tmp_dict])

                    # 'product_uom': 5,
                    # 'date_planned': '2019-11-18',
                    # 'price_unit': calculated_unit_price,
                    # 'taxes_id': [[6, False, []]],
                    # 'product_qty': 1,
                    # 'account_analytic_id': False,
                    # 'name': 'Service'

            purchase_vals["order_line"] =child_list
            # purchase_vals["order_line"] = [[0, False, order_tmp_dict]]
            purchase_vals["company_id"] = 1
            purchase_vals["currency_id"] = 1
            purchase_vals["date_order"] = '2019-11-18 12:17:13'
            purchase_vals["location_id"] = 12
            purchase_vals["message_ids"] = False
            purchase_vals["dest_address_id"] = False
            purchase_vals["fiscal_position"] = False
            purchase_vals["picking_type_id"] = 1
            purchase_vals["partner_id"] = 1
            purchase_vals["journal_id"] = 2
            purchase_vals["bid_validity"] = False
            purchase_vals["pricelist_id"] = 2
            purchase_vals["incoterm_id"] = False
            purchase_vals["payment_term_id"] = False
            purchase_vals["partner_ref"] = '0'
            purchase_vals["name"] = "PO001"+str(pi_obj.id)
            purchase_vals["notes"] = False
            purchase_vals["invoice_method"] = 'order'
            purchase_vals["minimum_planned_date"] = False





           ## Update By Kazi
            #
            # po_vals ={}
            #
            purchase_obj = self.pool.get('purchase.order')
            purchase_id = purchase_obj.create(cr, uid, vals=purchase_vals, context=context)

            ###

            ## Link up with PO
            # cr.execute('update proforma_invoice set po_id=%s where id=%s',(purchase_id,pi_obj ))
            cr.execute('update purchase_order set pi_id=%s where id=%s',(pi_obj.id,purchase_id ))
            cr.commit()
            ## Ends He


        return purchase_id


    def confirm(self,cr,uid,ids,context=None):
        if ids is not None:
            cr.execute("update proforma_invoice set state='done' where id=%s", (ids))
            cr.commit()
        return True

    _defaults = {
        'pi_date': fields.datetime.now,
        'state': 'pending',

    }


    def create(self, cr, uid, vals, context=None):
        pi_id = super(proforma_invoice, self).create(cr, uid, vals, context=context)
        # import pdb
        # pdb.set_trace()
        #
        #

        if pi_id is not None:
            sample_text = 'PI-00' + str(pi_id)
            cr.execute('update proforma_invoice set name=%s where id=%s', (sample_text, pi_id))
            cr.commit()

        return pi_id

    def write(self, cr, uid, ids, vals, context=None):
        cr.execute("select state from  proforma_invoice where id=%s", (ids))
        result_list = cr.fetchall()
        # import pdb
        # pdb.set_trace()

        for item in result_list:
            if str(item[0]) == 'done' or str(item[0]) == 'cancel':
                raise osv.except_osv(_('Message'), _("Sorry You Can not Edit it. Because it is already confirmed/Cancelled."))
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = super(proforma_invoice, self).write(cr, uid, ids, vals, context=context)
        return res



class pi_product_line(osv.osv):
    _name = 'pi.product.line'
    _description = "PI Product List"


    def _calculateunit(self,cr,uid,ids,field_name,arg,context=None):
        # unitcalculate={}
        # sum=0
        # for item in self.pool.get("proforma.invoice").browse(cr,uid,ids,context=None):
        #     # current_rate=item.equivalant
        #     for items in self.pool.get('pi.product.line').browse(cr,uid,ids,context=None):
        #
        #         currencyunit=items.cunit_price
        #         # bdtunit=current_rate*currencyunit
        #         # import pdb
        #         # pdb.set_trace()
        #
        # for record in self.browse(self,cr,uid,ids,context=None):
        #     unitcalculate[record.id]=bdtunit

        return 0

    _columns = {
        'pi_id': fields.many2one('proforma.invoice', 'PI Ids', required=True, ondelete='cascade', select=True,readonly=True),
        'product_id': fields.many2one('product.product', 'Product Name', required=True),
        'cunit_price':fields.float('Unit Price (Currency)'),
        'bunit_price': fields.function(_calculateunit,string='Unit Price (BDT)',type='float'),
        'btotal_price':fields.float('Total Price (BDT)'),
        'ctotal_price':fields.float('Total Price (Curency)'),
        'quantity':fields.float('Quantity/KG'),
        'calculated_unit_price':fields.float('Calculated Unit Price'),
        'calculated_total_price':fields.float('Calculated Total Price'),
    }

    def onchange_product(self,cr,uid,ids,product_id,pi_id,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
        # pi_obj=self.pool.get('proforma.invoice').browse(cr, uid, pi_id, context=None)
        # import pdb
        # pdb.set_trace()
        abc = {'cunit_price': dep_object.list_price,'ctotal_price':dep_object.list_price}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests

    def onchange_quantity(self,cr,uid,ids,product_id,quantity,cunit_price,context=None):
        tests = {'values': {}}
        dep_object = self.pool.get('product.product').browse(cr, uid, product_id, context=None)
        cunit_prices=cunit_price
        total=cunit_prices*quantity
        abc = {'ctotal_price': total}
        tests['value'] = abc
        # import pdb
        # pdb.set_trace()
        return tests


class purchase_order(osv.osv):
    _inherit = "purchase.order"

    _columns = {
        'pi_id': fields.many2one('proforma.invoice', string='Purchase Order')
    }


class pi_service_line(osv.osv):
    _name = 'pi.service.line'
    _description = "PI service List"

    _columns = {
        'pi_id': fields.many2one('proforma.invoice', 'PI Ids', ondelete='cascade', select=True, readonly=True),
        'service_cost': fields.float('Service Cost'),
        'service_name': fields.char('Service name'),

    }


