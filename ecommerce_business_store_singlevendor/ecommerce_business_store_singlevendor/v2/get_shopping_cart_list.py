import frappe
from ecommerce_business_store_singlevendor.utils.utils import role_auth,get_customer_from_token,other_exception



def shopping_cart_query(customer):
    cart_query = f"""   SELECT 
            CI.price,CI.old_price,CI.product,CI.product_name,CI.quantity,
            CI.total,CI.tax,SC.cart_type
        FROM 
            `tabCart Items` CI
        INNER JOIN 
            `tabShopping Cart` SC 
                ON SC.name = CI.parent
        WHERE SC.cart_type = 'Shopping Cart' AND 
            SC.customer = '{customer}'"""
    return cart_query

def shopping_cart_wl_query(customer):
    wl_query = f""" SELECT 
            CI.price,CI.old_price,CI.product,CI.product_name,CI.quantity,CI.total,
            CI.tax,SC.cart_type
        FROM 
            `tabCart Items` CI
        INNER JOIN 
            `tabShopping Cart` SC 
                ON SC.name = CI.parent
        WHERE SC.cart_type = 'Wishlist' AND 
            SC.customer = '{customer}'"""
    return wl_query
@frappe.whitelist()
@role_auth(role="Customer",method="POST")
def get_shopping_cart_items(customer_id =None):
    try:
        customer = get_customer_from_token()
        if customer_id:
            customer = customer_id
            cart_query = shopping_cart_query(customer)
            wl_query = shopping_cart_query(customer)
            s_data = frappe.db.sql(cart_query,as_dict=1)
            w_data = frappe.db.sql(wl_query,as_dict=1)
            return {'status':'Success',
                    "cart" : s_data,
                    "wishlist":w_data}
        else:
            return {'status':'Failed',
                    'message':'Your are not a valid customer'}    
    except Exception:
        other_exception("Error in v2.get_shopping_cart_list.get_shopping_cart_items")


def item_tochild__cus_id_check(cus_id, customer_id,product_id,quantity,cart_type):
    if cus_id:
        insert = frappe.new_doc('Cart Items')
        insert.product=product_id
        insert.quantity = quantity
        insert.parent = cus_id[0].name
        insert.parenttype = 'Shopping Cart'
        insert.parentfield = 'items'
        insert.save(ignore_permissions=True)
        return get_shopping_cart_items(customer_id)
    else:
        cart = frappe.new_doc('Shopping Cart')
        cart.customer = customer_id
        cart.cart_type = cart_type
        cart.website_type='Website'
        cart.append('items',{
        'product':product_id,
        'quantity':quantity
        })
        cart.save(ignore_permissions=True)
        return get_shopping_cart_items(customer_id)

@frappe.whitelist()
@role_auth(role="Customer",method="POST")
def insert_item_tochild(customer_id,product_id,quantity,cart_type):
    try:
        customer = get_customer_from_token()
        if customer_id:
            customer = customer_id
            cus_id = frappe.db.get_all('Shopping Cart',fields=['customer','cart_type','name'],
                        filters={'customer': customer,'cart_type':cart_type})
            item_tochild__cus_id_check(cus_id, customer_id,product_id,quantity,cart_type)
        else:
            return {'status':'Failed',
                    'message':'invalid customer'}
    except Exception:
        other_exception("Error in v2.get_shopping_cart_list.insert_item_tochild")
        return {'status':'Failed',
                'message':'invalid record'}


@frappe.whitelist()
@role_auth(role='Customer',method='POST')
def get_category_slots(shipping_method):
    try:
        if shipping_method:
            query = frappe.db.sql(f'''  SELECT DS.name 
                                        FROM 
                                            `tabDelivery Setting` DS 
                                        INNER JOIN 
                                            `tabDelivery Slot Shipping Method` SH 
                                            ON SH.parent = DS.name''')
            res = get_slot(query)
            return {'status':'success',
                    'message':res}
        else:
            return {'status':'failed',
                    'message':'invalid'}
    except Exception:
        other_exception('Error in v2.get_shopping_cart_list.get_category_slots')
        return {'status':'failed',
                'message':'invalid shipping_method'}

def get_slot(name):
    try:
        if name:
            data_list = []
            data = frappe.get_doc('Delivery Setting',name)
            if data.enable_start_date and data.no_of_dates_start_from>0:
                resp = get_slot(data.no_of_dates_start_from)
                if resp:
                    data_list.append(resp)
                    return resp
                return {'status':'success',
                        'data_list':data_list}
                
            return {'status':'failed',
                    'message':'no record'}
        else:
            return {'status':'failes',
                    'message':"no"}
    except Exception:
            other_exception('Error in v2.get_shopping_cart_list.get_category_slots')
            return {'status':'failed',
                    'message':'invalid name'}


def get_slot(slot):
    try:
        if slot:
            return {'status':'success',
                    'message':slot}
        else:
            return {'status':'failed',
                    'message':'no data'}
    except Exception:
        other_exception('Error in v2.get_shopping_cart_list.get_slot')
        return {'status':'failed',
                'message':'invalid record'}


@frappe.whitelist()
@role_auth(role='Customer',method='POST')
def calc_shipping_charges(customer_id,mobilecartitems=None):
    try:
        if customer_id:
            lists = ','.join(['"' + x + '"' for x in products_list])
            products_list = list(set([x.get('product') for x in mobilecartitems]))
            cart_items = frappe.db.sql(f""" SELECT product,quantity 
                                            FROM `tabProduct` 
                                            WHERE name IN('{lists}') """,as_dict=1)
            return {'status':'success',
                    'message':cart_items}
        else:
            return {'status':'failed',
                    'message':'no data'}
    except Exception:
        other_exception('Error in v2.get_shopping_cart_list.calc_shipping_charges')
        return {'status':'failed',
                'message':'Invalid Customer'}


@frappe.whitelist()
@role_auth(role='Customer',method='POST')
def shipping_charges(customer_id):
    try:
        if customer_id:
            query = frappe.db.sql(f"""  SELECT 
                                            name AS Id,shipping_rate_method AS Name 
                                        FROM 
                                            `tabShipping Rate Method` """,as_dict=1)
            return {'status':'success',
                    'message':query}
        else:
            return {'status':'failed',
                    'message':'no data'}
    except Exception:
        other_exception("Error in v2.get_shopping_cart_list.shipping_charges")
        return {'status':'failed',
                'message':'invalid customer'}