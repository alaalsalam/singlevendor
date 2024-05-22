frappe.listview_settings['Wallet Withdrawal Request'] = {
	get_indicator: function(doc) {
		if(doc.status === "Open") {
				return [__("Open"), "darkgrey", "status,=,Open"];
			}
		else if (doc.status  === "Pending") {
				return [__("Pending"), "darkgrey", "status,=,Pending"];
			} 
		else if (doc.status  === "Approved") {
				return [__("Approved"), "orange", "status,=,Approved"];
			} 
    	else if (doc.status  === "Paid") {
				return [__("Paid"), "green", "status,=,Paid"];
			} 
		else if (doc.status  === "Rejected") {
				return [__("Rejected"), "red", "status,=,Rejected"];
			} 	
	}
};

