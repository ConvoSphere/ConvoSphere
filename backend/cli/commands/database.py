"""Database management commands."""

import sys
from cli.utils.output import print_success, print_error, print_info
from cli.utils.validation import validate_revision
from cli.utils.helpers import get_alembic_path, run_alembic_command


class DatabaseCommands:
    """Database management commands."""
    
    def migrate(self) -> None:
        """Run Alembic migrations (upgrade head)."""
        try:
            alembic_path = get_alembic_path()
            if not alembic_path:
                print_error(
                    "Alembic not found in PATH. Please install alembic or run in a virtual environment with backend dependencies."
                )
                sys.exit(1)

            result = run_alembic_command([alembic_path, "upgrade", "head"])
            if result.returncode != 0:
                print_error(result.stderr)
                sys.exit(result.returncode)
                
            print_success("Database migrations completed successfully")
        except FileNotFoundError:
            print_error(
                "Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.",
            )
            sys.exit(1)

    def status(self) -> None:
        """Show Alembic migration status."""
        try:
            alembic_path = get_alembic_path()
            if not alembic_path:
                print_error(
                    "Alembic not found in PATH. Please install alembic or run in a virtual environment with backend dependencies."
                )
                sys.exit(1)

            result = run_alembic_command([alembic_path, "current"])
            if result.returncode != 0:
                print_error(result.stderr)
                sys.exit(result.returncode)
                
            print_info("Current migration status:")
            print(result.stdout)
        except FileNotFoundError:
            print_error(
                "Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.",
            )
            sys.exit(1)

    def downgrade(self, revision: str) -> None:
        """Downgrade DB to a specific revision."""
        if not validate_revision(revision):
            print_error("Invalid revision parameter. Must be a non-empty string.")
            sys.exit(1)
            
        try:
            alembic_path = get_alembic_path()
            if not alembic_path:
                print_error(
                    "Alembic not found in PATH. Please install alembic or run in a virtual environment with backend dependencies."
                )
                sys.exit(1)

            result = run_alembic_command([alembic_path, "downgrade", revision])
            if result.returncode != 0:
                print_error(result.stderr)
                sys.exit(result.returncode)
                
            print_success(f"Database downgraded to revision: {revision}")
        except FileNotFoundError:
            print_error(
                "Alembic not found. Please install alembic or run in a virtual environment with backend dependencies.",
            )
            sys.exit(1)

    def test_connection(self) -> None:
        """Test database connection."""
        try:
            from app.core.database import get_db
            from sqlalchemy import text
            
            db = next(get_db())
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            db.close()
            
            print_success("Database connection test successful")
        except Exception as e:
            print_error(f"Database connection test failed: {str(e)}")
            sys.exit(1)

    def info(self) -> None:
        """Show database information."""
        try:
            from app.core.database import get_db
            from sqlalchemy import text, inspect
            
            db = next(get_db())
            inspector = inspect(db.bind)
            
            print_info("Database Information:")
            print(f"URL: {db.bind.url}")
            print(f"Tables: {inspector.get_table_names()}")
            
            # Get table sizes
            for table_name in inspector.get_table_names():
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    print(f"  {table_name}: {count} rows")
                except Exception:
                    print(f"  {table_name}: Unable to get row count")
            
            db.close()
        except Exception as e:
            print_error(f"Failed to get database info: {str(e)}")
            sys.exit(1)

    def reset(self, confirm: bool = False) -> None:
        """Reset database (drop all tables and recreate)."""
        if not confirm:
            print_error("This will delete all data. Use --confirm to proceed.")
            sys.exit(1)
            
        try:
            from app.core.database import engine
            from app.models import Base
            
            print_info("Dropping all tables...")
            Base.metadata.drop_all(bind=engine)
            
            print_info("Creating all tables...")
            Base.metadata.create_all(bind=engine)
            
            print_success("Database reset completed successfully")
        except Exception as e:
            print_error(f"Database reset failed: {str(e)}")
            sys.exit(1)

    def clear_data(self, confirm: bool = False) -> None:
        """Clear all data from database (keep structure)."""
        if not confirm:
            print_error("This will delete all data. Use --confirm to proceed.")
            sys.exit(1)
            
        try:
            from app.core.database import get_db
            from app.models import Base
            from sqlalchemy import text
            
            db = next(get_db())
            
            # Disable foreign key constraints temporarily
            db.execute(text("PRAGMA foreign_keys=OFF"))
            
            # Clear all tables
            for table in reversed(Base.metadata.sorted_tables):
                db.execute(text(f"DELETE FROM {table.name}"))
            
            # Re-enable foreign key constraints
            db.execute(text("PRAGMA foreign_keys=ON"))
            
            db.commit()
            db.close()
            
            print_success("Database data cleared successfully")
        except Exception as e:
            print_error(f"Failed to clear database data: {str(e)}")
            sys.exit(1)