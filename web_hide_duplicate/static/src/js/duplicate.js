openerp.web_hide_duplicate = function (instance) {
    var _t = instance.web._t;

    instance.web.FormView.include({
        load_form: function(data) {
            this._super(data);
            // Now lets delete duplicate button from <More> section.
            if (!this.is_action_enabled('duplicate')) {
                var no_dup = _.reject(this.sidebar.items.other, function (item) {
                    return item.label === _t('Duplicate');
                });
                this.sidebar.items.other = no_dup;
            }
        }
    });
};
