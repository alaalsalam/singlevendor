frappe.pages['razor-pay-payments'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Razor Pay Payments',
    single_column: true
  });
    $('.page-content').find('.layout-main').append(frappe.render_template("razor_pay_payments"));
    $('.page-content').find('.layout-main').prepend('<div class="formlist"></div>')
}

var changedRows=[];
var dt;
frappe.pages['razor-pay-payments'].refresh = function(wrapper) {
    var date = new Date();         

    date.setDate(date.getDate()+5);
  
        $('.page-title .title-text').text('Razor Pay Payments')
   
   frappe.call({
                method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_all_razorpay_order',
                args: {},
                callback: function(r) {
                    console.log(r.message.length)
                    if(r.message.length>0){
                     dt= new DataTable('#listing', {
                    
  columns: [
  { name: 'Transaction Id',width: 1,editable:false },
  { name: 'Order Date',width: 1,editable:false },
  { name: 'Order Id',width: 1,editable:false   },
  { name: 'Order Total',width: 1,editable:false   },
  { name: 'Settlement Amount',width: 1,editable:false   },
  { name: 'Customer Name',width: 1,editable:false,align:"left" },
  { name: 'Refund Payments',width: 1,editable:false,align:"left" ,
  format: value => {if(value != 1 && value != '') {return `<button class="btn-primary" onclick="payment_refund('${value}')">Refund</button>`} else {return `<button class="btn-primary" onclick="payment_refund('${value}')" disabled>Refunded</button>`}  } },
 
   ],

   
  data:r.message,
  inlineFilters: true,
  layout:'ratio',
  noDataMessage:"No Data Found",
  dropdownButton: '▼',
  sortIndicator: {
        asc: '↑',
        desc: '↓',
        none: ''
    },

    events: {
        onRemoveColumn(column) {
          console.log(column.id)
        },
        onSwitchColumn(column1, column2) {},
        onSortColumn(column) {},
        onCheckRow(row) {}
    },
});
                   }
                   else{
                    var html = "No Records found!"
                    $('#listing').html(html)
                   }
                },
            });


}

function payment_refund(order_id){
  frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.create_payment_refund',
        args: {
          order_id:order_id
        },
        callback: function(r) {
          console.log(r.message)
          if(r.message){
             frappe.msgprint("Success")
             cur_frm.set_value('payment_status','Paid');
            cur_frm.save_or_update();
          }
          }
        });
}
