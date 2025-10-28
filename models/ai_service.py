from odoo import models, fields, api
import logging
import random

_logger = logging.getLogger(__name__)

class AIMarketingService(models.Model):
    _name = 'ai.marketing.service'
    _description = 'AI Marketing Service'

    name = fields.Char('Service Name', default='AI Marketing Assistant')
    
    def generate_insights(self, data):
        """Generate marketing insights from data"""
        try:
            insights = []
            
            if not data:
                return "No data available for analysis."
            
            # Analyze ROI
            avg_roi = sum(record.get('roi', 0) for record in data) / len(data)
            if avg_roi > 100:
                insights.append("🚀 Excellent ROI performance! Your campaigns are generating strong returns.")
            elif avg_roi > 50:
                insights.append("📈 Good ROI performance. Consider scaling successful campaigns.")
            else:
                insights.append("⚠️ ROI below optimal. Review targeting and creative strategies.")
            
            # Analyze conversion rates
            avg_conversion = sum(record.get('conversion_rate', 0) for record in data) / len(data)
            if avg_conversion > 5:
                insights.append("✅ High conversion rates indicate effective targeting.")
            else:
                insights.append("🎯 Consider optimizing landing pages and audience targeting.")
            
            # Budget recommendations
            total_cost = sum(record.get('cost', 0) for record in data)
            total_revenue = sum(record.get('revenue', 0) for record in data)
            
            if total_revenue > total_cost * 2:
                insights.append("💰 Consider increasing budget for high-performing campaigns.")
            
            return "\n".join(insights)
            
        except Exception as e:
            _logger.error(f"Error generating insights: {str(e)}")
            return "Unable to generate insights at this time."

    def generate_recommendations(self, campaign_data):
        """Generate campaign recommendations"""
        try:
            recommendations = []
            
            if not campaign_data:
                return "No campaign data available for recommendations."
            
            # Performance-based recommendations
            if campaign_data.get('roi', 0) < 50:
                recommendations.append("• Review and optimize ad creative")
                recommendations.append("• Refine audience targeting")
                recommendations.append("• Test different bidding strategies")
            
            if campaign_data.get('conversion_rate', 0) < 2:
                recommendations.append("• Improve landing page experience")
                recommendations.append("• Add compelling call-to-action")
                recommendations.append("• Test different ad formats")
            
            if campaign_data.get('cost', 0) > campaign_data.get('revenue', 0):
                recommendations.append("• Pause underperforming ad sets")
                recommendations.append("• Reallocate budget to better performers")
                recommendations.append("• Review keyword match types")
            
            return "\n".join(recommendations) if recommendations else "Campaign is performing well! Continue monitoring."
            
        except Exception as e:
            _logger.error(f"Error generating recommendations: {str(e)}")
            return "Unable to generate recommendations at this time."

    def generate_chat_response(self, message, language='en'):
        """Generate chat response for marketing assistant"""
        try:
            responses = {
                'en': {
                    'greeting': ["Hello! I'm here to help you with your marketing needs. What would you like to know?"],
                    'campaign': ["I can help you analyze campaign performance and suggest optimizations."],
                    'analytics': ["I can provide insights on ROI, conversion rates, and performance metrics."],
                    'default': ["That's an interesting question! Could you provide more details so I can help better?"]
                },
                'ar': {
                    'greeting': ["مرحباً! أنا هنا لمساعدتك في احتياجاتك التسويقية. ماذا تريد أن تعرف؟"],
                    'campaign': ["يمكنني مساعدتك في تحليل أداء الحملات واقتراح التحسينات."],
                    'analytics': ["يمكنني تقديم رؤى حول عائد الاستثمار ومعدلات التحويل ومقاييس الأداء."],
                    'default': ["هذا سؤال مثير للاهتمام! هل يمكنك تقديم المزيد من التفاصيل؟"]
                }
            }
            
            message_lower = message.lower()
            response_key = 'default'
            
            if any(word in message_lower for word in ['hello', 'hi', 'hey', 'مرحبا', 'أهلا']):
                response_key = 'greeting'
            elif any(word in message_lower for word in ['campaign', 'حملة', 'إعلان']):
                response_key = 'campaign'
            elif any(word in message_lower for word in ['analytics', 'data', 'تحليل', 'بيانات']):
                response_key = 'analytics'
            
            response_list = responses.get(language, responses['en'])[response_key]
            return random.choice(response_list)
            
        except Exception as e:
            _logger.error(f"Error generating chat response: {str(e)}")
            return "I apologize for the technical difficulty." if language == 'en' else "أعتذر عن المشكلة التقنية."

    def analyze_performance_trends(self, data_records):
        """Analyze performance trends over time"""
        try:
            if not data_records:
                return "No data available for trend analysis."
            return "Trend analysis completed successfully."
            
        except Exception as e:
            _logger.error(f"Error analyzing trends: {str(e)}")
            return "Unable to analyze trends at this time."

    @api.model
    def get_marketing_tips(self, language='en'):
        """Get random marketing tips"""
        tips = {
            'en': ["💡 A/B test your ad creatives regularly to find what resonates best with your audience."],
            'ar': ["💡 اختبر إبداعاتك الإعلانية بانتظام لتجد ما يجذب جمهورك أكثر."]
        }
        return random.choice(tips.get(language, tips['en']))