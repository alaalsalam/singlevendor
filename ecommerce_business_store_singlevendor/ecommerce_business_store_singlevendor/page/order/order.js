frappe.pages['order'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Order',
        single_column: true
    });
    $('#page-order .page-content').find('.layout-main').append(frappe.render_template("cartitems"));
    $('#page-order .page-content').find('.layout-main').prepend('<div class="formlist"></div>')
    let height=$(window).height();
    $('#page-order .page-content').find('.layout-main').css('min-height',(height-120)+'px');
    page.set_secondary_action(__('Refresh'), () => {
        cur_page.page.refresh(wrapper);
    });

   
}
let item_group;
frappe.pages['order'].refresh = function(wrapper) {
    get_currency()
    run_items()
    $('.cartdiv .cart-items').css('height', ($(window).height()-415)+'px');
    setTimeout(function(){ $(".page-loader").hide();$(".order-container").show(); }, 3000);
    
}
function get_currency(){
    frappe.call({
        method: "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.order.order.get_currency",
        freeze: true,
        args: {},
        async: false,
        callback: function(data) {
            if(data.message){
                $('.cartdiv .set_currency').text(data.message)
            }
        }
    })
}

function get_item_html(item) {
        const { item_code, item_name, item_image, price} = item;
        const item_title = item_name || item_code;

        const template = `
            <div class="pos-item-wrapper image-view-item" data-item-code="${escape(item_code)}">
                <div class="image-view-header">
                    <div>
                        <a class="grey list-id" data-name="${item_code}" title="${item_title}">
                            ${item_title}
                        </a>
                    </div>
                </div>
                <div class="image-view-body">
                    <a  data-item-code="${item_code}"
                        title="${item_title}"
                    >
                        <div class="image-field"
                            style="${!item_image ? 'background-color: #fafbfc;' : ''} border: 0px;"
                        >
                            ${!item_image ? `<span class="placeholder-text">
                                    ${frappe.get_abbr(item_title)}
                                </span>` : '' }
                            ${item_image ? `<img src="${item_image}" alt="${item_title}">` : '' }
                        </div>
                        <span class="price-info">
                            ${price}
                        </span>
                    </a>
                </div>
            </div>
        `;
        $('.page-content').find('.pos-item-wrapper').html(template);
        return template;
    }

    function get_items({start = 0, page_length = 40, search_txt = '', search_term = ''}={}) {
            frappe.call({
                method: "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.order.order.get_items",
                freeze: true,
                args: {
                    start,
                    page_length,
                    search_txt,
                    search_term
                },
                async: false,
                callback: function(data) {
                    var content = data.message
                    let row_items = [];
                    let curr_row = 0;
                    console.log(data.message.items)
                    if (data.message) {
                        if(data.message.items && data.message.items.length > 0){
                            $('#page-order .maindiv .items-wrapper').html(frappe.render_template("order", { content: data.message.items }));
                        }
                        else{
                            $('#page-order .maindiv .items-wrapper').html(frappe.render_template("order", { content: '' }));
                        }
                    }
                    else{
                        $('#page-order .maindiv .items-wrapper').html(frappe.render_template("order", { content: '' }));
                    }
                }
            })
        }
 function set_filters(){
    const me = this;
    if($('#page-order .maindiv .item-container .fields .search-field').find('.input-max-width').length === 0) {
    this.search_field = frappe.ui.form.make_control({
        df: {
            fieldtype: 'Data',
            label: __('Search Item'),
            placeholder: __('Search by item name')

        },
        parent:$('#page-order .maindiv .item-container .fields').find('.search-field'),
        render_input: true,
    });
}
    this.search_field.$input.on('input', (e) => {
        this.last_search = setTimeout(() => {
            const search_term = e.target.value;
            const item_group = this.item_group_field ?
                this.item_group_field.get_value() : '';

            get_items({ search_term:search_term,  search_txt: item_group});
        }, 300);
    });
    if($('#page-order .maindiv .item-container .fields .item-group-field').find('.input-max-width').length === 0) {
        this.item_group_field = frappe.ui.form.make_control({
            df: {
                fieldtype: 'Link',
                label: 'Product Category',
                options: 'Product Category',
                fieldname: 'product_category',
                placeholder: __('Search by category'),
                onchange: ()=> {
                    item_group = this.item_group_field.get_value();
                    console.log(item_group)
                    if (item_group) {
                        get_items({ search_txt: item_group });
                    }
                    else{
                        get_items({ search_txt: '' });
                    }
                },
                get_query: () => {
                    return "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.order.order.item_group_query"
                }
            },
            parent: $('#page-order .maindiv .item-container .fields').find('.item-group-field'),
            render_input: true
        });
    }
 }

 function run_items(){
    frappe.run_serially([
            () => {
                get_items()
            },
            () => {
                set_filters()
            }
        ])
 }

 function bind_events(e) {
        var me = this;
        let item_code = $(e).attr('data-item-code');
        frappe.call({
            method: "ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.order.order.get_item",
            freeze: true,
            args: {
                item_code
            },
            async: false,
            callback: function(data) {
                if(data.message.items){
                    console.log(data.message.currency)
                    var currency = data.message.currency
        var allow = 0;
        $('.cartdiv .cart-items .cart-list-items').each(function(k, v){
                if($(this).attr('data-item-code')==data.message.items[0].name){
                    allow = 1;
                let amt = $(this).find('.ttl_price').find('.rate').attr('data-rate');
                let tax = $(this).find('.ttl_price').find('.rate').attr('data-tax');
                let qty1 = $(this).find('.ttl_price').find('.item_qty').val();
                var amount = data.message.items[0].price + parseFloat(amt);
                var qty = 1 + parseInt(qty1);
                $(this).find('.ttl_price').find('.rate').text(amount.toFixed(2));
                $(this).find('.ttl_price').find('.rate').attr('data-rate', amount);
                $(this).find('.ttl_price').find('.item_qty').val(qty);
                $(this).find('.ttl_price').find('.qty').text(qty);
                var grand = $('.cartdiv .grand-total-value').text();
                var tot_grand = data.message.items[0].price + parseFloat(grand);
                $('.cartdiv .grand-total-value').text(tot_grand.toFixed(2));
                var tot_qty = $('.cartdiv .quantity-total').text();
                var tot_qty1 = 1 + parseInt(tot_qty);
                var add_tax = parseFloat(tax) * parseInt(qty)
                $(this).find('.ttl_price').find('.rate').attr('data-tax', add_tax.toFixed(2));
                $('.cartdiv .quantity-total').text(tot_qty1);
            }
            })
            
        
        if(allow==0){
        data.message.items.map(f => {
                        var row = $( `
            <div class="list-item cart-list-items" data-item-code="${escape(f.name)}"
                 title="Item: ${f.name}  Available Qty: ">
                <div class="row">
                
    <div class="col-md-12 col-sm-12 col-xs-9">
        <div class="product-title" style="font-weight: 600;
    font-size: 14px;">${f.item}</div>
    </div>
</div>
<div class="row ttl_price">
    <div class="col-md-3 col-sm-4 col-xs-3 items-qty">
        ${get_quantity_html(f.minimum_order_qty,f.name)}
    </div>
    <div class="col-md-7 col-sm-6 col-xs-5"><span class="qtyx">x</span><div class="product-price">${currency} ${f.price.toFixed(2)}</div><div class="item-total-price rate" data-rate="${f.price}" data-tax="${f.tax.toFixed(2)}" data-orgi-tax="${f.tax.toFixed(2)}" data-tax-label="${f.tax_label}" data-orgi-rate="${f.price}" style="
    font-weight: 500;">${currency} ${f.price.toFixed(2)}</div></div>
    <div class="col-md-2 col-sm-2 col-xs-4" style="padding:0px;"><div class="product-delete"><span class="fa fa-trash btn-sm btn-danger" data-id="${f.name}" onclick="deleteItem($(this))"></span>
    </div></div>
</div>
        `)
                        $('.empty-state').hide();
                        $('#page-order .cartdiv .cart-wrapper').find('.cart-items').append(row);
                    })
    }
                }
            }
        })
        var amount = 0;
        var qty = 0;
        var tax = 0;
        var tax_label = ''
        $('.cartdiv .cart-items .cart-list-items').each(function(k, v){
            let amt = $(this).find('.ttl_price').find('.rate').attr('data-rate');
            let qty1 = $(this).find('.ttl_price').find('.item_qty').val();
            let tax1 = $(this).find('.ttl_price').find('.rate').attr('data-tax');
            amount = amount + parseFloat(amt);
            qty = qty + parseInt(qty1);
            tax = tax + parseFloat(tax1);
            if(tax_label==''){
                tax_label = $(this).find('.ttl_price').find('.rate').attr('data-tax-label');
            }
        })
        console.log(amount)
        $('.cartdiv .grand-total-value').text(amount.toFixed(2));
        $('.cartdiv .grand-tax-value').text(tax.toFixed(2));
        $('#hdnTax').val(tax);
        var discount = $('#hdnDiscount').val();
        if(discount){
            discount = discount
        }else{discount = 0}
        if(tax_label == "Excl"){
            var tot = amount + tax - discount
            $('.cartdiv .total-value').text(tot.toFixed(2));
        }
        else{
            var tot = amount - discount
            $('.cartdiv .total-value').text(tot.toFixed(2));
        }
        $('.cartdiv .quantity-total').text(qty);
    }

