var isAlreadyClick = 0;
var totalQuickCash = 0;
var page_no=1;
var page_len=30;
var scroll=true;
$('.slimScrollBar').scroll(function(){
    console.log("---1")
})
$('.slimScrollDiv').scroll(function(){
    console.log("---2")
})
var $scrollable = $('.slimScrollDiv');
$scrollable.slimScroll().bind('slimscrolling', function (e, pos) {
    console.log("---0")
 
});
$(document).scroll(function(){
    if(scroll==true){
        page_no=page_no+1;
        scroll=false;
        $.ajax({
            type: 'POST',
            Accept: 'application/json',
            ContentType: 'application/json;charset=utf-8',
            url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.sale.api.get_productlist_scroll',
            data: {'page_no':page_no,'page_len':page_len},
            dataType: "json",
            async: false,
            headers:{
                'X-Frappe-CSRF-Token':'{{csrf_token}}'
            },
            success: function(data){
                if(data.message){
                    var html='';
                    scroll=true;
                    $(data.message).each(function(i,items){
                     
                     html+='<div class="col-md-3 col-sm-4 col-xs-6 border-s cartitems" style="padding:0"><div><div class="productitem" onclick="addtoCart(this)">'

                     html+='<a class="cartincr" data-attr="'+items.name+'" style="cursor:pointer" data-title="'+items.item+'" data-price="'+items.price+'" data-stock="'+items.stock+'" data-tax="'+items.tax_category+'" data-inventory="'+items.inventory_method+'" data-maxcount="'+items.maximum_order_qty+'" data-mincount="'+items.minimum_order_qty+'"><div class="itemImage">'
                                  
                                      if (items.images){
                                        html+='<img src="'+items.images[0].product_image+'" style="width: 100%;height: 150px;object-fit: contain;">'
                                      }
                                       else{ 
                                       html+='<img src="/assets/cmswebsite/images/no-image-800x511.png" style="width: 100%;height: 150px;object-fit: contain;">'
                                             
                                       }
                                       
                                  html+='</div> <div class="producttitle"><span class="producttitle_overflow">'+items.item+'</span><br><span class="price-1">₹'+items.price+'</span></div>'
                                 
                                 if (items.inventory_method != "Dont Track Inventory"){
                                  if(items.stock <= 0 ){
                                    html+='<span class="itemprice">Out of stock</span>'
                                  }
                                 }
                                 html+='<span class="addicon"><i class="lni-plus" aria-hidden="true"></i></span></a>'
                                  
                              if (items.addons){
                                html+='<div class="addons" data-addon="true">'
                                $(items.addons).each(function(i,addon){
                                  html+='<div><h3 style="margin: 10px 0px;"><strong>'+addon.attribute_unique_name+':</strong></h3></div><div style="padding-left: 15px" class="form_group" data-addonid="'+addon.product_attribute+'" data-item_id="'+items.name+'">'
                                  if (addon.options){
                                    $( addon.options).each(function(i,options){
                                      html+='<input type="radio" name="'+addon.product_attribute+'" value="'+options.name+'" data-optionval="'+options.option_value+'" data-optionprice="'+options.price_adjustment+'">'+options.option_value+' - ₹'+options.price_adjustment+'<br>'
                                    })
                                  }
                                  html+='</div>'
                                  
                                })
                                html+=' </div>'
                              }else{
                                html+='<div class="addons" data-addon="false"></div>'
                              }    
                         html+='</div></div></div>'
                    })
                    $('.rightCart').append(html)
                    
                    if ($('.rightCart .cartitems').length > 8) {
                      $('.rightCart').slimScroll({
                          height: ($(window).height() - 217)
                      })
                  }
                }else{
                    scroll=false;
                }
            }
        })
    }
    
})
$(document).scroll(function(){
    console.log("----122")
    if(scroll==true){
        page_no=page_no+1;
        scroll=false;
        $.ajax({
            type: 'POST',
            Accept: 'application/json',
            ContentType: 'application/json;charset=utf-8',
            url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.sale.api.get_productlist_scroll',
            data: {'page_no':page_no,'page_len':page_len},
            dataType: "json",
            async: false,
            headers:{
                'X-Frappe-CSRF-Token':'{{csrf_token}}'
            },
            success: function(data){
                if(data.message){
                    var html='';
                    scroll=true;
                    $(data.message).each(function(i,items){
                     
                     html+='<div class="col-md-3 col-sm-4 col-xs-6 border-s cartitems" style="padding:0"><div><div class="productitem" onclick="addtoCart(this)">'

                     html+='<a class="cartincr" data-attr="'+items.name+'" style="cursor:pointer" data-title="'+items.item+'" data-price="'+items.price+'" data-stock="'+items.stock+'" data-tax="'+items.tax_category+'" data-inventory="'+items.inventory_method+'" data-maxcount="'+items.maximum_order_qty+'" data-mincount="'+items.minimum_order_qty+'"><div class="itemImage">'
                                  
                                      if (items.images){
                                        html+='<img src="'+items.images[0].product_image+'" style="width: 100%;height: 150px;object-fit: contain;">'
                                      }
                                       else{ 
                                       html+='<img src="/assets/cmswebsite/images/no-image-800x511.png" style="width: 100%;height: 150px;object-fit: contain;">'
                                             
                                       }
                                       
                                  html+='</div> <div class="producttitle"><span class="producttitle_overflow">'+items.item+'</span><br><span class="price-1">₹'+items.price+'</span></div>'
                                 
                                 if (items.inventory_method != "Dont Track Inventory"){
                                  if(items.stock <= 0 ){
                                    html+='<span class="itemprice">Out of stock</span>'
                                  }
                                 }
                                 html+='<span class="addicon"><i class="lni-plus" aria-hidden="true"></i></span></a>'
                                  
                              if (items.addons){
                                html+='<div class="addons" data-addon="true">'
                                $(items.addons).each(function(i,addon){
                                  html+='<div><h3 style="margin: 10px 0px;"><strong>'+addon.attribute_unique_name+':</strong></h3></div><div style="padding-left: 15px" class="form_group" data-addonid="'+addon.product_attribute+'" data-item_id="'+items.name+'">'
                                  if (addon.options){
                                    $( addon.options).each(function(i,options){
                                      html+='<input type="radio" name="'+addon.product_attribute+'" value="'+options.name+'" data-optionval="'+options.option_value+'" data-optionprice="'+options.price_adjustment+'">'+options.option_value+' - ₹'+options.price_adjustment+'<br>'
                                    })
                                  }
                                  html+='</div>'
                                  
                                })
                                html+=' </div>'
                              }else{
                                html+='<div class="addons" data-addon="false"></div>'
                              }    
                         html+='</div></div></div>'
                    })
                    $('.rightCart').append(html)
                    
                    if ($('.rightCart .cartitems').length > 8) {
                      $('.rightCart').slimScroll({
                          height: ($(window).height() - 217)
                      })
                  }
                }else{
                    scroll=false;
                }
            }
        })
    }
})
$('.admin_icon').click(function(){
   window.location.href=window.location.origin + '/desk';
})


$(document).ready(function() {
  
    GetCustomerBalance()
    get_all_table()
    get_all_floor()
    get_allorder_ids()
    get_holdorder_List()
    $(function(){
    if($(window).width() < 768) {
        $("#quickpay-btns").removeClass("btn-group-vertical");
    }
    if($(window).width() > 768) {
        $("#quickpay-btns").addClass("btn-group-vertical");
    }
    $("#side_panel").slimScroll({
      size: '8px', 
      width: '100%', 
      height: 'calc(100% - 54px)', 
      color: '#ff4800', 
      allowPageScroll: true, 
      alwaysVisible: true     
    });
    $(".panel-body").slimScroll({
      size: '8px', 
      width: '56%', 
      height: 'calc(100% - 54px)', 
      color: '#ff4800', 
      allowPageScroll: true, 
      alwaysVisible: true     
    });

    $('#amount_1').keyup(function () {
            if($("#amount_1").val() != ""){
                totalQuickCash=(parseFloat($("#amount_1").val()));
            }
            else{
                totalQuickCash=0;
            }
            
            var tobePaid = parseFloat($("#quick-payable").text().split("₹")[1]);
            $("#total_paying").text("₹" + parseFloat(totalQuickCash).toFixed(2));
            $("#balance").text("₹" +((totalQuickCash - tobePaid).toFixed(2)));
    });
  });

});
var toggle = 0;
var Table_list=[];
var floors=[];
var ordertype="";

var ToggleCartView = function(){
   
    if (toggle == 0){
        $(".leftCart").css({"display": "block"});
        $(".panel-body").css({"display": "none"});
        $(".panel-body-header").css({"display": "none"});
        $(".pannel-heading-side").css({"display": "none"});
        toggle = 1;
    }
    else{
        $(".leftCart").css({"display": "none"});
        $(".panel-body").css({"display": "block"});
        $(".panel-body-header").css({"display": "block"});
        $(".pannel-heading-side").css({"display": "block"});
        toggle = 0;
    }
}
var merge_toggle = 0
var ToggleMergeView = function(){
    if (merge_toggle == 0){
        $(".merge_order_detail").css({"display": "block"});
        $(".merge_order_list").css({"display": "none"});
        merge_toggle = 1;
    }
    else{
        $(".merge_order_detail").css({"display": "none"});
        $(".merge_order_list").css({"display": "block"});
        merge_toggle = 0;
    }
}
var split_toggle = 0
var ToggleSplitView = function(){
    if (split_toggle == 0){
        $(".split_order_cards").css({"display": "block"});
        $(".split_order_items").css({"display": "none"});
        split_toggle = 1;
    }
    else{
        $(".split_order_cards").css({"display": "none"});
        $(".split_order_items").css({"display": "block"});
        split_toggle = 0;
    }
}
var totalItems = 0
var totalAmount = 0;
var gst = 0;
var customer_details;
var GetCustomerBalance = function(){
    var customer_id = $('.customer_email').text()
    if( customer_id) { 
    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_customer_info',
        args: {
            email:customer_id
        },
        async:false,
        callback: function(data){
            if (data.message){
                customer_details=data.message[0];
            }
        }
    })
    frappe.call({
                        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.GetCustomerBalance',
                        args: {
                            name:customer_id
                        },
                        async:false,
                        callback: function(data){
                            var previous_bal = data.message[0];
                            var balAmount = previous_bal.balance;
                            $("#AvailBalance").text("₹ "+balAmount); 

                    }
                })
}
    
}

function holdedOrdersModel(){
            $("#HoldOrdersModel").modal("show");
        }

function mergeOrdersModel(){
            $("#holdorderdiv").css("display","none");
            $("#posmergeorders").html('');
            $("#MergeNo").text(0);                                        
            temp_mergeList = [];
            $("#MergeOrdersModel").modal("show");
            var html = '<tr class="no-data"><td colspan="6">No records found</td></tr>';
            $("#mergeOrderItems").html(html);
            get_all_PosCart()
        }

function splitOrdersModel(){
            $("#holdorderdiv").css("display","none");
            $("#possplitorders").html('');
            $("#HoldOrdersModel").modal("hide");
            $("#splitOrdersModel").modal("show");
            get_all_PosCart();
}

function shippingAddressModel(){
            $("#ShippingAddressModel").modal("show")
}

function TableReservationModel(){
            $("#TableReservationModel").modal("show")
}

function cancelTableReservation(){
    $(".table_details").css("display","none");
    $("#TableReservationModel").modal("hide");
    $("#DineIn_table").text("Dine in");
    Table_list=[];
    get_all_table();
    floors=[];
    ordertype="";
    table_id ="";
    order_type('');
    $(".tablelist .col-md-4").each(function () {
                        var title = $(this).find(".tabledetail").attr("data-tablocation");

                            $(this).hide();

                    });

            $(".tablelist .col-sm-3").each(function () {
                        var title = $(this).find(".tabledetail").attr("data-tablocation");
                        
                            $(this).hide();

                    });

            $(".tablelist .col-xs-6").each(function () {
                        var title = $(this).find(".tabledetail").attr("data-tablocation");

                            $(this).hide();

                    });
}

var order_ids;
var get_allorder_ids = function(){
    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_AllOrderId',
        args: {
        },
        async:false,
        callback: function(data){
            if (data.message){
                $("#allorderid").html('');
                var order_ids = [];
                    order_ids = data.message
                    for(i=0; i<order_ids.length; i++){
                        var ord_id = order_ids[i];
                    var html='<a class="list-group-item" id ="'+ord_id+'" onclick="get_returnorder_items($(this))" style="margin: 0px; border-radius: 0px; border-width: 0px 0px 1px; border-style: solid; border-bottom-color: rgb(222, 222, 222); border-image: initial; border-top-color: initial; border-right-color: initial; padding-left: 30px; border-left-color: initial;">'+ ord_id +'</a>'
                        $("#allorderid").append(html);

                    }
                   
            }
        }
    })
}

