from odoo import models, fields, api
import logging
import psycopg2
import json
from psycopg2.extras import RealDictCursor

_logger = logging.getLogger(__name__)

class AIMarketingService(models.Model):
    _name = 'ai.marketing.service'
    _description = 'AI Marketing Service'

    name = fields.Char('Service Name', default='AI Marketing Assistant')
    
    def _get_pg_connection(self):
        """Get PostgreSQL connection to ai_marketing database"""
        try:
            connection = psycopg2.connect(
                host="localhost",  # Ajustez selon votre configuration
                database="ai_marketing",
                user="odoo",  # Remplacez par votre utilisateur PostgreSQL
                password="odoo",  # Remplacez par votre mot de passe
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
            
            # Détection du type de question
            if any(word in message_lower for word in ['campaign', 'campaigns', 'حملة', 'حملات']):
                return self._handle_campaign_question(message, language)
            elif any(word in message_lower for word in ['roi', 'return', 'profit', 'عائد', 'ربح']):
                return self._handle_roi_question(message, language)
            elif any(word in message_lower for word in ['conversion', 'convert', 'تحويل', 'تحويلات']):
                return self._handle_conversion_question(message, language)
            elif any(word in message_lower for word in ['performance', 'أداء', 'نتائج']):
                return self._handle_performance_question(message, language)
            elif any(word in message_lower for word in ['budget', 'cost', 'ميزانية', 'تكلفة']):
                return self._handle_budget_question(message, language)
            elif any(word in message_lower for word in ['hello', 'hi', 'مرحبا', 'أهلا']):
                return self._get_greeting_with_stats(language)
            else:
                return self._handle_general_question(message, language)
                
        except Exception as e:
            _logger.error(f"Error generating chat response: {str(e)}")
            return self._get_error_response(language)

    def _handle_campaign_question(self, message, language):
        """Handle campaign-related questions"""
        # Récupérer les données des campagnes
        query = """
            SELECT name, cost, revenue, conversions, status, 
                   CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END as roi
            FROM marketing_data 
            ORDER BY roi DESC 
            LIMIT 5
        """
        
        campaigns = self._query_marketing_data(query)
        if not campaigns:
            return "No campaign data available." if language == 'en' else "لا توجد بيانات حملات متاحة."
        
        if language == 'en':
            response = f"📊 Here are your top campaigns:\n\n"
            for camp in campaigns:
                response += f"• {camp['name']}: ROI {camp['roi']:.1f}%, Revenue ${camp['revenue']:,.0f}\n"
            
            # Ajouter des insights
            best_campaign = campaigns[0]
            response += f"\n🏆 Best performer: {best_campaign['name']} with {best_campaign['roi']:.1f}% ROI!"
            
            if len(campaigns) > 1:
                avg_roi = sum(c['roi'] for c in campaigns) / len(campaigns)
                response += f"\n📈 Average ROI across top campaigns: {avg_roi:.1f}%"
        
        else:  # Arabic
            response = f"📊 إليك أفضل حملاتك:\n\n"
            for camp in campaigns:
                response += f"• {camp['name']}: عائد استثمار {camp['roi']:.1f}%، إيرادات ${camp['revenue']:,.0f}\n"
            
            best_campaign = campaigns[0]
            response += f"\n🏆 الأفضل أداءً: {best_campaign['name']} بعائد استثمار {best_campaign['roi']:.1f}%!"
            
            if len(campaigns) > 1:
                avg_roi = sum(c['roi'] for c in campaigns) / len(campaigns)
                response += f"\n📈 متوسط عائد الاستثمار للحملات الأفضل: {avg_roi:.1f}%"
        
        return response

    def _handle_roi_question(self, message, language):
        """Handle ROI-related questions"""
        query = """
            SELECT 
                AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as avg_roi,
                COUNT(*) as total_campaigns,
                COUNT(CASE WHEN ((revenue - cost) / cost) * 100 > 100 THEN 1 END) as profitable_campaigns,
                MAX(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as best_roi,
                SUM(revenue) as total_revenue,
                SUM(cost) as total_cost
            FROM marketing_data 
            WHERE status = 'active'
        """
        
        data = self._query_marketing_data(query)
        if not data or not data[0]:
            return "No ROI data available." if language == 'en' else "لا توجد بيانات عائد استثمار متاحة."
        
        stats = data[0]
        
        if language == 'en':
            response = f"💰 ROI Analysis:\n\n"
            response += f"📊 Average ROI: {stats['avg_roi']:.1f}%\n"
            response += f"🎯 Profitable campaigns: {stats['profitable_campaigns']}/{stats['total_campaigns']}\n"
            response += f"🏆 Best ROI: {stats['best_roi']:.1f}%\n"
            response += f"💵 Total revenue: ${stats['total_revenue']:,.0f}\n"
            response += f"💸 Total cost: ${stats['total_cost']:,.0f}\n\n"
            
            overall_roi = ((stats['total_revenue'] - stats['total_cost']) / stats['total_cost']) * 100
            response += f"📈 Overall ROI: {overall_roi:.1f}%"
            
            if overall_roi > 100:
                response += "\n✅ Excellent! Your campaigns are highly profitable."
            elif overall_roi > 50:
                response += "\n👍 Good performance! Consider scaling successful campaigns."
            else:
                response += "\n⚠️ ROI could be improved. Review targeting and budgets."
        
        else:  # Arabic
            response = f"💰 تحليل عائد الاستثمار:\n\n"
            response += f"📊 متوسط عائد الاستثمار: {stats['avg_roi']:.1f}%\n"
            response += f"🎯 حملات مربحة: {stats['profitable_campaigns']}/{stats['total_campaigns']}\n"
            response += f"🏆 أفضل عائد استثمار: {stats['best_roi']:.1f}%\n"
            response += f"💵 إجمالي الإيرادات: ${stats['total_revenue']:,.0f}\n"
            response += f"💸 إجمالي التكاليف: ${stats['total_cost']:,.0f}\n\n"
            
            overall_roi = ((stats['total_revenue'] - stats['total_cost']) / stats['total_cost']) * 100
            response += f"📈 عائد الاستثمار الإجمالي: {overall_roi:.1f}%"
            
            if overall_roi > 100:
                response += "\n✅ ممتاز! حملاتك مربحة جداً."
            elif overall_roi > 50:
                response += "\n👍 أداء جيد! فكر في توسيع الحملات الناجحة."
            else:
                response += "\n⚠️ يمكن تحسين عائد الاستثمار. راجع الاستهداف والميزانيات."
        
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
        """Get greeting with current stats"""
        query = """
            SELECT 
                COUNT(*) as total_campaigns,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_campaigns,
                SUM(revenue) as total_revenue,
                SUM(conversions) as total_conversions
            FROM marketing_data
        """
        
        data = self._query_marketing_data(query)
        
        if language == 'en':
            greeting = "Hello! I'm your AI Marketing Assistant. 👋\n\n"
            if data and data[0]:
                stats = data[0]
                greeting += f"📊 Quick Overview:\n"
                greeting += f"• {stats['active_campaigns']}/{stats['total_campaigns']} campaigns active\n"
                greeting += f"• ${stats['total_revenue']:,.0f} total revenue\n"
                greeting += f"• {stats['total_conversions']:,} total conversions\n\n"
            greeting += "What would you like to know about your marketing performance?"
        
        else:  # Arabic
            greeting = "مرحباً! أنا مساعد التسويق الذكي. 👋\n\n"
            if data and data[0]:
                stats = data[0]
                greeting += f"📊 نظرة سريعة:\n"
                greeting += f"• {stats['active_campaigns']}/{stats['total_campaigns']} حملة نشطة\n"
                greeting += f"• ${stats['total_revenue']:,.0f} إجمالي الإيرادات\n"
                greeting += f"• {stats['total_conversions']:,} إجمالي التحويلات\n\n"
            greeting += "ماذا تود أن تعرف عن أداء التسويق الخاص بك؟"
        
        return greeting

    def _handle_general_question(self, message, language):
        """Handle general questions"""
        if language == 'en':
            return ("I can help you with:\n"
                   "• Campaign performance analysis\n"
                   "• ROI calculations and insights\n"
                   "• Conversion rate optimization\n"
                   "• Budget allocation recommendations\n\n"
                   "Try asking about your campaigns, ROI, conversions, or performance!")
        else:
            return ("يمكنني مساعدتك في:\n"
                   "• تحليل أداء الحملات\n"
                   "• حسابات ورؤى عائد الاستثمار\n"
                   "• تحسين معدل التحويل\n"
                   "• توصيات توزيع الميزانية\n\n"
                   "جرب السؤال عن حملاتك أو عائد الاستثمار أو التحويلات أو الأداء!")

    def _get_error_response(self, language):
        """Get error response"""
        if language == 'en':
            return "I apologize, but I'm having trouble accessing the data right now. Please try again later."
        else:
            return "أعتذر، ولكنني أواجه مشكلة في الوصول للبيانات حالياً. يرجى المحاولة لاحقاً."