function get_quantity_html(value,name) {
    return `
       <div class="product-qty">
    <span class="fa fa-minus" data-id="${name}" onclick="decrqty($(this))"></span> 
    <span class="qty">${value}</span>
    <input type="hidden" class="form-control item_qty" type="number" value="${value}" readonly>
    <span class="fa fa-plus" data-id="${name}" onclick="incrqty($(this))"></span>
  </div>
    `;
} 

function incrqty(e){
    console.log("----------e")
    let incr_qty = $(e).parent().find('.item_qty').val()
    incr_qty = flt(incr_qty) + 1
    $(e).parent().find('.item_qty').val(incr_qty)
    $(e).parent().find('.qty').text(incr_qty);
    var rate = $(e).parent().parent().parent().parent().find('.rate').attr('data-rate');
    var rate1 = $(e).parent().parent().parent().parent().find('.rate').attr('data-orgi-rate');
    var tot_rate = parseFloat(rate1) * parseInt(incr_qty);
    var org_tax = $(e).parent().parent().parent().parent().find('.rate').attr('data-orgi-tax');
    var tot_tax = parseFloat(org_tax) * parseInt(incr_qty);
    $(e).parent().parent().parent().find('.rate').text(tot_rate.toFixed(2));
    $(e).parent().parent().parent().find('.rate').attr('data-rate', tot_rate.toFixed(2));
    $(e).parent().parent().parent().find('.rate').attr('data-tax', tot_tax.toFixed(2));
    var amount = 0;
    var qty = 0;
    var tax_label = ''
    var tax = 0
    $('.cartdiv .cart-items .cart-list-items').each(function(k, v){
        let amt = $(this).find('.ttl_price').find('.rate').attr('data-rate');
        let qty1 = $(this).find('.ttl_price').find('.item_qty').val();
        tax_label = $(this).find('.ttl_price').find('.rate').attr('data-tax-label');
        let tax1 = $(this).find('.ttl_price').find('.rate').attr('data-tax');
        tax = tax + parseFloat(tax1);
        amount = amount + parseFloat(amt);
        qty = qty + parseInt(qty1);
    })
    $('.cartdiv .grand-total-value').text(amount.toFixed(2));
    $('.cartdiv .quantity-total').text(qty);
    $('.cartdiv .grand-tax-value').text(tax.toFixed(2));
    $('#hdnTax').val(tax);
    var discount = $('#hdnDiscount').val();
    if(discount){
        discount = discount
    }else{discount = 0}
    if(tax_label == "Excl"){
        var tot = amount + tax - discount
        $('.cartdiv .total-value').text(tot.toFixed(2));
    }
    else{
        var tot = amount - discount
        $('.cartdiv .total-value').text(amount.toFixed(2));
    }
}

