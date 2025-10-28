import psycopg2
import random
from datetime import datetime, timedelta

def populate_database():
    try:
        connection = psycopg2.connect(
            host="localhost",
            database="ai_marketing",
            user="odoo",
            password="odoo",
            port="5432"
        )
        
        cursor = connection.cursor()
        
        # Vider la table existante (optionnel)
        print("🗑️ Clearing existing data...")
        cursor.execute("DELETE FROM marketing_data;")
        
        # Données pour générer des campagnes réalistes
        channels = ['Google Ads', 'Facebook', 'Instagram', 'LinkedIn', 'YouTube', 'Email', 'TikTok', 'Pinterest', 'Twitter', 'Snapchat']
        types = ['Search', 'Display', 'Video', 'Social', 'Email', 'Shopping', 'Brand', 'Performance', 'Retargeting', 'Awareness']
        statuses = ['active', 'paused', 'completed']
        
        # Campagnes prédéfinies avec des données réalistes
        predefined_campaigns = [
            ('Google Ads - Electronics', 2500.00, 8500.00, 85, 'active', 'Google Ads', 'Search'),
            ('Facebook Campaign - Fashion', 1800.00, 5400.00, 54, 'active', 'Facebook', 'Social'),
            ('Instagram Influencers', 3200.00, 9600.00, 96, 'active', 'Instagram', 'Influencer'),
            ('LinkedIn B2B Campaign', 4500.00, 13500.00, 135, 'active', 'LinkedIn', 'B2B'),
            ('YouTube Pre-roll Ads', 2200.00, 6600.00, 66, 'paused', 'YouTube', 'Video'),
            ('Email Marketing - Newsletter', 500.00, 2000.00, 100, 'active', 'Email', 'Newsletter'),
            ('TikTok Brand Campaign', 1500.00, 3000.00, 30, 'paused', 'TikTok', 'Social'),
            ('Pinterest Shopping Ads', 800.00, 2400.00, 48, 'active', 'Pinterest', 'Shopping'),
            ('Twitter Promoted Tweets', 1200.00, 2400.00, 24, 'completed', 'Twitter', 'Social'),
            ('Snapchat Stories Ads', 900.00, 1800.00, 18, 'completed', 'Snapchat', 'Stories'),
        ]
        
        print("📊 Inserting predefined campaigns...")
        cursor.executemany("""
            INSERT INTO marketing_data (name, cost, revenue, conversions, status, channel, campaign_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, predefined_campaigns)
        
        # Générer 40 campagnes supplémentaires aléatoires
        print("🎲 Generating random campaigns...")
        random_campaigns = []
        for i in range(40):
            name = f"{random.choice(channels)} Campaign {i+11}"
            cost = round(random.uniform(500, 5000), 2)
            # ROI entre 50% et 300%
            roi_multiplier = random.uniform(1.5, 4.0)
            revenue = round(cost * roi_multiplier, 2)
            conversions = int(revenue / random.uniform(20, 100))
            status = random.choice(statuses)
            channel = random.choice(channels)
            campaign_type = random.choice(types)
            
            random_campaigns.append((name, cost, revenue, conversions, status, channel, campaign_type))
        
        cursor.executemany("""
            INSERT INTO marketing_data (name, cost, revenue, conversions, status, channel, campaign_type) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, random_campaigns)
        
        connection.commit()
        
        # Vérifier les données insérées (sans ROUND)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_campaigns,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active,
                CAST(AVG(CASE WHEN cost > 0 THEN ((revenue - cost) / cost) * 100 END) AS DECIMAL(10,2)) as avg_roi,
                SUM(revenue) as total_revenue
            FROM marketing_data;
        """)
        
        stats = cursor.fetchone()
        
        print(f"\n✅ SUCCESS!")
        print(f"📊 Total campaigns: {stats[0]}")
        print(f"🟢 Active campaigns: {stats[1]}")
        print(f"💰 Average ROI: {stats[2]}%")
        print(f"💵 Total revenue: ${stats[3]:,.0f}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    populate_database()
