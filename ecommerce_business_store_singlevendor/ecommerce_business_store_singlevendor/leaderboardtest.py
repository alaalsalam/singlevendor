import frappe
from frappe.utils import cint

def get_leaderboards():
    leaderboards = {
        "leaderboardtest": {
           "fields": [
    {"fieldname": "total_sales_amount", "fieldtype": "Currency"},
    {"fieldname": "total_qty_sold", "fieldtype": "Float"},
    {"fieldname": "outstanding_amount", "fieldtype": "Currency"},
],

            "method": "ecommerce_business_store_singlevendor.page.cust.get_customers",
            "icon": "customer",
         

        },
    }
    return leaderboards

@frappe.whitelist()
def get_customers(date_range, company, field, limit=None):
    if field == "outstanding_amount":
        filters = [["docstatus", "=", 1], ["company", "=", company]]
        date_range = frappe.parse_json(date_range)
        if date_range:
            filters.append(["posting_date", "between", [date_range[0], date_range[1]]])
        return frappe.get_all(
            "Sales Invoice",
            fields=["customer as name", "sum(outstanding_amount) as value"],
            filters=filters,
            group_by="customer",
            order_by="value desc",
            limit=limit,
        )
    else:
        if field == "total_sales_amount":
            select_field = "sum(so_item.base_net_amount)"
        elif field == "total_qty_sold":
            select_field = "sum(so_item.stock_qty)"
        date_condition = get_date_condition(date_range, "so.transaction_date")

    return frappe.db.sql(
    f"""
    SELECT so.customer AS name, {select_field} AS value
    FROM `tabOrder` AS so
    LEFT JOIN `tabOrder Item` AS so_item ON so.name = so_item.parent
    WHERE so.docstatus = 1 {date_condition} and so.company = %s
    GROUP BY so.customer
    ORDER BY value DESC
    LIMIT %s
    """,
    (company, cint(limit)),
    as_dict=1,
)


def get_date_condition(date_range, field):
    date_condition = ""
    if date_range:
        date_range = frappe.parse_json(date_range)
        from_date, to_date = date_range
        date_condition = f"and {field} between {frappe.db.escape(from_date)} and {frappe.db.escape(to_date)}"
    return date_condition















