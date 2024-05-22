frappe.provide('core.seoTool');
frappe.pages['seo-tool'].on_page_load = function(wrapper) {
    core.seoTool = new SEOTool(wrapper);
}

class SEOTool {
    constructor(wrapper) {
        this.wrapper = wrapper;
        
        this.active_tab = 'Product';
        this.make();
    }
    make() {
        let me = this;
        this.page = frappe.ui.make_app_page({
            parent: this.wrapper,
            title: 'SEO Tool',
            single_column: true
        });
        this.page.set_primary_action(__("Submit API for Google Indexing"), () => {
            this.update_google_index();
        }, 'fa fa-plus');
        this.page.set_secondary_action(__("Refresh"), () => {
            this.refresh();
        });
        this.page.main.append(frappe.render_template("seo_tool"));
        
        this.page.main.find('a[data-id="business"]').hide();
        
        this.$table_area = this.page.main.find('#listing');
        this.$nav_tabs = this.page.main.find('.nav-tabs');
        this.$nav_tabs.find('a').click(function() {
            let id = $(this).attr('id');
            me.active_tab = id;
            if (id != 'Connect') {
                me.get_data();
            } else {
                me.connect_data();
            }
        })
    }
    refresh() {
        this.get_data();
    }
    get_data() {
        let me = this;
        frappe.call({
            method: 'ecommerce_business_store_singlevendor.accounts.api.get_all_data',
            args: {
                'document_type': me.active_tab
            },
            callback: function(r) {
                let opts = me.make_datatable_opts(r.message);
                if (me.datatable) {
                    me.datatable.refresh(opts.data, opts.columns);
                } else {
                    me.datatable = new DataTable(me.$table_area[0], opts);
                }
            },
        });
    }
    update_google_index() {
        frappe.call({
            method: 'ecommerce_business_store_singlevendor.utils.google_indexing.update_bulk_apiindexing',
            args: {},
            callback: function(r) {

            }
        });
    }
    connect_data() {
        frappe.call({
            method: 'ecommerce_business_store_singlevendor.utils.domain_setup.connect_server',
            args: {},
            callback: function(r) {
                console.log(r)
            }
        })
    }
    make_datatable_opts(data_list) {
        let me = this;
        return {
            columns: [
                { name: 'ID', id: 'id', doctype: 'doctype', docname: 'docname', width: 150, editable: false, resizable: true },
                { name: 'Name', id: 'name', doctype: 'doctype', docname: 'docname', width: 150, editable: false, resizable: true },
                { name: 'Meta Title', id: 'meta_title', doctype: 'doctype', docname: 'docname', width: 300, editable: true, resizable: true },
                { name: 'Meta Keywords', id: 'meta_keywords', doctype: 'doctype', docname: 'docname', width: 300, editable: true, resizable: true },
                { name: 'Meta Description', id: 'meta_description', doctype: 'doctype', docname: 'docname', width: 500, editable: true, align: "left", resizable: true },
            ],
            data: data_list,
            inlineFilters: true,
            treeView: false,
            layout: 'ratio',
            noDataMessage: "No Data Found",
            dynamicRowHeight: true,
            pasteFromClipboard: true,
            cellHeight: null,
            dropdownButton: '▼',
            sortIndicator: {
                asc: '↑',
                desc: '↓',
                none: ''
            },
            getEditor(colIndex, rowIndex, value, parent, column, row, data) {
                let $input = document.createElement('input');
                $input.type = 'text';
                $input.setAttribute('id', 'meta');
                $input.setAttribute('name', 'meta');
                $input.setAttribute('style', 'margin: -7px;padding: 5px;width: 100% !important;');
                if(value)
                    $input.setAttribute('value', value);
                parent.appendChild($input)
                return {
                    initValue(value) {

                        $input.focus();
                        $input.value = value;
                    },
                    setValue(value) {
                        $input.value = value;
                        let cell = me.datatable.datamanager.getCell(colIndex, rowIndex);
                        let fieldname = me.datatable.datamanager.getColumn(colIndex);
                        let docname = data.docname || data.id;
                        let doctype = data.doctype;
                        let fieldname1 = cell.column.id;
                        let value1 = value;
                        frappe.call({
                            method: 'ecommerce_business_store_singlevendor.accounts.api.update_meta_data',
                            args: {
                                'doctype': doctype,
                                'docname': docname,
                                'fieldname': fieldname1,
                                'value': value1
                            },
                            async: false,
                            callback: function(data) {
                                if (has_common(frappe.user_roles, ['Vendor', 'Partner'])) {
                                    update_progress();
                                }
                                me.get_data();
                            }
                        })
                    },
                    getValue() {
                        return $input.value;
                    }
                }
            },
            events: {
                onRemoveColumn(column) {

                },
                onSwitchColumn(column1, column2) {},
                onSortColumn(column) {},
                onCheckRow(row) {}
            },
        }
    }
}

var changedRows = [];
var dt;

frappe.pages['seo-tool'].refresh = function(wrapper) {
    core.seoTool.refresh();
}

function set_control_value(doctype, docname, fieldname, value) {

    frappe.call({
        method: 'ecommerce_business_store_singlevendor.ecommerce_business_store_singlevendor.doctype.product.product.insert_bulk_data',
        args: {
            'name': docname,
            'value': value
        },
        async: false,
        callback: function(data) {

        }
    })
}

var update_progress = function() {
    let business = frappe.boot.user.defaults.business;
    if (business) {
        let business_setup = frappe.boot.sysdefaults.business_defaults[business];
        if (business_setup) {
            let opts = JSON.parse(business_setup);
            if (opts.indexOf('SEO') < 0) {
                opts.push('SEO');
                frappe.boot.sysdefaults.business_defaults[business] = JSON.stringify(opts);
                core.update_default(business, JSON.stringify(opts));
                frappe.ui.toolbar.clear_cache();
            }
        }
    }
}