"""Backup and restore commands."""

import os
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from cli.utils.helpers import confirm_action, format_file_size, get_backup_dir
from cli.utils.output import print_error, print_info, print_success


class BackupCommands:
    """Backup and restore commands."""

    def create(self, output: str = None) -> None:
        """Create database backup."""
        try:
            import json

            from app.core.database import get_db
            from app.models import Base
            from sqlalchemy import text

            # Determine backup filename
            if not output:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = get_backup_dir()
                os.makedirs(backup_dir, exist_ok=True)
                output = os.path.join(backup_dir, f"backup_{timestamp}.zip")

            print_info(f"Creating backup: {output}")

            # Create backup directory
            backup_path = Path(output)
            backup_path.parent.mkdir(parents=True, exist_ok=True)

            # Get database connection
            db = next(get_db())

            # Create backup data
            backup_data = {"timestamp": datetime.now().isoformat(), "tables": {}}

            # Export each table
            for table in Base.metadata.sorted_tables:
                table_name = table.name
                print_info(f"Backing up table: {table_name}")

                try:
                    # Get table data
                    result = db.execute(text(f"SELECT * FROM {table_name}"))
                    rows = result.fetchall()

                    # Convert to list of dicts
                    columns = result.keys()
                    table_data = []
                    for row in rows:
                        row_dict = {}
                        for i, column in enumerate(columns):
                            value = row[i]
                            # Handle datetime objects
                            if hasattr(value, "isoformat"):
                                value = value.isoformat()
                            row_dict[column] = value
                        table_data.append(row_dict)

                    backup_data["tables"][table_name] = table_data

                except Exception as e:
                    print_error(f"Failed to backup table {table_name}: {str(e)}")
                    continue

            db.close()

            # Create ZIP file
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add data file
                zipf.writestr("backup_data.json", json.dumps(backup_data, indent=2))

                # Add schema file
                schema_data = {
                    "tables": [table.name for table in Base.metadata.sorted_tables]
                }
                zipf.writestr("schema.json", json.dumps(schema_data, indent=2))

            # Get file size
            file_size = os.path.getsize(output)
            print_success(f"Backup created successfully: {output}")
            print_info(f"Size: {format_file_size(file_size)}")

        except Exception as e:
            print_error(f"Failed to create backup: {str(e)}")
            sys.exit(1)

    def restore(self, backup_file: str, confirm: bool = False) -> None:
        """Restore database from backup."""
        try:
            import json

            from app.core.database import get_db
            from app.models import Base
            from sqlalchemy import text

            if not os.path.exists(backup_file):
                print_error(f"Backup file not found: {backup_file}")
                sys.exit(1)

            if not confirm:
                if not confirm_action(
                    f"Are you sure you want to restore from '{backup_file}'? This will overwrite current data."
                ):
                    print_info("Restore cancelled")
                    return

            print_info(f"Restoring from backup: {backup_file}")

            # Extract backup
            with zipfile.ZipFile(backup_file, "r") as zipf:
                # Read backup data
                backup_data = json.loads(zipf.read("backup_data.json"))
                schema_data = json.loads(zipf.read("schema.json"))

            # Get database connection
            db = next(get_db())

            # Clear existing data
            print_info("Clearing existing data...")
            for table in reversed(Base.metadata.sorted_tables):
                try:
                    db.execute(text(f"DELETE FROM {table.name}"))
                except Exception as e:
                    print_error(f"Failed to clear table {table.name}: {str(e)}")

            # Restore data
            print_info("Restoring data...")
            for table_name, table_data in backup_data["tables"].items():
                if not table_data:
                    continue

                print_info(f"Restoring table: {table_name} ({len(table_data)} rows)")

                try:
                    for row_data in table_data:
                        # Build INSERT statement
                        columns = list(row_data.keys())
                        values = list(row_data.values())
                        placeholders = ", ".join(["?" for _ in columns])
                        column_list = ", ".join(columns)

                        query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
                        db.execute(text(query), values)

                except Exception as e:
                    print_error(f"Failed to restore table {table_name}: {str(e)}")
                    continue

            db.commit()
            db.close()

            print_success("Database restored successfully")

        except Exception as e:
            print_error(f"Failed to restore backup: {str(e)}")
            sys.exit(1)

    def list(self, backup_dir: str = None) -> None:
        """List available backups."""
        try:
            if not backup_dir:
                backup_dir = get_backup_dir()

            if not os.path.exists(backup_dir):
                print_info(f"Backup directory not found: {backup_dir}")
                return

            print_info(f"Available backups in: {backup_dir}")
            print("-" * 80)
            print(f"{'Filename':<30} {'Size':<12} {'Date':<20}")
            print("-" * 80)

            backup_files = []
            for file in os.listdir(backup_dir):
                if file.endswith(".zip"):
                    file_path = os.path.join(backup_dir, file)
                    file_size = os.path.getsize(file_path)
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                    backup_files.append(
                        {"name": file, "size": file_size, "time": file_time}
                    )

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x["time"], reverse=True)

            for backup in backup_files:
                print(
                    f"{backup['name']:<30} {format_file_size(backup['size']):<12} {backup['time'].strftime('%Y-%m-%d %H:%M:%S'):<20}"
                )

            if not backup_files:
                print_info("No backup files found")

        except Exception as e:
            print_error(f"Failed to list backups: {str(e)}")
            sys.exit(1)

    def info(self, backup_file: str) -> None:
        """Show backup information."""
        try:
            import json

            if not os.path.exists(backup_file):
                print_error(f"Backup file not found: {backup_file}")
                sys.exit(1)

            print_info(f"Backup Information: {backup_file}")
            print("-" * 50)

            # File info
            file_size = os.path.getsize(backup_file)
            file_time = datetime.fromtimestamp(os.path.getmtime(backup_file))

            print(f"Size: {format_file_size(file_size)}")
            print(f"Created: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Extract and read backup data
            with zipfile.ZipFile(backup_file, "r") as zipf:
                try:
                    backup_data = json.loads(zipf.read("backup_data.json"))
                    schema_data = json.loads(zipf.read("schema.json"))

                    print(f"Backup Date: {backup_data.get('timestamp', 'Unknown')}")
                    print(f"Tables: {len(backup_data.get('tables', {}))}")

                    print("\nTable Details:")
                    for table_name, table_data in backup_data.get("tables", {}).items():
                        row_count = len(table_data) if table_data else 0
                        print(f"  {table_name}: {row_count} rows")

                except Exception as e:
                    print_error(f"Failed to read backup data: {str(e)}")

        except Exception as e:
            print_error(f"Failed to get backup info: {str(e)}")
            sys.exit(1)
