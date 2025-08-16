"""Main CLI entry point."""

import argparse
import sys

from cli.commands.assistant import AssistantCommands
from cli.commands.backup import BackupCommands
from cli.commands.database import DatabaseCommands
from cli.commands.dev import DevCommands
from cli.commands.monitoring import MonitoringCommands
from cli.commands.user import UserCommands
from cli.utils.output import print_error, print_header


class AdminCLI:
    """Main CLI application."""

    def __init__(self):
        self.commands = {
            "db": DatabaseCommands(),
            "user": UserCommands(),
            "backup": BackupCommands(),
            "monitoring": MonitoringCommands(),
            "assistant": AssistantCommands(),
            "dev": DevCommands(),
        }

    def run(self, args):
        """Run the CLI command."""
        command = args.command
        subcommand = args.subcommand

        if command in self.commands:
            # Convert hyphenated subcommands to underscore format for method names
            method_name = subcommand.replace('-', '_')
            handler = getattr(self.commands[command], method_name, None)
            if handler:
                # Extract arguments for the handler
                handler_args = {}
                for key, value in vars(args).items():
                    if key not in ["command", "subcommand"] and value is not None:
                        handler_args[key] = value

                handler(**handler_args)
            else:
                print_error(f"Unknown subcommand: {subcommand}")
                self.show_help()
        else:
            print_error(f"Unknown command: {command}")
            self.show_help()

    def show_help(self):
        """Show help information."""
        print_header("ChatAssistant Admin CLI")
        print(
            """
Usage: python admin.py [COMMAND] [SUBCOMMAND] [OPTIONS]

Commands:
  db          Database management
    migrate   Run database migrations
    status    Show migration status
    downgrade Downgrade to specific revision
    test-connection Test database connection
    info      Show database information
    reset     Reset database (drop all tables)
    clear-data Clear all data from database

  user        User management
    create-admin    Create admin user interactively
    create-secure   Create secure user with strong password
    list            List all users
    show            Show user details
    create          Create user with parameters
    update          Update user
    delete          Delete user
    reset-password  Reset user password

  backup      Backup and restore
    create    Create database backup
    restore   Restore from backup
    list      List available backups
    info      Show backup information

  monitoring  System monitoring
    health    Check system health
    logs      Show recent logs
    containers Show Docker container status

  assistant   Assistant management
    list      List all assistants
    show      Show assistant details
    create    Create assistant interactively
    delete    Delete assistant
    activate  Activate assistant
    deactivate Deactivate assistant

  dev         Development tools
    quality-check Run code quality checks
    api-test  Test API endpoints
    test-data Generate test data

Examples:
  python admin.py db migrate
  python admin.py user create-admin
  python admin.py backup create
  python admin.py monitoring health
  python admin.py dev quality-check
        """
        )


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="ChatAssistant Admin CLI", add_help=False
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Database commands
    db_parser = subparsers.add_parser("db", help="Database management")
    db_subparsers = db_parser.add_subparsers(
        dest="subcommand", help="Database subcommands"
    )

    db_subparsers.add_parser("migrate", help="Run database migrations")
    db_subparsers.add_parser("status", help="Show migration status")

    downgrade_parser = db_subparsers.add_parser(
        "downgrade", help="Downgrade to specific revision"
    )
    downgrade_parser.add_argument("revision", help="Revision to downgrade to")

    db_subparsers.add_parser("test-connection", help="Test database connection")
    db_subparsers.add_parser("info", help="Show database information")

    reset_parser = db_subparsers.add_parser("reset", help="Reset database")
    reset_parser.add_argument("--confirm", action="store_true", help="Confirm reset")

    clear_parser = db_subparsers.add_parser("clear-data", help="Clear all data")
    clear_parser.add_argument("--confirm", action="store_true", help="Confirm clear")

    # User commands
    user_parser = subparsers.add_parser("user", help="User management")
    user_subparsers = user_parser.add_subparsers(
        dest="subcommand", help="User subcommands"
    )

    user_subparsers.add_parser("create-admin", help="Create admin user")
    user_subparsers.add_parser("create-secure", help="Create secure user")
    user_subparsers.add_parser("list", help="List all users")

    show_parser = user_subparsers.add_parser("show", help="Show user details")
    show_parser.add_argument("identifier", help="User ID, email, or username")

    create_parser = user_subparsers.add_parser("create", help="Create user")
    create_parser.add_argument("email", help="User email")
    create_parser.add_argument("username", help="Username")
    create_parser.add_argument("password", help="Password")
    create_parser.add_argument("--first-name", help="First name")
    create_parser.add_argument("--last-name", help="Last name")
    create_parser.add_argument("--role", default="user", help="User role")
    create_parser.add_argument("--status", default="active", help="User status")

    update_parser = user_subparsers.add_parser("update", help="Update user")
    update_parser.add_argument("identifier", help="User ID, email, or username")
    update_parser.add_argument("--email", help="New email")
    update_parser.add_argument("--username", help="New username")
    update_parser.add_argument("--role", help="New role")
    update_parser.add_argument("--status", help="New status")
    update_parser.add_argument("--first-name", help="New first name")
    update_parser.add_argument("--last-name", help="New last name")

    delete_parser = user_subparsers.add_parser("delete", help="Delete user")
    delete_parser.add_argument("identifier", help="User ID, email, or username")
    delete_parser.add_argument(
        "--confirm", action="store_true", help="Confirm deletion"
    )

    user_subparsers.add_parser("reset-password", help="Reset user password")

    # Backup commands
    backup_parser = subparsers.add_parser("backup", help="Backup and restore")
    backup_subparsers = backup_parser.add_subparsers(
        dest="subcommand", help="Backup subcommands"
    )

    create_backup_parser = backup_subparsers.add_parser("create", help="Create backup")
    create_backup_parser.add_argument("--output", help="Output file path")

    restore_parser = backup_subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup_file", help="Backup file path")
    restore_parser.add_argument(
        "--confirm", action="store_true", help="Confirm restore"
    )

    list_backup_parser = backup_subparsers.add_parser("list", help="List backups")
    list_backup_parser.add_argument("--backup-dir", help="Backup directory")

    info_backup_parser = backup_subparsers.add_parser("info", help="Show backup info")
    info_backup_parser.add_argument("backup_file", help="Backup file path")

    # Monitoring commands
    monitoring_parser = subparsers.add_parser("monitoring", help="System monitoring")
    monitoring_subparsers = monitoring_parser.add_subparsers(
        dest="subcommand", help="Monitoring subcommands"
    )

    monitoring_subparsers.add_parser("health", help="Check system health")

    logs_parser = monitoring_subparsers.add_parser("logs", help="Show logs")
    logs_parser.add_argument(
        "--lines", type=int, default=50, help="Number of lines to show"
    )
    logs_parser.add_argument("--level", default="INFO", help="Log level filter")

    monitoring_subparsers.add_parser("containers", help="Show container status")

    # Assistant commands
    assistant_parser = subparsers.add_parser("assistant", help="Assistant management")
    assistant_subparsers = assistant_parser.add_subparsers(
        dest="subcommand", help="Assistant subcommands"
    )

    assistant_subparsers.add_parser("list", help="List assistants")

    show_assistant_parser = assistant_subparsers.add_parser(
        "show", help="Show assistant details"
    )
    show_assistant_parser.add_argument("assistant_id", help="Assistant ID or name")

    assistant_subparsers.add_parser("create", help="Create assistant")

    delete_assistant_parser = assistant_subparsers.add_parser(
        "delete", help="Delete assistant"
    )
    delete_assistant_parser.add_argument("assistant_id", help="Assistant ID or name")
    delete_assistant_parser.add_argument(
        "--confirm", action="store_true", help="Confirm deletion"
    )

    activate_parser = assistant_subparsers.add_parser(
        "activate", help="Activate assistant"
    )
    activate_parser.add_argument("assistant_id", help="Assistant ID or name")

    deactivate_parser = assistant_subparsers.add_parser(
        "deactivate", help="Deactivate assistant"
    )
    deactivate_parser.add_argument("assistant_id", help="Assistant ID or name")

    # Dev commands
    dev_parser = subparsers.add_parser("dev", help="Development tools")
    dev_subparsers = dev_parser.add_subparsers(
        dest="subcommand", help="Dev subcommands"
    )

    dev_subparsers.add_parser("quality-check", help="Run quality checks")

    api_test_parser = dev_subparsers.add_parser("api-test", help="Test API")
    api_test_parser.add_argument(
        "--url", default="http://localhost:8000", help="API URL"
    )

    test_data_parser = dev_subparsers.add_parser("test-data", help="Generate test data")
    test_data_parser.add_argument(
        "--users", type=int, default=5, help="Number of test users"
    )

    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        cli = AdminCLI()
        cli.show_help()
        sys.exit(1)

    if not args.subcommand:
        print_error(f"Missing subcommand for '{args.command}'")
        cli = AdminCLI()
        cli.show_help()
        sys.exit(1)

    cli = AdminCLI()
    cli.run(args)


if __name__ == "__main__":
    main()