function get_all_PosCart(){
                $.ajax({
                        type: 'POST',
                        Accept: 'application/json',
                        ContentType: 'application/json;charset=utf-8',
                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_all_PosCart',
                        data: {
                            name:hold_order_id
                        },
                        dataType: "json",
                        async: false,
                        headers:{
                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                        },
                        success: function(data){
                            if(data){
                                for (i = 0; i < data.message.length; i++){
                                    var cart_id= data.message[i].name;
                                    var cus_name = data.message[i].customer_name;
                                    var cus_id = data.message[i].customer;
                                    var no_items = data.message[i].items.length;
                                    var total = data.message[i].total;
                                    var html='<div id="mc-'+cart_id+'" onclick="addto_mergelist($(this))" class="col-md-4 col-sm-6" style="padding: 10px"><div class="card" style="width: 100%;"><ul id="ul-'+cart_id+'" class="list-group list-group-flush" style="margin-bottom: 0px !important;border: 3px solid transparent;border-radius: 12px !important;"><li class="list-group-item" style=" border-top-left-radius: 8px !important; border-top-right-radius: 8px !important;"><b>'+cart_id+'</b></li><li class="list-group-item">Name:<span class="merge_card_items">'+cus_name+'</span></li><li class="list-group-item">Cus_Id:<span class="merge_card_items">'+cus_id+'</span></li><li class="list-group-item">No.Items:<span class="merge_card_items">'+no_items+'</span></li><li class="list-group-item" style=" border-bottom-left-radius: 8px !important; border-bottom-right-radius: 8px !important;">Total:<span class="merge_card_items">'+total+'</span></li></ul></div></div>';
                                    $("#posmergeorders").append(html);
                                    var html2='<div id="spc-'+cart_id+'" class="col-md-4 col-sm-6" style="padding: 10px"><div class="card" style="width: 100%;"><ul id="ul-'+cart_id+'" class="list-group list-group-flush" style="margin-bottom: 0px !important;border: 3px solid transparent;border-radius: 12px !important;"><li class="list-group-item" style=" border-top-left-radius: 8px !important; border-top-right-radius: 8px !important;"><b>'+cart_id+'</b></li><li class="list-group-item">Name:<span class="merge_card_items">'+cus_name+'</span></li><li class="list-group-item">Cus_Id:<span class="merge_card_items">'+cus_id+'</span></li><li class="list-group-item">No.Items:<span class="merge_card_items">'+no_items+'</span></li><li class="list-group-item">Total:<span class="merge_card_items">'+total+'</span></li><li class="list-group-item" style=" border-bottom-left-radius: 8px !important; border-bottom-right-radius: 8px !important;text-align: center;"><span><button type="button" class="btn btn-success" style="width:40%; border-top-right-radius: 0px; border-bottom-right-radius: 0px;" data-dismiss="modal" id="'+cart_id+'" onclick="checkout_poscart($(this))"><i class="lni-cart-full" style="padding: 0px 10px;"aria-hidden="true"></i>Checkout</button><button type="button" class="btn btn-primary" style="width:40%; border-top-left-radius: 0px; border-bottom-left-radius: 0px;" id="split-'+cart_id+'" onclick="split_order_modal($(this))">Split Order</button></span></li></ul></div></div>';
                                    $("#possplitorders").append(html2);      
                                    }
                            }
                    }
                })
}
var merge_order_items=[]
var merge_order_CusId='';
var merge_order_tax = 0;
var merge_order_total = 0;
var temp_mergeList = [];

var addto_mergelist = function(e){
    merge_order_tax = 0;
    merge_order_total = 0;
    var temp_id =e.attr("id").split('mc-')[1];
    if(jQuery.inArray(temp_id, temp_mergeList) == -1){
        $("#mergeOrderItems").html('');
        temp_mergeList.push(temp_id);
        $('#ul-'+temp_id).css("border","3px solid orange");
        $("#MergeNo").text(temp_mergeList.length);
        $.each(temp_mergeList, function( index, value ) {
            insert_mergeorder_items(value);
        });
    }
    else{
        $("#mergeOrderItems").html('');
        temp_mergeList.splice( $.inArray(temp_id, temp_mergeList), 1 );
        $('#ul-'+temp_id).css("border","3px solid transparent");
        $("#MergeNo").text(temp_mergeList.length);
        if(temp_mergeList.length > 0){
            $.each(temp_mergeList, function( index, value ) {
                insert_mergeorder_items(value);
            });
        }
        else{
            var html = '<tr class="no-data"><td colspan="6">No records found</td></tr>';
            $("#mergeOrderItems").html(html);
        }
    }
}

function insert_mergeorder_items(name){
    var temp_id = name;
                $.ajax({
                        type: 'POST',
                        Accept: 'application/json',
                        ContentType: 'application/json;charset=utf-8',
                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_holdorderitems',
                        data: {
                            name:temp_id
                        },
                        dataType: "json",
                        async: false,
                        headers:{
                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                        },
                        success: function(data){
                            if(data){
                                merge_order_items=[];        
                                if(data.message){
                                    merge_order_items = data.message[0].order_item;
                                    for (i = 0; i < merge_order_items.length; i++){
                                        var producttitle = merge_order_items[i].product_name;
                                        var price = parseFloat(merge_order_items[i].price).toFixed(2);
                                        var tot_qty = merge_order_items[i].quantity;
                                        var id = merge_order_items[i].product;
                                        var product_tax= merge_order_items[i].tax;
                                        var tot_price = parseFloat(merge_order_items[i].total).toFixed(2);
                                        if ($("#mtr-" + id).length == 0) {
                                        var html = 
                                        '<tr id="mtr-' + id + '"><td style="width: 70%; text-align:left;">' + producttitle + '</td><td style="width: 10%; text-align:center;">₹' + price + '</td><td style="width: 10%; text-align:center;""><input type="text" removeClass="holdQtyLbl" style="width: 30px; height: 15px; margin: 5px;text-align: center;" value="'+tot_qty+'" id="'+id+'"  readonly/><div style="display: none" class="holdTaxLib">'+product_tax+'</div></td><td  style="width: 10%; text-align:center;">₹' + tot_price  + '</td></tr>';
                                        $("#mergeOrderItems").append(html);
                                        }
                                        else{
                                            var new_qty = parseInt($("#mtr-" + id).find("td:eq(2)").find("input").val()) + parseInt(tot_qty);
                                            var new_product_tax = (parseFloat($("#mtr-" + id).find("td:eq(2)").find(".holdTaxLib").text()) + parseFloat(product_tax)).toFixed(2);
                                            var new_tot_price = (parseFloat($("#mtr-" + id).find("td:eq(3)").text().split("₹")[1]) + parseFloat(tot_price)).toFixed(2);
                                            $("#mtr-" + id).find("td:eq(2)").find("input").val(new_qty);
                                            $("#mtr-" + id).find("td:eq(2)").find(".holdTaxLib").text(new_product_tax);
                                            $("#mtr-" + id).find("td:eq(3)").text("₹"+new_tot_price)
                                        }

                                        } 
                                        $("#mergeOrderItems tr").each(function () {
                                            merge_order_tax = (parseFloat(merge_order_tax)+parseFloat($(this).find("td:eq(2)").find(".holdTaxLib").text())).toFixed(2);
                                        });

                                }
                                else{
                                    var html = '<tr class="no-data"><td colspan="6">No records found</td></tr>'
                                    $("#mergeOrderItems").append(html);
                                }
                            }                                                       
                    }
                })
}

function mergeOrder(){
    if(temp_mergeList.length > 1){
                var merge_cus_id=$("#mergeCustomer").val();
                var products = [];
                hold_order_id='';
                $("#mergeOrderItems tr").each(function () {
                    var product = {};
                    product.item = $(this).attr("id").split('mtr-')[1];
                    product.price = $(this).find("td:eq(1)").text().split("₹")[1];
                    product.quantity = $(this).find("td:eq(2)").find("input").val();
                    product.item_total = $(this).find("td:eq(3)").text().split("₹")[1];
                    product.tax = parseFloat($(this).find("td:eq(2)").find(".holdTaxLib").text()).toFixed(2);
                    products.push(product);
                });
                frappe.call({
                        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.posHoldOrder',
                        args: {
                            cus_id: merge_cus_id,
                            amount: 0,
                            tax: merge_order_tax,
                            items : products,
                            hold_Id: hold_order_id
                        },
                        async:false,
                    callback: function (data) {
                        if (data.message == true) {
                            hold_order_id='';
                            merge_order_items=[]
                            merge_order_CusId='';
                            merge_order_tax = 0;
                            merge_order_total = 0;
                            
                            $.each(temp_mergeList, function( index, value ) {
                                delete_POScartOrders(value);
                                get_holdorder_List();
                            });
                            alert("Merge orders completed!")
                            setTimeout(function(){ temp_mergeList=[] }, 2000);

                        }
                    }

                });
                $("#MergeOrdersModel").modal("hide");
            }
            else{
                alert("Select 2 or more orders to merge!");
            }
        }

