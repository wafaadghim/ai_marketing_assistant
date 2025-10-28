from odoo import http, fields
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
            
            # Generate response based on actual database data from ai_marketing
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
        """Test endpoint for database connection to ai_marketing"""
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
                    'message': f'Database ai_marketing connected successfully! Found {count} campaigns.',
                    'count': count
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to connect to ai_marketing database'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection error to ai_marketing: {str(e)}'
            }

    @http.route('/ai_marketing_assistant/get_module_stats', type='json', auth='user')
    def get_module_statistics(self):
        """Récupère les statistiques des modules installés depuis la base ai_marketing"""
        try:
            ai_service = request.env['ai.marketing.service']
            
            # Récupérer les stats des campagnes depuis ai_marketing
            stats_query = """
                SELECT 
                    COUNT(*) as total_campaigns,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_campaigns,
                    SUM(cost) as total_cost,
                    SUM(revenue) as total_revenue,
                    SUM(conversions) as total_conversions,
                    AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as avg_roi
                FROM marketing_data
            """
            
            stats = ai_service._query_marketing_data(stats_query)
            
            if stats and stats[0]:
                return {
                    'success': True,
                    'stats': stats[0],
                    'message': 'Module statistics retrieved successfully from ai_marketing database'
                }
            else:
                return {
                    'success': False,
                    'message': 'No data found in ai_marketing database'
                }
                
        except Exception as e:
            _logger.error(f"Error getting module stats: {str(e)}")
            return {
                'success': False,
                'message': f'Error retrieving module statistics: {str(e)}'
            }

    @http.route('/ai_marketing_assistant/get_installed_modules', type='json', auth='user')
    def get_installed_modules_info(self):
        """Récupère les informations sur les modules installés et leurs données"""
        try:
            # Informations sur les modules Odoo installés
            installed_modules = request.env['ir.module.module'].search([
                ('state', '=', 'installed'),
                '|', ('name', 'ilike', 'marketing'), 
                ('name', 'ilike', 'ai_marketing_assistant')
            ])
            
            modules_info = []
            for module in installed_modules:
                modules_info.append({
                    'name': module.name,
                    'display_name': module.display_name,
                    'version': module.latest_version,
                    'state': module.state,
                    'summary': module.summary or 'No summary available'
                })
            
            # Récupérer aussi les données de la base ai_marketing
            ai_service = request.env['ai.marketing.service']
            marketing_data = ai_service._query_marketing_data(
                "SELECT COUNT(*) as count FROM marketing_data"
            )
            
            return {
                'success': True,
                'installed_modules': modules_info,
                'ai_marketing_campaigns': marketing_data[0]['count'] if marketing_data else 0,
                'message': f'Found {len(modules_info)} marketing-related modules installed'
            }
            
        except Exception as e:
            _logger.error(f"Error getting installed modules: {str(e)}")
            return {
                'success': False,
                'message': f'Error retrieving installed modules: {str(e)}'
            }

    def test_chat_integration(self):
        """Test l'intégration complète du chatbot avec la base ai_marketing"""
        try:
            # Tester le service AI avec des questions sur les modules
            ai_service = request.env['ai.marketing.service']
            
            # Test des différents types de questions sur les modules et données
            test_questions = [
                ('Hello', 'en'),
                ('Show me my campaigns from ai_marketing database', 'en'),
                ('What is my ROI from the installed modules?', 'en'),
                ('How many marketing campaigns do I have?', 'en'),
                ('Bonjour', 'fr'),
                ('Montrez-moi mes campagnes de la base ai_marketing', 'fr'),
                ('Quel est mon ROI des modules installés?', 'fr'),
                ('مرحبا', 'ar'),
                ('أظهر لي حملاتي من قاعدة البيانات', 'ar')
            ]
            
            results = []
            results.append("🤖 CHAT INTEGRATION TEST WITH AI_MARKETING DATABASE:\n")
            
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
            
            # Test de connexion à la base ai_marketing
            try:
                connection = ai_service._get_pg_connection()
                if connection:
                    cursor = connection.cursor()
                    cursor.execute("SELECT COUNT(*) FROM marketing_data")
                    count = cursor.fetchone()[0]
                    results.append(f"🔗 Database Connection: ✅ Connected to ai_marketing")
                    results.append(f"📊 Found {count} campaigns in ai_marketing database")
                    cursor.close()
                    connection.close()
                else:
                    results.append("🔗 Database Connection: ❌ Failed to connect to ai_marketing")
            except Exception as e:
                results.append(f"🔗 Database Connection: ❌ Error: {str(e)}")
            
            test_results_text = "\n".join(results)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Chat Integration Test Complete',
                    'message': 'Chat integration with ai_marketing database tested successfully!',
                    'type': 'success'
                }
            }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Chat Test Failed',
                    'message': f'Error testing chat integration: {str(e)}',
                    'type': 'danger'
                }
            }