openerp.web_hide_toolbar = function (instance) {
    instance.web.WebClient.include({
        start: function () {
            var toolbar = $.deparam.querystring().toolbar;
            if (toolbar === 'hide'){
                this.hidetoolbar()
            }
            return this._super();
        },
        hidetoolbar: function(ev) {
            $("#oe_main_menu_navbar").hide();
        },
    });
    instance.web.View.include({
        start: function () {
            var toolbar = $.deparam.querystring().toolbar;
            if (toolbar === 'hide'){
                this.hidetoolbar()
            }
            return this._super();
        },
        hidetoolbar: function(ev) {
            $(".oe_leftbar").hide();
        },
    });
};
