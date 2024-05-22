import frappe
from frappe.utils import cint
@frappe.whitelist()
def get_leaderboards():
	leaderboards = {
	
		"Product": {
			"fields": [
				{"fieldname": "total_sales_amount", "fieldtype": "Currency"},
				"total_qty_sold",
				"available_stock_qty",
				{"fieldname": "available_stock_value", "fieldtype": "Currency"},
			],
			"method": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.leaders.get_all_items",
			"icon": "stock",
		},
        "Business": {
                "fields": [
                    {"fieldname": "total_sales_amount", "fieldtype": "Currency"},
                    {"fieldname": "total_commission", "fieldtype": "Currency"},
                ],
                "method": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.leaders.get_all_sales_partner",
                "icon": "hr",
            },
	}

	return leaderboards

@frappe.whitelist()
def get_all_items(date_range, field, limit=None):
    if field in ("available_stock_qty", "available_stock_value"):
        select_field = "sum(actual_qty)" if field == "available_stock_qty" else "sum(stock_value)"
        results = frappe.db.sql(
            """
            SELECT product AS name, {0} AS value
            FROM `tabBin`
            GROUP BY product
            ORDER BY value DESC
            LIMIT %s
            """.format(select_field),
            (cint(limit)),
            as_dict=1,
        )
    else:
        if field == "total_sales_amount":
            select_field = "sum(order_item.amount)"
            select_doctype = "Order"
        elif field == "total_qty_sold":
            select_field = "sum(order_item.current_stock)"
            select_doctype = "Order"
        date_condition = get_date_condition(date_range, "o.order_date")

        results = frappe.db.sql(
            """
            SELECT order_item.item AS name, {0} AS value
            FROM `tab{1}` o
            JOIN `tab{1} Item` AS order_item ON o.name = order_item.parent
            WHERE o.docstatus = 1 {2}
            GROUP BY order_item.item
            ORDER BY value DESC
            LIMIT %s
            """.format(select_field, select_doctype, date_condition),
            (cint(limit)),
            as_dict=1,
        )

    return results


@frappe.whitelist()
def get_all_sales_partner(date_range, field, limit=None):
    if field == "total_sales_amount":
        select_field =  "sum(`total_amount`)"
        select_doctype = "Order"
    elif field == "total_commission":
        select_field = "sum(`commission_amt`)"
        select_doctype = "Order"

    date_condition = get_date_condition(date_range, "o.order_date")
    value = frappe.db.get_list("Bin", fields=["business"])
    results = []

    for name in value:
        data = frappe.db.sql(
            f"""
            SELECT oi.business AS name, {select_field} AS value
            FROM `tabOrder Item` AS oi
            JOIN `tab{select_doctype}` AS o ON oi.parent = o.name
            JOIN `tabBusiness` AS p ON oi.business = p.name
            WHERE o.docstatus = 1 AND oi.business = %s {date_condition} AND p.name = %s
            ORDER BY value DESC
            LIMIT %s
            """,
            (name.business, name.business, cint(limit)),
            as_dict=1,
        )
        results.extend(data)

    return results

@frappe.whitelist()
def get_all_product(date_range, field, limit=None):
    product_names = frappe.get_all("Product", pluck="name")

    if field == "available_stock_qty":
        filters = [["docstatus", "=", 1]]

        return frappe.get_all(
            "Product",
            fields=["SUM(stock) as stock", "customer"],
            filters=filters,
            group_by="customer",
            order_by="stock DESC",
            limit=limit,
        )
    else:
        if field == "total_sales_amount":
            select_field = "SUM(oi.amount)"
            select_doctype = "Order Item"
        elif field == "total_qty_sold":
            select_field = "SUM(oi.quantity)"
            select_doctype = "Order Item"
        
        date_condition = get_date_condition(date_range, "o.delivery_date")

        results = []
        for product_name in product_names:
            data = frappe.db.sql(
                f"""
                SELECT {select_field} AS value
                FROM `tab{select_doctype}` As oi
                JOIN `tabOrder` AS o ON oi.parent = o.name
                JOIN `tabProduct` AS p ON oi.item = p.name
                WHERE o.docstatus = 1 {date_condition} AND p.name = %s
                GROUP BY o.customer
                ORDER BY value DESC
                LIMIT %s
                """,
                ( product_name, cint(limit)),
                as_dict=1,
            )
            results.extend(data)

        return results


def get_date_condition(date_range, field):
	date_condition = ""
	if date_range:
		date_range = frappe.parse_json(date_range)
		from_date, to_date = date_range
		date_condition = "and {0} between {1} and {2}".format(
			field, frappe.db.escape(from_date), frappe.db.escape(to_date)
		)
	return date_condition