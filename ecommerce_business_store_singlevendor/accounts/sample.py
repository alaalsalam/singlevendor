@frappe.whitelist()
def validate_expiry_date():

	Order=frappe.db.sql('''select * from `tabInvestment Order`''',as_dict=1)
	if Order:
		
		for x in Order:
			lockperiod=int(x.lock_in_period)
			Check=x.order_date+ timedelta(days=lockperiod)
			if Check == date.today() or Check <= date.today():
				print("order completed")
				frappe.db.set_value('Investment Order',x.name,'status',"Completed")
			else:
				print("order in progress")
				frappe.db.set_value("Investment Order", x.name , "status", "In-progress")
				frappe.db.set_value("Investment Order", x.name , "payment_status", "Paid")

@frappe.whitelist()
def scheduled_wallet_update():
	w_settings=frappe.get_single('Wallet Settings')
	listx = []
	Trans=frappe.db.sql('''select * from `tabWallet Transaction` where status=%(status)s''',{'status':"Pending"},as_dict=1)
	if Trans:
		for x in Trans:
			dur= x.transaction_date
			Check=x.modified+ timedelta(hours=dur)
			print(x.modified.strftime('%Y-%m-%d %H:%M:%S'))
		
			Rejectstatus= datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			print(Rejectstatus)
			print(Check.strftime('%Y-%m-%d %H:%M:%S'))
			if Check.strftime('%Y-%m-%d %H:%M:%S') <= Rejectstatus:
				Bid=frappe.db.sql('''select * from `tabBidding Entry` where requirement_id=%(id)s and status=%(status)s''',{'id':x.name,'status':"Pending"},as_dict=1)
				for y in Bid:
					listx.append(y.investor_bidding_amount)
				print(listx)
				if listx:
					num=min(listx)
					Bidding=frappe.db.sql('''select * from `tabBidding Entry` where investor_bidding_amount=%(amount)s order by creation asc limit 1''',{'amount':num},as_dict=1)
					for d in Bidding:
						print("Awarded")
						frappe.db.set_value('Bidding Entry',d.name,'status',"Awarded")
						# frappe.db.set_value('Requirement',x.name,'status',"Awarded")
						Bidd=frappe.db.sql('''select * from `tabBidding Entry` where requirement_id=%(id)s and status=%(status)s''',{'id':x.name,'status':"Pending"},as_dict=1)
						for t in Bidd:
							frappe.db.set_value('Bidding Entry',t.name,'status',"Rejected")
				else:
					print("Closed")
					frappe.db.set_value('Requirement',x.name,'status',"Closed")