function decrqty(e){
    console.log("----------e1")
    let desc_qty = $(e).parent().find('.item_qty').val();
    let desc_qty1 = $(e).parent().find('.item_qty').val();
    if(desc_qty > 1){
        desc_qty = flt(desc_qty) - 1
        $(e).parent().find('.item_qty').val(desc_qty);
        $(e).parent().find('.qty').text(desc_qty);
    }
    if(desc_qty1 == 1){
        var id = $(e).attr('data-id');
        $(e).parent().parent().parent().parent().attr('data-item-code',id).remove();
        if($('#page-order .cartdiv .cart-items').find('.cart-list-items').length === 0) {
            $('.empty-state').show();
        }
    }
    var rate = $(e).parent().parent().parent().find('.rate').attr('data-rate');
    var rate1 = $(e).parent().parent().parent().find('.rate').attr('data-orgi-rate');
    var tot_rate = parseFloat(rate1) * parseInt(desc_qty);
    $(e).parent().parent().parent().find('.rate').text(tot_rate.toFixed(2));
    $(e).parent().parent().parent().find('.rate').attr('data-rate', tot_rate.toFixed(2));
     var org_tax = $(e).parent().parent().parent().parent().find('.rate').attr('data-orgi-tax');
    var tot_tax = parseFloat(org_tax) * parseInt(desc_qty);
    $(e).parent().parent().parent().find('.rate').text(tot_rate.toFixed(2));
    $(e).parent().parent().parent().find('.rate').attr('data-rate', tot_rate.toFixed(2));
    $(e).parent().parent().parent().find('.rate').attr('data-tax', tot_tax.toFixed(2));
    var amount = 0;
    var qty = 0;
    var tax_label = ''
    var tax = 0
    $('.cartdiv .cart-items .cart-list-items').each(function(k, v){
        let amt = $(this).find('.ttl_price').find('.rate').attr('data-rate');
        let qty1 = $(this).find('.ttl_price').find('.item_qty').val();
         tax_label = $(this).find('.ttl_price').find('.rate').attr('data-tax-label');
        let tax1 = $(this).find('.ttl_price').find('.rate').attr('data-tax');
        tax = tax + parseFloat(tax1);
        amount = amount + parseFloat(amt);
        qty = qty + parseInt(qty1);
    })
    $('.cartdiv .grand-total-value').text(amount.toFixed(2));
    $('.cartdiv .quantity-total').text(qty);
    $('.cartdiv .grand-tax-value').text(tax.toFixed(2));
    $('#hdnTax').val(tax);
    var discount = $('#hdnDiscount').val();
    if(discount){
        discount = discount
    }else{discount = 0}
    if(tax_label == "Excl"){
        var tot = amount + tax - discount
        $('.cartdiv .total-value').text(tot.toFixed(2));
    }
    else{
        var tot = amount - discount
        $('.cartdiv .total-value').text(amount.toFixed(2));
    }
}
function deleteItem(e){
    var id = $(e).attr('data-id');
    var cur_amt = $(e).parent().parent().parent().find('.rate').attr('data-rate');
    var cur_tax = $(e).parent().parent().parent().find('.rate').attr('data-tax');
    var cur_qty = $(e).parent().parent().parent().find('.item_qty').val();
    var grand_total = $('.cartdiv .grand-total-value').text();
    var total_value = $('.cartdiv .total-value').text();
    var total_tax = $('.cartdiv .grand-tax-value').text();
    var total_qty = $('.cartdiv .quantity-total').text();
    var cur_tot_tax = parseFloat(total_tax) - parseFloat(cur_tax);
    var cur_tot_tax1 = 0
    if(cur_tot_tax){
        cur_tot_tax1 = cur_tot_tax
    }
    var cur_total_value = parseFloat(total_value) - parseFloat(cur_amt) - parseFloat(cur_tax);
    var cur_grand_total = parseFloat(grand_total) - parseFloat(cur_amt);
    var cur_total_qty = parseInt(total_qty) - parseInt(cur_qty)
    $(e).parent().parent().parent().parent().attr('data-item-code',id).remove();
    $('.cartdiv .grand-total-value').text(cur_grand_total.toFixed(2));
    $('.cartdiv .grand-tax-value').text(cur_tot_tax.toFixed(2));
    $('.cartdiv .total-value').text(cur_total_value.toFixed(2));
    $('.cartdiv .quantity-total').text(cur_total_qty);
    if($('#page-order .cartdiv .cart-items').find('.cart-list-items').length === 0) {
        $('.empty-state').show();
    }
}

