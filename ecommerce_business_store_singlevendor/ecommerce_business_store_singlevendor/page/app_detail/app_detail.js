frappe.pages['app-detail'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'App Detail',
		single_column: true
	});
	$('.page-content').find('.layout-main').append(frappe.render_template("app_detail"));
}

frappe.pages['app-detail'].refresh = function(wrapper) {
    // location.reload();
    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.app_detail.app_detail.get_app_details',
        args: { doctype: "Product" },
        callback: function(r) {
        	html = '<div class="table">'
        	$('#detail-app').empty()
            console.log(r.message)
            // $.each(r.message,function(i, v){
            	html +='<div class="list-jobs">  <p class="text-muted"><b> App Title :</b>'+r.message.title+'</p> </div><hr>'
                html +='<div class="list-jobs">  <p class="text-muted"><b> App Description :</b>'+r.message.description+'</p> </div><hr>'
                 html +='<div class="list-jobs">  <p class="text-muted"><b> Version :</b>'+r.message.version+'</p> </div><hr>'
            	html +='<div class="list-jobs">  <p class="text-muted"><b> App Ratings :</b>'
            	if(r.message.ratings){
            		html +=r.message.ratings
            	}
            	else{
            		html +=0
            	}
            	html+='</p> </div><hr>'
            	
            	html +='<div class="list-jobs">  <p class="text-muted"><b> Installed App Count :</b>'+r.message.installs+'</p> </div>'
            	
            // })
            html +="</div>"
   		    $('#detail-app').append(html)
   		}
	})
}