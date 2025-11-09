"""
Migration script to add applicant metadata fields to applications table.
Run this script if you have an existing database that needs the new columns.
"""
from app import create_app, db
from sqlalchemy import text


def add_column_if_missing(column_name: str, column_definition: str) -> None:
    """Add a column to the applications table if it is missing."""
    result = db.session.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='applications' AND column_name=:column_name
            """
        ),
        {'column_name': column_name}
    )

    if result.fetchone():
        print(f"✓ Column '{column_name}' already exists in applications table")
        return

    print(f"Adding column '{column_name}' to applications table...")
    db.session.execute(
        text(f"ALTER TABLE applications ADD COLUMN {column_definition}")
    )
    db.session.commit()
    print(f"✓ Column '{column_name}' added successfully!")


def migrate_add_application_metadata():
    """Ensure the applications table contains metadata columns."""
    app = create_app()

    with app.app_context():
        try:
            add_column_if_missing('ip_address', 'VARCHAR(45)')
            add_column_if_missing('local_time', 'VARCHAR(255)')
            add_column_if_missing('timezone', 'VARCHAR(100)')
        except Exception as exc:
            db.session.rollback()
            print(f"Error during migration: {exc}")
            print("Please check your database connection and try again.")
            raise


if __name__ == '__main__':
    migrate_add_application_metadata()