function insertOrder(){
    var customer_name = $('#customerName').val();
    var items_len = $('#page-order .cartdiv .cart-items').find('.cart-list-items').length;
    console.log("-----------12")
    console.log(customer_name)
    if(customer_name && items_len>0){
        ShowPopup()
    }
    else{
        console.log("------ewr")
        var html = ''
        if(customer_name == ''){
            html = 'Select the customer.'
        }
        else if(items_len==0){
            html = 'Cart is empty. Please add items to cart.'
        }
        frappe.msgprint(html, 'Alert')
    }
}
function ShowPopup(){
    var grand_total = $('.cartdiv .grand-total-value').text();
    let title = __('Total Amount {0}',
            [grand_total]);
    var dialog = new frappe.ui.Dialog({
        title: __(title),
        fields: [{ "fieldtype": "Link", "fieldname": "shipping_method", "label": __("Shipping Method"), "reqd": 1, "options":"Shipping Method",
        "onchange": function () {
                    let val = this.get_value();
                    if (val) {
                        frappe.call({
                            method: 'frappe.client.get_value',
                            args: {
                                'doctype': "Shipping Method",
                                'filters': { 'name': val },
                                'fieldname': "shipping_method_name"
                            },
                            callback: function (r) {
                                if (r.message) {
                                    shipping_method_name = r.message.shipping_method_name
                                    dialog.fields_dict.shipping_method_name.set_value(shipping_method_name);
                                }
                            }
                        })
                    }
                }
         },
         { "fieldtype": "Link", "fieldname": "payment_method", "label": __("Payment Method"), "reqd": 1, "options":"Payment Method",
         "onchange": function () {
                    let val = this.get_value();
                    if (val) {
                        frappe.call({
                            method: 'frappe.client.get_value',
                            args: {
                                'doctype': "Payment Method",
                                'filters': { 'name': val },
                                'fieldname': "payment_method"
                            },
                            callback: function (r) {
                                if (r.message) {
                                    payment_method = r.message.payment_method
                                    dialog.fields_dict.payment_method_name.set_value(payment_method);
                                }
                            }
                        })
                    }
                }
          },
         { 'fieldtype': 'Column Break', 'fieldname': 'predefined_col_br_1' },
         { "fieldtype": "Data", "fieldname": "shipping_method_name", "label": __("Shipping Method Name"), "read_only": 1},
        { "fieldtype": "Read Only", "fieldname": "payment_method_name", "label": __("Payment Method Name")}]
    });
    dialog.set_primary_action(__('Submit'), function() {
        var formData = {}
        let items_list = [];
        var values = dialog.get_values();
        if(values.shipping_method && values.payment_method){
            formData.shipping_method = values.shipping_method;
            formData.payment_method = values.payment_method;
            formData.customer_name = $('#customerName').val();
            var subtotal =  $('.cartdiv .grand-total-value').text();
            var total_tax = $('.cartdiv .grand-tax-value').text();
            if(total_tax){
                total_tax = total_tax
            }else{total_tax = 0}
            var total_amt =  $('.cartdiv .total-value').text();
            var discount = $('#hdnDiscount').val();
             if(discount){
                discount = discount
            }else{discount = 0}
            formData.subtotal = parseFloat(subtotal);
            formData.total_tax = parseFloat(total_tax)
            formData.total_amt = parseFloat(total_amt)
            formData.discount = parseFloat(discount)
            $('.cartdiv .cart-items .cart-list-items').each(function(k, v){
                let amt = $(this).find('.ttl_price').find('.rate').attr('data-rate');
                let tax = $(this).find('.ttl_price').find('.rate').attr('data-tax');
                let qty1 = $(this).find('.ttl_price').find('.item_qty').val();
                items_list.push({
                    "name": $(this).attr('data-item-code'),
                    "quantity": parseInt(qty1),
                    "rate": parseFloat(amt),
                    "tax": parseFloat(tax)
                })
            })
            formData.items_list = items_list
            frappe.call({
                method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.page.order.order.inserOrder',
                args: {
                    doc: JSON.stringify(formData)
                },
                callback: function(r) {
                    if (r.message) {
                        cur_dialog.hide();
                        frappe.show_alert(__("Order Inserted !"));
                        $('#page-order .cartdiv .cart-items').find('.cart-list-items').remove();
                        $('.empty-state').show();
                        $('.cartdiv .grand-total-value').text("0.00");
                        $('.cartdiv .grand-tax-value').text("0.00");
                        $('.cartdiv .total-value').text("0.00");
                        $('.cartdiv .grand-discount-value').text("0.00");
                        $('#hdnDiscount').val(0)
                        $('.cartdiv .quantity-total').text(0);
                    }
                }
            })
        }
    })
    dialog.show();
}

