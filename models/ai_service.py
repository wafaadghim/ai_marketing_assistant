from odoo import models, fields, api
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import re
from datetime import datetime

_logger = logging.getLogger(__name__)

class AIMarketingService(models.Model):
    _name = 'ai.marketing.service'
    _description = 'AI Marketing Service'

    name = fields.Char('Service Name', default='AI Marketing Assistant')
    
    def _get_pg_connection(self):
        """Get PostgreSQL connection to ai_marketing database"""
        try:
            connection = psycopg2.connect(
                host="localhost",
                database="ai_marketing",
                user="odoo",
                password="odoo",
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

    def _detect_language(self, message):
        """Détection automatique de la langue"""
        french_keywords = ['bonjour', 'salut', 'merci', 'campagne', 'performances', 'comment', 'quoi', 'pourquoi', 'où', 'quand']
        arabic_keywords = ['مرحبا', 'أهلا', 'شكرا', 'حملة', 'كيف', 'ماذا', 'لماذا', 'أين', 'متى']
        
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in french_keywords):
            return 'fr'
        elif any(keyword in message for keyword in arabic_keywords):
            return 'ar'
        else:
            return 'en'

    def _classify_question(self, message_lower):
        """Classification intelligente des questions"""
        classifications = {
            'greeting': ['hello', 'hi', 'hey', 'bonjour', 'salut', 'مرحبا', 'أهلا'],
            'campaign': ['campaign', 'campaigns', 'campagne', 'campagnes', 'حملة', 'حملات', 'ads', 'advertising'],
            'roi': ['roi', 'return', 'profit', 'rentabilité', 'bénéfice', 'عائد', 'ربح', 'profitable'],
            'conversion': ['conversion', 'convert', 'conversions', 'تحويل', 'تحويلات', 'rate', 'taux'],
            'performance': ['performance', 'performances', 'résultats', 'أداء', 'نتائج', 'results', 'analytics'],
            'budget': ['budget', 'cost', 'coût', 'coûts', 'ميزانية', 'تكلفة', 'spend', 'spending'],
            'best_channel': ['best channel', 'top performing', 'meilleur canal', 'أفضل قناة'],
            'worst_campaigns': ['worst performing', 'low performance', 'pire performance', 'أسوأ أداء'],
            'help': ['help', 'aide', 'مساعدة', 'how', 'comment', 'كيف'],
            'time': ['time', 'when', 'date', 'today', 'temps', 'quand', 'وقت', 'متى'],
            'math': ['calculate', 'computation', 'math', 'calculer', 'حساب'],
            'personal': ['who are you', 'your name', 'qui es-tu', 'من أنت'],
        }
        
        scores = {}
        for category, keywords in classifications.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return 'general'

    def generate_chat_response(self, message, language='en'):
        """Generate intelligent response to ANY question"""
        try:
            message_lower = message.lower()
            
            # Auto-detect language if not specified
            if not language or language == 'auto':
                language = self._detect_language(message)
            
            # Classify the question
            question_type = self._classify_question(message_lower)
            
            # Route to appropriate handler
            if question_type == 'greeting':
                return self._handle_greeting(message, language)
            elif question_type == 'best_channel':
                return self._handle_best_channel_question(message, language)
            elif question_type == 'worst_campaigns':
                return self._handle_worst_campaigns_question(message, language)
            elif question_type == 'campaign':
                return self._handle_campaign_question(message, language)
            elif question_type == 'roi':
                return self._handle_roi_question(message, language)
            elif question_type == 'conversion':
                return self._handle_conversion_question(message, language)
            elif question_type == 'performance':
                return self._handle_performance_question(message, language)
            elif question_type == 'budget':
                return self._handle_budget_question(message, language)
            elif question_type == 'help':
                return self._handle_help_question(message, language)
            elif question_type == 'time':
                return self._handle_time_question(message, language)
            elif question_type == 'math':
                return self._handle_math_question(message, language)
            elif question_type == 'personal':
                return self._handle_personal_question(message, language)
            else:
                return self._handle_general_intelligent_question(message, language)
                
        except Exception as e:
            _logger.error(f"Error generating chat response: {str(e)}")
            return self._get_error_response(language)

    def _handle_greeting(self, message, language):
        """Handle greetings with real-time stats"""
        try:
            # Try PostgreSQL first, fallback to Odoo
            pg_data = self._get_pg_stats()
            odoo_data = self._get_odoo_stats()
            
            # Use whichever data source has more campaigns
            if pg_data and pg_data.get('total_campaigns', 0) > 0:
                stats = pg_data
                source = "PostgreSQL ai_marketing"
            elif odoo_data and odoo_data.get('total_campaigns', 0) > 0:
                stats = odoo_data
                source = "Odoo"
            else:
                stats = None
                source = "No data"
            
            greetings = {
                'fr': {
                    'hello': "Bonjour ! Je suis votre assistant marketing IA. 👋\n\n",
                    'overview': "📊 Aperçu rapide :\n",
                    'question': "Comment puis-je vous aider aujourd'hui ?"
                },
                'en': {
                    'hello': "Hello! I'm your AI Marketing Assistant. 👋\n\n",
                    'overview': "📊 Quick Overview:\n",
                    'question': "How can I help you today?"
                },
                'ar': {
                    'hello': "مرحباً! أنا مساعد التسويق الذكي. 👋\n\n",
                    'overview': "📊 نظرة سريعة:\n",
                    'question': "كيف يمكنني مساعدتك اليوم؟"
                }
            }
            
            lang_text = greetings.get(language, greetings['en'])
            greeting = lang_text['hello']
            
            if stats and stats['total_campaigns'] > 0:
                greeting += lang_text['overview']
                
                if language == 'fr':
                    greeting += f"• {stats['active_campaigns']}/{stats['total_campaigns']} campagnes actives\n"
                    greeting += f"• ${stats['total_revenue']:,.0f} revenus totaux\n"
                    greeting += f"• {stats['total_conversions']:,} conversions totales\n"
                    greeting += f"• {stats['avg_roi']:.1f}% ROI moyen\n"
                    greeting += f"• Source: {source}\n\n"
                elif language == 'ar':
                    greeting += f"• {stats['active_campaigns']}/{stats['total_campaigns']} حملة نشطة\n"
                    greeting += f"• ${stats['total_revenue']:,.0f} إجمالي الإيرادات\n"
                    greeting += f"• {stats['total_conversions']:,} إجمالي التحويلات\n"
                    greeting += f"• {stats['avg_roi']:.1f}% متوسط عائد الاستثمار\n"
                    greeting += f"• المصدر: {source}\n\n"
                else:
                    greeting += f"• {stats['active_campaigns']}/{stats['total_campaigns']} campaigns active\n"
                    greeting += f"• ${stats['total_revenue']:,.0f} total revenue\n"
                    greeting += f"• {stats['total_conversions']:,} total conversions\n"
                    greeting += f"• {stats['avg_roi']:.1f}% average ROI\n"
                    greeting += f"• Source: {source}\n\n"
            
            greeting += lang_text['question']
            return greeting
            
        except Exception as e:
            _logger.error(f"Error in greeting: {str(e)}")
            return self._get_error_response(language)

    def _get_pg_stats(self):
        """Get stats from PostgreSQL ai_marketing database"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_campaigns,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_campaigns,
                    COALESCE(SUM(revenue), 0) as total_revenue,
                    COALESCE(SUM(conversions), 0) as total_conversions,
                    COALESCE(AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END), 0) as avg_roi
                FROM marketing_data
            """
            
            data = self._query_marketing_data(query)
            return data[0] if data and data[0] else None
        except:
            return None

    def _get_odoo_stats(self):
        """Get stats from Odoo marketing.data"""
        try:
            campaigns = self.env['marketing.data'].search([])
            active_campaigns = self.env['marketing.data'].search([('status', '=', 'active')])
            
            total_revenue = sum(campaign.revenue for campaign in campaigns)
            total_conversions = sum(campaign.conversions for campaign in campaigns)
            avg_roi = sum(campaign.roi for campaign in campaigns) / len(campaigns) if campaigns else 0
            
            return {
                'total_campaigns': len(campaigns),
                'active_campaigns': len(active_campaigns),
                'total_revenue': total_revenue,
                'total_conversions': total_conversions,
                'avg_roi': avg_roi
            }
        except:
            return None

    def _handle_best_channel_question(self, message, language):
        """Handle best channel questions using chat_assistant logic"""
        try:
            # Try to use existing chat_assistant method
            chat_assistant = self.env['chat.assistant']
            response = chat_assistant._get_best_channel()
            return self._format_response_by_language(response, language)
        except:
            # Fallback to PostgreSQL query
            return self._handle_best_channel_pg(language)

    def _handle_best_channel_pg(self, language):
        """Handle best channel using PostgreSQL data"""
        query = """
            SELECT 
                channel,
                COUNT(*) as campaign_count,
                AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as avg_roi,
                SUM(revenue) as total_revenue,
                SUM(conversions) as total_conversions
            FROM marketing_data 
            WHERE channel IS NOT NULL
            GROUP BY channel
            ORDER BY avg_roi DESC
            LIMIT 5
        """
        
        data = self._query_marketing_data(query)
        if not data:
            return {
                'fr': "Aucune donnée de canal trouvée.",
                'en': "No channel data found.",
                'ar': "لم يتم العثور على بيانات القنوات."
            }.get(language, "No channel data found.")
        
        if language == 'fr':
            response = "🏆 **Meilleur Canal de Performance** :\n\n"
            best_channel = data[0]
            response += f"📊 **{best_channel['channel']}**\n"
            response += f"• ROI Moyen: {best_channel['avg_roi']:.1f}%\n"
            response += f"• Nombre de campagnes: {best_channel['campaign_count']}\n"
            response += f"• Revenus totaux: ${best_channel['total_revenue']:,.0f}\n"
            response += f"• Conversions totales: {best_channel['total_conversions']:,}\n\n"
            
            if len(data) > 1:
                response += "📈 **Top 3 canaux** :\n"
                for i, channel in enumerate(data[:3], 1):
                    response += f"{i}. {channel['channel']}: {channel['avg_roi']:.1f}% ROI\n"
        
        elif language == 'ar':
            response = "🏆 **أفضل قناة أداء** :\n\n"
            best_channel = data[0]
            response += f"📊 **{best_channel['channel']}**\n"
            response += f"• متوسط عائد الاستثمار: {best_channel['avg_roi']:.1f}%\n"
            response += f"• عدد الحملات: {best_channel['campaign_count']}\n"
            response += f"• إجمالي الإيرادات: ${best_channel['total_revenue']:,.0f}\n"
            response += f"• إجمالي التحويلات: {best_channel['total_conversions']:,}\n\n"
            
            if len(data) > 1:
                response += "📈 **أفضل 3 قنوات** :\n"
                for i, channel in enumerate(data[:3], 1):
                    response += f"{i}. {channel['channel']}: {channel['avg_roi']:.1f}% عائد\n"
        
        else:
            response = "🏆 **Best Performing Channel** :\n\n"
            best_channel = data[0]
            response += f"📊 **{best_channel['channel']}**\n"
            response += f"• Average ROI: {best_channel['avg_roi']:.1f}%\n"
            response += f"• Campaign count: {best_channel['campaign_count']}\n"
            response += f"• Total revenue: ${best_channel['total_revenue']:,.0f}\n"
            response += f"• Total conversions: {best_channel['total_conversions']:,}\n\n"
            
            if len(data) > 1:
                response += "📈 **Top 3 channels** :\n"
                for i, channel in enumerate(data[:3], 1):
                    response += f"{i}. {channel['channel']}: {channel['avg_roi']:.1f}% ROI\n"
        
        return response

    def _handle_worst_campaigns_question(self, message, language):
        """Handle worst campaigns questions"""
        try:
            chat_assistant = self.env['chat.assistant']
            response = chat_assistant._get_worst_campaigns()
            return self._format_response_by_language(response, language)
        except:
            return self._handle_worst_campaigns_pg(language)

    def _handle_worst_campaigns_pg(self, language):
        """Handle worst campaigns using PostgreSQL data"""
        query = """
            SELECT 
                name, 
                cost, 
                revenue, 
                conversions,
                status,
                CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END as roi
            FROM marketing_data 
            ORDER BY roi ASC
            LIMIT 5
        """
        
        campaigns = self._query_marketing_data(query)
        if not campaigns:
            return {
                'fr': "Aucune donnée de campagne trouvée.",
                'en': "No campaign data found.",
                'ar': "لم يتم العثور على بيانات حملات."
            }.get(language, "No campaign data found.")
        
        if language == 'fr':
            response = "📉 **Campagnes les Moins Performantes** :\n\n"
            for i, campaign in enumerate(campaigns, 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • ROI: {campaign['roi']:.1f}%\n"
                response += f"   • Revenus: ${campaign['revenue']:,.0f}\n"
                response += f"   • Coût: ${campaign['cost']:,.0f}\n"
                response += f"   • Statut: {campaign['status']}\n\n"
        
        elif language == 'ar':
            response = "📉 **أسوأ الحملات أداءً** :\n\n"
            for i, campaign in enumerate(campaigns, 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • عائد الاستثمار: {campaign['roi']:.1f}%\n"
                response += f"   • الإيرادات: ${campaign['revenue']:,.0f}\n"
                response += f"   • التكلفة: ${campaign['cost']:,.0f}\n"
                response += f"   • الحالة: {campaign['status']}\n\n"
        
        else:
            response = "📉 **Worst Performing Campaigns** :\n\n"
            for i, campaign in enumerate(campaigns, 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • ROI: {campaign['roi']:.1f}%\n"
                response += f"   • Revenue: ${campaign['revenue']:,.0f}\n"
                response += f"   • Cost: ${campaign['cost']:,.0f}\n"
                response += f"   • Status: {campaign['status']}\n\n"
        
        return response

    def _handle_campaign_question(self, message, language):
        """Handle campaign questions - try both data sources"""
        try:
            # First try PostgreSQL
            pg_campaigns = self._get_campaigns_pg()
            if pg_campaigns:
                return self._format_campaigns_response(pg_campaigns, language, "PostgreSQL")
            
            # Fallback to Odoo
            odoo_campaigns = self._get_campaigns_odoo()
            if odoo_campaigns:
                return self._format_campaigns_response(odoo_campaigns, language, "Odoo")
            
            # No data found
            return {
                'fr': "Aucune donnée de campagne trouvée. Créez quelques campagnes pour commencer !",
                'en': "No campaign data found. Create some campaigns to get started!",
                'ar': "لم يتم العثور على بيانات حملات. أنشئ بعض الحملات للبدء!"
            }.get(language, "No campaign data found.")
            
        except Exception as e:
            _logger.error(f"Error in campaign question: {str(e)}")
            return self._get_error_response(language)

    def _get_campaigns_pg(self):
        """Get campaigns from PostgreSQL"""
        query = """
            SELECT name, cost, revenue, conversions, status,
                   CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END as roi
            FROM marketing_data 
            ORDER BY roi DESC 
            LIMIT 5
        """
        return self._query_marketing_data(query)

    def _get_campaigns_odoo(self):
        """Get campaigns from Odoo"""
        try:
            campaigns = self.env['marketing.data'].search([], order='roi desc', limit=5)
            return [{
                'name': c.name,
                'cost': c.cost,
                'revenue': c.revenue,
                'conversions': c.conversions,
                'status': c.status,
                'roi': c.roi
            } for c in campaigns]
        except:
            return None

    def _format_campaigns_response(self, campaigns, language, source):
        """Format campaigns response"""
        if language == 'fr':
            response = f"📊 **Vos Meilleures Campagnes** ({source}):\n\n"
            for i, campaign in enumerate(campaigns, 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   💰 ROI: {campaign['roi']:.1f}%\n"
                response += f"   💵 Revenus: ${campaign['revenue']:,.0f}\n"
                response += f"   🎯 Conversions: {campaign['conversions']}\n"
                response += f"   📊 Statut: {campaign['status']}\n\n"
        elif language == 'ar':
            response = f"📊 **أفضل حملاتك** ({source}):\n\n"
            for i, campaign in enumerate(campaigns, 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   💰 عائد الاستثمار: {campaign['roi']:.1f}%\n"
                response += f"   💵 الإيرادات: ${campaign['revenue']:,.0f}\n"
                response += f"   🎯 التحويلات: {campaign['conversions']}\n"
                response += f"   📊 الحالة: {campaign['status']}\n\n"
        else:
            response = f"📊 **Your Top Campaigns** ({source}):\n\n"
            for i, campaign in enumerate(campaigns, 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   💰 ROI: {campaign['roi']:.1f}%\n"
                response += f"   💵 Revenue: ${campaign['revenue']:,.0f}\n"
                response += f"   🎯 Conversions: {campaign['conversions']}\n"
                response += f"   📊 Status: {campaign['status']}\n\n"
        
        return response

    def _handle_roi_question(self, message, language):
        """Handle ROI questions"""
        try:
            chat_assistant = self.env['chat.assistant']
            response = chat_assistant._get_roi_analysis()
            return self._format_response_by_language(response, language)
        except:
            return self._handle_roi_pg(language)

    def _handle_roi_pg(self, language):
        """Handle ROI using PostgreSQL data"""
        query = """
            SELECT 
                AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as avg_roi,
                COUNT(*) as total_campaigns,
                COUNT(CASE WHEN ((revenue - cost) / cost) * 100 > 100 THEN 1 END) as profitable_campaigns,
                MAX(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as best_roi,
                MIN(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END) as worst_roi,
                SUM(revenue) as total_revenue,
                SUM(cost) as total_cost
            FROM marketing_data
        """
        
        data = self._query_marketing_data(query)
        if not data or not data[0]:
            return {
                'fr': "Aucune donnée de ROI disponible.",
                'en': "No ROI data available.",
                'ar': "لا توجد بيانات عائد استثمار متاحة."
            }.get(language, "No ROI data available.")
        
        stats = data[0]
        overall_roi = ((stats['total_revenue'] - stats['total_cost']) / stats['total_cost']) * 100 if stats['total_cost'] > 0 else 0
        
        if language == 'fr':
            response = f"💰 **Analyse du ROI** :\n\n"
            response += f"📊 ROI moyen: **{stats['avg_roi']:.1f}%**\n"
            response += f"🎯 Campagnes rentables: **{stats['profitable_campaigns']}/{stats['total_campaigns']}**\n"
            response += f"🏆 Meilleur ROI: **{stats['best_roi']:.1f}%**\n"
            response += f"📉 Plus faible ROI: **{stats['worst_roi']:.1f}%**\n"
            response += f"📈 ROI global: **{overall_roi:.1f}%**\n\n"
            
            if overall_roi > 150:
                response += "🚀 **Exceptionnel !** Vos campagnes génèrent des profits extraordinaires !"
            elif overall_roi > 100:
                response += "✅ **Excellent !** Vos campagnes sont très rentables."
            elif overall_roi > 50:
                response += "👍 **Bon !** Performance solide, vous pouvez optimiser davantage."
            else:
                response += "⚠️ **Attention !** Le ROI pourrait être amélioré."
        
        elif language == 'ar':
            response = f"💰 **تحليل عائد الاستثمار** :\n\n"
            response += f"📊 متوسط عائد الاستثمار: **{stats['avg_roi']:.1f}%**\n"
            response += f"🎯 حملات مربحة: **{stats['profitable_campaigns']}/{stats['total_campaigns']}**\n"
            response += f"🏆 أفضل عائد: **{stats['best_roi']:.1f}%**\n"
            response += f"📉 أقل عائد: **{stats['worst_roi']:.1f}%**\n"
            response += f"📈 العائد الإجمالي: **{overall_roi:.1f}%**\n\n"
            
            if overall_roi > 150:
                response += "🚀 **استثنائي !** حملاتك تحقق أرباحاً مذهلة !"
            elif overall_roi > 100:
                response += "✅ **ممتاز !** حملاتك مربحة جداً."
            elif overall_roi > 50:
                response += "👍 **جيد !** أداء قوي، يمكنك التحسين أكثر."
            else:
                response += "⚠️ **تنبيه !** عائد الاستثمار يحتاج تحسين."
        
        else:
            response = f"💰 **ROI Analysis** :\n\n"
            response += f"📊 Average ROI: **{stats['avg_roi']:.1f}%**\n"
            response += f"🎯 Profitable campaigns: **{stats['profitable_campaigns']}/{stats['total_campaigns']}**\n"
            response += f"🏆 Best ROI: **{stats['best_roi']:.1f}%**\n"
            response += f"📉 Worst ROI: **{stats['worst_roi']:.1f}%**\n"
            response += f"📈 Overall ROI: **{overall_roi:.1f}%**\n\n"
            
            if overall_roi > 150:
                response += "🚀 **Outstanding!** Your campaigns are generating exceptional profits!"
            elif overall_roi > 100:
                response += "✅ **Excellent!** Your campaigns are highly profitable."
            elif overall_roi > 50:
                response += "👍 **Good!** Solid performance, room for optimization."
            else:
                response += "⚠️ **Attention!** ROI could be improved."
        
        return response

    def _handle_conversion_question(self, message, language):
        """Handle conversion questions"""
        try:
            chat_assistant = self.env['chat.assistant']
            response = chat_assistant._get_conversion_analysis()
            return self._format_response_by_language(response, language)
        except:
            return self._handle_conversion_pg(language)

    def _handle_conversion_pg(self, language):
        """Handle conversion using PostgreSQL data"""
        query = """
            SELECT 
                name,
                conversions,
                cost,
                revenue,
                CASE WHEN cost > 0 THEN (conversions::float / cost) * 100 ELSE 0 END as conversion_rate
            FROM marketing_data 
            WHERE status = 'active' AND cost > 0
            ORDER BY conversion_rate DESC
            LIMIT 5
        """
        
        data = self._query_marketing_data(query)
        if not data:
            return {
                'fr': "Aucune donnée de conversion disponible.",
                'en': "No conversion data available.",
                'ar': "لا توجد بيانات تحويل متاحة."
            }.get(language, "No conversion data available.")
        
        total_conversions = sum(d['conversions'] for d in data)
        avg_rate = sum(d['conversion_rate'] for d in data) / len(data) if data else 0
        
        if language == 'fr':
            response = f"🎯 **Analyse des Conversions** :\n\n"
            response += f"📈 Total des conversions: **{total_conversions:,}**\n"
            response += f"📊 Taux de conversion moyen: **{avg_rate:.2f}%**\n\n"
            response += f"🏆 **Top performers** :\n"
            
            for i, campaign in enumerate(data[:3], 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • {campaign['conversions']} conversions\n"
                response += f"   • Taux: {campaign['conversion_rate']:.2f}%\n\n"
        
        elif language == 'ar':
            response = f"🎯 **تحليل التحويلات** :\n\n"
            response += f"📈 إجمالي التحويلات: **{total_conversions:,}**\n"
            response += f"📊 متوسط معدل التحويل: **{avg_rate:.2f}%**\n\n"
            response += f"🏆 **الأفضل أداءً** :\n"
            
            for i, campaign in enumerate(data[:3], 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • {campaign['conversions']} تحويل\n"
                response += f"   • المعدل: {campaign['conversion_rate']:.2f}%\n\n"
        
        else:
            response = f"🎯 **Conversion Analysis** :\n\n"
            response += f"📈 Total conversions: **{total_conversions:,}**\n"
            response += f"📊 Average conversion rate: **{avg_rate:.2f}%**\n\n"
            response += f"🏆 **Top performers** :\n"
            
            for i, campaign in enumerate(data[:3], 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • {campaign['conversions']} conversions\n"
                response += f"   • Rate: {campaign['conversion_rate']:.2f}%\n\n"
        
        return response

    def _handle_performance_question(self, message, language):
        """Handle performance questions"""
        try:
            chat_assistant = self.env['chat.assistant']
            response = chat_assistant._get_campaign_report()
            return self._format_response_by_language(response, language)
        except:
            return self._handle_performance_pg(language)

    def _handle_performance_pg(self, language):
        """Handle performance using PostgreSQL data"""
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
            return {
                'fr': "Aucune donnée de performance disponible.",
                'en': "No performance data available.",
                'ar': "لا توجد بيانات أداء متاحة."
            }.get(language, "No performance data available.")
        
        if language == 'fr':
            response = f"📊 **Rapport de Performance des Campagnes** :\n\n"
            status_map = {'active': 'Actives', 'paused': 'En pause', 'completed': 'Terminées'}
            for status_data in data:
                status = status_map.get(status_data['status'], status_data['status'])
                response += f"🔴 **Campagnes {status}** :\n"
                response += f"   • Nombre: {status_data['campaign_count']}\n"
                response += f"   • ROI moyen: {status_data['avg_roi']:.1f}%\n"
                response += f"   • Revenus: ${status_data['total_revenue']:,.0f}\n"
                response += f"   • Conversions: {status_data['total_conversions']:,}\n\n"
        
        elif language == 'ar':
            response = f"📊 **تقرير أداء الحملات** :\n\n"
            status_map = {'active': 'نشطة', 'paused': 'متوقفة', 'completed': 'مكتملة'}
            for status_data in data:
                status = status_map.get(status_data['status'], status_data['status'])
                response += f"🔴 **الحملات ال{status}** :\n"
                response += f"   • العدد: {status_data['campaign_count']}\n"
                response += f"   • متوسط عائد الاستثمار: {status_data['avg_roi']:.1f}%\n"
                response += f"   • الإيرادات: ${status_data['total_revenue']:,.0f}\n"
                response += f"   • التحويلات: {status_data['total_conversions']:,}\n\n"
        
        else:
            response = f"📊 **Campaign Performance Report** :\n\n"
            for status_data in data:
                status = status_data['status'].title()
                response += f"🔴 **{status} Campaigns** :\n"
                response += f"   • Count: {status_data['campaign_count']}\n"
                response += f"   • Avg ROI: {status_data['avg_roi']:.1f}%\n"
                response += f"   • Revenue: ${status_data['total_revenue']:,.0f}\n"
                response += f"   • Conversions: {status_data['total_conversions']:,}\n\n"
        
        return response

    def _handle_budget_question(self, message, language):
        """Handle budget questions"""
        query = """
            SELECT 
                name, cost, revenue,
                CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END as roi,
                conversions,
                status
            FROM marketing_data 
            WHERE status = 'active'
            ORDER BY cost DESC
            LIMIT 5
        """
        
        data = self._query_marketing_data(query)
        if not data:
            return {
                'fr': "Aucune donnée de budget disponible.",
                'en': "No budget data available.",
                'ar': "لا توجد بيانات ميزانية متاحة."
            }.get(language, "No budget data available.")
        
        total_cost = sum(d['cost'] for d in data)
        total_revenue = sum(d['revenue'] for d in data)
        
        if language == 'fr':
            response = f"💰 **Analyse du Budget** :\n\n"
            response += f"📊 Budget total actif: **${total_cost:,.0f}**\n"
            response += f"💵 Revenus générés: **${total_revenue:,.0f}**\n"
            response += f"📈 Efficacité globale: **{((total_revenue - total_cost) / total_cost * 100):.1f}% ROI**\n\n"
            response += f"🏆 **Campagnes à plus gros budget** :\n"
            
            for i, campaign in enumerate(data[:3], 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • Budget: ${campaign['cost']:,.0f}\n"
                response += f"   • Revenus: ${campaign['revenue']:,.0f}\n"
                response += f"   • ROI: {campaign['roi']:.1f}%\n\n"
        
        elif language == 'ar':
            response = f"💰 **تحليل الميزانية** :\n\n"
            response += f"📊 إجمالي الميزانية النشطة: **${total_cost:,.0f}**\n"
            response += f"💵 الإيرادات المحققة: **${total_revenue:,.0f}**\n"
            response += f"📈 الكفاءة الإجمالية: **{((total_revenue - total_cost) / total_cost * 100):.1f}% عائد استثمار**\n\n"
            response += f"🏆 **الحملات الأعلى ميزانية** :\n"
            
            for i, campaign in enumerate(data[:3], 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • الميزانية: ${campaign['cost']:,.0f}\n"
                response += f"   • الإيرادات: ${campaign['revenue']:,.0f}\n"
                response += f"   • عائد الاستثمار: {campaign['roi']:.1f}%\n\n"
        
        else:
            response = f"💰 **Budget Analysis** :\n\n"
            response += f"📊 Total active budget: **${total_cost:,.0f}**\n"
            response += f"💵 Revenue generated: **${total_revenue:,.0f}**\n"
            response += f"📈 Overall efficiency: **{((total_revenue - total_cost) / total_cost * 100):.1f}% ROI**\n\n"
            response += f"🏆 **Highest budget campaigns** :\n"
            
            for i, campaign in enumerate(data[:3], 1):
                response += f"{i}. **{campaign['name']}**\n"
                response += f"   • Budget: ${campaign['cost']:,.0f}\n"
                response += f"   • Revenue: ${campaign['revenue']:,.0f}\n"
                response += f"   • ROI: {campaign['roi']:.1f}%\n\n"
        
        return response

    def _handle_help_question(self, message, language):
        """Handle help questions"""
        help_messages = {
            'fr': (
                "🤖 **Je peux vous aider avec** :\n\n"
                "📊 **Analyses** :\n"
                "• Performances de campagnes\n"
                "• Calculs ROI et insights\n"
                "• Analyses de conversions\n"
                "• Rapports de performance\n\n"
                "💡 **Questions que vous pouvez poser** :\n"
                "• \"Montre-moi mes campagnes\"\n"
                "• \"Quel est mon ROI ?\"\n"
                "• \"Meilleur canal de performance\"\n"
                "• \"Pires campagnes\"\n"
                "• \"Analyse des conversions\"\n\n"
                "🌐 **Langues supportées** : Français, English, العربية"
            ),
            'en': (
                "🤖 **I can help you with** :\n\n"
                "📊 **Analytics** :\n"
                "• Campaign performance analysis\n"
                "• ROI calculations and insights\n"
                "• Conversion rate optimization\n"
                "• Performance reports\n\n"
                "💡 **Questions you can ask** :\n"
                "• \"Show me my campaigns\"\n"
                "• \"What's my ROI?\"\n"
                "• \"Best performing channel\"\n"
                "• \"Worst campaigns\"\n"
                "• \"Conversion analysis\"\n\n"
                "🌐 **Supported languages** : English, Français, العربية"
            ),
            'ar': (
                "🤖 **يمكنني مساعدتك في** :\n\n"
                "📊 **التحليلات** :\n"
                "• تحليل أداء الحملات\n"
                "• حسابات ورؤى عائد الاستثمار\n"
                "• تحسين معدل التحويل\n"
                "• تقارير الأداء\n\n"
                "💡 **أسئلة يمكنك طرحها** :\n"
                "• \"أرني حملاتي\"\n"
                "• \"ما هو عائد استثماري؟\"\n"
                "• \"أفضل قناة أداء\"\n"
                "• \"أسوأ الحملات\"\n"
                "• \"تحليل التحويلات\"\n\n"
                "🌐 **اللغات المدعومة** : العربية، English، Français"
            )
        }
        return help_messages.get(language, help_messages['en'])

    def _handle_time_question(self, message, language):
        """Handle time-related questions"""
        now = datetime.now()
        
        responses = {
            'fr': f"🕐 Il est actuellement **{now.strftime('%H:%M')}** le **{now.strftime('%d/%m/%Y')}**.\n\nVoulez-vous voir les performances de vos campagnes aujourd'hui ?",
            'en': f"🕐 It's currently **{now.strftime('%H:%M')}** on **{now.strftime('%m/%d/%Y')}**.\n\nWould you like to see today's campaign performance?",
            'ar': f"🕐 الوقت الحالي **{now.strftime('%H:%M')}** في **{now.strftime('%d/%m/%Y')}**.\n\nهل تريد رؤية أداء حملاتك اليوم؟"
        }
        
        return responses.get(language, responses['en'])

    def _handle_math_question(self, message, language):
        """Handle mathematical questions"""
        try:
            # Extract mathematical expressions
            math_expr = re.search(r'(\d+(?:\.\d+)?)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', message)
            
            if math_expr:
                num1 = float(math_expr.group(1))
                operator = math_expr.group(2)
                num2 = float(math_expr.group(3))
                
                if operator == '+':
                    result = num1 + num2
                elif operator == '-':
                    result = num1 - num2
                elif operator == '*':
                    result = num1 * num2
                elif operator == '/':
                    if num2 != 0:
                        result = num1 / num2
                    else:
                        return {
                            'fr': "❌ Division par zéro impossible !",
                            'en': "❌ Division by zero is not allowed!",
                            'ar': "❌ القسمة على صفر غير مسموحة!"
                        }.get(language, "Division by zero error!")
                
                responses = {
                    'fr': f"🧮 **Calcul** : {num1} {operator} {num2} = **{result:.2f}**\n\nVoulez-vous calculer le ROI d'une campagne ?",
                    'en': f"🧮 **Calculation** : {num1} {operator} {num2} = **{result:.2f}**\n\nWould you like to calculate campaign ROI?",
                    'ar': f"🧮 **حساب** : {num1} {operator} {num2} = **{result:.2f}**\n\nهل تريد حساب عائد استثمار حملة؟"
                }
                
                return responses.get(language, responses['en'])
        except:
            pass
        
        responses = {
            'fr': "🧮 Je peux faire des calculs ! Essayez : '100 + 50' ou demandez-moi de calculer votre ROI.",
            'en': "🧮 I can do calculations! Try: '100 + 50' or ask me to calculate your ROI.",
            'ar': "🧮 يمكنني القيام بحسابات! جرب: '100 + 50' أو اطلب مني حساب عائد استثمارك."
        }
        
        return responses.get(language, responses['en'])

    def _handle_personal_question(self, message, language):
        """Handle personal questions about the AI"""
        responses = {
            'fr': (
                "🤖 **Je suis l'Assistant Marketing IA** !\n\n"
                "✨ **Créé pour vous aider avec** :\n"
                "• Analyser vos campagnes marketing\n"
                "• Calculer les ROI et métriques\n"
                "• Donner des recommandations\n"
                "• Répondre à vos questions\n\n"
                "🔗 **Je peux accéder** :\n"
                "• Base PostgreSQL ai_marketing\n"
                "• Données Odoo marketing.data\n\n"
                "🌐 **Langues** : Français, English, العربية\n\n"
                "Comment puis-je vous aider avec votre marketing ?"
            ),
            'en': (
                "🤖 **I'm the AI Marketing Assistant** !\n\n"
                "✨ **Created to help you with** :\n"
                "• Analyze your marketing campaigns\n"
                "• Calculate ROI and metrics\n"
                "• Provide recommendations\n"
                "• Answer your questions\n\n"
                "🔗 **I can access** :\n"
                "• PostgreSQL ai_marketing database\n"
                "• Odoo marketing.data records\n\n"
                "🌐 **Languages** : English, Français, العربية\n\n"
                "How can I help you with your marketing?"
            ),
            'ar': (
                "🤖 **أنا مساعد التسويق الذكي** !\n\n"
                "✨ **تم إنشائي لمساعدتك في** :\n"
                "• تحليل حملاتك التسويقية\n"
                "• حساب عائد الاستثمار والمقاييس\n"
                "• تقديم التوصيات\n"
                "• الإجابة على أسئلتك\n\n"
                "🔗 **يمكنني الوصول إلى** :\n"
                "• قاعدة بيانات PostgreSQL ai_marketing\n"
                "• بيانات Odoo marketing.data\n\n"
                "🌐 **اللغات** : العربية، English، Français\n\n"
                "كيف يمكنني مساعدتك في التسويق؟"
            )
        }
        
        return responses.get(language, responses['en'])

    def _handle_general_intelligent_question(self, message, language):
        """Handle general questions intelligently"""
        message_lower = message.lower()
        
        # Questions about capabilities
        if any(word in message_lower for word in ['can you', 'are you able', 'peux-tu', 'es-tu capable', 'هل تستطيع', 'هل يمكنك']):
            return self._handle_help_question(message, language)
        
        # Questions about how to do something
        elif any(word in message_lower for word in ['how to', 'how do i', 'comment faire', 'comment', 'كيف أفعل', 'كيف']):
            responses = {
                'fr': "💡 **Pour vous aider au mieux**, voici des exemples :\n\n🎯 *\"Comment améliorer mes campagnes ?\"*\n💰 *\"Comment calculer mon ROI ?\"*\n📊 *\"Comment analyser mes performances ?\"*\n🚀 *\"Comment augmenter mes conversions ؟\"*\n\n*Posez une question spécifique !*",
                'en': "💡 **To help you better**, here are examples :\n\n🎯 *\"How to improve my campaigns?\"*\n💰 *\"How to calculate my ROI?\"*\n📊 *\"How to analyze my performance?\"*\n🚀 *\"How to increase conversions?\"*\n\n*Ask a specific question!*",
                'ar': "💡 **لمساعدتك بشكل أفضل**, إليك أمثلة :\n\n🎯 *\"كيف أحسن حملاتي؟\"*\n💰 *\"كيف أحسب عائد الاستثمار؟\"*\n📊 *\"كيف أحلل أدائي؟\"*\n🚀 *\"كيف أزيد التحويلات؟\"*\n\n*اطرح سؤالاً محدداً!*"
            }
            return responses.get(language, responses['en'])
        
        # Default response
        responses = {
            'fr': f"🤖 **Question intéressante !**\n\n*Reçu* : \"{message[:50]}{'...' if len(message) > 50 else ''}\"\n\n💡 **Suggestions** :\n• *\"Montre-moi mes campagnes\"*\n• *\"Quel est mon ROI ?\"*\n• *\"Meilleur canal\"*\n• *\"Analyse des conversions\"*\n\n*Reformulez pour une aide précise !*",
            'en': f"🤖 **Interesting question!**\n\n*Received* : \"{message[:50]}{'...' if len(message) > 50 else ''}\"\n\n💡 **Suggestions** :\n• *\"Show me my campaigns\"*\n• *\"What's my ROI?\"*\n• *\"Best channel\"*\n• *\"Conversion analysis\"*\n\n*Rephrase for precise help!*",
            'ar': f"🤖 **سؤال مثير!**\n\n*استلمت* : \"{message[:50]}{'...' if len(message) > 50 else ''}\"\n\n💡 **اقتراحات** :\n• *\"أرني حملاتي\"*\n• *\"ما هو عائد استثماري؟\"*\n• *\"أفضل قناة\"*\n• *\"تحليل التحويلات\"*\n\n*أعد الصياغة للمساعدة الدقيقة!*"
        }
        
        return responses.get(language, responses['en'])

    def _format_response_by_language(self, odoo_response, language):
        """Format Odoo response according to language"""
        if not odoo_response:
            return self._get_error_response(language)
            
        if language == 'fr':
            # French translations
            response = odoo_response.replace("Best Performing Channel", "🏆 Meilleur Canal de Performance")
            response = response.replace("Average ROI", "ROI Moyen")
            response = response.replace("Worst Performing Campaigns", "📉 Campagnes les Moins Performantes")
            response = response.replace("Conversion Analysis", "🎯 Analyse des Conversions")
            response = response.replace("Total Conversions", "Total des Conversions")
            response = response.replace("Total Cost", "Coût Total")
            response = response.replace("Average Conversion Rate", "Taux de Conversion Moyen")
            response = response.replace("ROI Analysis", "💰 Analyse du ROI")
            response = response.replace("Total Revenue", "Chiffre d'Affaires Total")
            response = response.replace("Overall ROI", "ROI Global")
            response = response.replace("Average Campaign ROI", "ROI Moyen des Campagnes")
            response = response.replace("Campaign Performance Report", "📊 Rapport de Performance des Campagnes")
            return response
            
        elif language == 'ar':
            # Arabic translations
            response = odoo_response.replace("Best Performing Channel", "🏆 أفضل قناة أداء")
            response = response.replace("Average ROI", "متوسط عائد الاستثمار")
            response = response.replace("Worst Performing Campaigns", "📉 أسوأ الحملات أداءً")
            response = response.replace("Conversion Analysis", "🎯 تحليل التحويلات")
            response = response.replace("Total Conversions", "إجمالي التحويلات")
            response = response.replace("Total Cost", "التكلفة الإجمالية")
            response = response.replace("Average Conversion Rate", "متوسط معدل التحويل")
            response = response.replace("ROI Analysis", "💰 تحليل عائد الاستثمار")
            response = response.replace("Total Revenue", "إجمالي الإيرادات")
            response = response.replace("Overall ROI", "عائد الاستثمار الإجمالي")
            response = response.replace("Average Campaign ROI", "متوسط عائد استثمار الحملات")
            response = response.replace("Campaign Performance Report", "📊 تقرير أداء الحملات")
            return response
            
        else:
            # Add emojis to English responses
            response = odoo_response.replace("Best Performing Channel", "🏆 Best Performing Channel")
            response = response.replace("Worst Performing Campaigns", "📉 Worst Performing Campaigns")
            response = response.replace("Conversion Analysis", "🎯 Conversion Analysis")
            response = response.replace("ROI Analysis", "💰 ROI Analysis")
            response = response.replace("Campaign Performance Report", "📊 Campaign Performance Report")
            return response

    def _get_error_response(self, language):
        """Get error response"""
        error_messages = {
            'fr': "Désolé, j'ai rencontré une difficulté technique. Pouvez-vous reformuler votre question ?",
            'en': "Sorry, I encountered a technical difficulty. Could you rephrase your question?",
            'ar': "آسف، واجهت صعوبة تقنية. هل يمكنك إعادة صياغة سؤالك؟"
        }
        return error_messages.get(language, error_messages['en'])