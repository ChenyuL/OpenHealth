#!/usr/bin/env python3
"""
Database Initialization Script for OpenHealth
Creates database, applies schema, and sets up initial data
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DATABASE_HOST', 'localhost'),
    'port': os.getenv('DATABASE_PORT', '5432'),
    'user': os.getenv('DATABASE_USER', 'postgres'),
    'password': os.getenv('DATABASE_PASSWORD', 'password'),
    'database': os.getenv('DATABASE_NAME', 'openhealth')
}

def check_postgresql_connection():
    """Check if PostgreSQL is running and accessible"""
    try:
        # Connect to default postgres database first
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.close()
        logger.info("✅ PostgreSQL connection successful")
        return True
    except psycopg2.Error as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.error("Please ensure PostgreSQL is running and credentials are correct")
        return False

def database_exists():
    """Check if OpenHealth database exists"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (DB_CONFIG['database'],)
        )
        exists = cursor.fetchone() is not None
        
        cursor.close()
        conn.close()
        return exists
    except psycopg2.Error as e:
        logger.error(f"Error checking database existence: {e}")
        return False

def create_database():
    """Create the OpenHealth database"""
    try:
        logger.info(f"Creating database '{DB_CONFIG['database']}'...")
        
        # Connect to postgres database to create our database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f'CREATE DATABASE "{DB_CONFIG["database"]}"')
        
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Database '{DB_CONFIG['database']}' created successfully")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Failed to create database: {e}")
        return False

def apply_schema():
    """Apply database schema from schema.sql"""
    try:
        logger.info("Applying database schema...")
        
        # Read schema file
        schema_path = Path(__file__).parent / 'schema.sql'
        if not schema_path.exists():
            logger.error(f"❌ Schema file not found: {schema_path}")
            return False
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Connect to OpenHealth database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Execute schema
        cursor.execute(schema_sql)
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Database schema applied successfully")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Failed to apply schema: {e}")
        return False
    except FileNotFoundError as e:
        logger.error(f"❌ Schema file not found: {e}")
        return False

def insert_sample_data():
    """Insert sample data for development"""
    try:
        logger.info("Inserting sample data...")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Sample users
        sample_users = [
            ("john.doe@healthtech.com", "John Doe", "HealthTech Innovations", "CEO", "+1-555-0123"),
            ("sarah.smith@medai.com", "Sarah Smith", "MedAI Solutions", "CTO", "+1-555-0124"),
            ("mike.johnson@biocare.com", "Mike Johnson", "BioCare Systems", "Founder", "+1-555-0125"),
        ]
        
        for email, name, company, role, phone in sample_users:
            cursor.execute("""
                INSERT INTO users (email, name, company, role, phone, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
            """, (email, name, company, role, phone, {"source": "sample_data"}))
        
        # Sample knowledge base entries
        knowledge_entries = [
            (
                "Healthcare AI Trends 2024",
                "AI and machine learning are revolutionizing healthcare with applications in diagnostics, drug discovery, and personalized medicine. Key trends include federated learning, explainable AI, and AI-powered clinical decision support systems.",
                "healthcare_trends",
                ["AI", "machine learning", "diagnostics", "drug discovery"]
            ),
            (
                "Investment Criteria for Healthcare Startups",
                "Healthcare investors typically look for: strong clinical evidence, regulatory pathway clarity, experienced team with healthcare background, large addressable market, and clear reimbursement strategy.",
                "investment_criteria",
                ["investment", "criteria", "healthcare", "startups"]
            ),
            (
                "FDA Regulatory Pathway for Digital Health",
                "Digital health products may require FDA approval depending on their intended use. The FDA provides guidance for Software as Medical Device (SaMD) classification and regulatory pathways.",
                "regulatory",
                ["FDA", "regulatory", "digital health", "SaMD"]
            ),
        ]
        
        for title, content, category, tags in knowledge_entries:
            cursor.execute("""
                INSERT INTO knowledge_base (title, content, category, tags)
                VALUES (%s, %s, %s, %s)
            """, (title, content, category, tags))
        
        # Sample conversations and messages
        cursor.execute("""
            INSERT INTO conversations (user_id, title, status, priority)
            SELECT id, 'Healthcare AI Discussion', 'active', 1
            FROM users 
            WHERE email = 'john.doe@healthtech.com'
            LIMIT 1
        """)
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content)
            SELECT c.id, 'user', 'I have an idea for an AI-powered diagnostic tool for early cancer detection. Can you help me understand the market potential?'
            FROM conversations c
            JOIN users u ON c.user_id = u.id
            WHERE u.email = 'john.doe@healthtech.com'
            LIMIT 1
        """)
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content)
            SELECT c.id, 'assistant', 'That sounds like a promising healthcare AI application! Early cancer detection is a critical area with significant market potential. Let me help you explore this idea further. Can you tell me more about the specific type of cancer you are targeting and what makes your approach unique?'
            FROM conversations c
            JOIN users u ON c.user_id = u.id
            WHERE u.email = 'john.doe@healthtech.com'
            LIMIT 1
        """)
        
        cursor.close()
        conn.close()
        
        logger.info("✅ Sample data inserted successfully")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Failed to insert sample data: {e}")
        return False

