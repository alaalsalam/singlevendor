frappe.pages['product-bulk-update'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Product Bulk Update',
        single_column: true
    });
    $('.page-content').find('.layout-main').append(frappe.render_template("product_bulk_update"));
    $('.page-content').find('.layout-main').prepend('<div class="formlist"></div>')


}

var changedRows = [];
var dt;

function formatMoney(amount, decimalCount = 2, decimal = ".", thousands = ",") {
    try {
        decimalCount = Math.abs(decimalCount);
        decimalCount = isNaN(decimalCount) ? 2 : decimalCount;

        const negativeSign = amount < 0 ? "-" : "";

        let i = parseInt(amount = Math.abs(Number(amount) || 0).toFixed(decimalCount)).toString();
        let j = (i.length > 3) ? i.length % 3 : 0;

        return negativeSign + (j ? i.substr(0, j) + thousands : '') + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + thousands) + (decimalCount ? decimal + Math.abs(amount - i).toFixed(decimalCount).slice(2) : "");
    } catch (e) {
        console.log(e)
    }
};
frappe.pages['product-bulk-update'].refresh = function(wrapper) {

    $('.page-title .title-text').text('Product Bulk Update')

    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.get_all_products',
        args: { doctype: "Product" },
        callback: function(r) {
            console.log(r.message)
            var items = r.message
            dt = new DataTable('#listing', {
                columns: [
                    { name: 'Id', width: 1, editable: false },
                    { name: 'Product', width: 2, editable: true },
                    { name: 'SKU', width: 1, editable: true },
                    { name: 'Price', width: 1, editable: true, format: value => formatMoney(value) },
                    { name: 'Old Price', width: 1, editable: true, format: value => formatMoney(value) },
                    { name: 'Stock', width: 1, editable: true, align: "left" },
                    { name: 'Inventory Method', width: 2, editable: true, align: "left" },
                    { name: 'Active', width: 1, editable: true, align: "left" },
                    { name: 'Featured Product', width: 1, editable: true, align: "left" },
                    { name: 'Categories', width: 2, align: "left", format: value => `<button class="btn-primary" onclick="get_category('${value}')">Edit Category</button>` },
                    { name: 'Image', width: 2, align: "left", format: value => `<button class="btn-primary" onclick="get_image('${value}')">Add / Edit Image</button>` },

                ],
                data: r.message,
                inlineFilters: true,
                layout: 'ratio',
                noDataMessage: "No Data Found",
                dropdownButton: '▼',
                sortIndicator: {
                    asc: '↑',
                    desc: '↓',
                    none: ''
                },
                getEditor(colIndex, rowIndex, value, parent, column, row, data) {
                    if (jQuery.inArray(rowIndex, changedRows) == -1) {
                        changedRows.push(rowIndex);
                    }
                    if (colIndex == 4 && colIndex == 5) {
                        const $input = document.createElement('input');
                        $input.type = 'number';
                        parent.appendChild($input);

                        return {
                            initValue(value) {
                                $input.focus();
                                $input.value = value;
                            },
                            setValue(value) {

                                $input.value = value;
                            },
                            getValue() {
                                return format($input.value);
                            }
                        }
                    }
                    if (colIndex == 7) {
                        const $input = document.createElement('select');
                        var option1 = new Option("Track Inventory", "Track Inventory");
                        var option2 = new Option("Dont Track Inventory", "Dont Track Inventory");
                        var option3 = new Option("Track Inventory By Product Attributes", "Track Inventory By Product Attributes");
                        if (value == "Track Inventory") {
                            option1.setAttribute("selected", "selected");
                        }
                        if (value == "Dont Track Inventory") {
                            option2.setAttribute("selected", "selected");
                        }
                        if (value == "Track Inventory By Product Attributes") {
                            option3.setAttribute("selected", "selected");
                        }
                        var drpClass = "InventoryDrp-";
                        var changeName = 'InventoryDropUpdate';

                        $input.append(option1);
                        $input.append(option2);
                        $input.append(option3);
                        $input.setAttribute("id", drpClass + rowIndex);
                        $input.setAttribute("style", 'width:100%;height:26px');
                        $input.setAttribute("onchange", changeName + '(' + rowIndex + ')');
                        parent.appendChild($input);
                        return {
                            initValue(value) {
                                $input.focus();
                                $input.value = value;
                            },
                            setValue(value) {
                                $input.value = value;
                            },
                            getValue() {
                                return format($input.value);
                            }
                        }
                        return {
                            initValue(value) {
                                $input.focus();
                                $input.value = value;
                            },
                            setValue(value) {

                                $input.value = value;
                            },
                            getValue() {
                                return format($input.value);
                            }
                        }
                    }
                    if (colIndex == 8 || colIndex == 9) {

                        const $input = document.createElement('select');
                        var option1 = new Option("Yes", "Yes");
                        var option2 = new Option("No", "No");
                        if (value == "Yes") {
                            option1.setAttribute("selected", "selected");
                        }
                        if (value == "No") {
                            option2.setAttribute("selected", "selected");
                        }
                        var drpClass = "ActiveDrp-";
                        var changeName = 'ActiveDropUpdate';
                        if (colIndex == 9) {
                            drpClass = "RecomDrp-";
                            changeName = 'RecomDropUpdate';
                        }
                        $input.append(option1);
                        $input.append(option2);
                        $input.setAttribute("id", drpClass + rowIndex);
                        $input.setAttribute("style", 'width:100%;height:26px');
                        $input.setAttribute("onchange", changeName + '(' + rowIndex + ')');
                        parent.appendChild($input);
                        return {
                            initValue(value) {
                                $input.focus();
                                $input.value = value;
                            },
                            setValue(value) {
                                $input.value = value;
                            },
                            getValue() {
                                return format($input.value);
                            }
                        }
                    }

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
        },
    });


}

function ActiveDropUpdate(rowIndex) {
    $(".dt-cell--col-8").removeClass("dt-cell--focus dt-cell--editing");
    dt.cellmanager.submitEditing();
    dt.cellmanager.deactivateEditing();

}

function RecomDropUpdate(rowIndex) {
    $(".dt-cell--col-9").removeClass("dt-cell--focus dt-cell--editing");
    dt.cellmanager.submitEditing();
    dt.cellmanager.deactivateEditing();
}

function updatemenuitems() {
    var alldata = dt.datamanager.getRows();

    var datas = [];
    for (var i = 0; i < changedRows.length; i++) {
        var obj = {
            'data': alldata[parseInt(changedRows[i])],
            'rowIndex': parseInt(changedRows[i])
        }
        datas.push(obj);
    }
    for (var i = 0; i < datas.length; i++) {

        var item = datas[i];
        var itemid = item.data[1].content;
        var itemTitle = item.data[2].content;
        var itemSKU = item.data[3].content;
        var itemPrice = item.data[4].content;
        var itemOldPrice = item.data[5].content;
        var itemStock = item.data[6].content;
        var itemInventoryMethod = item.data[7].content;
        var itemActive = item.data[8].content;
        var itemFeaturedProduct = item.data[9].content;
        console.log(item);
        frappe.call({
            method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.update_products',
            args: {
                name: itemid,
                title: itemTitle,
                sku: itemSKU,
                price: itemPrice,
                oldprice: itemOldPrice,
                stock: itemStock,
                inventorymethod: itemInventoryMethod,
                active: itemActive,
                displayhomepage: itemFeaturedProduct,
            },
            callback: function(r) {
                if (i == datas.length) {


                }
            }
        });

    }
    frappe.msgprint("Successfully updated");

    changedRows = [];
}

function get_category(id) {
    frappe.run_serially([
        () => {
            get_all_category_list()
        },
        () => {
            $('.modal').empty();
            $('.modal').removeClass('in');
            frappe.call({
                method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.get_product',
                args: {
                    name: id
                },
                async: false,
                callback: function(data) {
                    if (data.message) {
                        data1 = data.message;
                        category_dialog(data1)
                    }
                }
            })


        }
    ])


}

function get_all_category_list() {
    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.get_all_category_list',
        args: {},
        async: false,
        callback: function(data) {
            if (data.message) {
                category_list = data.message;
                console.log(category_list)
            }
        }
    })
}