function delete_POScartOrders(id){
                $.ajax({
                                    type: 'POST',
                                    Accept: 'application/json',
                                    ContentType: 'application/json;charset=utf-8',
                                    url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.delete_poscart',
                                    data: {
                                        name:id
                                    },
                                    dataType: "json",
                                    async: false,
                                    headers:{
                                        'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                    },
                                    success: function(data){
                                        get_holdorder_List();
                                }
                            })
        }
var splits_count = 0;
var splits_avl=[];
var SplitOrderId="";
var active_split_card="";
var active_split_cus="";
function split_order_modal(e){
    $("#active_split_card").text("");
    $("#active_split_cus").text("");
    splits_count=0;
    var id =(e.attr("id")).split("split-")[1];
    SplitOrderId = id;
    $("#splitModel").modal("show");
    $("#SplitOrderId").text(id);
    $("#Noofsplits").html('');
    splits_avl=[];
    $.ajax({
                        type: 'POST',
                        Accept: 'application/json',
                        ContentType: 'application/json;charset=utf-8',
                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_holdorderitems',
                        data: {
                            name:id
                        },
                        dataType: "json",
                        async: false,
                        headers:{
                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                        },
                        success: function(data){
                            if(data){                            
                                if(data.message){
                                    $(".splitorderitems").html('');
                                    var split_order_items = data.message[0].order_item;
                                    for (i = 0; i < split_order_items.length; i++){
                                        var producttitle = split_order_items[i].product_name;
                                        var price = parseFloat(split_order_items[i].price).toFixed(2);
                                        var tot_qty = parseInt(split_order_items[i].quantity);
                                        var id = split_order_items[i].product;
                                        var product_tax= split_order_items[i].tax;
                                        var tot_price = parseFloat(split_order_items[i].total).toFixed(2);
                                        var html = '<li class="list-group-item" style="height: 40px !important;line-height: 20px;"><span style="float: left;">'+producttitle+'</span><span style="float: right;text-align: right;width: 10%;"><button type="button" class="btn .btn-link" style="height: 20px;line-height: 10px;text-align: center;padding: 0px 10px 0px 10px;" data-attr="'+id+'" data-title="'+producttitle+'" data-price="'+price+'" onclick="addto_splits($(this))">+</button></span><span style="float: right;width: 15%;text-align: center;" id="SPI-'+id+'">x'+tot_qty+'</span></li>';
                                        $(".splitorderitems").append(html);
                                        splits_count += tot_qty; 
                                    
                                        } 
                                }
                            }                                                       
                    }
                })
    for(i=1; i<=splits_count; i++){
        splits_avl.push({"value":i});
    }
    for(i=0; i<splits_avl.length; i++){
        var html='<option value="'+splits_avl[i].value+'">'+splits_avl[i].value+'</option>'
        $("#Noofsplits").append(html);
    }
    no_of_splits();
}

var split_count=1;
function no_of_splits(){
    split_count=$("#Noofsplits").val();
    $("#splitOrdermain").html('');
    for(i=1; i<=split_count; i++){
        var html='<div class="col-md-6 col-sm-12" style="padding: 0px;" id="splitCard'+i+'" onclick="activeSplitCard($(this))"><div id="splitcardinner'+i+'" style="min-height: 200px;border: 2px solid #DDD;border-radius: 8px; overflow: hidden;position: relative;display: block;margin: 15px"><div style="float:left;width:100%;text-align:center;margin-top: 0; top: 0px; left: 0px;"><h5 style="text-align: left;margin: 0px 10px">Select customer:</h5><div  class="customer_select" style="text-align: left">{% if customers %}<select id="splitCustomer'+i+'" name="splitCustomer'+i+'" style="margin-left: 0px;width: 100%;margin: 10px;width: 60%">{% for item in customers %}<option value="{{item.name}}">{{item.full_name}}</option>{% endfor %}</select>{% endif %}</div><div style="padding: 0px 5px; width: 100%;"><table class="table table-striped table-bordered"><tbody id="splitItems'+i+'"></tbody></table></div></div></div></div>'
        $("#splitOrdermain").append(html);
    
    }
    $.ajax({
                        type: 'POST',
                        Accept: 'application/json',
                        ContentType: 'application/json;charset=utf-8',
                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_holdorderitems',
                        data: {
                            name:SplitOrderId
                        },
                        dataType: "json",
                        async: false,
                        headers:{
                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                        },
                        success: function(data){
                            if(data){                      
                                if(data.message){
                                    $(".splitorderitems").html('');
                                    var split_order_items = data.message[0].order_item;
                                    for (i = 0; i < split_order_items.length; i++){
                                        var producttitle = split_order_items[i].product_name;
                                        var price = parseFloat(split_order_items[i].price).toFixed(2);
                                        var tot_qty = parseInt(split_order_items[i].quantity);
                                        var id = split_order_items[i].product;
                                        var product_tax= split_order_items[i].tax;
                                        var tot_price = parseFloat(split_order_items[i].total).toFixed(2);
                                        var html = '<li class="list-group-item" style="height: 40px !important;line-height: 20px;"><span style="float: left;display: block; width: 75% !important;overflow: hidden;text-overflow: ellipsis;">'+producttitle+'</span><span style="float: right;text-align: right;width: 10%;"><button type="button" class="btn .btn-link" style="height: 20px;line-height: 10px;text-align: center;padding: 0px 10px 0px 10px;" data-attr="'+id+'" data-title="'+producttitle+'" data-price="'+price+'" onclick="addto_splits($(this))">+</button></span><span style="float: right;width: 15%;text-align: center;" id="SPI-'+id+'" class="tot_avl_qty">x'+tot_qty+'</span></li>'
                                        $(".splitorderitems").append(html);
                                        splits_count += tot_qty; 
                                        } 
                                }
                            }                                                       
                    }
                })
}

function activeSplitCard(e){
    active_split_card=e.attr("id")
    $("#active_split_card").text(active_split_card);
    var split_id=(e.attr("id")).split("splitCard")[1];
    active_split_cus=$("#splitCustomer"+split_id+" :selected").text();
    $("#active_split_cus").text(active_split_cus);
    for(i=1; i<=split_count; i++){
        if(i != split_id){
            $("#splitcardinner"+i).css("border","2px solid #DDD");
            $("#splitcardinner"+i).find("tr").find("a").css("pointer-events", "none");
        }
        if(i == split_id){
            $("#splitcardinner"+i).css("border","2px solid orange");         
            $("#splitcardinner"+i).find("tr").find("a").css("pointer-events", "auto");
        }
    }
}


function addto_splits(e){
    var tax="";
    var product_tax="";
    var item_id = e.attr("data-attr");
    var item_title = e.attr("data-title");
    var item_price = e.attr("data-price");
    var avl_qty = parseInt($("#SPI-"+item_id).text().split("x")[1])
    if(active_split_card != ""){
        var id=active_split_card.split("splitCard")[1];
        if(avl_qty){
            if ($("#spc"+id+"-" + item_id).length == 0) {
                var new_avl_qty = avl_qty - 1;
                var tot_price = parseFloat(item_price).toFixed(2);
                var html ='<tr id="spc'+id+'-' + item_id + '"><td>' + item_title + '</td><td>₹' + item_price + '</td><td style="width:20%" style="text-align: center"><input type="text" class="QtyLbl" style="width: 34px; height: 15px;border:none;background:transparent;text-align:center;" value="x1" id="'+item_id+'" readonly/><div style="display: none" class="TaxLib">'+product_tax+'</div><div style="display: none" class="TaxTemplate">'+tax+'</div></td><td>₹' + tot_price + '</td><td><a style="color:#000;cursor:pointer" id="'+item_id+'" onClick="reduce_split_itmqty($(this))"><i class="fa fa-minus"></i></a></td></tr>';
                $("#splitItems"+id).append(html);
                $("#SPI-"+item_id).text("x"+new_avl_qty)                                       
            }
            else{
                var new_avl_qty = avl_qty - 1;
                var new_qty = parseInt($("#spc"+id+"-" + item_id).find("td:eq(2)").find("input").val().split("x")[1]) + 1;
                var new_tot_price = parseFloat(item_price*parseInt(new_qty)).toFixed(2);
                $("#spc"+id+"-" + item_id).find("td:eq(2)").find("input").val("x"+new_qty);
                $("#spc"+id+"-" + item_id).find("td:eq(3)").text("₹"+new_tot_price);
                $("#SPI-"+item_id).text("x"+new_avl_qty)
            }
        }
        else{
            alert("No more items to split!");
        }
    }
    else{
       alert("Please select the split part to add item!"); 
    }
}

function reduce_split_itmqty(e){
    var item_id = e.attr("id");
    
    var avl_qty = parseInt($("#SPI-"+item_id).text().split("x")[1])
    var id=active_split_card.split("splitCard")[1];
                var item_price = parseFloat($("#spc"+id+"-" + item_id).find("td:eq(1)").text().split("₹")[1]).toFixed(2);
               
                var new_avl_qty = avl_qty + 1;
                var new_qty = parseInt($("#spc"+id+"-" + item_id).find("td:eq(2)").find("input").val().split("x")[1]) - 1;
                var new_tot_price = parseFloat(item_price*parseInt(new_qty)).toFixed(2);
                if (new_qty >0){  
                    $("#spc"+id+"-" + item_id).find("td:eq(2)").find("input").val("x"+new_qty);
                    $("#spc"+id+"-" + item_id).find("td:eq(3)").text("₹"+new_tot_price);
                    $("#SPI-"+item_id).text("x"+new_avl_qty)
                }
                else{
                    $("#spc"+id+"-" + item_id).remove();
                    $("#SPI-"+item_id).text("x"+new_avl_qty);
                }

}
function check_splitOrder(){
    var check = false;
    for(i=1; i<=split_count; i++){
        var row = $("#splitItems"+i+" tr").length;
        if(row>0){
            var check =true;
        }
        else{
            var check = false;
            $("#splitcardinner"+i).css("border","2px solid red");
            $(".split_order_cards").css({"display": "block"});
            $(".split_order_items").css({"display": "none"});
        }
    }
    if(check){
        splitOrder();
    }
    else{
        alert("Some order cards are still not yet assigned!. Make sure you assign all the available items to available split carts");
    }
}

function splitOrder(){
    var productsCount = 0;
    $("#SplitOrderItems li").each(function () {
                            productsCount =parseInt(productsCount) + parseInt($(this).find(".tot_avl_qty").text().split("x")[1]);
                        });
    if( productsCount == 0 ){
        $("#splitModel").modal("hide")
        $("#splitOrdersModel").modal("hide");
        for(i=1; i<=split_count; i++){
                    var split_cus_id=$("#splitCustomer"+i).val();
                    var products = [];
                    hold_order_id='';
                    $("#splitItems"+i+" tr").each(function () {
                        var product = {};
                        product.item = $(this).attr("id").split('spc'+i+'-')[1];
                        product.price = $(this).find("td:eq(1)").text().split("₹")[1];
                        product.quantity = $(this).find("td:eq(2)").find("input").val().split("x")[1];
                        product.item_total = $(this).find("td:eq(3)").text().split("₹")[1];
                        products.push(product);
                    });
                    frappe.call({
                            method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.posHoldOrder',
                            args: {
                                cus_id: split_cus_id,
                                amount: 0,
                                tax: 0,
                                items : products,
                                hold_Id: ''
                            },
                            async:false,
                        callback: function (data) {
                            if (data) {
                                
                            }
                            
                        }

                    });
                    if(i == split_count){
                                    delete_POScartOrders(SplitOrderId)
                                    alert("Split order completed!")
                                }
                }
        }
        else{
            alert("Some order items are still not yet assigned!. Make sure you assign all the available items to available split carts");
            $(".split_order_cards").css({"display": "block"});
            $(".split_order_items").css({"display": "none"});
        }
    }


var holdorder_ids;
var get_holdorder_List = function(){
    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_HoldOrderList',
        args: {
        },
        async:false,
        callback: function(data){
            if (data.message){
                $("#searchholdOrder").html('');
                $(".hold_label").text(data.message.length);
                for (i = 0; i < data.message.length; i++){
                    var cus_name = data.message[i].label;
                    var ord_id = data.message[i].value;
                    var html='<a class="list-group-item" id ="'+ord_id+'"onclick="get_holdorder_items($(this))" style="margin: 0px; border-radius: 0px; border-width: 0px 0px 1px; border-style: solid; border-bottom-color: rgb(222, 222, 222); border-image: initial; border-top-color: initial; border-right-color: initial; padding-left: 30px; border-left-color: initial;">'+ cus_name+' - '+ ord_id +'</a>'
                    $("#searchholdOrder").append(html);
                    
                }
            }
        }
    })
}

var hold_order_items=[]
var hold_order_CusId='';
var hold_order_id='';
function get_holdorder_items(e){
    $("#holdorderdiv").css("display","block");
    $(".PosCartList").css("display","none");
    $(".PosCartDetail").css("display","block");
    hold_order_id =e.attr("id");
                $.ajax({
                        type: 'POST',
                        Accept: 'application/json',
                        ContentType: 'application/json;charset=utf-8',
                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_holdorderitems',
                        data: {
                            name:hold_order_id
                        },
                        dataType: "json",
                        async: false,
                        headers:{
                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                        },
                        success: function(data){
                            if(data){
                                hold_order_items=[];
                                $("#holdproductsbody").html('');                                
                                if(data.message){
                                    hold_order_items   = data.message[0].order_item;
                                    hold_order_CusId   = data.message[0].customer;
                                    hold_order_CusName = data.message[0].customer_name;
                                    hold_order_Id      = data.message[0].name;
                                    hold_order_Amount  = data.message[0].total;
                                    var detailshtml='<div class="col-md-6 col-sm-12 hold_OrderDetails_Left"><h4 class="modal-title" style="font-size: 14px;"><span><b>Customer Name: </b></span><span>'+hold_order_CusName+'</span></h4><h4 class="modal-title" style="font-size: 14px;"><span><b>Customer ID: </b></span><span>'+hold_order_CusId+'</span></h4></div><div class="col-md-6 col-sm-12 hold_OrderDetails_Right"><h4 class="modal-title" style="font-size: 14px;"><span><b>Cart ID: </b></span><span>'+hold_order_Id+'</span></h4><h4 class="modal-title" style="font-size: 14px;"><span><b>Total:</b></span><span>'+hold_order_Amount+'</span></h4></div>'
                                        $("#hold_OrderDetails").html(detailshtml);
                                    for (i = 0; i < hold_order_items.length; i++){
                                        var producttitle = hold_order_items[i].product_name;
                                        var price = parseFloat(hold_order_items[i].price).toFixed(2);
                                        var tot_qty = hold_order_items[i].quantity;
                                        var id = hold_order_items[i].product;
                                        var product_tax= hold_order_items[i].tax;
                                        var tot_price = parseFloat(hold_order_items[i].total).toFixed(2);
                                        var html = 
                                        '<tr id="tr-' + id + '"><td style="width: 70%; text-align:left;">' + producttitle + '</td><td style="width: 10%; text-align:center;">₹' + price + '</td><td style="width: 10%; text-align:center;""><input type="text" removeClass="holdQtyLbl" style="width: 40px; height: 20px; margin: 5px;text-align: center;" value="'+tot_qty+'" id="'+id+'"  readonly/><div style="display: none" class="holdTaxLib">'+product_tax+'</div></td><td  style="width: 10%; text-align:center;">₹' + tot_price  + '</td></tr>';
                                        $("#holdproductsbody").append(html);
                                        } 
                                }
                                else{
                                    var html = '<tr class="no-data"><td colspan="6">No records found</td></tr>'
                                    $("#holdproductsbody").append(html);
                                }
                            }                                                       
                    }
                })
}
function insert_holdorder_items(){
    
    $("#holdorderdiv").css("display","none");
    $(".leftCart").css({"display": "block"});
        $(".panel-body").css({"display": "none"});
        $(".panel-body-header").css({"display": "none"});
        $(".pannel-heading-side").css({"display": "none"});
        toggle = 1;
    var checkStock= true;
    $("#autocomplete").val(hold_order_CusId);
   $(".CartList").html('');
    
    for (i = 0; i < hold_order_items.length; i++){
                                        var tax="";
                                        var producttitle = hold_order_items[i].product_name;
                                        var price = parseFloat(hold_order_items[i].price).toFixed(2);
                                        var tot_qty = hold_order_items[i].quantity;
                                        var id = hold_order_items[i].product;
                                        var product_tax= hold_order_items[i].tax;
                                        var tot_price = parseFloat(hold_order_items[i].total).toFixed(2);
   var html = '<li style="margin: 5px;" data-row="1" data-id="'+id+'" class="CartItem clearfix" data-discount="None" data-discount-amt="" data-discount-percent="" data-type="1" data-price="'+ price +'" data-title="'+producttitle+'" data-service="" data-addons="">'               
   html +='<span class="serviceTitle"><img src="" style="height:10px;margin-right: 5px;display:none">'                
  html +='<span class="CartQty" style="float:right"><div style="display: none" class="TaxLib">'+product_tax+'</div><div style="display: none" class="TaxTemplate">'+tax+'</div><a id="'+id+'" onclick="DecrementQty($(this))" style="margin-right:5px;margin-left:0;cursor:pointer;">-</a> '               
  html +='<span class="QtyLbl" id="'+id+'">'+ tot_qty +'</span><a id="'+id+'" onclick="IncrementQty($(this))" style="margin-left:5px;cursor:pointer;">+</a></span>'+producttitle+'</span>'
  html +='<a class="CartDelete" id="'+id+'" onclick="deleteCartItem($(this))" style="font-size: 18px;">  '              
 html +='<i class="fa fa-trash-o" style="cursor:pointer"></i></a>'
 html +='<span style="float:right;font-size: 17px;" class="CartAmount">$'+ tot_price +'</span>'       
                            html +='</ul>'
                            $(".CartList").append(html);
                                       }
                                        if (checkStock) {
                                            var productsCount = 0;
                                            var productsTotal = 0;
                                            gst = 0;
                                             $(".CartList li").each(function () {
                                                productsCount += parseInt($(this).find(".QtyLbl").text());
                                                productsTotal += parseFloat($(this).find(".CartAmount").text().split("$")[1]);
                                                gst += parseFloat($(this).find(".TaxLib").text());
                                                
                                            });
                                           
                                            totalItems += 1;
                                            totalAmount += parseFloat(price);
                                            $("#titems").text(productsCount);
                                            $(".cart_label").text(productsCount);
                                            $("#total").text("₹" + productsTotal.toFixed(2));
                                            $("#tax").text("₹" + gst.toFixed(2));
                                            $("#gtotal").text("₹" + ( gst + productsTotal).toFixed(2));
                                            $("#item_count").text(productsCount);
                                            $("#twt").text("₹" + ( gst + productsTotal).toFixed(2));
                                            $("#quick-payable").text("₹" + ( gst + productsTotal).toFixed(2));
                                            $("#quick-payable").attr("data-value", ( gst + productsTotal).toFixed(2));
                                        } 
                                        setTimeout(function(){ $("#holdproductsbody").html(''); }, 50);
}