function chooseCustomer(){
    let title = __('Select Customer');
    var dialog = new frappe.ui.Dialog({
        title: __(title),
        fields: [{ "fieldtype": "Link", "fieldname": "customer", "label": __("Customer"), "reqd": 1, "options":"Customers",
        "onchange": function () {
                let val = this.get_value();
                if (val) {
                    frappe.call({
                        method: 'frappe.client.get_value',
                        args: {
                            'doctype': "Customers",
                            'filters': { 'name': val },
                            'fieldname': "first_name"
                        },
                        callback: function (r) {
                            if (r.message) {
                                customer_name = r.message.first_name
                                dialog.fields_dict.customer_name.set_value(customer_name);
                            }
                        }
                    })
                }
            }
        },
        { "fieldtype": "Data", "fieldname": "customer_name", "label": __("Customer Name"), "read_only": 1}
        ]
    })
    dialog.set_primary_action(__('Save'), function() {
        var values = dialog.get_values();
        $('#customerName').val(values.customer)
        $('.cartdiv .customer-field1 .customerName').text(values.customer_name);
        dialog.hide();
    })
    dialog.show();
}

function openDiscount(){
    let title = __('Discounts');
    var dialog = new frappe.ui.Dialog({
        title: __(title),
        fields: [{ "fieldtype": "Int", "fieldname": "discount_amount", "label": __("Enter Discount Amount")}
        ]
    })
    dialog.set_primary_action(__('Save'), function() {
        var values = dialog.get_values();
        $('#hdnDiscount').val(values.discount_amount);
        $('.cartdiv .grand-discount-value').text(values.discount_amount.toFixed(2));
        var tot_amt = $('.cartdiv .total-value').text();
        var tot_amount = parseFloat(tot_amt) - values.discount_amount
        $('.cartdiv .total-value').text(tot_amount.toFixed(2));
        $('.cartdiv .apply_discount').hide();
        $('.cartdiv .remove_discount').show();
        dialog.hide();
    })
    dialog.show();
}

function removeDiscount(){
    $('.cartdiv .apply_discount').show();
    $('.cartdiv .remove_discount').hide();
    $('#hdnDiscount').val(0);
    var discount = $('.cartdiv .grand-discount-value').text();
    var tot_amt = $('.cartdiv .grand-total-value').text();
    var tot_tax = $('.cartdiv .grand-tax-value').text();
    var tot_amount = parseFloat(tot_amt) + parseFloat(tot_tax)
    $('.cartdiv .total-value').text(tot_amount.toFixed(2));
    $('.cartdiv .grand-discount-value').text("0.00");
}