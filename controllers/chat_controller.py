from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class MarketingChatController(http.Controller):
    
    @http.route('/ai_marketing_assistant/chat', type='json', auth='user', methods=['POST'])
    def chat_response(self, message, language='en'):
        try:
            # Get AI service
            ai_service = request.env['ai.marketing.service']
            
            # Generate response based on actual database data
            response = ai_service.generate_chat_response(message, language)
            
            return {'response': response}
            
        except Exception as e:
            _logger.error(f"Chat error: {str(e)}")
            error_msg = {
                'en': "I apologize, but I'm experiencing technical difficulties accessing the marketing data.",
                'ar': "أعتذر، ولكنني أواجه صعوبات تقنية في الوصول لبيانات التسويق."
            }
            return {'response': error_msg.get(language, error_msg['en'])}