from odoo import models, fields, api
from datetime import datetime, timedelta
import json

class ChatAssistant(models.Model):
    _name = 'chat.assistant'
    _description = 'Marketing Chat Assistant'

    name = fields.Char('Session ID')
    user_input = fields.Text('User Question')
    ai_response = fields.Text('AI Response')
    session_date = fields.Datetime('Session Date', default=fields.Datetime.now)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)

    @api.model
    def process_query(self, query):
        """Process user query and return AI response"""
        query_lower = query.lower()
        response = ""

        if 'best channel' in query_lower or 'top performing' in query_lower:
            response = self._get_best_channel()
        elif 'worst performing' in query_lower or 'low performance' in query_lower:
            response = self._get_worst_campaigns()
        elif 'conversion rate' in query_lower:
            response = self._get_conversion_analysis()
        elif 'roi' in query_lower or 'return on investment' in query_lower:
            response = self._get_roi_analysis()
        elif 'campaign' in query_lower and 'report' in query_lower:
            response = self._get_campaign_report()
        else:
            response = "I can help you with:\n- Best performing channels\n- Campaign performance reports\n- Conversion rate analysis\n- ROI analysis\n- Low performing campaigns\n\nPlease ask me a specific question about your marketing data."

        # Save the conversation
        self.create({
            'name': f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'user_input': query,
            'ai_response': response
        })

        return response

    def _get_best_channel(self):
        """Get best performing channel"""
        campaigns = self.env['marketing.data'].search([])
        
        if not campaigns:
            return "No marketing data available for analysis."

        # Group by channel and calculate average ROI
        channel_performance = {}
        for campaign in campaigns:
            channel = campaign.channel_id.name
            if channel not in channel_performance:
                channel_performance[channel] = {
                    'total_roi': 0,
                    'count': 0,
                    'total_conversion_rate': 0
                }
            channel_performance[channel]['total_roi'] += campaign.roi
            channel_performance[channel]['total_conversion_rate'] += campaign.conversion_rate
            channel_performance[channel]['count'] += 1

        # Find best channel
        best_channel = None
        best_avg_roi = -float('inf')
        
        for channel, data in channel_performance.items():
            avg_roi = data['total_roi'] / data['count']
            if avg_roi > best_avg_roi:
                best_avg_roi = avg_roi
                best_channel = channel

        return f"📊 Best Performing Channel: {best_channel}\nAverage ROI: {best_avg_roi:.2f}%"

    def _get_worst_campaigns(self):
        """Get worst performing campaigns"""
        campaigns = self.env['marketing.data'].search([], order='roi asc', limit=5)
        
        if not campaigns:
            return "No marketing data available."

        response = "📉 Worst Performing Campaigns:\n"
        for i, campaign in enumerate(campaigns, 1):
            response += f"{i}. {campaign.name}: ROI {campaign.roi:.2f}%, Cost ${campaign.cost:.2f}\n"

        return response

    def _get_conversion_analysis(self):
        """Get conversion rate analysis"""
        campaigns = self.env['marketing.data'].search([])
        
        if not campaigns:
            return "No marketing data available."

        total_conversions = sum(campaign.conversions for campaign in campaigns)
        total_cost = sum(campaign.cost for campaign in campaigns)
        avg_conversion_rate = sum(campaign.conversion_rate for campaign in campaigns) / len(campaigns)

        return f"🎯 Conversion Analysis:\nTotal Conversions: {total_conversions}\nTotal Cost: ${total_cost:.2f}\nAverage Conversion Rate: {avg_conversion_rate:.2f}%"

    def _get_roi_analysis(self):
        """Get ROI analysis"""
        campaigns = self.env['marketing.data'].search([])
        
        if not campaigns:
            return "No marketing data available."

        total_revenue = sum(campaign.revenue for campaign in campaigns)
        total_cost = sum(campaign.cost for campaign in campaigns)
        total_roi = ((total_revenue - total_cost) / total_cost) * 100 if total_cost > 0 else 0
        avg_roi = sum(campaign.roi for campaign in campaigns) / len(campaigns)

        return f"💰 ROI Analysis:\nTotal Revenue: ${total_revenue:.2f}\nTotal Cost: ${total_cost:.2f}\nOverall ROI: {total_roi:.2f}%\nAverage Campaign ROI: {avg_roi:.2f}%"

    def _get_campaign_report(self):
        """Get comprehensive campaign report"""
        campaigns = self.env['marketing.data'].search([], limit=10)
        
        if not campaigns:
            return "No campaign data available."

        response = "📈 Campaign Performance Report:\n"
        for campaign in campaigns:
            status_icon = "🟢" if campaign.status == 'active' else "🟡" if campaign.status == 'paused' else "🔴"
            response += f"{status_icon} {campaign.name}\n   ROI: {campaign.roi:.2f}% | Cost: ${campaign.cost:.2f} | Conv Rate: {campaign.conversion_rate:.2f}%\n"

        return response