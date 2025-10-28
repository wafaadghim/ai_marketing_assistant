from odoo import models, fields, api

class MarketingData(models.Model):
    _name = 'marketing.data'
    _description = 'Marketing Performance Data'
    _rec_name = 'name'

    name = fields.Char('Campaign Name', required=True)
    channel_id = fields.Many2one('utm.medium', 'Channel', required=True)
    cost = fields.Float('Cost', required=True)
    revenue = fields.Float('Revenue', required=True)
    conversions = fields.Integer('Conversions', default=0)
    conversion_rate = fields.Float('Conversion Rate', compute='_compute_conversion_rate', store=True)
    roi = fields.Float('ROI', compute='_compute_roi', store=True)
    date_from = fields.Date('From Date')
    date_to = fields.Date('To Date')
    status = fields.Selection([
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed')
    ], string='Status', default='active')

    @api.depends('cost', 'conversions')
    def _compute_conversion_rate(self):
        for record in self:
            if record.cost > 0:
                record.conversion_rate = (record.conversions / record.cost) * 100
            else:
                record.conversion_rate = 0.0

    @api.depends('cost', 'revenue')
    def _compute_roi(self):
        for record in self:
            if record.cost > 0:
                record.roi = ((record.revenue - record.cost) / record.cost) * 100
            else:
                record.roi = 0.0