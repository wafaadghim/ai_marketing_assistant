from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class AIAssistant(models.Model):
    _name = 'ai.assistant'
    _description = 'AI Marketing Assistant'

    name = fields.Char('Recommendation Title', required=True)
    recommendation_type = fields.Selection([
        ('stop_campaign', 'Stop Campaign'),
        ('increase_budget', 'Increase Budget'),
        ('optimize_ad', 'Optimize Ad'),
        ('channel_shift', 'Channel Shift')
    ], string='Type', required=True)
    campaign_id = fields.Many2one('marketing.data', 'Campaign')
    reason = fields.Text('Reason')
    impact_score = fields.Float('Impact Score', help='Expected impact (0-100)')
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], string='Priority', default='medium')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('applied', 'Applied'),
        ('rejected', 'Rejected')
    ], string='Status', default='pending')

    @api.model
    def generate_recommendations(self):
        """Generate AI recommendations based on marketing data"""
        campaigns = self.env['marketing.data'].search([])
        recommendations = []

        for campaign in campaigns:
            # Analyze campaign performance
            if campaign.roi < 0 and campaign.cost > 1000:
                # Stop campaign recommendation
                recommendations.append({
                    'name': f"Stop Campaign: {campaign.name}",
                    'recommendation_type': 'stop_campaign',
                    'campaign_id': campaign.id,
                    'reason': f"High cost ({campaign.cost}) with negative ROI ({campaign.roi:.2f}%)",
                    'impact_score': 85.0,
                    'priority': 'high'
                })

            # Increase budget for high-performing campaigns
            elif campaign.conversion_rate > 10 and campaign.roi > 50:
                recommendations.append({
                    'name': f"Increase Budget: {campaign.name}",
                    'recommendation_type': 'increase_budget',
                    'campaign_id': campaign.id,
                    'reason': f"High conversion rate ({campaign.conversion_rate:.2f}%) and ROI ({campaign.roi:.2f}%)",
                    'impact_score': 75.0,
                    'priority': 'medium'
                })

        # Create recommendation records
        for rec_data in recommendations:
            self.create(rec_data)

        return len(recommendations)

    def apply_recommendation(self):
        """Apply the selected recommendation"""
        for recommendation in self:
            if recommendation.recommendation_type == 'stop_campaign':
                recommendation.campaign_id.status = 'paused'
            elif recommendation.recommendation_type == 'increase_budget':
                # Implement budget increase logic
                pass
            
            recommendation.status = 'applied'