from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date, time

class add_service(osv.osv):
    _name = "add.service"


    # def button_add_service_action(self,cr,uid,ids,context=None):
        # eve_mee_obj = self.pool.get('proforma.invoice')
        # for record in self.browse(cr, uid, ids, context=context):
        #     a = eve_mee_obj.add_services(cr, uid, 20, context)
    #     # import pdb
    #     # pdb.set_trace()
    #     self.pool.get("proforma.incoice").add_services(self,cr,uid,ids,context=None)

        #


    _columns = {

         'add_service_line_id': fields.one2many('pi.service.line', 'add_service_id', 'Service', required=True),
        # 'bill_register_id': fields.many2one('bill.register', "Information"),
        # 'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
        #                               string="Currency", readonly=True, required=True),
        # 'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
    }

    # def create(self, cr, uid, vals, context=None):

        # values={}
        # if not package_name:
        #     return {}
        # # import pdb
        # # pdb.set_trace()
        # abc={'pi.service.line':[]}
        # package_object=self.pool.get('examine.package').browse(cr,uid,package_name,context=None)
        # # import pdb
        # # pdb.set_trace()
        # for item in package_object.examine_package_line_id:
        #     items=item.name
        #     for itemid in items:
        #         car=itemid.id
        #         abc['bill_register_line_id'].append([0, False, {'name':car, 'total_amount': 400}])

        # abc={'bill_register_line_id':[[0, False, {'discount': 0, 'price': 400, 'name': 2, 'total_amount': 400}]]}
        # abc['bill_register_line_id'].append([0, False, {'discount': 0, 'price': 400, 'name': 2, 'total_amount': 400}])
        # values['value']=abc

        # return values
        # import pdb
        # pdb.set_trace()



    # def onchange_test(self,cr,uid,ids,name,context=None):
    #     tests = {'values': {}}
    #     dep_object = self.pool.get('examination.entry').browse(cr, uid, name, context=None)
    #     abc = {'price': dep_object.rate,'total_amount':dep_object.rate}
    #     tests['value'] = abc
    #     # import pdb
    #     # pdb.set_trace()
    #     return tests