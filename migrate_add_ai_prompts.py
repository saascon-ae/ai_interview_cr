#!/usr/bin/env python3
"""
Database Migration: Add AI Prompts Table
This migration adds the ai_prompts table to store customizable AI prompts.
"""

from app import create_app, db
from sqlalchemy import text

def migrate():
    """Add ai_prompts table to database"""
    app = create_app()
    
    with app.app_context():
        print("Starting migration: Add AI Prompts table...")
        
        # Check if table already exists
        inspector = db.inspect(db.engine)
        if 'ai_prompts' in inspector.get_table_names():
            print("⚠️  Table 'ai_prompts' already exists. Skipping migration.")
            return
        
        # Create the ai_prompts table (PostgreSQL compatible)
        create_table_sql = text("""
            CREATE TABLE ai_prompts (
                id SERIAL PRIMARY KEY,
                key VARCHAR(100) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                system_message TEXT,
                prompt_template TEXT NOT NULL,
                model VARCHAR(50) DEFAULT 'gpt-3.5-turbo',
                temperature FLOAT DEFAULT 0.5,
                category VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        try:
            db.session.execute(create_table_sql)
            db.session.commit()
            print("✅ Successfully created 'ai_prompts' table")
            
            # Verify table creation
            inspector = db.inspect(db.engine)
            if 'ai_prompts' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('ai_prompts')]
                print(f"   Table columns: {', '.join(columns)}")
                print("\n✨ Migration completed successfully!")
                print("\n📝 Next steps:")
                print("   1. Run 'python init_ai_prompts.py' to populate default prompts")
                print("   2. Access AI Prompts management from Super Admin dashboard\n")
            else:
                print("⚠️  Warning: Table creation reported success but table not found")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error during migration: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()

