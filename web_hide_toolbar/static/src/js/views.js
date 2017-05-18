openerp.web_hide_toolbar = function (instance) {
    instance.web.WebClient.include({
        start: function () {
            var toolbar = $.deparam.querystring().toolbar;
            if (toolbar === 'hide'){
                this.showsheetonly()
            }
            return this._super();
        },
        showsheetonly: function(ev) {
            $("#oe_main_menu_navbar, .oe_leftbar, .oe_view_manager_header, .oe_chatter").hide();
            $('.oe_form_sheetbg').css('border-bottom','0px');
            $('body, .oe_view_manager_body').css('background','url(/web/static/src/img/form_sheetbg.png)');
        },
    });
    
    instance.web.View.include({
        start: function () {
            var toolbar = $.deparam.querystring().toolbar;
            if (toolbar === 'hide'){
                this.showsheetonly()
            }
            return this._super();
        },
        showsheetonly: function(ev) {
        	$("#oe_main_menu_navbar, .oe_leftbar, .oe_view_manager_header, .oe_chatter").hide();
            $('.oe_form_sheetbg').css('border-bottom','0px');
            $('body, .oe_view_manager_body').css('background','url(/web/static/src/img/form_sheetbg.png)');
        },
    });
};