function category_dialog(data1) {
    let categoryDialog;
    let random = Math.random() * 100;

    categoryDialog = new frappe.ui.Dialog({
        title: __('Categories'),
        fields: [{ fieldtype: 'HTML', fieldname: 'category_list', options: '<div id="mainCategoryList"><div id="category_list' + parseInt(random) + '"></div></div>' }],
        primary_action_label: __('Close')
    });
    let selected_category_list = [];
    categoryDialog.set_primary_action(__('Add'), function() {

        console.log(data1.name)
        frappe.call({
            method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.update_product_categories',
            args: {
                category1: selected_category_list,
                name: data1.name
            },
            async: false,
            callback: function(data) {
                categoryDialog.hide();
               
            }
        })

    });
    var table = new DataTable('#category_list' + parseInt(random), {
        columns: [
            { 'name': 'Category', 'id': 'category_name', 'width': 220, editable: false },
            {
                id: 'category_image',
                width: 150,
                editable: false,
                name: 'Image',
                format: (value) => {
                    if (value)
                        return `<img src="${value}" style="height:30px;" />`
                    else
                        return ''
                }
            },
            { 'name': 'Parent', 'id': 'parent_category_name', 'width': 220, editable: false },
            {
                'name': 'Status',
                'width': 135,
                'id': 'is_active',
                editable: false,
                format: (value) => {
                    if (value == 1)
                        return 'Active'
                    else
                        return 'Inactive'
                }
            },
            { 'name': 'Name', 'width': 134, 'id': 'name', editable: false }

        ],
        data: category_list,
        treeView: true,
        inlineFilters: true,
        checkboxColumn: true,
        dynamicRowHeight: true,
        pageLength: 5000,
        events: {
            onCheckRow: (row) => {
                let check_data = selected_category_list.find(obj => obj.category == row[6].content)
                if (check_data) {
                    let arr = [];
                    $(selected_category_list).each(function(k, v) {
                        if (v.category == row[6].content) {} else {
                            arr.push(v)
                        }
                    })
                    selected_category_list = arr;
                } else {
                    selected_category_list.push({ 'category': row[6].content, 'category_name': row[2].content })
                }
            },
            onSortColumn: (column) => {
                $('.datatable .dt-row-header input[type=checkbox]').hide();
                $('.datatable .dt-header .dt-row-filter').show()
                $('.datatable .dt-cell--header').css('background', '#f7f7f7')
            }
        }
    });

    $('.datatable .dt-row-header input[type=checkbox]').hide();
    $('.datatable .dt-header .dt-row-filter').show()
    $('.datatable .dt-cell--header').css('background', '#f7f7f7')
    $('.datatable').find('.dt-paste-target').css('position', 'relative')
    $('.datatable').find('.dt-paste-target').css('display', 'none')
    categoryDialog.$wrapper.find('div[data-fieldname="category_list"]').css('max-height', '400px')
    categoryDialog.$wrapper.find('div[data-fieldname="category_list"]').css('overflow-y', 'scroll')
    categoryDialog.get_close_btn().on('click', () => {
        $('.modal').removeClass('in');
        $('.modal').attr('aria-hidden', 'true')
        $('.modal').css('display', 'none')
        this.on_close && this.on_close(this.item);
    });
    categoryDialog.$wrapper.find('.modal-dialog').css("min-width", "1000px");
    $('.modal[data-types="category"').each(function() {
        $(this).remove();
    })
    categoryDialog.show();
    if (data1.product_categories) {
        $('div[data-fieldname="category_list"]').find('.dt-cell__content--col-6').each(function() {
            let category = $(this).text();
            let check_data = data1.product_categories.find(obj => obj.category == category.trim());
            if (check_data) {
                $(this).parent().parent().find('input[type=checkbox]').trigger('click')
            }
        })
    }
    $(categoryDialog.$wrapper).attr('data-types', 'category')
}

