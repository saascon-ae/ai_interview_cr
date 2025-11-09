"""
Database initialization script
Run this after setting up your .env file to create database tables
"""
from app import create_app, db
from app.models import User, Organization, Job, Question, Candidate, Application, Answer

def init_database():
    """Initialize the database with tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if super admin exists
        admin = User.query.filter_by(role='super_admin').first()
        if not admin:
            print("\nNo super admin found. Creating default super admin...")
            admin = User(
                email='admin@hrplatform.com',
                role='super_admin',
                is_active=True,
                must_change_password=False
            )
            admin.set_password('admin123')  # Change this password immediately!
            db.session.add(admin)
            db.session.commit()
            print("✓ Super admin created!")
            print(f"  Email: {admin.email}")
            print("  Password: admin123")
            print("\n⚠️  IMPORTANT: Change this password immediately after first login!")
        else:
            print(f"\n✓ Super admin already exists: {admin.email}")
        
        print("\nDatabase initialization complete!")
        print(f"Total users: {User.query.count()}")
        print(f"Total organizations: {Organization.query.count()}")

if __name__ == '__main__':
    init_database()

