from odoo import models, fields, api
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import json

_logger = logging.getLogger(__name__)

class AIMarketingService(models.Model):
    _name = 'ai.marketing.service'
    _description = 'AI Marketing Service'

    name = fields.Char('Service Name', default='AI Marketing Assistant')
    
    def _get_pg_connection(self):
        """Get PostgreSQL connection to ai_marketing database"""
        try:
            # Utiliser les mêmes paramètres que le test de connexion
            connection = psycopg2.connect(
                host="localhost",
                database="ai_marketing",
                user="odoo",  # Même utilisateur que dans le test
                password="odoo",  # Même mot de passe que dans le test
                port="5432"
            )
            return connection
        except Exception as e:
            _logger.error(f"Failed to connect to ai_marketing database: {str(e)}")
            return None

    def _query_marketing_data(self, query, params=None):
        """Execute query on ai_marketing database"""
        connection = self._get_pg_connection()
        if not connection:
            return None
        
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            _logger.error(f"Database query error: {str(e)}")
            return None
        finally:
            connection.close()

    def generate_chat_response(self, message, language='en'):
        """Generate intelligent chat response based on actual data"""
        try:
            message_lower = message.lower()
            
            # Détection du type de question avec mots-clés français et anglais
            if any(word in message_lower for word in ['campaign', 'campaigns', 'campagne', 'campagnes', 'حملة', 'حملات']):
                return self._handle_campaign_question(message, language)
            elif any(word in message_lower for word in ['roi', 'return', 'profit', 'rentabilité', 'bénéfice', 'عائد', 'ربح']):
                return self._handle_roi_question(message, language)
            elif any(word in message_lower for word in ['conversion', 'convert', 'conversions', 'تحويل', 'تحويلات']):
                return self._handle_conversion_question(message, language)
            elif any(word in message_lower for word in ['performance', 'performances', 'résultats', 'أداء', 'نتائج']):
                return self._handle_performance_question(message, language)
            elif any(word in message_lower for word in ['budget', 'cost', 'coût', 'coûts', 'ميزانية', 'تكلفة']):
                return self._handle_budget_question(message, language)
            elif any(word in message_lower for word in ['hello', 'hi', 'bonjour', 'salut', 'مرحبا', 'أهلا']):
                return self._get_greeting_with_stats(language)
            elif any(word in message_lower for word in ['help', 'aide', 'أساعدك', 'مساعدة']):
                return self._get_help_message(language)
            else:
                return self._handle_general_question(message, language)
                
        except Exception as e:
            _logger.error(f"Error generating chat response: {str(e)}")
            return self._get_error_response(language)

    def _handle_campaign_question(self, message, language):
        """Handle campaign-related questions with real data"""
        query = """
            SELECT name, cost, revenue, conversions, status, 
                   CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END as roi
            FROM marketing_data 
            ORDER BY roi DESC 
            LIMIT 5
        """
        
        campaigns = self._query_marketing_data(query)
        if not campaigns:
            return {
                'en': "I couldn't find campaign data in the database. Please check if data exists.",
                'fr': "Je n'ai pas trouvé de données de campagne dans la base. Vérifiez si des données existent.",
                'ar': "لم أتمكن من العثور على بيانات حملات في قاعدة البيانات."
            }.get(language, "No campaign data available.")
        
        if language == 'fr':
            response = f"📊 Voici vos meilleures campagnes :\n\n"
            for i, camp in enumerate(campaigns, 1):
                response += f"{i}. {camp['name']}\n"
                response += f"   💰 ROI: {camp['roi']:.1f}%\n"
                response += f"   💵 Revenus: ${camp['revenue']:,.0f}\n"
                response += f"   🎯 Conversions: {camp['conversions']}\n"
                response += f"   📊 Statut: {camp['status']}\n\n"
            
            best_campaign = campaigns[0]
            response += f"🏆 Meilleure performance : {best_campaign['name']} avec {best_campaign['roi']:.1f}% de ROI !"
        
        elif language == 'en':
            response = f"📊 Here are your top campaigns:\n\n"
            for i, camp in enumerate(campaigns, 1):
                response += f"{i}. {camp['name']}\n"
                response += f"   💰 ROI: {camp['roi']:.1f}%\n"
                response += f"   💵 Revenue: ${camp['revenue']:,.0f}\n"
                response += f"   🎯 Conversions: {camp['conversions']}\n"
                response += f"   📊 Status: {camp['status']}\n\n"
            
            best_campaign = campaigns[0]
            response += f"🏆 Best performer: {best_campaign['name']} with {best_campaign['roi']:.1f}% ROI!"
        
        else:  # Arabic
            response = f"📊 إليك أفضل حملاتك:\n\n"
            for i, camp in enumerate(campaigns, 1):
                response += f"{i}. {camp['name']}\n"
                response += f"   💰 عائد استثمار: {camp['roi']:.1f}%\n"
                response += f"   💵 إيرادات: ${camp['revenue']:,.0f}\n"
                response += f"   🎯 تحويلات: {camp['conversions']}\n"
                response += f"   📊 حالة: {camp['status']}\n\n"
            
            best_campaign = campaigns[0]
            response += f"🏆 الأفضل أداءً: {best_campaign['name']} بعائد استثمار {best_campaign['roi']:.1f}%!"
        
        return response

    def _handle_roi_question(self, message, language):
        """Handle ROI questions with real data"""
        query = """
            SELECT 
                AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as avg_roi,
                COUNT(*) as total_campaigns,
                COUNT(CASE WHEN ((revenue - cost) / cost) * 100 > 100 THEN 1 END) as profitable_campaigns,
                MAX(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as best_roi,
                SUM(revenue) as total_revenue,
                SUM(cost) as total_cost
            FROM marketing_data 
            WHERE status IN ('active', 'completed')
        """
        
        data = self._query_marketing_data(query)
        if not data or not data[0]:
            return {
                'en': "No ROI data available in the database.",
                'fr': "Aucune donnée de ROI disponible dans la base.",
                'ar': "لا توجد بيانات عائد استثمار متاحة."
            }.get(language, "No ROI data available.")
        
        stats = data[0]
        overall_roi = ((stats['total_revenue'] - stats['total_cost']) / stats['total_cost']) * 100 if stats['total_cost'] > 0 else 0
        
        if language == 'fr':
            response = f"💰 Analyse du ROI :\n\n"
            response += f"📊 ROI moyen: {stats['avg_roi']:.1f}%\n"
            response += f"🎯 Campagnes rentables: {stats['profitable_campaigns']}/{stats['total_campaigns']}\n"
            response += f"🏆 Meilleur ROI: {stats['best_roi']:.1f}%\n"
            response += f"💵 Revenus totaux: ${stats['total_revenue']:,.0f}\n"
            response += f"💸 Coûts totaux: ${stats['total_cost']:,.0f}\n"
            response += f"📈 ROI global: {overall_roi:.1f}%\n\n"
            
            if overall_roi > 100:
                response += "✅ Excellent ! Vos campagnes sont très rentables."
            elif overall_roi > 50:
                response += "👍 Bonne performance ! Considérez étendre les campagnes réussies."
            else:
                response += "⚠️ Le ROI pourrait être amélioré. Révisez le ciblage et les budgets."
        
        elif language == 'en':
            response = f"💰 ROI Analysis:\n\n"
            response += f"📊 Average ROI: {stats['avg_roi']:.1f}%\n"
            response += f"🎯 Profitable campaigns: {stats['profitable_campaigns']}/{stats['total_campaigns']}\n"
            response += f"🏆 Best ROI: {stats['best_roi']:.1f}%\n"
            response += f"💵 Total revenue: ${stats['total_revenue']:,.0f}\n"
            response += f"💸 Total cost: ${stats['total_cost']:,.0f}\n"
            response += f"📈 Overall ROI: {overall_roi:.1f}%\n\n"
            
            if overall_roi > 100:
                response += "✅ Excellent! Your campaigns are highly profitable."
            elif overall_roi > 50:
                response += "👍 Good performance! Consider scaling successful campaigns."
            else:
                response += "⚠️ ROI could be improved. Review targeting and budgets."
        
        return response

    def _handle_conversion_question(self, message, language):
        """Handle conversion-related questions"""
        query = """
            SELECT 
                AVG(CASE WHEN cost > 0 THEN (conversions / cost) * 100 ELSE 0 END) as avg_conversion_rate,
                SUM(conversions) as total_conversions,
                name, conversions, cost,
                CASE WHEN cost > 0 THEN (conversions / cost) * 100 ELSE 0 END as conversion_rate
            FROM marketing_data 
            WHERE status = 'active'
            GROUP BY name, conversions, cost
            ORDER BY conversion_rate DESC
            LIMIT 3
        """
        
        data = self._query_marketing_data(query)
        if not data:
            return "No conversion data available." if language == 'en' else "لا توجد بيانات تحويل متاحة."
        
        if language == 'en':
            response = f"🎯 Conversion Analysis:\n\n"
            total_conversions = sum(d['conversions'] for d in data)
            response += f"📈 Total conversions: {total_conversions:,}\n"
            
            if data:
                avg_rate = sum(d['conversion_rate'] for d in data) / len(data)
                response += f"📊 Average conversion rate: {avg_rate:.2f}%\n\n"
                response += f"🏆 Top performing campaigns:\n"
                
                for i, camp in enumerate(data[:3], 1):
                    response += f"{i}. {camp['name']}: {camp['conversion_rate']:.2f}% ({camp['conversions']} conversions)\n"
        
        else:  # Arabic
            response = f"🎯 تحليل التحويلات:\n\n"
            total_conversions = sum(d['conversions'] for d in data)
            response += f"📈 إجمالي التحويلات: {total_conversions:,}\n"
            
            if data:
                avg_rate = sum(d['conversion_rate'] for d in data) / len(data)
                response += f"📊 متوسط معدل التحويل: {avg_rate:.2f}%\n\n"
                response += f"🏆 أفضل الحملات أداءً:\n"
                
                for i, camp in enumerate(data[:3], 1):
                    response += f"{i}. {camp['name']}: {camp['conversion_rate']:.2f}% ({camp['conversions']} تحويل)\n"
        
        return response

    def _handle_performance_question(self, message, language):
        """Handle performance-related questions"""
        query = """
            SELECT 
                status,
                COUNT(*) as campaign_count,
                AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as avg_roi,
                SUM(revenue) as total_revenue,
                SUM(cost) as total_cost,
                SUM(conversions) as total_conversions
            FROM marketing_data 
            GROUP BY status
            ORDER BY avg_roi DESC
        """
        
        data = self._query_marketing_data(query)
        if not data:
            return "No performance data available." if language == 'en' else "لا توجد بيانات أداء متاحة."
        
        if language == 'en':
            response = f"📊 Performance Overview:\n\n"
            for status_data in data:
                status = status_data['status'].title()
                response += f"🔴 {status} Campaigns:\n"
                response += f"   • Count: {status_data['campaign_count']}\n"
                response += f"   • Avg ROI: {status_data['avg_roi']:.1f}%\n"
                response += f"   • Revenue: ${status_data['total_revenue']:,.0f}\n"
                response += f"   • Conversions: {status_data['total_conversions']:,}\n\n"
        
        else:  # Arabic
            response = f"📊 نظرة عامة على الأداء:\n\n"
            status_mapping = {'active': 'نشطة', 'paused': 'متوقفة', 'completed': 'مكتملة'}
            for status_data in data:
                status = status_mapping.get(status_data['status'], status_data['status'])
                response += f"🔴 الحملات ال{status}:\n"
                response += f"   • العدد: {status_data['campaign_count']}\n"
                response += f"   • متوسط عائد الاستثمار: {status_data['avg_roi']:.1f}%\n"
                response += f"   • الإيرادات: ${status_data['total_revenue']:,.0f}\n"
                response += f"   • التحويلات: {status_data['total_conversions']:,}\n\n"
        
        return response

    def _handle_budget_question(self, message, language):
        """Handle budget-related questions"""
        query = """
            SELECT 
                name, cost, revenue,
                CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END as roi,
                conversions
            FROM marketing_data 
            WHERE status = 'active'
            ORDER BY cost DESC
            LIMIT 5
        """
        
        data = self._query_marketing_data(query)
        if not data:
            return "No budget data available." if language == 'en' else "لا توجد بيانات ميزانية متاحة."
        
        total_cost = sum(d['cost'] for d in data)
        total_revenue = sum(d['revenue'] for d in data)
        
        if language == 'en':
            response = f"💰 Budget Analysis:\n\n"
            response += f"📊 Total active budget: ${total_cost:,.0f}\n"
            response += f"💵 Total revenue generated: ${total_revenue:,.0f}\n"
            response += f"📈 Overall efficiency: {((total_revenue - total_cost) / total_cost * 100):.1f}% ROI\n\n"
            response += f"🏆 Highest budget campaigns:\n"
            
            for i, camp in enumerate(data[:3], 1):
                response += f"{i}. {camp['name']}: ${camp['cost']:,.0f} → ${camp['revenue']:,.0f} ({camp['roi']:.1f}% ROI)\n"
        
        else:  # Arabic
            response = f"💰 تحليل الميزانية:\n\n"
            response += f"📊 إجمالي الميزانية النشطة: ${total_cost:,.0f}\n"
            response += f"💵 إجمالي الإيرادات المحققة: ${total_revenue:,.0f}\n"
            response += f"📈 الكفاءة الإجمالية: {((total_revenue - total_cost) / total_cost * 100):.1f}% عائد استثمار\n\n"
            response += f"🏆 الحملات الأعلى ميزانية:\n"
            
            for i, camp in enumerate(data[:3], 1):
                response += f"{i}. {camp['name']}: ${camp['cost']:,.0f} ← ${camp['revenue']:,.0f} ({camp['roi']:.1f}% عائد)\n"
        
        return response

    def _get_greeting_with_stats(self, language):
        """Get greeting with current stats from real data"""
        query = """
            SELECT 
                COUNT(*) as total_campaigns,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_campaigns,
                SUM(revenue) as total_revenue,
                SUM(conversions) as total_conversions,
                AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as avg_roi
            FROM marketing_data
        """
        
        data = self._query_marketing_data(query)
        
        greetings = {
            'fr': {
                'hello': "Bonjour ! Je suis votre assistant marketing IA. 👋\n\n",
                'overview': "📊 Aperçu rapide :\n",
                'campaigns': "• {active}/{total} campagnes actives\n",
                'revenue': "• ${revenue:,.0f} revenus totaux\n", 
                'conversions': "• {conversions:,} conversions totales\n",
                'roi': "• {roi:.1f}% ROI moyen\n\n",
                'question': "Que souhaitez-vous savoir sur vos performances marketing ?"
            },
            'en': {
                'hello': "Hello! I'm your AI Marketing Assistant. 👋\n\n",
                'overview': "📊 Quick Overview:\n",
                'campaigns': "• {active}/{total} campaigns active\n",
                'revenue': "• ${revenue:,.0f} total revenue\n",
                'conversions': "• {conversions:,} total conversions\n", 
                'roi': "• {roi:.1f}% average ROI\n\n",
                'question': "What would you like to know about your marketing performance?"
            },
            'ar': {
                'hello': "مرحباً! أنا مساعد التسويق الذكي. 👋\n\n",
                'overview': "📊 نظرة سريعة:\n",
                'campaigns': "• {active}/{total} حملة نشطة\n",
                'revenue': "• ${revenue:,.0f} إجمالي الإيرادات\n",
                'conversions': "• {conversions:,} إجمالي التحويلات\n",
                'roi': "• {roi:.1f}% متوسط عائد الاستثمار\n\n", 
                'question': "ماذا تود أن تعرف عن أداء التسويق الخاص بك؟"
            }
        }
        
        lang_text = greetings.get(language, greetings['en'])
        greeting = lang_text['hello']
        
        if data and data[0] and data[0]['total_campaigns'] > 0:
            stats = data[0]
            greeting += lang_text['overview']
            greeting += lang_text['campaigns'].format(
                active=stats['active_campaigns'],
                total=stats['total_campaigns']
            )
            greeting += lang_text['revenue'].format(revenue=stats['total_revenue'] or 0)
            greeting += lang_text['conversions'].format(conversions=stats['total_conversions'] or 0)
            greeting += lang_text['roi'].format(roi=stats['avg_roi'] or 0)
        
        greeting += lang_text['question']
        return greeting

    def _get_help_message(self, language):
        """Get help message"""
        help_messages = {
            'fr': (
                "Je peux vous aider avec :\n"
                "• 📊 Analyse des performances de campagne\n"
                "• 💰 Calculs et insights ROI\n" 
                "• 🎯 Optimisation du taux de conversion\n"
                "• 💵 Recommandations d'allocation budgétaire\n\n"
                "Essayez de demander sur vos campagnes, ROI, conversions, ou performances !"
            ),
            'en': (
                "I can help you with:\n"
                "• 📊 Campaign performance analysis\n"
                "• 💰 ROI calculations and insights\n"
                "• 🎯 Conversion rate optimization\n" 
                "• 💵 Budget allocation recommendations\n\n"
                "Try asking about your campaigns, ROI, conversions, or performance!"
            ),
            'ar': (
                "يمكنني مساعدتك في:\n"
                "• 📊 تحليل أداء الحملات\n"
                "• 💰 حسابات ورؤى عائد الاستثمار\n"
                "• 🎯 تحسين معدل التحويل\n"
                "• 💵 توصيات توزيع الميزانية\n\n"
                "جرب السؤال عن حملاتك أو عائد الاستثمار أو التحويلات أو الأداء!"
            )
        }
        return help_messages.get(language, help_messages['en'])

    def _handle_general_question(self, message, language):
        """Handle general questions"""
        return self._get_help_message(language)

    def _get_error_response(self, language):
        """Get error response"""
        error_messages = {
            'fr': "Désolé, j'ai des difficultés à accéder aux données. Veuillez réessayer plus tard.",
            'en': "I apologize, but I'm having trouble accessing the data right now. Please try again later.",
            'ar': "أعتذر، ولكنني أواجه مشكلة في الوصول للبيانات حالياً. يرجى المحاولة لاحقاً."
        }
        return error_messages.get(language, error_messages['en'])

    # Ajouter les autres méthodes (_handle_conversion_question, _handle_performance_question, _handle_budget_question)
    # similaires avec les vraies données de la base ai_marketing