function get_image(id) {
    localStorage.setItem('randomuppy', ' ');
    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.get_product',
        args: {
            name: id
        },
        async: false,
        callback: function(data) {
            if (data.message) {
                data1 = data.message;
                generate_image_html(data1)
                image_dialog(data1)
            }
        }
    })

}

function generate_image_html(data1) {
    let html = '<div class="uploadFiles"><div class="title">Uploaded Files<button id="saveImages" class="btn btn-primary" style="float:right;margin-top: -4px;">Save</button></div><ul id="sortable">'
    $(data1.product_images).each(function(i, j) {
        let checked = "";
        if (j.is_primary == 1)
            checked = 'checked="checked"'
        html += '<li data-id="' + j.name + '"><div class="row"><div class="col-md-4 image-element"><img src="' + j.list_image + '" />\
            </div><div class="col-md-6 img-name"><div class="imageName">' + j.image_name + '</div><div class="editImage" style="display:none;"><div>\
            <input type="text" name="image_name" placeholder="Image Alternate Text" value="' + j.image_name + '" /></div><div><label style="font-weight:400;font-size:12px;"><input type="checkbox" data-id="' + j.name + '" name="is_primary" ' + checked + '/> <span>Mark as Primary?</span></label></div></div></div><div class="col-md-2 img-name"><a class="img-edit" data-id="' + j.name + '">\
            <span class="fa fa-edit"></span></a><a class="img-close" data-id="' + j.name + '">\
            <span class="fa fa-trash"></span></a></div></div></li>'
    })
    html += '</ul></div>';
    files_html = html;
}

