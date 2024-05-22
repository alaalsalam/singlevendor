import frappe
from frappe.utils import cint

def get_leaderboards():
    leaderboards = {
        "Customers": {
            "fields": [
                {"fieldname": "total_sales_amount", "fieldtype": "Currency"},
                {"fieldname": "total_qty_sold", "fieldtype": "Float"},
                {"fieldname": "outstanding_amount", "fieldtype": "Currency"},
            ],
            "method": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.cust.get_customers",
            "icon": "customer",
        },
        "Supplier": {
            "fields": [
                {"fieldname": "total_purchase_amount", "fieldtype": "Currency"},
                {"fieldname": "total_qty_purchased", "fieldtype": "Float"},
                {"fieldname": "outstanding_amount", "fieldtype": "Currency"},
            ],
            "method": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.cust.get_all_suppliers",
            "icon": "buying",
        },
    }
    return leaderboards

@frappe.whitelist()
def get_customers(date_range, field, limit=None):
    if field == "outstanding_amount":
        filters = [["docstatus", "=", 1]]
        date_range = frappe.parse_json(date_range)
        if date_range:
            filters.append(["posting_date", "between", [date_range[0], date_range[1]]])
        return frappe.db.sql(
            f"""
            SELECT customer AS name, SUM(si.outstanding_amount) AS value
            FROM `tabSales Invoice` AS si
            WHERE si.docstatus = 1 
            GROUP BY si.customer
            ORDER BY value DESC
            LIMIT %s
            """,
            (cint(limit)),
            as_dict=1,
        )
    else:
        if field == "total_sales_amount":
            select_field = "sum(so_item.amount)"
        elif field == "total_qty_sold":
            select_field = "sum(so_item.quantity)"
        date_condition = get_date_condition(date_range, "so.order_date")

        return frappe.db.sql(
            f"""
            SELECT so.customer AS name, {select_field} AS value
            FROM `tabOrder` AS so
            JOIN `tabOrder Item` AS so_item ON so.name = so_item.parent
            JOIN `tabSales Invoice` AS si ON si.customer = so.customer
            WHERE so.docstatus = 1 {date_condition}
            GROUP BY so.customer
            ORDER BY value DESC
            LIMIT %s
            """,
            (cint(limit)),
            as_dict=1,
        )

@frappe.whitelist()
def get_all_suppliers(date_range, field, limit=None):
    if field == "outstanding_amount":
        filters = [["docstatus", "=", 1]]
        date_range = frappe.parse_json(date_range)
        if date_range:
            filters.append(["posting_date", "between", [date_range[0], date_range[1]]])
            return frappe.db.sql(
            f"""
            SELECT supplier AS name, SUM(purchase_order.outstanding_amount) AS value
            FROM `tabPurchase Invoice` AS purchase_order
            WHERE purchase_order.docstatus = 1 
            GROUP BY supplier
            ORDER BY value DESC
            LIMIT %s
            """,
            (cint(limit)),
            as_dict=1,
        )
        
    else:
        if field == "total_purchase_amount":
            select_field = "sum(purchase_order_item.amount)"
        elif field == "total_qty_purchased":
            select_field = "sum(purchase_order_item.quantity)"
        date_condition = get_date_condition(date_range, "purchase_order.modified")

        return frappe.db.sql(
            f"""
            SELECT purchase_order.supplier AS name, {select_field} AS value
            FROM `tabPurchase Order` AS purchase_order
            JOIN `tabPurchase Order Item` AS purchase_order_item ON purchase_order.name = purchase_order_item.parent
            WHERE purchase_order.docstatus = 1 {date_condition}
            GROUP BY purchase_order.supplier
            ORDER BY value DESC
            LIMIT %s
            OFFSET 0
            """,
            (cint(limit)),
            as_dict=1,
        )

def get_date_condition(date_range, field):
    date_condition = ""
    if date_range:
        date_range = frappe.parse_json(date_range)
        from_date, to_date = date_range
        date_condition = f"and {field} between {frappe.db.escape(from_date)} and {frappe.db.escape(to_date)}"
    return date_condition
