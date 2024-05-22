// Copyright (c) 2020, Tridots Tech and contributors
// For license information, please see license.txt


frappe.require("assets/ecommerce_business_store_singlevendor/css/toggle-slider.css");
frappe.ui.form.on('Service', {
	refresh: function(frm) {
		frm.trigger('all_time');
		frm.set_df_property('status', 'read_only', 1);
		if(!frm.__islocal){
			if(frappe.session.user == 'Administrator' || has_common(frappe.user_roles, ['Admin'])){
				if (frm.doc.status == 'Awaiting Approval') {
	                frm.add_custom_button(__('Approved'), function() {
	                    frm.set_value('status', 'Approved');
	                    cur_frm.save()
	                });
	                frm.add_custom_button(__('Rejected'), function() {
	                    frm.set_value('status', 'Rejected');
	                    cur_frm.save()
	                });
	            }
			}
		}
        frm.fields_dict.category_mapping.grid.grid_buttons.find('.grid-add-row').addClass('hidden');
        frm.fields_dict.add_categories.$wrapper.find('button').addClass('btn-primary').removeClass('btn-default');    
        frm.fields_dict.add_categories.$wrapper.find('button').addClass('btn-sm').removeClass('btn-xs');	
	},
	all_time:function(frm){
        if(frm.doc.all_time==0 && frm.doc.time_slot.length==0){
            frappe.call({
                method:'frappe.client.get_list',
                args:{
                    'doctype':'Opening Hour',
                    'filters':{
                        'parent':frm.doc.business,
                        'parenttype':'Business'
                    },
                    'fields':['day','status','from_hrs','to_hrs'],
                    'parent':'Business',
                    'order_by':'idx'
                },
                callback:function(r){
                    if(r.message){
                        $(r.message).each(function(k,v){
                            if(v.status=='Open'){
                                let row=frappe.model.add_child(cur_frm.doc,'Available Time Slot','time_slot',k+1)
                                row.day=v.day;
                                row.from_time=v.from_hrs;
                                row.to_time=v.to_hrs;
                            }
                        })
                        cur_frm.refresh_field('time_slot')
                    }
                }
            })
        } else if(frm.doc.all_time == 1){
            frm.set_value('time_slot',[])
        }
    },

    add_categories: function(frm){
    	category_dialog(frm)
    },

    build_multi_selector(frm, possible_val) {        
        $.each(possible_val, function(i, c) {
            var ref_fields = unescape(c.reference_fields);
            var ref_method = c.reference_method;
            var cls = c.cls;
            var field = c.tab_field;
            var linkedfield = c.link_name;
            var url = '/api/method/' + ref_method;
            let selected_items = cur_frm.doc[c.frm_field];
            $.ajax({
                type: 'POST',
                Accept: 'application/json',
                ContentType: 'application/json;charset=utf-8',
                url: window.location.origin + url,
                data: {
                    "reference_doc": c.reference_doc,
                    "reference_fields": ref_fields
                },
                dataType: "json",
                async: false,
                headers: {
                    'X-Frappe-CSRF-Token': frappe.csrf_token
                },
                success: function(r) {
                    var list_name = r.message.list_name;
                    var drp_html = `<div class="${c.cls}" style="padding: 0px;">
                                        <div class="awesomplete">
                                            <input type="text"  class="multi-drp" id="myInput" 
                                                    autocomplete="nope" onfocus="select_list_detail($(this))" 
                                                    onfocusout="disable_select_list($(this))" 
                                                    onkeyup="selected_lists_values($(this))" 
                                                    placeholder="${c.title}" title="${c.title}" 
                                                    style="background-position: 10px 12px;
                                                    background-repeat: no-repeat;width: 100%;
                                                    font-size: 16px;padding: 10px 15px 10px 10px;
                                                    border: 1px solid #d1d8dd;border-radius: 4px !important;
                                                    margin: 0px;" data-class="${c.cls}" 
                                                    data-field="${c.tab_field}" 
                                                    data-doctype="${c.doctype}" data-child="${c.is_child}" 
                                                    data-linkfield="${c.link_name}" 
                                                    data-reference_doc="${c.reference_doc}" 
                                                    data-reference_fields="${c.reference_fields}" 
                                                    data-search_fields="${c.search_fields}" 
                                                    data-reference_method="${c.reference_method}" 
                                                    data-child_link="c.child_tab_link">
                                                <h4 style="padding: 10px 10px;border: 1px solid #ddd;
                                                        border-bottom: none;margin: 30px 0px 0px 0px;
                                                        background: #f8f8f8;">
                                                    ${c.label}
                                                </h4>
                                                <ul role="listbox" id="assets" class= "assets" 
                                                        style="list-style-type: none;position: absolute;
                                                        width: 43%;margin: 0;background: rgb(255, 255, 255);
                                                        min-height:350px;height:350px;box-shadow:none">`
                    var k = 0
                    $.each(list_name, function(i, v) {
                        if (v[c.link_name]) {
                            k += 1
                            var args = {
                                txt: "",
                                searchfield: "name",
                                filters: { "name": v[c.link_name] }
                            };
                            let arr, check;
                            try{
                                check = selected_items.find(obj=>obj[c.child_field] == v[c.link_name]);
                            } catch(e){}                            
                            if(check)
                            	arr = [check[c.child_field]];
                            if ($.inArray(v[c.link_name], arr) == -1){
                                drp_html += `
                                            <li style="display: block; border-bottom: 1px solid #dfdfdf; cursor:auto;">
                                                <a style="display: none;">
                                                    <strong> 
                                                        ${v[c.link_name]} 
                                                    </strong>
                                                </a>
                                                <label class="switch" style="float:right; margin:0px; cursor:pointer;">
                                                    <input type="checkbox" class="popupCheckBox" 
                                                        name="vehicle1" value="0" id="${v[c.link_name]}" 
                                                        data-doctype="${c.doctype}" data-child="${c.is_child}" 
                                                        data-reference_doc="${c.reference_doc}" 
                                                        data-reference_fields="${c.reference_fields}" 
                                                        data-search_fields="${c.search_fields}"
                                                        data-child_link="${c.child_tab_link}" 
                                                        onclick="selected_multiselect_lists($(this))">
                                                    <span class=" slider round">
                                                    </span>
                                                </label>
                                                <p style="font-size: 16px;">
                                            `;
                                if(v["parent_categories"]){
                                    drp_html += ` ${v["parent_categories"]}</span></p></li>`;
                                }else{
                                    drp_html += `${v[c.search_fields]}</span></p></li>`;
                                }
                            }
                            else{
                                drp_html += `
                                            <li style="display: block; border-bottom: 1px solid #dfdfdf; cursor:auto;">
                                                <a style="display: none;">
                                                    <strong> 
                                                        ${v[c.link_name]} 
                                                    </strong>
                                                </a>
                                                <label class="switch" style="float:right; margin:0px; cursor:pointer;">
                                                    <input type="checkbox" class="popupCheckBox" name="vehicle1" value="0" 
                                                    id="${v[c.link_name]}" data-doctype="${c.doctype}" data-child="${c.is_child}" 
                                                    data-reference_doc="${c.reference_doc}" data-reference_fields="${c.reference_fields}" 
                                                    data-search_fields="${c.search_fields}" data-child_link="${c.child_tab_link}" 
                                                    onclick="selected_multiselect_lists($(this))" checked>
                                                    <span class=" slider round">
                                                    </span>
                                                </label>
                                                <p style="font-size: 16px;">`;
                                if ( v["parent_categories"] ) {
                                    drp_html += ` ${v["parent_categories"]} </span></p></li>`;
                                }
                                else {
                                    drp_html += `${v[c.search_fields]}</span></p></li>`;
                                }
                            }
                        } 
                        else {
                            drp_html += '<li> </li>';
                        }
                    })
                    drp_html += `</ul></div></div><p class="help-box small text-muted hidden-xs">${c.description} </p>`;
                    cur_dialog.fields_dict["category_html"].$wrapper.append(drp_html);
                }
            })
        });
    }
});
function category_dialog(frm) {
    frm.possible_val = [{
        "cls": "custom-product-category",
        "tab_html_field": "category_html",
        "tab_field": "category_json",
        "link_name": "name",
        "title": "Search product category here...",
        "label": "Choose Category",
        "doctype": "Service",
        "reference_doc": "Product Category",
        "reference_fields": escape(JSON.stringify(["name", "category_name"])),
        "search_fields": "category_name",
        "reference_method": "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.get_category_list",
        "is_child": 0,
        "description": "Please select the category for this plan.",
        "child_tab_link": "",
        "frm_field": "category_mapping" ,
        "child_field": "category"
    }];
    let categoryDialog;
    let random = Math.random() * 100;
    var content = []
    categoryDialog = new frappe.ui.Dialog({
        title: __('Select Categories'),
        fields: [
            { 
                label: "Select Category", 
                fieldtype: 'Table MultiSelect', 
                fieldname: 'category_list', 
                options: 'Product Category Mapping',
                hidden: 1 
            },
            { 
                label: "Select Category", 
                fieldtype: 'HTML', 
                fieldname: 'category_html', 
                options: '' 
            },
            { 
                label: "Selected Category", 
                fieldtype: 'Code', 
                fieldname: 'category_json', 
                options: '', 
                read_only: 1, 
                hidden: 1 
            }
        ],
        primary_action_label: __('Close')
    });
    $.each(cur_frm.doc.product_categories, function(i, s) {
        content.push(s.category)
    })
    categoryDialog.get_field('category_json').set_value(JSON.stringify(content));
    categoryDialog.get_field('category_json').refresh();
    categoryDialog.show();
    setTimeout(function() {
        frm.events.build_multi_selector(frm, frm.possible_val);
    }, 1000)
    categoryDialog.set_primary_action(__('Add'), function() {
        var cat = categoryDialog.get_values();
        var cat_json = JSON.parse(cat.category_json)
        cur_frm.doc.product_categories = [];
         $(cat_json).each(function(k, v) {            
            let row = frappe.model.add_child(frm.doc, "Product Category Mapping", "category_mapping");
            row.category = v;
        })
         if (cat_json.length <= 0) {
            frappe.throw(__('Please select any one category.'))
        } else {
            refresh_field("selected_category_list");
            frm.refresh_field('category_mapping')
            $('div[data-fieldname="category_mapping"] .grid-footer .grid-add-row').addClass('hidden')
            categoryDialog.hide();
            if (!frm.doc.__islocal)
                cur_frm.save();            
        }
    })
    categoryDialog.$wrapper.find('.modal-dialog').css("min-width", "1000px");
    categoryDialog.$wrapper.find('.modal-content').css("min-height", "575px");
}
frappe.ui.form.on('Product Category Mapping',{
    category_mapping_add: function(frm, cdt, cdn){
        frm.fields_dict.category_mapping.grid.grid_buttons.find('.grid-add-row').addClass('hidden');
    },
    category_mapping_remove: function(frm, cdt, cdn){
        frm.fields_dict.category_mapping.grid.grid_buttons.find('.grid-add-row').addClass('hidden');
    },
    category_mapping_move: function(frm, cdt, cdn){
        frm.fields_dict.category_mapping.grid.grid_buttons.find('.grid-add-row').addClass('hidden');
    }
})