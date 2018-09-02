openerp.web_pivot_table = function (instance) {
'use strict';
var _lt = instance.web._lt;
var _t = instance.web._t;

// odoo.define('web.PivotView', function (require) {
// "use strict";
/*---------------------------------------------------------
 * Odoo Pivot Table view
 *---------------------------------------------------------*/

var core = instance.web.core;
var formats = instance.web.formats;
var framework = instance.web.framework;
var Model = instance.web.Model;
var Sidebar = instance.web.Sidebar;
var View = instance.web.View;
var Graph = instance.web_graph.Graph

var QWeb = instance.web.qweb;
var total = _lt("Total");

Graph.include({
    events: {
        'click .graph_mode_selection label' : 'mode_selection',
        'click .graph_measure_selection li' : 'measure_selection',
        'click .graph_options_selection label' : 'option_selection',
        'click .graph_heatmap label' : 'heatmap_mode_selection',
        'click .web_graph_click' : 'header_cell_clicked',
        'click a.field-selection' : 'field_selection',
        'click td': 'on_cell_click',
    },
    make_cell: function (row, col, value, index, raw) {
        var formatted_value = raw && !_.isUndefined(value) ? value : openerp.web.format_value(value, {type:this.pivot.measures[index].type}),
            cell = {value:formatted_value};
        cell['row_id'] = row.id;
        cell['col_id'] = col.id;
        if (this.heatmap_mode === 'none') { return cell; }
        var total = (this.heatmap_mode === 'both') ? this.pivot.get_total()[index]
                  : (this.heatmap_mode === 'row')  ? this.pivot.get_total(row)[index]
                  : this.pivot.get_total(col)[index];
        var color = Math.floor(90 + 165*(total - Math.abs(value))/total);
        if (color < 255) {
            cell.color = color;
        }
        return cell;
    },
    draw_row: function (row, frozen_rows) {
        var $row = $('<tr>')
            .attr('data-indent', row.indent)
            .append(this.make_header_cell(row, frozen_rows));
        
        var cells_length = row.cells.length;
        var cells_list = [];
        var cell, hcell;
        
        for (var j = 0; j < cells_length; j++) {
            cell = row.cells[j];
            hcell = '<td class="oe-enable-linking"';
            if (cell.is_bold || cell.color) {
                hcell += ' style="';
                if (cell.is_bold) hcell += 'font-weight: bold;';
                if (cell.color) hcell += 'background-color:' + $.Color(255, cell.color, cell.color) + ';';
                hcell += '"';
            }
            hcell += ' col-id='+cell['col_id'];
            hcell += ' row-id='+row.id;

            
            hcell += '>' + cell.value + '</td>';
            cells_list[j] = hcell;
        }
        return $row.append(cells_list.join(''));
    },
    on_cell_click: function (event) {
        var $target = $(event.target);

        var id = event.target.getAttribute('data-id'),
            header = this.pivot.get_header(id);
        if ($target.hasClass('oe-closed') 
            || $target.hasClass('oe-opened') 
            || $target.hasClass('oe-empty')
            || id
            ) {
            return;
        }
        var targetPivot = this.pivot;
        
        var row_id = $target.attr('row-id'),
            col_id = event.target.getAttribute('col-id');
        
        var curr_row,curr_col;
        _.map(targetPivot.rows.headers, function(r){
            if(r.id === row_id){
                curr_row = r;
            }
        });
        _.map(targetPivot.cols.headers, function(c){
            if(c.id === col_id){
                curr_col = c;
            }
        });
        var row_domain = curr_row.domain,
            col_domain = curr_col.domain,
            context = _.omit(_.clone(this.context), 'group_by');
        var res_model = this.model.name;

        //Add your conditions here to open custom view of your choice.

        if (res_model === 'sale.report'){
            res_model = 'sale.order';
            _.map(col_domain, function(d){
                if(d[0] === 'date'){
                    d[0] = 'date_order';
                }
            });
        }
        else if (res_model === 'purchase.report'){
            res_model = 'purchase.order';
            _.map(col_domain, function(d){
                if(d[0] === 'date'){
                    d[0] = 'date_order';
                }
            });
        }
        else if (res_model === 'account.invoice.report'){
            res_model = 'account.invoice';
            _.map(col_domain, function(d){
                if(d[0] === 'date'){
                    d[0] = 'date_invoice';
                }
            });
        }
        else if (res_model === 'crm.lead.report'){
            res_model = 'crm.lead';
            _.map(col_domain, function(d){
                if(d[0] === 'date_deadline'){
                    d[0] = 'date_deadline';
                }
            });
        }
        else if (res_model === 'crm.opportunity.report'){
            res_model = 'crm.lead';
            _.map(col_domain, function(d){
                if(d[0] === 'date_deadline'){
                    d[0] = 'date_deadline';
                }
            });
        }
        else if (res_model === 'crm.phonecall.report'){
            res_model = 'crm.phonecall';
            _.map(col_domain, function(d){
                if(d[0] === 'date_closed'){
                    d[0] = 'date_closed';
                }
            });
        }
        else if (res_model === 'account.entries.report'){
            res_model = 'account.move.line';
            _.map(col_domain, function(d){
                if(d[0] === 'date'){
                    d[0] = 'date';
                }
            });
        }
        var action = {
            type: 'ir.actions.act_window',
            name: this.title,
            res_model: res_model,
            views: [[false, 'list'], [false, 'form']],
            view_type: 'tree',
            view_mode: 'tree,form',
            target: 'current',
            context: context,
            domain: this.domain.concat(row_domain, col_domain),
        };
        var self = this;
        context = this.pivot_options.context;
        var ctx_module_name = context.ctx_module_name; // pass 'ctx_module_name' in context
        var ctx_view_xml_id = context.ctx_view_xml_id; // pass 'ctx_view_xml_id' in context 
        console.log(context);
        if(ctx_module_name && ctx_view_xml_id){
            var id = false;
            new Model('ir.model.data').call('get_object_reference',[ctx_module_name, ctx_view_xml_id]).then(function(result) {
                if(result){
                    id = result[1];
                }
            }).pipe(function(){
                new Model('ir.actions.act_window').call('read', [[id],[]], context=self.context).done(function(res){
                    if(res.length > 0){
                        res = res[0]
                        res['domain'] = self.domain.concat(row_domain, col_domain);
                        return self.do_action(res);
                    }
                    else{
                        return self.do_action(action);
                    }
                });
            });
        }else{
            return self.do_action(action);
        }
        
    },

});

};