function clearHoldordermodel(){
    $("#holdproductsbody").html('');
    $("#holdorderdiv").css("display","none");
    $(".PosCartDetail").css("display","none");
    $(".PosCartList").css("display","block");
    hold_order_CusId='';
    hold_order_id='';
}

function checkout_poscart(e){
    var id =e.attr("id");
    hold_order_id = id;
    $.ajax({
                        type: 'POST',
                        Accept: 'application/json',
                        ContentType: 'application/json;charset=utf-8',
                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_holdorderitems',
                        data: {
                            name:id
                        },
                        dataType: "json",
                        async: false,
                        headers:{
                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                        },
                        success: function(data){
                            if(data){                              
                                if(data.message){
                                    var order_items   = data.message[0].order_item;
                                    var order_CusId   = data.message[0].customer;
                            
    var checkStock= true;
    $("#Customer").val(order_CusId);
    $("#productsbody").html('');
    for (i = 0; i < order_items.length; i++){
                                        var tax="";
                                        var producttitle = order_items[i].product_name;
                                        var price = parseFloat(order_items[i].price).toFixed(2);
                                        var tot_qty = order_items[i].quantity;
                                        var id = order_items[i].product;
                                        var product_tax= order_items[i].tax;
                                        var tot_price = parseFloat(order_items[i].total).toFixed(2);
                                        var html = 
                                        '<tr id="tr-' + id + '"><td>' + producttitle + '<div class="addonoptions"></div></td><td>₹' + price + '</td><td style="width:20% text-align: center;" style="text-align: center"><a class="qtyDecr"><i class="lni-minus" aria-hidden="true" id="'+id+'" onclick="DecrementQty($(this))"></i></a><input type="text" class="QtyLbl" style="width: 34px; height: 28px; margin: 5px;" value="'+ tot_qty +'" id="'+id+'" onkeyup="QtyKeyUp($(this))"/><div style="display: none" class="TaxLib">'+product_tax+'</div><div style="display: none" class="TaxTemplate">'+tax+'</div><a class="qtyIncr" id="'+id+'"  onclick="IncrementQty($(this))"><i class="lni-plus" aria-hidden="true"></i></a></td><td>₹' + tot_price + '</td><td><a style="color:#000;cursor:pointer" id="'+id+'" onclick="deleteCartItem($(this))"><i class="lni-close"></i></a></td></tr>';
                                        $("#productsbody").append(html);
                                        }
                                        
                                        if (checkStock) {
                                            var productsCount = 0;
                                            var productsTotal = 0;
                                            gst = 0;
                                            $("#productsbody tr").each(function () {
                                                productsCount += parseInt($(this).find(".QtyLbl").val());
                                                productsTotal += parseFloat($(this).find("td:eq(3)").text().split("₹")[1]);
                                                gst += parseFloat($(this).find("td:eq(2)").find(".TaxLib").text());
                                                
                                            });
                                            totalItems += 1;
                                            totalAmount += parseFloat(price);
                                            $("#titems").text(productsCount);
                                            $(".cart_label").text(productsCount);
                                            $("#total").text("₹" + productsTotal.toFixed(2));
                                            $("#tax").text("₹" + gst.toFixed(2));
                                            $("#gtotal").text("₹" + ( gst + productsTotal).toFixed(2));
                                            $("#item_count").text(productsCount);
                                            $("#twt").text("₹" + ( gst + productsTotal).toFixed(2));
                                            $("#quick-payable").text("₹" + ( gst + productsTotal).toFixed(2));
                                            $("#quick-payable").attr("data-value", ( gst + productsTotal).toFixed(2));
                                            $(".leftCart").css({"display": "block"});
                                            $(".panel-body").css({"display": "none"});
                                            $(".panel-body-header").css({"display": "none"});
                                            $(".pannel-heading-side").css({"display": "none"});
                                            toggle = 1;
                                        } 
                                        }
                            }                                                       
                    }
                })
}

function returnRequest(){
            $("#ReturnRequestModel").modal("show");
            $(".returnList").css("display","block");
            $(".returnDetail").css("display","none");
        }

var order_items=[]
function get_returnorder_items(e){
    var order_id=e.attr("id");
    $(".returnList").css("display","none");
    $(".returnDetail").css("display","block");
    $("#orderidlabel").html(order_id)
                $.ajax({
                        type: 'POST',
                        Accept: 'application/json',
                        ContentType: 'application/json;charset=utf-8',
                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_orderitems',
                        data: {
                            name:order_id
                        },
                        dataType: "json",
                        async: false,
                        headers:{
                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                        },
                        success: function(data){
                            var defhtml = ''
                            $("#returnitemsbody").html(defhtml);                                
                            if(data.message){
                                var rtrn_cusId = data.message[0].customer;
                                order_items = data.message[0].order_item;
                                for (i = 0; i < order_items.length; i++){
                                    var name = order_items[i].item;
                                    var item_name = order_items[i].item_name;
                                    var price = parseFloat(order_items[i].price).toFixed(2);
                                    var tot_qty = order_items[i].quantity;
                                    var rtrn_qty = 0;
                                    var html = 
                                    '<tr id="tr-'+order_items[i].name+'"><td colspan="3" id="'+order_items[i].name+'" style="text-align: left; width: 60%;">'+item_name+'<div style="display: none" class="ProductId">'+name+'</div><div style="display: none" class="rtrnCusId">'+rtrn_cusId+'</div></td><td id="'+order_items[i].name+'" style="text-align: center; width: 15%;">₹'+price+'</td><td id="'+order_items[i].name+'" style="width: 10%;text-align: center">'+tot_qty+'</div></td><td id="'+order_items[i].name+'" style="width: 15%;text-align: center"><input style="width: 45px; height: 28px; margin: 5px;" type="number" min="0" max="'+tot_qty+'" onKeyUp="maxReturnQty($(this))" id="'+order_items[i].name+'"  class="rtrnQtyLbl" value="' + rtrn_qty + '"/></td></tr>'
                                    $("#returnitemsbody").append(html);
                                   } 
                            }
                            else{
                                var html = '<tr class="no-data"><td colspan="6">No records found</td></tr>'
                                $("#returnitemsbody").append(html);
                            }
                    }
                })
}

function maxReturnQty(e){
    var id =e.attr("id");
    var qty=$("#tr-" + id).find("td:eq(3)").find(".rtrnQtyLbl").val();
    var max_qty=$("#tr-" + id).find("td:eq(2)").text();
    if(qty > max_qty){
        $("#tr-" + id).find("td:eq(3)").find(".rtrnQtyLbl").val(max_qty);
    } 
    else if (qty < 0) {
      $("#tr-" + id).find("td:eq(3)").find(".rtrnQtyLbl").val(0);   
    }

}

function clearReturnRqst(){
    $('#searchOrder').val('');
    $("#returnitemsbody").html('');
    $('#comments').val('');
    $(".returnList").css("display","block");
    $(".returnDetail").css("display","none");

}