function image_dialog(data1) {
    let selected_image_list = [];
    let random = Math.random() * 100;
    localStorage.setItem("upload_tab", "Product Image");
    localStorage.setItem('randomuppy', ' ');
    let imgDialog;
    $('body').find('.modal').each(function() {
        $(this).remove()
    })
    let randomuppy = Math.random() * 100
    localStorage.setItem('randomuppy', parseInt(randomuppy))
    let template = "<div id='drag-drop-area" + parseInt(randomuppy) + "'><div class='loader'>Loading.....</div></div>";
    imgDialog = new frappe.ui.Dialog({
        title: __('Attachments'),
        fields: [
            { fieldtype: 'HTML', fieldname: 'files_list', options: files_html },
            { fieldtype: 'Column Break', fieldname: 'clb' },
            { fieldtype: 'HTML', fieldname: 'uploader', options: template }
        ],
        primary_action_label: __('Close')
    });

    imgDialog.$wrapper.find('.modal-dialog').css("width", "1030px");
    $('.modal-dialog').css("width", "1070px !important");
    imgDialog.show();
    frappe.require("assets/frappe/js/page_fileupload.js", function() {
        setTimeout(function() {
            $(imgDialog.$wrapper).find('.loader').remove()
            upload_files(parseInt(randomuppy), 'product_images', image_doctype = "Product Image", doctype = "Product", product = data1.name)
        }, 600)
    });
    imgDialog.get_close_btn().on('click', () => {
        this.on_close && this.on_close(this.item);
    });
    $(imgDialog.$wrapper).find('.img-close').on('click', function() {
        let me = this;
        imgid = $(me).attr("data-id");
        console.log(imgid)
        frappe.confirm(__("Do you want to delete the image?"), () => {
            frappe.call({
                method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.api.delete_current_img',
                args: {
                    childname: imgid,
                    doctype: "Product"
                },
                async: false,
                callback: function(data) {
                    $(imgDialog.$wrapper).find('li[data-id="' + imgid + '"]').remove()
                    $(".menu-btn-group .dropdown-menu li a").each(function() {
                        if ($(this).text() == "Reload") {
                            $(this).click();
                            frappe.show_alert(__("Image deleted !"));
                        }
                    });
                    frm.reload_doc();
                }
            })
        });
    })
    $(imgDialog.$wrapper).find('#saveImages').click(function() {
        let length = $(imgDialog.$wrapper).find('div[data-fieldname="files_list"] ul li').length;
        if (length > 0) {
            let count = 0;
            $(imgDialog.$wrapper).find('div[data-fieldname="files_list"] ul li').each(function() {
                let childname = $(this).attr('data-id');
                count = count + 1;
                let image_name = $(this).find('input[name="image_name"]').val();
                let primary = $(this).find('input[name="is_primary"]:checked').val()
                let is_primary = 0;
                if (primary == 'on')
                    is_primary = 1;

                frappe.call({
                    method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.update_image',
                    args: {
                        count: count,
                        image_name: image_name,
                        primary: is_primary,
                        childname: childname
                    },
                    callback: function(r) {


                        imgDialog.hide();

                    }
                });

            })

        } else {
            frappe.throw('Please add images to edit them')
        }
    })
    $(imgDialog.$wrapper).find('.img-edit').click(function() {
        let me = this;
        let imgid = $(me).attr("data-id");
        let check_data = data1.product_images.find(obj => obj.name == imgid);
        $(imgDialog.$wrapper).find('#sortable li[data-id="' + imgid + '"]').find('.imageName').hide();
        $(imgDialog.$wrapper).find('#sortable li[data-id="' + imgid + '"]').find('.editImage').show();
    })
    $(imgDialog.$wrapper).find('div[data-fieldname="files_list"] ul').sortable({
        items: '.image-element',
        opacity: 0.7,
        distance: 30
    });
    $(imgDialog.$wrapper).find('input[name="is_primary"]').on('change', function() {
        let id = $(this).attr('data-id');
        $(imgDialog.$wrapper).find('input[name="is_primary"]').each(function() {
            if ($(this).attr('data-id') != id) {
                $(this).removeAttr('checked')
            }
        })
    })
}