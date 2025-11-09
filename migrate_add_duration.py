"""
Migration script to add duration column to answers table
Run this script if you have an existing database that needs the duration field
"""
from app import create_app, db
from sqlalchemy import text

def migrate_add_duration():
    """Add duration column to answers table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if column already exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='answers' AND column_name='duration'
            """))
            
            if result.fetchone():
                print("✓ Duration column already exists in answers table")
                return
            
            # Add duration column
            print("Adding duration column to answers table...")
            db.session.execute(text("""
                ALTER TABLE answers 
                ADD COLUMN duration FLOAT
            """))
            db.session.commit()
            print("✓ Duration column added successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error during migration: {e}")
            print("Please check your database connection and try again.")
            raise

if __name__ == '__main__':
    migrate_add_duration()

