from odoo import http
from odoo.http import request
import logging
import json

_logger = logging.getLogger(__name__)

class MarketingChatController(http.Controller):
    
    @http.route('/ai_marketing_assistant/chat', type='json', auth='user', methods=['POST'])
    def chat_response(self, message, language='en'):
        try:
            _logger.info(f"Chat request received: {message} (language: {language})")
            
            # Get AI service
            ai_service = request.env['ai.marketing.service']
            
            # Generate response based on actual database data
            response = ai_service.generate_chat_response(message, language)
            
            _logger.info(f"Chat response generated successfully")
            
            return {
                'response': response,
                'success': True,
                'timestamp': fields.Datetime.now().isoformat()
            }
            
        except Exception as e:
            _logger.error(f"Chat error: {str(e)}")
            
            error_messages = {
                'fr': "Désolé, je rencontre des difficultés techniques pour accéder aux données marketing.",
                'en': "I apologize, but I'm experiencing technical difficulties accessing the marketing data.",
                'ar': "أعتذر، ولكنني أواجه صعوبات تقنية في الوصول لبيانات التسويق."
            }
            
            return {
                'response': error_messages.get(language, error_messages['en']),
                'success': False,
                'error': str(e)
            }

    @http.route('/ai_marketing_assistant/test_connection', type='json', auth='user')
    def test_database_connection(self):
        """Test endpoint for database connection"""
        try:
            ai_service = request.env['ai.marketing.service']
            connection = ai_service._get_pg_connection()
            
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM marketing_data;")
                count = cursor.fetchone()[0]
                cursor.close()
                connection.close()
                
                return {
                    'success': True,
                    'message': f'Database connected successfully! Found {count} campaigns.',
                    'count': count
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to connect to database'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection error: {str(e)}'
            }

    def test_chat_integration(self):
        """Test l'intégration complète du chatbot avec la base ai_marketing"""
        try:
            # Tester le service AI
            ai_service = self.env['ai.marketing.service']
            
            # Test des différents types de questions
            test_questions = [
                ('Hello', 'en'),
                ('Show me my campaigns', 'en'),
                ('What is my ROI?', 'en'),
                ('Bonjour', 'fr'),
                ('Montrez-moi mes campagnes', 'fr'),
                ('مرحبا', 'ar')
            ]
            
            results = []
            results.append("🤖 CHAT INTEGRATION TEST RESULTS:\n")
            
            for question, lang in test_questions:
                try:
                    response = ai_service.generate_chat_response(question, lang)
                    results.append(f"✅ Question: '{question}' ({lang})")
                    results.append(f"   Response: {response[:100]}...")
                    results.append("")
                except Exception as e:
                    results.append(f"❌ Question: '{question}' ({lang})")
                    results.append(f"   Error: {str(e)}")
                    results.append("")
            
            self.test_results = "\n".join(results)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Chat Integration Test',
                    'message': 'Chat integration test completed! Check Test Results tab.',
                    'type': 'success'
                }
            }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Chat Test Failed',
                    'message': f'Error: {str(e)}',
                    'type': 'danger'
                }
            }