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
            
            # Créer la table si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS marketing_data (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    cost DECIMAL(10,2) DEFAULT 0,
                    revenue DECIMAL(10,2) DEFAULT 0,
                    conversions INTEGER DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'active',
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insérer des données d'exemple
            sample_data = [
                ('Google Ads Campaign 1', 1000.00, 2500.00, 25, 'active'),
                ('Facebook Campaign', 800.00, 1800.00, 18, 'active'),
                ('Instagram Ads', 600.00, 1200.00, 12, 'paused'),
                ('LinkedIn Campaign', 1200.00, 3000.00, 30, 'active'),
                ('Twitter Promotion', 400.00, 600.00, 6, 'completed'),
                ('Email Marketing', 300.00, 900.00, 15, 'active'),
                ('YouTube Ads', 1500.00, 4200.00, 42, 'active'),
                ('TikTok Campaign', 500.00, 850.00, 8, 'paused'),
                ('Pinterest Ads', 250.00, 400.00, 4, 'completed'),
                ('Reddit Marketing', 150.00, 300.00, 3, 'active')
            ]
            
            cursor.executemany("""
                INSERT INTO marketing_data (name, cost, revenue, conversions, status) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, sample_data)
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return {
                'success': True,
                'message': f'Sample data created successfully! {len(sample_data)} campaigns added.'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create sample data.'
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