def verify_installation():
    """Verify that database setup completed successfully"""
    try:
        logger.info("Verifying database installation...")
        
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = [
            'admin_users', 'analytics_events', 'audit_log', 'conversations',
            'documents', 'extraction_schemas', 'knowledge_base', 'meetings',
            'messages', 'system_settings', 'users', 'ventures'
        ]
        
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            return False
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM knowledge_base")
        knowledge_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        admin_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(f"✅ Database verification successful:")
        logger.info(f"   - Tables: {len(tables)} created")
        logger.info(f"   - Users: {user_count} records")
        logger.info(f"   - Knowledge base: {knowledge_count} entries")
        logger.info(f"   - Admin users: {admin_count} records")
        
        return True
        
    except psycopg2.Error as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main initialization function"""
    logger.info("🏥 OpenHealth Database Initialization")
    logger.info("=" * 50)
    
    # Check if PostgreSQL is running
    if not check_postgresql_connection():
        logger.error("Please start PostgreSQL and ensure credentials are correct:")
        logger.error(f"Host: {DB_CONFIG['host']}")
        logger.error(f"Port: {DB_CONFIG['port']}")
        logger.error(f"User: {DB_CONFIG['user']}")
        sys.exit(1)
    
    # Check if database already exists
    if database_exists():
        logger.info(f"Database '{DB_CONFIG['database']}' already exists")
        response = input("Do you want to recreate it? (y/N): ").lower().strip()
        if response == 'y':
            logger.info("Dropping existing database...")
            try:
                conn = psycopg2.connect(
                    host=DB_CONFIG['host'],
                    port=DB_CONFIG['port'],
                    user=DB_CONFIG['user'],
                    password=DB_CONFIG['password'],
                    database='postgres'
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cursor = conn.cursor()
                cursor.execute(f'DROP DATABASE IF EXISTS "{DB_CONFIG["database"]}"')
                cursor.close()
                conn.close()
                logger.info("✅ Existing database dropped")
            except psycopg2.Error as e:
                logger.error(f"❌ Failed to drop database: {e}")
                sys.exit(1)
        else:
            logger.info("Keeping existing database. Exiting.")
            sys.exit(0)
    
    # Create database
    if not create_database():
        sys.exit(1)
    
    # Apply schema
    if not apply_schema():
        sys.exit(1)
    
    # Insert sample data
    if not insert_sample_data():
        logger.warning("⚠️  Sample data insertion failed, but database is functional")
    
    # Verify installation
    if not verify_installation():
        sys.exit(1)
    
    logger.info("\n🎉 Database initialization completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Update your .env file with the correct database credentials")
    logger.info("2. Start the backend server: cd shared-backend && python -m main")
    logger.info("3. Start the frontend: cd chat-system/web-interface && npm start")
    logger.info("4. Access the application at http://localhost:3000")
    logger.info("5. Access admin dashboard at http://localhost:3001")
    
    # Display connection info
    logger.info(f"\nDatabase connection details:")
    logger.info(f"Host: {DB_CONFIG['host']}")
    logger.info(f"Port: {DB_CONFIG['port']}")
    logger.info(f"Database: {DB_CONFIG['database']}")
    logger.info(f"User: {DB_CONFIG['user']}")

if __name__ == "__main__":
    # Load environment variables from .env file if it exists
    env_file = Path(__file__).parent.parent / 'shared-backend' / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.strip().startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    main()