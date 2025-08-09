"""Assistant management commands."""

import sys

from cli.utils.helpers import confirm_action
from cli.utils.output import print_error, print_info, print_success


class AssistantCommands:
    """Assistant management commands."""

    def list(self) -> None:
        """List all assistants."""
        try:
            from app.core.database import get_db
            from app.models.assistant import Assistant

            db = next(get_db())
            assistants = db.query(Assistant).all()

            if not assistants:
                print_info("No assistants found")
                db.close()
                return

            print_info(f"Found {len(assistants)} assistants:")
            print("-" * 80)
            print(
                f"{'ID':<10} {'Name':<20} {'Model':<15} {'Status':<10} {'Created':<20}"
            )
            print("-" * 80)

            for assistant in assistants:
                status = "Active" if assistant.is_active else "Inactive"
                created = (
                    assistant.created_at.strftime("%Y-%m-%d %H:%M")
                    if assistant.created_at
                    else "Unknown"
                )
                print(
                    f"{assistant.id:<10} {assistant.name:<20} {assistant.model:<15} {status:<10} {created:<20}"
                )

            db.close()

        except Exception as e:
            print_error(f"Failed to list assistants: {str(e)}")
            sys.exit(1)

    def show(self, assistant_id: str) -> None:
        """Show assistant details."""
        try:
            from app.core.database import get_db
            from app.models.assistant import Assistant

            db = next(get_db())

            # Try to find assistant by ID or name
            assistant = (
                db.query(Assistant)
                .filter(
                    (Assistant.id == assistant_id) | (Assistant.name == assistant_id)
                )
                .first()
            )

            if not assistant:
                print_error(f"Assistant not found: {assistant_id}")
                db.close()
                sys.exit(1)

            print_info(f"Assistant Details for '{assistant.name}':")
            print(f"  ID: {assistant.id}")
            print(f"  Name: {assistant.name}")
            print(f"  Description: {assistant.description or 'N/A'}")
            print(f"  Model: {assistant.model}")
            print(f"  Instructions: {assistant.instructions or 'N/A'}")
            print(f"  Status: {'Active' if assistant.is_active else 'Inactive'}")
            print(f"  Created At: {assistant.created_at}")
            print(f"  Updated At: {assistant.updated_at}")

            db.close()

        except Exception as e:
            print_error(f"Failed to show assistant: {str(e)}")
            sys.exit(1)

    def create(self) -> None:
        """Create assistant interactively."""
        try:
            from datetime import datetime

            from app.core.database import get_db
            from app.models.assistant import Assistant

            print_info("Creating new assistant...")

            # Get user input
            name = input("Name: ").strip()
            if not name:
                print_error("Name is required")
                sys.exit(1)

            description = input("Description (optional): ").strip() or None
            model = input("Model (default: gpt-3.5-turbo): ").strip() or "gpt-3.5-turbo"
            instructions = input("Instructions (optional): ").strip() or None

            # Create assistant
            db = next(get_db())

            # Check if assistant already exists
            existing_assistant = (
                db.query(Assistant).filter(Assistant.name == name).first()
            )
            if existing_assistant:
                print_error("Assistant with this name already exists")
                db.close()
                sys.exit(1)

            # Create new assistant
            new_assistant = Assistant(
                name=name,
                description=description,
                model=model,
                instructions=instructions,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )

            db.add(new_assistant)
            db.commit()
            db.refresh(new_assistant)
            db.close()

            print_success(f"Assistant '{name}' created successfully")

        except Exception as e:
            print_error(f"Failed to create assistant: {str(e)}")
            sys.exit(1)

    def delete(self, assistant_id: str, confirm: bool = False) -> None:
        """Delete assistant."""
        try:
            from app.core.database import get_db
            from app.models.assistant import Assistant

            if not confirm:
                if not confirm_action(
                    f"Are you sure you want to delete assistant '{assistant_id}'?"
                ):
                    print_info("Assistant deletion cancelled")
                    return

            db = next(get_db())

            # Find assistant
            assistant = (
                db.query(Assistant)
                .filter(
                    (Assistant.id == assistant_id) | (Assistant.name == assistant_id)
                )
                .first()
            )

            if not assistant:
                print_error(f"Assistant not found: {assistant_id}")
                db.close()
                sys.exit(1)

            name = assistant.name
            db.delete(assistant)
            db.commit()
            db.close()

            print_success(f"Assistant '{name}' deleted successfully")

        except Exception as e:
            print_error(f"Failed to delete assistant: {str(e)}")
            sys.exit(1)

    def activate(self, assistant_id: str) -> None:
        """Activate assistant."""
        try:
            from datetime import datetime

            from app.core.database import get_db
            from app.models.assistant import Assistant

            db = next(get_db())

            # Find assistant
            assistant = (
                db.query(Assistant)
                .filter(
                    (Assistant.id == assistant_id) | (Assistant.name == assistant_id)
                )
                .first()
            )

            if not assistant:
                print_error(f"Assistant not found: {assistant_id}")
                db.close()
                sys.exit(1)

            if assistant.is_active:
                print_info(f"Assistant '{assistant.name}' is already active")
                db.close()
                return

            assistant.is_active = True
            assistant.updated_at = datetime.utcnow()
            db.commit()
            db.close()

            print_success(f"Assistant '{assistant.name}' activated successfully")

        except Exception as e:
            print_error(f"Failed to activate assistant: {str(e)}")
            sys.exit(1)

    def deactivate(self, assistant_id: str) -> None:
        """Deactivate assistant."""
        try:
            from datetime import datetime

            from app.core.database import get_db
            from app.models.assistant import Assistant

            db = next(get_db())

            # Find assistant
            assistant = (
                db.query(Assistant)
                .filter(
                    (Assistant.id == assistant_id) | (Assistant.name == assistant_id)
                )
                .first()
            )

            if not assistant:
                print_error(f"Assistant not found: {assistant_id}")
                db.close()
                sys.exit(1)

            if not assistant.is_active:
                print_info(f"Assistant '{assistant.name}' is already inactive")
                db.close()
                return

            assistant.is_active = False
            assistant.updated_at = datetime.utcnow()
            db.commit()
            db.close()

            print_success(f"Assistant '{assistant.name}' deactivated successfully")

        except Exception as e:
            print_error(f"Failed to deactivate assistant: {str(e)}")
            sys.exit(1)
