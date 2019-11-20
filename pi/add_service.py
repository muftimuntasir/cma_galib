from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class add_service(osv.osv):
    _name = "add.service"

    #
    # def button_add_action(self,cr,uid,ids,context):
    #     # import pdb
    #     # pdb.set_trace()
    #     return 0
    #     #


    _columns = {

         'add_service_line_id': fields.one2many('pi.service.line', 'add_service_id', 'Service', required=True),
        # 'bill_register_id': fields.many2one('bill.register', "Information"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
    }

    # def onchange_test(self,cr,uid,ids,name,context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
    #     abc = {'price': dep_object.rate,'total_amount':dep_object.rate}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests