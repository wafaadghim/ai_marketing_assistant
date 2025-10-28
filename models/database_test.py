from odoo import models, fields, api
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import json

_logger = logging.getLogger(__name__)

class DatabaseTest(models.TransientModel):
    _name = 'database.test'
    _description = 'Database Connection Test'

    name = fields.Char('Test Name', default='PostgreSQL Connection Test')
    connection_status = fields.Text('Connection Status', readonly=True)
    test_results = fields.Text('Test Results', readonly=True)
    last_test_time = fields.Datetime('Last Test', readonly=True)

    def test_connection_wizard(self):
        """Test connection avec retour immédiat"""
        self.test_connection()
        
        # Retourner la même vue mais avec les données mises à jour
        return {
            'type': 'ir.actions.act_window',
            'name': 'Database Test Results',
            'res_model': 'database.test',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
            'context': {'form_view_initial_mode': 'readonly'}
        }
    
    def test_connection(self):
        """Test PostgreSQL connection to ai_marketing database"""
        self.last_test_time = fields.Datetime.now()

        # Liste des configurations à tester
        connection_configs = [
            {'user': 'odoo', 'password': 'odoo', 'desc': 'odoo user'},
            {'user': 'wafa', 'password': 'wafa', 'desc': 'wafa user'},
            {'user': 'postgres', 'password': '', 'desc': 'postgres user (no password)'},
            {'user': 'postgres', 'password': 'postgres', 'desc': 'postgres user (with password)'},
        ]

        for config in connection_configs:
            try:
                connection_params = {
                    'host': 'localhost',
                    'database': 'ai_marketing',
                    'user': config['user'],
                    'password': config['password'],
                    'port': '5432'
                }
                
                _logger.info(f"Testing connection with {config['desc']}...")
                
                # Test de connexion
                connection = psycopg2.connect(**connection_params)
                
                # Si on arrive ici, la connexion a réussi
                connection_msg = f"✅ Connection successful with {config['desc']}!\n"
                connection_msg += f"Host: {connection_params['host']}\n"
                connection_msg += f"Database: {connection_params['database']}\n"
                connection_msg += f"User: {connection_params['user']}\n"
                connection_msg += f"Port: {connection_params['port']}\n"
                connection_msg += f"Test Time: {self.last_test_time}"
                
                self.connection_status = connection_msg
                
                # Test des requêtes
                results = self._test_database_queries(connection)
                self.test_results = results
                
                connection.close()
                _logger.info("Database connection test completed successfully")
                
                # FORCER la sauvegarde immédiate
                self.env.cr.commit()
                
                # Retourner une action pour montrer les résultats
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'database.test',
                    'res_id': self.id,
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'form_view_initial_mode': 'edit'}
                }
                
            except psycopg2.OperationalError as e:
                _logger.warning(f"Connection failed with {config['desc']}: {str(e)}")
                continue  # Essayer la configuration suivante
            except Exception as e:
                _logger.error(f"Unexpected error with {config['desc']}: {str(e)}")
                continue

        # Si on arrive ici, aucune configuration n'a fonctionné
        error_msg = "❌ All connection attempts failed!\n\n"
        error_msg += "Tested configurations:\n"
        for config in connection_configs:
            error_msg += f"- {config['desc']}\n"
        error_msg += "\nPossible solutions:\n"
        error_msg += "1. Check if PostgreSQL is running: sudo systemctl status postgresql\n"
        error_msg += "2. Create database: sudo -u postgres createdb ai_marketing\n"
        error_msg += "3. Create user: sudo -u postgres createuser -P wafa\n"
        error_msg += "4. Grant permissions: sudo -u postgres psql -c \"GRANT ALL ON DATABASE ai_marketing TO wafa;\"\n"
        error_msg += f"\nTest Time: {self.last_test_time}"
        
        self.connection_status = error_msg
        self.test_results = "All connection attempts failed"
        
        # FORCER la sauvegarde même en cas d'échec
        self.env.cr.commit()
        
        # Retourner une notification d'erreur
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection Test Failed',
                'message': 'All connection attempts failed! Check the logs for details.',
                'type': 'warning'
            }
        }

    def _test_database_queries(self, connection):
        """Test various queries on the ai_marketing database"""
        results = []
        
        try:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            # 1. Lister les tables disponibles
            results.append("📋 AVAILABLE TABLES:")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            if tables:
                for table in tables:
                    results.append(f"   • {table['table_name']}")
            else:
                results.append("   ⚠️ No tables found in public schema")
            
            results.append("")
            
            # 2. Vérifier la table marketing_data
            results.append("📊 MARKETING_DATA TABLE:")
            try:
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'marketing_data'
                    ORDER BY ordinal_position;
                """)
                columns = cursor.fetchall()
                
                if columns:
                    results.append("   Structure:")
                    for col in columns:
                        results.append(f"     - {col['column_name']} ({col['data_type']})")
                    
                    # Compter les enregistrements
                    cursor.execute("SELECT COUNT(*) as count FROM marketing_data;")
                    count_result = cursor.fetchone()
                    results.append(f"\n   📈 Total records: {count_result['count']}")
                    
                    # Échantillon de données
                    if count_result['count'] > 0:
                        cursor.execute("""
                            SELECT name, cost, revenue, conversions, status,
                                   CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END as roi
                            FROM marketing_data 
                            ORDER BY revenue DESC 
                            LIMIT 5;
                        """)
                        sample_data = cursor.fetchall()
                        
                        results.append("\n   📋 Sample data (Top 5 by revenue):")
                        for i, row in enumerate(sample_data, 1):
                            results.append(f"     {i}. {row['name']}")
                            results.append(f"        Cost: ${row['cost']:,.2f}")
                            results.append(f"        Revenue: ${row['revenue']:,.2f}")
                            results.append(f"        Conversions: {row['conversions']}")
                            results.append(f"        ROI: {row['roi']:.1f}%")
                            results.append(f"        Status: {row['status']}")
                            results.append("")
                    else:
                        results.append("\n   ⚠️ No data found in marketing_data table")
                    
                else:
                    results.append("   ⚠️ marketing_data table not found")
                    
            except psycopg2.Error as e:
                results.append(f"   ❌ Error querying marketing_data: {str(e)}")
            
            results.append("")
            
            # 3. Statistiques générales
            results.append("📊 GENERAL STATISTICS:")
            try:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_campaigns,
                        COUNT(CASE WHEN status = 'active' THEN 1 END) as active_campaigns,
                        COUNT(CASE WHEN status = 'paused' THEN 1 END) as paused_campaigns,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_campaigns,
                        COALESCE(SUM(cost), 0) as total_cost,
                        COALESCE(SUM(revenue), 0) as total_revenue,
                        COALESCE(SUM(conversions), 0) as total_conversions,
                        COALESCE(AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 ELSE 0 END), 0) as avg_roi
                    FROM marketing_data;
                """)
                stats = cursor.fetchone()
                
                if stats and stats['total_campaigns'] > 0:
                    results.append(f"   📈 Total Campaigns: {stats['total_campaigns']}")
                    results.append(f"   🟢 Active: {stats['active_campaigns']}")
                    results.append(f"   🟡 Paused: {stats['paused_campaigns']}")
                    results.append(f"   🔴 Completed: {stats['completed_campaigns']}")
                    results.append(f"   💰 Total Cost: ${stats['total_cost']:,.2f}")
                    results.append(f"   💵 Total Revenue: ${stats['total_revenue']:,.2f}")
                    results.append(f"   🎯 Total Conversions: {stats['total_conversions']:,}")
                    results.append(f"   📊 Average ROI: {stats['avg_roi']:.1f}%")
                else:
                    results.append("   ⚠️ No campaign statistics available")
                
            except psycopg2.Error as e:
                results.append(f"   ❌ Error getting statistics: {str(e)}")
            
            cursor.close()
            
        except Exception as e:
            results.append(f"❌ Error during query testing: {str(e)}")
        
        return "\n".join(results)

    def get_sample_data(self):
        """Récupère un échantillon de données pour test"""
        try:
            connection_params = {
                'host': 'localhost',
                'database': 'ai_marketing',
                'user': 'odoo',
                'password': 'odoo',
                'port': '5432'
            }
            
            connection = psycopg2.connect(**connection_params)
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM marketing_data 
                ORDER BY id DESC 
                LIMIT 10;
            """)
            
            data = cursor.fetchall()
            
            # Convertir en format JSON pour affichage
            sample_data = []
            for row in data:
                sample_data.append(dict(row))
            
            cursor.close()
            connection.close()
            
            return {
                'success': True,
                'data': sample_data,
                'count': len(sample_data)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': [],
                'count': 0
            }

    @api.model
    def run_connection_test(self):
        """Méthode pour exécuter le test via RPC"""
        test_record = self.create({'name': 'Connection Test'})
        test_record.test_connection()
        
        return {
            'connection_status': test_record.connection_status,
            'test_results': test_record.test_results
        }

    def create_sample_data(self):
        """Créer des données d'exemple dans la base ai_marketing"""
        try:
            connection_params = {
                'host': 'localhost',
                'database': 'ai_marketing',
                'user': 'odoo',
                'password': 'odoo',
                'port': '5432'
            }
            
            connection = psycopg2.connect(**connection_params)
            cursor = connection.cursor()
            
            # 1. Créer la table si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS marketing_data (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    cost DECIMAL(10,2) DEFAULT 0,
                    revenue DECIMAL(10,2) DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'active',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    channel VARCHAR(100),
                    campaign_type VARCHAR(100)
                );
            """)
            
            # 2. Vider la table existante (optionnel)
            cursor.execute("DELETE FROM marketing_data;")
            
            # 3. Insérer des données d'exemple réalistes
            sample_campaigns = [
                ('Google Ads - Electronics', 2500.00, 8500.00, 85, 'active', 'Google Ads', 'Search'),
                ('Facebook Campaign - Fashion', 1800.00, 5400.00, 54, 'active', 'Facebook', 'Social Media'),
                ('Instagram Influencers', 3200.00, 9600.00, 96, 'active', 'Instagram', 'Influencer'),
                ('LinkedIn B2B Campaign', 4500.00, 13500.00, 135, 'active', 'LinkedIn', 'B2B'),
                ('YouTube Pre-roll Ads', 2200.00, 6600.00, 66, 'paused', 'YouTube', 'Video'),
                ('Email Marketing - Newsletter', 500.00, 2000.00, 100, 'active', 'Email', 'Newsletter'),
                ('TikTok Brand Campaign', 1500.00, 3000.00, 30, 'paused', 'TikTok', 'Social Media'),
                ('Pinterest Shopping Ads', 800.00, 2400.00, 48, 'active', 'Pinterest', 'Shopping'),
                ('Twitter Promoted Tweets', 1200.00, 2400.00, 24, 'completed', 'Twitter', 'Social Media'),
                ('Snapchat Stories Ads', 900.00, 1800.00, 18, 'completed', 'Snapchat', 'Stories'),
                ('Amazon PPC Campaign', 3500.00, 10500.00, 105, 'active', 'Amazon', 'PPC'),
                ('Reddit Community Marketing', 600.00, 1200.00, 12, 'active', 'Reddit', 'Community'),
                ('WhatsApp Business Ads', 750.00, 2250.00, 45, 'active', 'WhatsApp', 'Messaging'),
                ('Telegram Channel Promotion', 400.00, 800.00, 8, 'paused', 'Telegram', 'Messaging'),
                ('Google Shopping Campaign', 2800.00, 8400.00, 84, 'active', 'Google Shopping', 'E-commerce'),
                ('Microsoft Ads - Bing', 1600.00, 4800.00, 48, 'active', 'Bing', 'Search'),
                ('Spotify Audio Ads', 1100.00, 2200.00, 22, 'completed', 'Spotify', 'Audio'),
                ('Twitch Gaming Campaign', 1300.00, 2600.00, 26, 'paused', 'Twitch', 'Gaming'),
                ('Discord Community Ads', 500.00, 1000.00, 10, 'active', 'Discord', 'Gaming'),
                ('Clubhouse Audio Campaign', 700.00, 1400.00, 14, 'completed', 'Clubhouse', 'Audio')
            ]
            
            # Insérer les données avec la nouvelle structure
            cursor.executemany("""
                INSERT INTO marketing_data (name, cost, revenue, conversions, status, channel, campaign_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, sample_campaigns)
            
            connection.commit()
            
            # 4. Vérifier les données insérées
            cursor.execute("SELECT COUNT(*) FROM marketing_data;")
            count = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            self.connection_status = f"✅ Sample data created successfully!\n\n📊 Statistics:\n• {count} campaigns created\n• Mix of active, paused, and completed campaigns\n• Various channels: Google, Facebook, Instagram, etc.\n• Realistic cost, revenue, and conversion data\n\nYou can now test the chatbot with real data!"
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success!',
                    'message': f'Created {count} sample campaigns in ai_marketing database!',
                    'type': 'success'
                }
            }
            
        except Exception as e:
            error_msg = f"❌ Error creating sample data: {str(e)}"
            self.connection_status = error_msg
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': f'Failed to create sample data: {str(e)}',
                    'type': 'danger'
                }
            }
    
    def simple_test(self):
        """Test simple avec notification immédiate"""
        try:
            # Test de base
            import psycopg2
            conn = psycopg2.connect(
                host='localhost',
                database='ai_marketing', 
                user='odoo',
                password='odoo'
            )
            
            # Test simple
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            
            # Notification de succès
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Success!',
                    'message': f'Connected successfully to ai_marketing database!\nPostgreSQL version: {version[0][:50]}...',
                    'type': 'success'
                }
            }
            
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Failed',
                    'message': f'Error: {str(e)[:100]}...',
                    'type': 'danger'
                }
            }
    
    def populate_database(self):
        """Remplit la base de données avec des campagnes aléatoires pour test"""
        try:
            connection_params = {
                'host': 'localhost',
                'database': 'ai_marketing',
                'user': 'odoo',
                'password': 'odoo',
                'port': '5432'
            }
            
            connection = psycopg2.connect(**connection_params)
            cursor = connection.cursor()
            
            # Données pour générer des campagnes aléatoires
            channels = ['Google Ads', 'Facebook', 'Instagram', 'LinkedIn', 'YouTube', 'Email', 'TikTok', 'Pinterest']
            types = ['Search', 'Display', 'Video', 'Social', 'Email', 'Shopping', 'Brand', 'Performance']
            statuses = ['active', 'paused', 'completed']
            
            campaigns = []
            for i in range(100):  # Créer 100 campagnes
                name = f"{random.choice(channels)} Campaign {i+1}"
                cost = round(random.uniform(500, 5000), 2)
                # ROI entre 50% et 300%
                roi_multiplier = random.uniform(1.5, 4.0)
                revenue = round(cost * roi_multiplier, 2)
                conversions = int(revenue / random.uniform(20, 100))
                status = random.choice(statuses)
                channel = random.choice(channels)
                campaign_type = random.choice(types)
                
                campaigns.append((name, cost, revenue, conversions, status, channel, campaign_type))
            
            cursor.executemany("""
                INSERT INTO marketing_data (name, cost, revenue, conversions, status, channel, campaign_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, campaigns)
            
            connection.commit()
            _logger.info(f"✅ Created {len(campaigns)} campaigns successfully!")
            
            cursor.close()
            connection.close()
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success!',
                    'message': f'Created {len(campaigns)} random campaigns in ai_marketing database!',
                    'type': 'success'
                }
            }
            
        except Exception as e:
            error_msg = f"❌ Error populating database: {str(e)}"
            _logger.error(error_msg)
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Error',
                    'message': error_msg,
                    'type': 'danger'
                }
            }