function insertReturnRequest(){
   
    $("#returnitemsbody tr").each(function () {
        console.log("---------")
                    var Order_Id = $('#orderidlabel').text()
                    var product = $(this).find("td:eq(0)").find(".ProductId").text();
                    var return_cus_id = $(this).find("td:eq(0)").find(".rtrnCusId").text();
                    var quantity = $(this).find("td:eq(3)").find(".rtrnQtyLbl").val();
                    var reason = $('#returnReason').val();
                    var comment = $('#comments').val();
                    if(quantity > 0 && quantity != ''){
                             $.ajax({
                                type: 'POST',
                                Accept: 'application/json',
                                ContentType: 'application/json;charset=utf-8',
                                url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.sale.api.insert_ReturnRequest',
                                data: {
                                    order_id:Order_Id,
                                    product:product,
                                    quantity:quantity,
                                    reason:reason,
                                    comments:comment,
                                    customer:return_cus_id
                                },
                                dataType: "json",
                                async: false,
                                headers:{
                                    'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                },
                                success: function(data){
                                   if(data.message == "success"){
                                        clearReturnRqst()
                                    }
                                   
                            }
                        })
                       
                    }
                });
}

var addon_options = [];
function get_Addon_values(){
    $("#variantBody .form_group").each(function () {
        var addonid = $(this).attr("data-addonid");
        var itemid = $(this).attr("data-item_id");
        $("#tr-"+itemid).find("td:eq(0)").find(".addonoptions").html("")
        var options = $("input[name='"+addonid+"']:checked").val();
        var optionname = $("input[name='"+addonid+"']:checked").attr("data-optionval");
        var optionprice = $("input[name='"+addonid+"']:checked").attr("data-optionprice");
        addon_options.push({"option_name":optionname, "option_price":optionprice, "addon_id":addonid, "addon_options":options, "item_id":itemid});
        });
    if(addon_options.length != 0){
        for(i=0; i<addon_options.length;i++){
            var product_price = parseFloat($("#tr-" +addon_options[i].item_id).find("td:eq(3)").text().split("₹")[1])
            var addon_price = parseFloat(addon_options[i].option_price);
            var optionshtml='<span data-addonid="'+addon_options[i].addon_id+'" data-optionid="'+addon_options[i].addon_options+'" data-option="'+addon_options[i].option_name+'" data-optionprice="'+addon_options[i].option_price+'" style="font-size:10px; color:grey"><br>'+addon_options[i].option_name+' - ₹'+addon_options[i].option_price+'</span>'
            var new_price = parseFloat(product_price+addon_price).toFixed(2)
            $("#tr-" + addon_options[i].item_id).find("td:eq(0)").find(".addonoptions").append(optionshtml)
            $("#tr-" + addon_options[i].item_id).find("td:eq(1)").text("₹"+new_price)
            $("#tr-" + addon_options[i].item_id).find("td:eq(3)").text("₹"+new_price)
        }
    }
}

function addtoCart(element)
{
    var checkStock = true;
    var id = $(element).find(".cartincr").attr("data-attr");
    var producttitle = $(element).find(".cartincr").attr("data-title");
    var productprice = $(element).find(".cartincr").attr("data-price");
    var stock = parseInt($(element).find(".cartincr").attr("data-stock"));
    var min_count = parseInt($(element).find(".cartincr").attr("data-mincount"));
    var max_count = parseInt($(element).find(".cartincr").attr("data-maxcount"));
    var inventory_method = ($(element).find(".cartincr").attr("data-inventory"));
    var tax = $(element).find(".cartincr").attr("data-tax");
    var addons = $(element).find(".addons").attr("data-addon");
    var addons_innerhtml= $(element).find(".addons").html();
    var tax_rate = 0;
    var product_tax = 0;
    var ord_qty = 1;
    if(inventory_method != "Dont Track Inventory"){
        ord_qty = min_count;
    }

console.log("---------addcartitem")
   if ($(".CartItem[data-id=" + id + "]").length == 0) {
   
       if (stock > 0 || inventory_method == "Dont Track Inventory") {
           if (tax != "" && tax != "None"){
                    $.ajax({
                        type: 'POST',
                        Accept: 'application/json',
                        ContentType: 'application/json;charset=utf-8',
                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_Products_Tax_Template',
                        data: {
                            name:tax
                        },
                        dataType: "json",
                        async: false,
                        headers:{
                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                        },
                        success: function(data){
                            var tax_rates=data.message[0].tax_rate
                            
                            for (i = 0; i < tax_rates.length; i++) { 
                              tax_rate += tax_rates[i].rate ;
                            }
                            product_tax = (parseFloat(productprice * (tax_rate/100))).toFixed(2);
                    }
                })
           }
           else{
            tax=""
           }

           var html = '<li style="margin: 5px;" data-row="1" data-id="'+id+'" class="CartItem clearfix" data-discount="None" data-discount-amt="" data-discount-percent="" data-type="1" data-price="'+ $(".cartincr[data-attr=" + id + "]").attr("data-price") +'" data-title="'+producttitle+'" data-service="" data-addons="">'               
           html +='<span class="serviceTitle"><img src="" style="height:10px;margin-right: 5px;display:none">'                
           html +='<span class="CartQty" style="float:right"><div style="display: none" class="TaxLib">'+product_tax+'</div><div style="display: none" class="TaxTemplate">'+tax+'</div><a id="'+id+'" onclick="DecrementQty($(this))" style="margin-right:5px;margin-left:0;cursor:pointer;">-</a> '               
           html +='<span class="QtyLbl" id="'+id+'">'+ord_qty+'</span><a id="'+id+'" onclick="IncrementQty($(this))" style="margin-left:5px;cursor:pointer;">+</a></span>'+producttitle+'</span>'
           html +='<a class="CartDelete" id="'+id+'" onclick="deleteCartItem($(this))" style="font-size: 18px;">  '              
           html +='<i class="fa fa-trash-o" style="cursor:pointer"></i></a>'
           html +='<span style="font-size: 17px;" class="CartAmount">$'+ $(".cartincr[data-attr=" + id + "]").attr("data-price") +'</span>'       
           html +='</ul>'
           $(".CartList").append(html);
            
                    }
                    else {
                        alert("Stock is not available for this product.");
                        
                    }
   }
   else {

                var newQty = parseInt($(".CartItem[data-id=" + id + "]").find(".QtyLbl").text()) + 1;
                if (stock >= newQty || inventory_method == "Dont Track Inventory") {
                    if( newQty <= max_count || inventory_method == "Dont Track Inventory"){
                    var newPrice = (parseFloat($(".CartItem[data-id=" + id + "]").find(".CartAmount").text().split("$")[1]) + parseFloat($(".CartItem[data-id=" + id + "]").find(".CartAmount").text().split("$")[1])).toFixed(2);

                    if (tax != "" && tax != "None"){
                        
                                $.ajax({
                                    type: 'POST',
                                    Accept: 'application/json',
                                    ContentType: 'application/json;charset=utf-8',
                                    url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_Products_Tax_Template',
                                    data: {
                                        name:tax
                                    },
                                    dataType: "json",
                                    async: false,
                                    headers:{
                                        'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                    },
                                    success: function(data){
                                        var tax_rates=data.message[0].tax_rate
                                        for (i = 0; i < tax_rates.length; i++) { 
                                          tax_rate += tax_rates[i].rate ;
                                        }
                                        product_tax = (parseFloat(newPrice * (tax_rate/100))).toFixed(2);
                                  
                                }
                            })
                       }
                       else{
                        tax=""
                       }
                       $(".CartItem[data-id=" + id + "]").find('.CartQty').html('<div style="display: none" class="TaxLib">'+tax+'</div><div style="display: none" class="TaxTemplate">'+product_tax+'</div><a id="'+id+'" onclick="DecrementQty($(this))" style="margin-right:5px;margin-left:0;cursor:pointer;">-</a><span class="QtyLbl" id="'+id+'">'+newQty+'</span><a id="'+id+'" onclick="IncrementQty($(this))" style="margin-left:5px;cursor:pointer;">+</a>')
                       $(".CartItem[data-id=" + id + "]").find('.CartAmount').text("$" + newPrice);
                    
                    }
                    else {
                        alert("The max order count for this product is : " + max_count);
                        checkStock = false;
                    }
                }
                else {
                    alert("The available stock for this product is : " + stock);
                    checkStock = false;
                }
            }

            if (checkStock) {
                var productsCount = 0;
                var productsTotal = 0;
                gst = 0;
                $(".CartList li").each(function () {
                    
                    productsCount += parseInt($(this).find(".QtyLbl").text());
                    productsTotal += parseFloat($(this).find(".CartAmount").text().split("$")[1]);
                    gst += parseFloat($(this).find(".TaxLib").text());
              
                });
                totalItems += 1;
                totalAmount += parseFloat(productprice);
                $("#titems").text(productsCount);
                $(".cart_label").text(productsCount);
                $("#total").text("₹" + productsTotal.toFixed(2));
                $("#tax").text("₹" + gst.toFixed(2));
                $("#gtotal").text("₹" + ( gst + productsTotal).toFixed(2));
                $("#item_count").text(productsCount);
                $("#twt").text("₹" + ( gst + productsTotal).toFixed(2));
                $("#quick-payable").text("₹" + ( gst + productsTotal).toFixed(2));
                $("#quick-payable").attr("data-value", ( gst + productsTotal).toFixed(2));
            }
        }


function QtyKeyUp(e) {
    var id =e.attr("id")
            if ($.isNumeric($("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val())) {
                if (!($("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val().indexOf("-") > -1)) {
                    var checkStock = true;
                    var producttitle = $(".cartincr[data-attr=" + id + "]").attr("data-title");
                    var productprice = $(".cartincr[data-attr=" + id + "]").attr("data-price");0
                    var stock = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-stock"));
                    var min_count = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-mincount"));
                    var max_count = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-maxcount"));
                    var inventory_method = ($(".cartincr[data-attr=" + id + "]").attr("data-inventory"));
                    var tax = $(".cartincr[data-attr=" + id + "]").attr("data-tax");
                    var tax_rate = 0;
                    var product_tax = 0;
                    var ord_qty = 1;
                    if(inventory_method != "Dont Track Inventory"){
                        ord_qty = min_count;
                    }

                    if ($("#tr-" + id).length == 0) {
                        if (stock > 0 || inventory_method == "Dont Track Inventory") {
                            var appendhtml = '<tr id="tr-' + id + '"><td>' + producttitle + '<div class="addonoptions"></div></td><td>₹' + $(".cartincr[data-attr=" + id + "]").attr("data-price") + '</td><td style="width:20%; text-align: center;" style="text-align: center"><a class="qtyDecr"><i class="lni-minus" aria-hidden="true" id="'+id+'" onclick="DecrementQty($(this))""></i></a><input style="width: 34px; height: 28px; margin: 5px;" type="text" type="text" class="QtyLbl" value="'+ord_qty+'" id="'+id+'" onkeyup="QtyKeyUp($(this))"/><div style="display: none" class="TaxLib">'+product_tax+'</div><div style="display: none" class="TaxTemplate">'+tax+'</div><a class="qtyIncr" id="'+id+'"  onclick="IncrementQty($(this))"><i class="lni-plus" aria-hidden="true"></i></a></td><td>₹' + $(".cartincr[data-attr=" + id + "]").attr("data-price") + '</td><td><a style="color:#000;cursor:pointer" onclick="deleteCartItem(' + id + ')"><i class="lni-close"></i></a></td></tr>';
                            $("#productsbody").append(appendhtml);
                        }
                        else {
                            alert("Stock is not available for this product.");
                            checkStock = false;
                        }

                    }
                    else {

                        var newQty = parseInt($("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val());
                        if (stock >= newQty || inventory_method == "Dont Track Inventory") {
                            if( newQty <= max_count && newQty >= min_count || inventory_method == "Dont Track Inventory"){                           
                            var newPrice = (parseFloat($("#tr-" + id).find("td:eq(1)").text().split("₹")[1]) * parseFloat(newQty)).toFixed(2);

                            if (tax != "" && tax != "None"){
                                
                                        $.ajax({
                                            type: 'POST',
                                            Accept: 'application/json',
                                            ContentType: 'application/json;charset=utf-8',
                                            url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_Products_Tax_Template',
                                            data: {
                                                name:tax
                                            },
                                            dataType: "json",
                                            async: false,
                                            headers:{
                                                'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                            },
                                            success: function(data){
                                                var tax_rates=data.message[0].tax_rate
                                               
                                                
                                                for (i = 0; i < tax_rates.length; i++) { 
                                                  tax_rate += tax_rates[i].rate ;
                                                }
                                                product_tax = (parseFloat(newPrice * (tax_rate/100))).toFixed(2);
                                               
                                        }
                                    })
                               }
                               else{
                                    tax=""
                                   }
                            $("#tr-" + id).find("td:eq(2)").html('<a class="qtyDecr" id="'+id+'" onclick="DecrementQty($(this))""><i class="lni-minus" aria-hidden="true"></i></a><input style="width: 25px; height: 25px; margin: 5px;" type="text" type="text" id="'+id+'" onkeyup="QtyKeyUp($(this))"  class="QtyLbl" value="' + newQty + '"/><div style="display: none" class="TaxLib">'+product_tax+'</div><div style="display: none" class="TaxTemplate">'+tax+'</div><a class="qtyIncr" id="'+id+'"  onclick="IncrementQty($(this))"><i class="lni-plus" aria-hidden="true"></i></a>');
                            $("#tr-" + id).find("td:eq(3)").text("₹" + newPrice);
                            }
                            else {
                                alert("The min & max order count for this product is : " + min_count+","+ max_count);
                                if(newQty > max_count){
                                    $("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val(max_count);
                                }
                                if(newQty < min_count){
                                    $("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val(min_count);
                                }
                                checkStock = false;
                            }
                        }
                        else {
                            alert("The available stock for this product is : " + stock);
                            checkStock = false;
                        }
                    }
                    if (checkStock) {
                        var productsCount = 0;
                        var productsTotal = 0;
                        gst = 0;
                        $("#productsbody tr").each(function () {
                            productsCount += parseInt($(this).find(".QtyLbl").val());
                            productsTotal += parseFloat($(this).find("td:eq(3)").text().split("₹")[1]);
                            gst += parseFloat($(this).find("td:eq(2)").find(".TaxLib").text());
                        });
                        totalItems += 1;
                        totalAmount += parseFloat(productprice);
                        $("#titems").text(productsCount);
                        $(".cart_label").text(productsCount);
                        $("#total").text("₹" + productsTotal.toFixed(2));
                        $("#tax").text("₹" + gst.toFixed(2));
                        $("#gtotal").text("₹" + ( gst + productsTotal).toFixed(2));
                        $("#item_count").text(productsCount);
                        $("#twt").text("₹" + ( gst + productsTotal).toFixed(2));
                        $("#quick-payable").text("₹" + productsTotal.toFixed(2));
                        $("#quick-payable").attr("data-value", productsTotal.toFixed(2));
                    }
                    isAlreadyClick = 0;
                    scrollingDiv();
                    var el = $("#tr-" + id).find("td:eq(2)").find(".QtyLbl").get(0);
                    var elemLen = el.value.length;
                    el.selectionStart = elemLen;
                    el.selectionEnd = elemLen;
                    el.focus();
                }
                else
                {
                    var value = $("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val().replace(/-/g, '');
                    $("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val(value);
                }
            }
            else {
                var value = $("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val().replace(/([a-zA-Z])/g, "");
                $("#tr-" + id).find("td:eq(2)").find(".QtyLbl").val(value);
            }
        }

function deleteCartItem(e) {
  var id =e.attr("id")
          var re = confirm("Are you sure want to remove?");
          if (re) {
              var productprice = $(".CartItem[data-id=" + id + "]").attr("data-price") 
              var productRate = parseFloat(productprice);
              var selectedQty = parseInt($(".CartItem[data-id=" + id + "]").find(".QtyLbl").text());
              var availbalance = parseFloat($("#AvailBalance").text().split("₹")[1]);
              var customerBalance = $("#hdnCustomerBalance").val();
              totalItems = totalItems - selectedQty;
                          totalAmount = totalAmount - parseFloat(productprice.split("₹")[1]);
                         
                          $(".CartItem[data-id=" + id + "]").remove();
                          var productsCount = 0;
                          var productsTotal = 0;
                          var totalPayable = 0;
                          gst = 0;
                          $(".CartList li").each(function () {

                              productsCount += parseInt($(this).find(".QtyLbl").text());
                              productsTotal += parseFloat( $(this).attr("data-price"));
                              gst += parseFloat($(this).find(".TaxLib").text());
                          });
                          totalItems += 1;
                          totalAmount += parseFloat(productprice);
                          if (customerBalance >= productsTotal) {
                              availbalance = customerBalance - productsTotal;
                          }
                          else {
                              availbalance = 0;
                              totalPayable = productsTotal - customerBalance;
                          }
                          $("#titems").text(productsCount);
                          $(".cart_label").text(productsCount);
                          $("#total").text("₹" + productsTotal.toFixed(2));
                          $("#tax").text("₹" + gst.toFixed(2));
                          $("#gtotal").text("₹" + ( gst + productsTotal).toFixed(2));
                          $("#item_count").text(productsCount);
                          $("#twt").text("₹" + ( gst + productsTotal).toFixed(2));
                          $("#quick-payable").text("₹" + productsTotal.toFixed(2));
                          $("#quick-payable").attr("data-value", productsTotal.toFixed(2));
                     

          }
      }

function IncrementQty(e){
    var id =e.attr("id")
            var checkStock = true;
            var producttitle = $(".cartincr[data-attr=" + id + "]").attr("data-title");
            var productprice = $(".cartincr[data-attr=" + id + "]").attr("data-price");
            var stock = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-stock"));
            var min_count = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-mincount"));
            var max_count = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-maxcount"));
            var inventory_method = ($(".cartincr[data-attr=" + id + "]").attr("data-inventory"));
            var availbalance = parseFloat($("#AvailBalance").text().split("₹")[1]);
            var tax = $(".cartincr[data-attr=" + id + "]").attr("data-tax");
            var tax_rate = 0;
            var product_tax = 0;
            var ord_qty = 1;
          ord_qty = min_count;
                     
          if ($(".CartItem[data-id=" + id + "]").length == 0) {
              if (stock > 0 || inventory_method == "Dont Track Inventory") {
                var html = '<li style="margin: 5px;" data-row="1" data-id="'+id+'" class="CartItem clearfix" data-discount="None" data-discount-amt="" data-discount-percent="" data-type="1" data-price="'+ $(".cartincr[data-attr=" + id + "]").attr("data-price") +'" data-title="'+producttitle+'" data-service="" data-addons="">'               
                html +='<span class="serviceTitle"><img src="" style="height:10px;margin-right: 5px;display:nonedisplay:none">'                
                html +='<span class="CartQty" style="float:right"><div style="display: none" class="TaxLib">'+tax+'</div><div style="display: none" class="TaxTemplate">'+product_tax+'</div><a id="'+id+'" onclick="DecrementQty($(this))" style="margin-right:5px;margin-left:0;cursor:pointer;">-</a> '               
                html +='<span class="QtyLbl" id="'+id+'">1</span><a id="'+id+'" onclick="IncrementQty($(this))" style="margin-left:5px;cursor:pointer;">+</a></span>'+producttitle+'</span>'
                html +='<a class="CartDelete" id="'+id+'" onclick="deleteCartItem($(this))" style="font-size: 18px;">  '              
                html +='<i class="fa fa-trash-o" style="cursor:pointer"></i></a>'
                html +='<span style="float:right;font-size: 17px;" class="CartAmount">$'+ $(".cartincr[data-attr=" + id + "]").attr("data-price") +'</span>'       
                html +='</ul>'
                $(".CartList").append(html);
              
              }
              else {
                  alert("Stock is not available for this product.");
                  checkStock = false;
              }

          }
          else {

              var newQty = parseInt($(".CartItem[data-id=" + id + "]").find(".QtyLbl").text()) + 1;
                if (stock >= newQty ) {
                  if( newQty <= max_count){
                  
                  var newPrice = (parseFloat($(".CartItem[data-id=" + id + "]").find('.CartAmount').text().split("$")[1]) + parseFloat($(".CartItem[data-id=" + id + "]").attr('data-price'))).toFixed(2);

                  if (tax != "" && tax != "None"){
                     
                              $.ajax({
                                  type: 'POST',
                                  Accept: 'application/json',
                                  ContentType: 'application/json;charset=utf-8',
                                  url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_Products_Tax_Template',
                                  data: {
                                      name:tax
                                  },
                                  dataType: "json",
                                  async: false,
                                  headers:{
                                      'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                  },
                                  success: function(data){
                                      var tax_rates=data.message[0].tax_rate
                                     
                                      
                                      for (i = 0; i < tax_rates.length; i++) { 
                                        tax_rate += tax_rates[i].rate ;
                                      }
                                      product_tax = (parseFloat(newPrice * (tax_rate/100))).toFixed(2);
                                     
                              }
                          })
                     }
                     else{
                      tax=""
                     }
                    
                     $(".CartItem[data-id=" + id + "]").find('.CartQty').html('<div style="display: none" class="TaxLib">'+product_tax+'</div><div style="display: none" class="TaxTemplate">'+tax+'</div><a id="'+id+'" onclick="DecrementQty($(this))" style="margin-right:5px;margin-left:0;cursor:pointer;">-</a><span class="QtyLbl" id="'+id+'">'+newQty+'</span><a id="'+id+'" onclick="IncrementQty($(this))" style="margin-left:5px;cursor:pointer;">+</a>')
                    $(".CartItem[data-id=" + id + "]").find('.CartAmount').text("$" + newPrice);
                  
                      }
                      else {
                          alert("The max order count for this product is : " + max_count);
                          checkStock = false;
                      }
              }
              else {
                  alert("The available stock for this product is : " + stock);
                  checkStock = false;
              }
          }
          if (checkStock) {
              var productsCount = 0;
              var productsTotal = 0;
              var totalPayable = 0;
              gst = 0;
              var customerBalance = $("#hdnCustomerBalance").val();
              $(".CartList li").each(function () {
                  productsCount += parseInt($(this).find(".QtyLbl").text());
                  productsTotal += parseFloat($(this).find(".CartAmount").text().split("$")[1]);
                  gst += parseFloat($(this).find(".TaxLib").text());
              });
              if (customerBalance >= productsTotal) {
                  availbalance = customerBalance - productsTotal;
              }
              else {
                  availbalance = 0;
                  totalPayable = productsTotal - customerBalance;
              }
              totalItems += 1;
              totalAmount += parseFloat(productprice);
              $("#titems").text(productsCount);
              $(".cart_label").text(productsCount);
              $("#total").text("₹" + productsTotal.toFixed(2));
              $("#tax").text("₹" + gst.toFixed(2));
              $("#gtotal").text("₹" + ( gst + productsTotal).toFixed(2));
              $("#item_count").text(productsCount);
              $("#twt").text("₹" + ( gst + productsTotal).toFixed(2));
              $("#quick-payable").text("₹" + productsTotal.toFixed(2));
              $("#quick-payable").attr("data-value", productsTotal.toFixed(2));
          }
          isAlreadyClick = 0;
      }

function DecrementQty(e){
            var id =e.attr("id")
            var checkStock = true;
            var producttitle = $(".cartincr[data-attr=" + id + "]").attr("data-title");
            var productprice = $(".cartincr[data-attr=" + id + "]").attr("data-price");
            var stock = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-stock"));
            var min_count = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-mincount"));
            var max_count = parseInt($(".cartincr[data-attr=" + id + "]").attr("data-maxcount"));
            var inventory_method = ($(".cartincr[data-attr=" + id + "]").attr("data-inventory"));
            var availbalance = parseFloat($("#AvailBalance").text().split("₹")[1]);
            var customerBalance = $("#hdnCustomerBalance").val();
            var tax = $(".cartincr[data-attr=" + id + "]").attr("data-tax");
            var tax_rate = 0; 
            var product_tax = 0;
            var ord_qty = 1;
            ord_qty = min_count;
                    if ($(".CartItem[data-id=" + id + "]").length == 0) {
               
                if (stock > 0 || inventory_method == "Dont Track Inventory") {
                    var html = '<li style="margin: 5px;" data-row="1" data-id="'+id+'" class="CartItem clearfix" data-discount="None" data-discount-amt="" data-discount-percent="" data-type="1" data-price="'+ $(".cartincr[data-attr=" + id + "]").attr("data-price") +'" data-title="'+producttitle+'" data-service="" data-addons="">'               
                    html +='<span class="serviceTitle"><img src="" style="height:10px;margin-right: 5px;display:none">'                
                    html +='<span class="CartQty" style="float:right"><div style="display: none" class="TaxLib">'+tax+'</div><div style="display: none" class="TaxTemplate">'+product_tax+'</div><a id="'+id+'" onclick="DecrementQty($(this))" style="margin-right:5px;margin-left:0;cursor:pointer;">-</a> '               
                    html +='<span class="QtyLbl" id="'+id+'">1</span><a id="'+id+'" onclick="IncrementQty($(this))" style="margin-left:5px;cursor:pointer;">+</a></span>'+producttitle+'</span>'
                    html +='<a class="CartDelete" id="'+id+'" onclick="deleteCartItem($(this))" style="font-size: 18px;">  '              
                    html +='<i class="fa fa-trash-o" style="cursor:pointer"></i></a>'
                    html +='<span style="float:right;font-size: 17px;" class="CartAmount">$'+ $(".cartincr[data-attr=" + id + "]").attr("data-price") +'</span>'       
                    html +='</ul>'
                    $(".CartList").append(html);
                 
                }
                else {

                    alert("Stock is not available for this product.");
                    checkStock = false;
                }
            }
            else {
                var newQty = parseInt($(".CartItem[data-id=" + id + "]").find(".QtyLbl").text()) - 1;
                if (newQty != 0) {
                   
                    if (stock >= newQty || inventory_method == "Dont Track Inventory") {
                        if( newQty >= min_count ){
                        var newPrice = (parseFloat($(".CartItem[data-id=" + id + "]").find(".CartAmount").text().split("$")[1]) - parseFloat($(".CartItem[data-id=" + id + "]").attr("data-price"))).toFixed(2);
                        
                        if (tax != "" && tax != "None"){
                                    $.ajax({
                                        type: 'POST',
                                        Accept: 'application/json',
                                        ContentType: 'application/json;charset=utf-8',
                                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_Products_Tax_Template',
                                        data: {
                                            name:tax
                                        },
                                        dataType: "json",
                                        async: false,
                                        headers:{
                                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                        },
                                        success: function(data){
                                            var tax_rates=data.message[0].tax_rate
                                            for (i = 0; i < tax_rates.length; i++) { 
                                              tax_rate += tax_rates[i].rate ;
                                            }
                                            product_tax = (parseFloat(newPrice * (tax_rate/100))).toFixed(2);
                                    }
                                })
                           }
                           else{
                                tax=""
                               }
                $(".CartItem[data-id=" + id + "]").find('.CartQty').html('<div style="display: none" class="TaxLib">'+product_tax+'</div><div style="display: none" class="TaxTemplate">'+tax+'</div><a id="'+id+'" onclick="DecrementQty($(this))" style="margin-right:5px;margin-left:0;cursor:pointer;">-</a><span class="QtyLbl" id="'+id+'">'+newQty+'</span><a id="'+id+'" onclick="IncrementQty($(this))" style="margin-left:5px;cursor:pointer;">+</a>')
                $(".CartItem[data-id=" + id + "]").find('.CartAmount').text("$" + newPrice);
                  
                        }
                        else {
                            alert("The min order count for this product is : " + min_count);
                            checkStock = false;
                        }
                    }
                    else {
                        alert("The available stock for this product is : " + stock);
                        checkStock = false;
                    }
                }
                else {
                  
                    checkStock = false;
                }
            }
            if (checkStock) {
                var productsCount = 0;
                var productsTotal = 0;
                var totalPayable = 0;
                gst = 0;
                $(".CartList li").each(function () {
                    productsCount += parseInt($(this).find(".QtyLbl").text());
                    productsTotal += parseFloat($(this).find(".CartAmount").text().split("$")[1]);
                    gst += parseFloat($(this).find(".TaxLib").text());
                });
              
                if (customerBalance >= productsTotal) {
                    availbalance = customerBalance - productsTotal;
                }
                else {
                    availbalance = 0;
                    totalPayable = productsTotal - customerBalance;
                }
                totalItems += 1;
                totalAmount += parseFloat(productprice);
                $("#titems").text(productsCount);
                $(".cart_label").text(productsCount);
                $("#total").text("₹" + productsTotal.toFixed(2));
                $("#tax").text("₹" + gst.toFixed(2));
                $("#gtotal").text("₹" + ( gst + productsTotal).toFixed(2));
                $("#item_count").text(productsCount);
                $("#twt").text("₹" + ( gst + productsTotal).toFixed(2));
                $("#quick-payable").text("₹" + productsTotal.toFixed(2));
                $("#quick-payable").attr("data-value", productsTotal.toFixed(2));
            }
            isAlreadyClick = 0;
        }
        function scrollingDiv()
        {
            var scrollTo_int = $('#left-middle').prop('scrollHeight') + 'px';
            var scrollheight = ($('#left-middle').height()) + 'px';
            $('#left-middle').slimscroll({
                scrollTo: scrollTo_int,
                height: scrollheight,
                start: 'bottom',
            });
        }
            function searchkeyup(){
                if ($("#instantsearch").val()!="")
                {
                    $(".rightCart #ProductDiv").each(function () {

                        var title = $(this).find(".cartincr").attr("data-title").toLowerCase();
                        var searchKey = $("#instantsearch").val().toLowerCase();
                        if (title.indexOf(searchKey) >= 0)
                        {
                            $(this).show();
                        }
                        else{
                            $(this).hide();
                        }
                    });
                    
                }
                 else{
                        $(".rightCart #ProductDiv").show();
                    }
                var contentHeight = $(window).height() - 170;
                $('#maincontent').slimscroll({
                    height: contentHeight + 'px',
                });
    }


function movetoPayment()
        {
            if (parseFloat($("#titems").text()) > 0)
            {
                if (isAlreadyClick == 0) {
                    var customer_id=$('.customer_email').text()
                    frappe.call({
                        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.GetCustomerBalance',
                        args: {
                            name:customer_id
                        },
                        async:false,
                        callback: function(data){
                            var previous_bal = data.message[0];
                            var balAmount = previous_bal.balance;
                            var temp_amt = parseFloat($("#gtotal").text().split("₹")[1]).toFixed(2)
                            totalQuickCash = 0;
                            $("#twt").text("₹" + temp_amt.toString());
                            if (parseFloat(balAmount) <= 0) {
                                var totalamount = 0;
                                var amt = balAmount.toString().replace("-", "");
                                totalamount = (parseFloat($("#twt").text().split("₹")[1]) - parseFloat(amt)).toFixed(2);
                                $("#twt").text("₹" + totalamount.toString());
                                $("#balance").text("₹-" + $("#twt").text().split("₹")[1]);
                                $("#quick-payable").text("₹" + $("#twt").text().split("₹")[1]);
                                $("#quick-payable").attr("data-value", $("#twt").text().split("₹")[1]);
                                var balance_amount = Math.abs(balAmount);
                                if (parseFloat(balAmount) < 0) {
                                $("#pendingBalance").html("This customer has paid ₹<span id='PreviousBalance'>" + balance_amount + " </span>extra in the previous payment");
                                }
                                else if (parseFloat(balAmount) == 0){
                                   $("#pendingBalance").html("Balance: ₹<span id='PreviousBalance'>" + balance_amount + " </span>"); 
                                }
                            }
                            else {
                                var amt = balAmount.toString().replace("-", "");
                                var totalamount = (parseFloat($("#twt").text().split("₹")[1]) + parseFloat(amt)).toFixed(2);
                                $("#twt").text("₹" + totalamount.toString());
                                $("#balance").text("₹-" + $("#twt").text().split("₹")[1]);
                                $("#quick-payable").text("₹" + $("#twt").text().split("₹")[1]);
                                $("#quick-payable").attr("data-value", $("#twt").text().split("₹")[1]);
                                $("#pendingBalance").html("Customer pending Balance : ₹<span id='PreviousBalance'>" + amt + " </span>");
                            }
                var tobePaid = parseFloat($("#quick-payable").text().split("₹")[1]);
                var amount = parseFloat($('.quick-cash').attr("data-value"));
                totalQuickCash += amount;
                if ($('.quick-cash').find(".badge").text() == "")
                {
                    $('.quick-cash').append("<span class='badge'>1</span>");
                }
                else {
                    var badgevalue = parseInt($('.quick-cash').find(".badge").text()) + 1;
                    $('.quick-cash').find(".badge").text(badgevalue);
                }
                
                $("#amount_1").val(totalQuickCash.toFixed(2));
                $("#total_paying").text("₹" + totalQuickCash.toFixed(2));
                $("#balance").text("₹" +((totalQuickCash - tobePaid).toFixed(2)));
                            $(".badge").remove();
                            $("#paymentModel").modal("show");
                            
                    }
                })
                }
                else {
                    $(".badge").remove();
                    $("#amount_1").val('');
                    $("#total_paying").text(0);
                    $("#balance").text("₹-" + $("#twt").text().split("₹")[1]);
                    $("#paymentModel").modal("show");
                }
            }
            else{
                alert("Please add atleast one product.");
            }
        }

        
        $(document).ready(function () {
            $(".quick-cash").click(function () {
                var tobePaid = parseFloat($("#quick-payable").text().split("₹")[1]);
                var amount = parseFloat($(this).attr("data-value"));
                totalQuickCash += amount;
                if ($(this).find(".badge").text() == "")
                {
                    $(this).append("<span class='badge'>1</span>");
                }
                else {
                    var badgevalue = parseInt($(this).find(".badge").text()) + 1;
                    $(this).find(".badge").text(badgevalue);
                }
                $("#amount_1").val(totalQuickCash.toFixed(2));
                $("#total_paying").text("₹" + totalQuickCash.toFixed(2));
                $("#balance").text("₹" +((totalQuickCash - tobePaid).toFixed(2)));
            });
            $("#clear-cash-notes").click(function () {
                totalQuickCash = 0;
                $(".badge").remove();
                var tobePaid = parseFloat($("#quick-payable").text().split("₹")[1]);
                $("#amount_1").val(totalQuickCash.toFixed(2));
                $("#total_paying").text("₹" + totalQuickCash.toFixed(2));
                $("#balance").text("₹ -" + (tobePaid.toFixed(2)));
            });
        });

        function order_type(value){
            ordertype = value;
           
            if (ordertype == "DineIn"){
                $("#type_DineIn").addClass("order_type_btn_active")
                $("#type_Pickup").removeClass("order_type_btn_active")
                $("#type_Delivery").removeClass("order_type_btn_active")
                $("#left-middle").css("height","calc(90% - 216px)")
                $("#shipping_charges").css("display","none")
                $(".shipping_btn").css("display","none")
                $("#shipping_manual_charge").val("");
                $("#shippingcharges").text(0);
                TableReservationModel()
            }
            if (ordertype == "Pickup"){
                $("#type_DineIn").removeClass("order_type_btn_active")
                $("#type_Pickup").addClass("order_type_btn_active")
                $("#type_Delivery").removeClass("order_type_btn_active")
                $("#left-middle").css("height","calc(90% - 216px)")
                $("#shipping_charges").css("display","none")
                $(".shipping_btn").css("display","none")
                $("#shipping_manual_charge").val("");
                $("#shippingcharges").text(0);
            }
            if (ordertype == "Delivery"){
                $("#type_DineIn").removeClass("order_type_btn_active")
                $("#type_Pickup").removeClass("order_type_btn_active")
                $("#type_Delivery").addClass("order_type_btn_active")
                $("#left-middle").css("height","calc(90% - 247px)")
                $("#shipping_charges").css("display","table-row")
                $(".shipping_btn").css("display","block")
                $("#shipping_manual_charge").val("");
                $("#shippingcharges").text(0);
            }
            if(ordertype == ""){
                $("#type_DineIn").removeClass("order_type_btn_active")
                $("#type_Pickup").removeClass("order_type_btn_active")
                $("#type_Delivery").removeClass("order_type_btn_active")
                $("#left-middle").css("height","calc(90% - 216px)")
                $("#shipping_charges").css("display","none")
                $(".shipping_btn").css("display","none")
                $("#shipping_manual_charge").val("");
                $("#shippingcharges").text(0);
            }
        }

        function shipping_charges(){
            var Shipping_charge = $("#shipping_manual_charge").val();
            $("#shippingcharges").text("₹"+Shipping_charge);
        }

        

        function get_all_table(){
            Table_list=[];
            $("#TableList").html('');
            $.ajax({
                                        type: 'POST',
                                        Accept: 'application/json',
                                        ContentType: 'application/json;charset=utf-8',
                                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.getTable',
                                        data: {
                                        },
                                        dataType: "json",
                                        async: false,
                                        headers:{
                                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                        },
                                        success: function(data){
                                            if(data.message){
                                                Table_list=data.message;
                                               
                                                for(i=0; i<Table_list.length; i++){
                                                    var name= Table_list[i].name;
                                                    var table_location = Table_list[i].table_location;
                                                    var seating_capacity = Table_list[i].seating_capacity;
                                                    var seats_occupied = Table_list[i].seats_occupied;
                                                    var table_status = Table_list[i].table_status;
                                                    var table_type = Table_list[i].table_type;
                                                    var border_color = "#ddd";
                                                    if(table_status == "Available"){
                                                        border_color = "green";
                                                    }
                                                    else if(table_status == "Reserved"){
                                                        border_color = "orange";
                                                    }
                                                    else{
                                                        border_color = "red";
                                                    }
                                                    var table_html='<div class="col-md-3 col-sm-6 col-xs-12" style="padding: 10px;"><div class="tabledetail" id="tableid'+i+'" data-name="'+name+'" data-tablocation="'+table_location+'" data-status="'+table_status+'" onclick="table_details($(this))"><div class="card" style="width: 100%;border: 3px solid '+border_color+';padding: 0px 10px;border-radius: 8px;"><img class="card-img-top" src="/assets/frappe/images/table-representation.jpg" alt="Table image" /><div class="card-body" style="text-align: center;"><h4 class="card-text">'+name+'</h4><input style="width: 34px; height: 20px;text-align: center;border: 1.2px solid #9e9e9e;" type="text" value="'+seats_occupied+'/'+seating_capacity+'" readonly/><p class="card-body">'+table_type+'</p></div></div></div></div>'
                                                    $("#TableList").append(table_html);
                                                }
                                            }
                                    }
                                })
        }

        function get_all_floor(){
            $("#FloorList").html('');
            $.ajax({
                                        type: 'POST',
                                        Accept: 'application/json',
                                        ContentType: 'application/json;charset=utf-8',
                                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_tab_location',
                                        data: {
                                        },
                                        dataType: "json",
                                        async: false,
                                        headers:{
                                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                        },
                                        success: function(data){
                                            if(data.message){
                                                floors=data.message;
                                                
                                                for(i=0; i<floors.length; i++){
                                                    var name = floors[i].name;
                                                    var title=floors[i].location_name;
                                                    var floorlist='<a class="list-group-item" id="floor'+i+'" data-name="'+name+'" onclick="select_floor($(this))" style="margin: 0px; border-radius: 0px; border-width: 0px 0px 1px; border-style: solid; border-bottom-color: rgb(222, 222, 222); border-image: initial; border-top-color: initial; border-right-color: initial; padding-left: 30px; border-left-color: initial;">'+title+'</a>'
                                                    $("#FloorList").append(floorlist);
                                                }
                                            }
                                    }
                                })
        }

        function select_floor(e){
            $(".table_details").css("display","block");
            var floor = e.attr("data-name");
           
            $(".tablelist .col-md-3").each(function () {
                        var title = $(this).find(".tabledetail").attr("data-tablocation");
                        
                        if (title == floor)
                        {
                            $(this).show();
                        }
                        else{
                            $(this).hide();
                        }
                    });

            $(".tablelist .col-sm-6").each(function () {
                        var title = $(this).find(".tabledetail").attr("data-tablocation");
                        if (title == floor)
                        {
                            $(this).show();
                        }
                        else{
                            $(this).hide();
                        }
                    });

            $(".tablelist .col-xs-12").each(function () {
                        var title = $(this).find(".tabledetail").attr("data-tablocation");
                        if (title == floor)
                        {
                            $(this).show();
                        }
                        else{
                            $(this).hide();
                        }
                    });
        }

        var table_id ="";
        function table_details(e){
            $("#seating_count").html('')
            $("#TableDetailsModel").modal("show");
            var table = e.attr("data-name");
            table_id="";
            for(i=0; i<Table_list.length; i++){
                if(table == Table_list[i].name){
                    var name= Table_list[i].name;
                    table_id = Table_list[i].name;
                    var table_location = Table_list[i].table_location;
                    var seating_capacity = Table_list[i].seating_capacity;
                    var seats_occupied = Table_list[i].seats_occupied;
                    var table_status = Table_list[i].table_status;
                    $("#tabletitle").text("Table : "+name);
                    $("#max_seats").text(seating_capacity);
                    $("#table_status").text(table_status);
                    $("#seats_occupied").text(seats_occupied);
                    if(table_status == "Available"){
                        var html='How many people to be seated? <input style="width: 45px; height: 28px; margin: 5px;" type="number" id="tablecount_id" data-max="'+seating_capacity+'" min="0" max="'+seating_capacity+'" onKeyUp="maxSeatCapacity($(this))" class="enterdSeatcpcty" value="' + seats_occupied + '"/><br><br><button type="button" class="btn btn-success" data-dismiss="modal" style="float: right;" onclick="alot_table()">Submit</button>'
                        $("#seating_count").append(html);
                    }
                    if(table_status == "InUse"){
                        var html='<br><button onclick="make_table_available()" type="button" class="btn btn-success" style="border-top-right-radius: 0px; border-bottom-right-radius: 0px;width:33%""><i class="lni-hand" aria-hidden="true" style="padding-right: 5px;"></i>Available</button><button type="button" class="btn btn-info" style="border-radius: 0px;width: 33%;"><i class="fa fa-plus" aria-hidden="true" style="padding-right: 5px;"></i>Add Item</button><button type="button" class="btn btn-info" style="border-top-left-radius: 0px; border-bottom-left-radius: 0px;width: 33%;"><i class="lni-enter" aria-hidden="true" style="padding-right: 5px;"></i>Print</button>'
                        $("#seating_count").append(html);
                    }
                    if(table_status == "Reserved"){
                        var html='<br><button onclick="make_table_available()" type="button" class="btn btn-success" style="border-top-right-radius: 0px; border-bottom-right-radius: 0px;width:33%"><i class="lni-hand" aria-hidden="true" style="padding-right: 5px;"></i>Available</button><button type="button" class="btn btn-info" style="border-radius: 0px;width: 33%;"><i class="fa fa-plus" aria-hidden="true" style="padding-right: 5px;"></i>Add Item</button><button type="button" class="btn btn-info" style="border-top-left-radius: 0px; border-bottom-left-radius: 0px;width: 33%;"><i class="lni-enter" aria-hidden="true" style="padding-right: 5px;"></i>Print</button>'
                        $("#seating_count").append(html);
                    }
                }
            }
        }

        function maxSeatCapacity(e){
            
            var max = parseInt(e.attr('data-max'));
            var count = parseInt($("#seating_count").find(".enterdSeatcpcty").val());
           
            if (count > max){
                $("#seating_count").find(".enterdSeatcpcty").val(max);
            }
            else if(count < 0){
                $("#seating_count").find(".enterdSeatcpcty").val(0);
            }
           
        }

        function alot_table(){
            $("#DineIn_table").text("Dine in on "+table_id);
            $("#TableReservationModel").modal("hide")
            update_table_status(table_id,"assign_seats")
        }

        function make_table_available(){
            update_table_status(table_id,"make_available")
            $("#TableDetailsModel").modal("hide");
            $("#DineIn_table").text("Dine in");
        }

        function update_table_status(name,value){
            var total_seats = $("#tablecount_id").val();
           
            if(value == "assign_seats"){
                $.ajax({
                                        type: 'POST',
                                        Accept: 'application/json',
                                        ContentType: 'application/json;charset=utf-8',
                                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.updateTableStatus',
                                        data: {
                                            name:name,
                                            status:"InUse",
                                            seats:total_seats
                                        },
                                        dataType: "json",
                                        async: false,
                                        headers:{
                                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                        },
                                        success: function(data){
                                            if(data){
                                                get_all_table()
                                                $(".table_details").css("display","none");
                                                $("#TableReservationModel").modal("hide");
                                            }
                                    }
                                })
            }
            if(value == "make_available"){
                $.ajax({
                                        type: 'POST',
                                        Accept: 'application/json',
                                        ContentType: 'application/json;charset=utf-8',
                                        url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.updateTableStatus',
                                        data: {
                                            name:name,
                                            status:"Available",
                                            seats:0
                                        },
                                        dataType: "json",
                                        async: false,
                                        headers:{
                                            'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                        },
                                        success: function(data){
                                            if(data){
                                                get_all_table()
                                                $(".table_details").css("display","none");
                                                $("#TableReservationModel").modal("hide");
                                                $("#type_DineIn").removeClass("order_type_btn_active")
                                            }
                                    }
                                })
            }

        }

function insertOrder()
{
  var customer_id = $('.customer_email').text()
  
  if( customer_id) { 
    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_customer_info',
        args: {
            email:customer_id
        },
        async:false,
        callback: function(data){
            if (data.message){
                var cust_details=data.message;
              
            if(cust_details.length>0){
              if ($("#amount_1").val() != "") {
                  var formdata ={};
                  var orders = {};
                  var orderId;
                  var payment_type = $("#PaymentMethod").val();
                  orders.payment_method = $("#PaymentMethod").val();
                  orders.payment_notes = $("#payment_note_1").val();
                  orders.customer_name = cust_details[0].full_name;
                  orders.customer_email = cust_details[0].email;
                  orders.customer = cust_details[0].name;
                  orders.customer_phone = cust_details[0].phone;
                  orders.payment_status = "Paid";
                  orders.type ="Pickup";
                  orders.status ="Delivered";
                  orders.sub_total = $("#total").text().split("₹")[1];                    
                  var products = [];
                  var Total_amount = 0;
                $(".CartList li").each(function () {
                      var product = {};
                      product.item = $(this).attr("data-id");
                      product.price = $(this).find("data-price");
                      product.quantity = $(this).find(".QtyLbl").text();
                      product.item_total = $(this).find(".CartAmount").text().split("$")[1];
                      product.tax_template = $(this).find(".TaxTemplate").text();
                      product.tax = parseFloat($(this).find(".TaxLib").text()).toFixed(2);
                      Total_amount += (parseFloat($(this).find("data-price")) * parseFloat($(this).find(".QtyLbl").text()));
                      products.push(product);
                  });
                  orders.order_item = products;
                  orders.total_amount = Total_amount;
                  formdata.orders = orders;                  
                  orders.TotalPay = parseFloat($("#gtotal").text().split("₹")[1]);
                  orders.tax =parseFloat( $("#tax").text().split("₹")[1]);
                  orders.total_paying = parseFloat($("#total_paying").text().split("₹")[1]); 
                  orders.balance = parseFloat($("#total_paying").text().split("₹")[1]);
                  frappe.call({
                          method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.posInsertOrder',
                          args: {
                              name: customer_details.full_name,
                              email: customer_details.email,
                              cus_id: customer_details.name,
                              sub_total: orders.sub_total,
                              payment_type: payment_type,
                              amount: orders.TotalPay,
                              tax: orders.tax,
                              items : products,
                              total_paying : orders.total_paying,
                              balance : orders.balance,
                              notes : orders.payment_notes
                          },
                          async:false,
                      callback: function (data) {
                          success =data.message;
                      
                          if (success == true) {
                              alert("Order inserted successfully!");                                
                              $("#titems").text(0);
                              $(".cart_label").text(0);
                              $("#item_count").text(0);
                              $("#twt").text(0);
                              $("#total").text(0);
                              $("#gtotal").text(0);
                              $("#tax").text(0);
                              $("#quick-payable").text(0);
                              $("#quick-payable").attr("data-value", 0);
                              $("#paymentModel").modal("hide");
                              $("#productsbody").html('');
                              $("#payment_note_1").text('');
                              delete_holdorder();
                          }
                          
                          location.reload(true);
                      }
          
                  });
                 
              }
              else
              {
                 alert("Please enter amount");
              }
          }
        }
    }
})
  }
else{
    alert("Please select the customer");
}
   
   
}

        function holdOrder(){
            if (parseFloat($("#titems").text()) > 0){
            var result = confirm("Are you sure want Hold this order?")
            if (result) {
                var formdata ={};
                var orders = {};
                var orderId;
                var payment_type = $("#PaymentMethod").val();
                orders.payment_method = $("#PaymentMethod").val();
                orders.customer_name = customer_details.full_name;
                orders.customer_email = customer_details.email;
                orders.customer = customer_details.name;
                orders.customer_phone = customer_details.phone;
                orders.payment_status = "Paid";
                orders.type ="Pickup";
                orders.status ="Delivered";
                orders.sub_total = $("#total").text().split("₹")[1];                    
                var products = [];
                var Total_amount = 0;

                $("#productsbody tr").each(function () {
                    var product = {};
                    product.item = $(this).attr("id").split('tr-')[1];
                    product.price = $(this).find("td:eq(1)").text().split("₹")[1];
                    product.quantity = $(this).find("td:eq(2)").find(".QtyLbl").val();
                    product.item_total = $(this).find("td:eq(3)").text().split("₹")[1];
                    product.tax = parseFloat($(this).find("td:eq(2)").find(".TaxLib").text()).toFixed(2);
                    Total_amount += (parseFloat($(this).find("td:eq(1)").text().split("₹")[1]) * parseFloat($(this).find("td:eq(2)").find(".QtyLbl").val()));
                    products.push(product);
                });
                orders.order_item = products;
                orders.total_amount = Total_amount;
                formdata.orders = orders;                  
                orders.TotalPay = $("#total").text().split("₹")[1];
                orders.tax = $("#tax").text().split("₹")[1];
                orders.total_paying = $("#total_paying").text().split("₹")[1]; 
                orders.balance = $("#balance").text().split("₹")[1];

                frappe.call({
                        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.posHoldOrder',
                        args: {
                            cus_id: customer_details.name,
                            amount: orders.TotalPay,
                            tax: orders.tax,
                            items : products,
                            hold_Id: hold_order_id
                        },
                        async:false,
                    callback: function (data) {
                        if (data.message == true) {
                            get_holdorder_List();
                            $("#titems").text(0);
                            $(".cart_label").text(0);
                            $("#item_count").text(0);
                            $("#twt").text(0);
                            $("#total").text(0);
                            $("#gtotal").text(0);
                            $("#tax").text(0);
                            $("#quick-payable").text(0);
                            $("#quick-payable").attr("data-value", 0);
                            $("#paymentModel").modal("hide");
                            $("#productsbody").html('');
                            $("#payment_note_1").text('');
                            hold_order_id='';
                        }
                    }

                });
            }
            }
            else{
                alert("Please add atleast one product.");
            }
        }

        function delete_holdorder(){
            if(hold_order_id != ''){
                $.ajax({
                                    type: 'POST',
                                    Accept: 'application/json',
                                    ContentType: 'application/json;charset=utf-8',
                                    url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.delete_poscart',
                                    data: {
                                        name:hold_order_id
                                    },
                                    dataType: "json",
                                    async: false,
                                    headers:{
                                        'X-Frappe-CSRF-Token':'{{csrf_token}}'
                                    },
                                    success: function(data){
                                       
                                        get_holdorder_List();
                                }
                            })
            }

        }

        function cancelOrder()
        {
            var result = confirm("Are you sure want cancel this order?")
            if (result) {
                ordertype="";
                table_id="";
                $("#shippingcharges").text(0);
                $("#shipping_manual_charge").val("");
                order_type("")
                hold_order_id='';
                total_paying = 0;
                totalAmount = 0;
                item_count = 0;
                totalItems = 0;
                $("#titems").text(0);
                $(".cart_label").text(0);
                $("#item_count").text(0);
                $("#twt").text(0);
                $("#total").text(0);
                $("#gtotal").text(0);
                $("#tax").text(0);
                $("#quick-payable").text(0);
                $("#quick-payable").attr("data-value", 0);
                $("#paymentModel").modal("hide");
                $(".CartList").html('');
                $("#DineIn_table").text("Dine in");
            }
        }

         function validateFloatKeyPress(el, evt) {
            var charCode = (evt.which) ? evt.which : event.keyCode;
            var number = el.value.split('.');
            if (charCode != 46 && charCode > 31 && (charCode < 48 || charCode > 57)) {
                return false;
            }
            if (number.length > 1 && charCode == 46) {
                return false;
            }
            var caratPos = getSelectionStart(el);
            var dotPos = el.value.indexOf(".");
            if (caratPos > dotPos && dotPos > -1 && (number[1].length > 1)) {
                return false;
            }
            return true;
        }

        function get_entered_amount(){
            totalQuickCash=(parseFloat($("#amount_1").val())).toFixed(2);
           
            var tobePaid = parseFloat($("#quick-payable").text().split("₹")[1]);
            $("#total_paying").text("₹" + parseFloat(totalQuickCash).toFixed(2));
            $("#balance").text("₹" +((totalQuickCash - tobePaid).toFixed(2)));
        }


        function getSelectionStart(o) {
            if (o.createTextRange) {
                var r = document.selection.createRange().duplicate()
                r.moveEnd('character', o.value.length)
                if (r.text == '') return o.value.length
                return o.value.lastIndexOf(r.text)
            } else return o.selectionStart
        }

        $(function () {
            $('#displayElem').html('1');
         
            $('#myTab a[href="#addTab"]').on('click', function () {
                var nbrLiElem = ($('ul#myTab li').length) - 1;
                
            
            
                $('ul#myTab li:last-child').before('<li id="li' + (nbrLiElem + 1) + '"><a href="#tab' + (nbrLiElem + 1) + '" role="tab" data-toggle="tab">Tab ' + (nbrLiElem + 1) + ' <button type="button" class="btn btn-xs" onclick="removeTab(' + (nbrLiElem + 1) + ');"><span class="glyphicon glyphicon-remove"></span></button></a>');
                
            
                $('div.tab-content div:last-child').after('<div class="tab-pane fade" id="tab' + (nbrLiElem + 1) + '"></div>');
                nbrLiElem = nbrLiElem + 1;
                $('#displayElem').html(nbrLiElem);
            });
        });

        function removeTab(liElem) {
            if (confirm("Are you sure?")) {
                $('ul#myTab > li#li' + liElem).fadeOut(1000, function () { 
                    $(this).remove();
                    $('#messagesAlert').text('');
                });
                
                $('div.tab-content div#tab' + liElem).remove();
                
                $('ul#myTab > li').not('#last').not('#li' + liElem).each(function(i){
                    var getAttr = $(this).attr('id').split('li');
                    $('ul#myTab li#li' + getAttr[1]).attr('id', 'li' + (i + 1));
                    
                    var tabContent = 'Tab ' + (i + 1);
                    if (getAttr[1] != 1) tabContent += ' <button type="button" class="btn btn-xs" onclick="removeTab(' + (i + 1) + ');"><span class="glyphicon glyphicon-remove"></span></button>';
                    $('#myTab a[href="#tab' + getAttr[1] + '"]').html(tabContent)
                                                                .attr('href', '#tab' + (i + 1));
                    
                    $('div.tab-content div#tab' + getAttr[1]).html()
                                                            .attr('id', 'tab' + (i + 1));
                                                            
                    $('#displayElem').html(i+1);
                });
                
                $('#messagesAlert').html('<div class="alert alert-danger" id="alertFadeOut">This tab has been deleted!</div>');
            }
            return false;
        }

$('#autocomplete').on('click',function(){
      $.ajax({
    type: 'POST',
    Accept: 'application/json',
    ContentType: 'application/json;charset=utf-8',
    url: window.location.origin + '/api/method/ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.getCustomerList',
    data: {
    },
    dataType: "json",
    async: false,
    headers:{
        'X-Frappe-CSRF-Token':'{{csrf_token}}'
    },
    success: function(data){
        var customers=[];
        if(data.message.length>0){
            customers.push(data.message)
        }
       autocomplete(document.getElementById("autocomplete"),customers);
    }
})

})

function autocomplete(inp, arr) {
  
var currentFocus;
inp.addEventListener("input", function(e) {
    var a, b, i, val = this.value;

    closeAllLists();
    if (!val) { return false; }
    currentFocus = -1;

    a = document.createElement("DIV");
    a.setAttribute("id", this.id + "autocomplete-list");
    a.setAttribute("class", "autocomplete-items");
    a.setAttribute("style", "border:1px solid #ddd;position:absolute;z-index:99;width:228px;background-color: #f6f6f6;background-size: 1px;padding: 10px;max-height: 300px;overflow-y: scroll;");
    this.parentNode.appendChild(a);
    for (i = 0; i < arr[0].length; i++) {
        if (arr[0][i].name.substr(0, val.length).toUpperCase() == val.toUpperCase()) {
            var cust_email;
            var cust_name;
            
            b = document.createElement("DIV");
            b.setAttribute("id", "sec-auto");
            $("div#sec-auto").css("padding", "3px");
            $("div#sec-auto").css("margin", "5px");
            $("div#sec-auto").css("font-size", "14px");
            $("div#sec-auto").css("border-bottom","1px solid #d2d2d2 !important");


            b.innerHTML = "<strong>" + arr[0][i].name.substr(0, val.length) + "</strong>";

            b.innerHTML += arr[0][i].name.substr(val.length);

            b.innerHTML += "<input type='hidden' value='" + arr[0][i].name + "'>";
            b.innerHTML += "<div>";
            if(arr[0][i].first_name){
                cust_name=arr[0][i].first_name
            }
            if(arr[0][i].last_name){
                cust_name+=' '+ arr[0][i].last_name
            }
            
            if(cust_name){
                b.innerHTML += "<span>"+cust_name+"</span>";
            }
            if(arr[0][i].email){
                cust_email=arr[0][i].email
                 b.innerHTML += ", <span>"+ arr[0][i].email+"</span>";
            }
            
            
            b.innerHTML += "</div>";

            b.addEventListener("click", function(e) {
               
                
                inp.value = this.getElementsByTagName("input")[0].value;
                    $('.customer_email').text("")
                    $('#cust_names').text("")
                    $('input[data-fieldname="customers"]').val(inp.value);

                    $('.customer_email').text(cust_email)
                    $('#cust_names').text(cust_name)
                    $('.myInput').hide()
                    
                    
                    GetCustomerBalance()
            
     closeAllLists();
            });
            a.appendChild(b);
        }
    }
});

inp.addEventListener("keydown", function(e) {
    var x = document.getElementById(this.id + "autocomplete-list");
    if (x) x = x.getElementsByTagName("div");
    if (e.keyCode == 40) {
        currentFocus++;
        addActive(x);
    } else if (e.keyCode == 38) {
        currentFocus--;
        addActive(x);
    } else if (e.keyCode == 13) {
        e.preventDefault();
        if (currentFocus > -1) {
            if (x) x[currentFocus].click();
        }
    }
});

function addActive(x) {
   
    $('#sec-auto').removeAttr("style");
    if (!x) return false;
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (x.length - 1);
    x[currentFocus].classList.add("autocomplete-active");
}

function removeActive(x) {
    for (var i = 0; i < x.length; i++) {
        x[i].classList.remove("autocomplete-active");
    }
}

function closeAllLists(elmnt) {

    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
        if (elmnt != x[i] && elmnt != inp) {
            x[i].parentNode.removeChild(x[i]);
        }
    }
}

document.addEventListener("click", function(e) {
    closeAllLists(e.target);
});
}