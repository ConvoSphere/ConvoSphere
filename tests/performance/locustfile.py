"""
Performance testing with Locust for AI Assistant Platform.
"""
import random

from locust import HttpUser, between, events, task


class AIAssistantUser(HttpUser):
    """Simulate a user interacting with the AI Assistant Platform."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    def on_start(self):
        """Setup user session - login and get token."""
        self.token = None
        self.user_id = None
        self.assistant_id = None
        self.conversation_id = None

        # Register and login
        self._register_and_login()

    def _register_and_login(self):
        """Register a new user and login to get token."""
        try:
            # Generate unique user data
            user_id = random.randint(1000, 9999)
            user_data = {
                "email": f"perf_user_{user_id}@test.com",
                "username": f"perf_user_{user_id}",
                "password": "perfpassword123",
                "first_name": f"Perf{user_id}",
                "last_name": "User",
            }

            # Register user
            with self.client.post(
                "/api/auth/register",
                json=user_data,
                catch_response=True,
            ) as response:
                if response.status_code == 201:
                    self.user_id = user_id
                elif response.status_code == 400:
                    # User might already exist, try to login
                    pass
                else:
                    response.failure(f"Registration failed: {response.status_code}")
                    return

            # Login
            login_data = {
                "username": user_data["email"],
                "password": user_data["password"],
            }

            with self.client.post(
                "/api/auth/login",
                data=login_data,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    login_response = response.json()
                    self.token = login_response.get("access_token")
                    if not self.token:
                        response.failure("No access token in response")
                        return
                else:
                    response.failure(f"Login failed: {response.status_code}")
                    return

            # Get or create assistant
            self._setup_assistant()

        except Exception as e:
            self.environment.runner.quit()
            raise e

    def _setup_assistant(self):
        """Setup assistant for the user."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}

            # Get available assistants
            with self.client.get("/api/assistants", headers=headers) as response:
                if response.status_code == 200:
                    assistants = response.json()
                    if assistants:
                        self.assistant_id = assistants[0]["id"]
                    else:
                        # Create assistant if none exist
                        self._create_assistant()
                else:
                    # Create assistant if endpoint fails
                    self._create_assistant()

        except Exception as e:
            print(f"Error setting up assistant: {e}")

    def _create_assistant(self):
        """Create a test assistant."""
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            assistant_data = {
                "name": f"Perf Assistant {random.randint(1000, 9999)}",
                "description": "Performance test assistant",
                "system_prompt": "You are a helpful assistant for performance testing.",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
            }

            with self.client.post(
                "/api/assistants",
                json=assistant_data,
                headers=headers,
            ) as response:
                if response.status_code == 201:
                    assistant = response.json()
                    self.assistant_id = assistant["id"]

        except Exception as e:
            print(f"Error creating assistant: {e}")

    @task(3)
    def get_user_profile(self):
        """Get user profile - high frequency task."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        with self.client.get("/api/users/me", headers=headers) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get profile: {response.status_code}")

    @task(2)
    def get_assistants(self):
        """Get list of assistants - medium frequency task."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        with self.client.get("/api/assistants", headers=headers) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get assistants: {response.status_code}")

    @task(2)
    def get_conversations(self):
        """Get user conversations - medium frequency task."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        with self.client.get("/api/conversations", headers=headers) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get conversations: {response.status_code}")

    @task(1)
    def create_conversation(self):
        """Create new conversation - low frequency task."""
        if not self.token or not self.assistant_id:
            return

        headers = {"Authorization": f"Bearer {self.token}"}
        conversation_data = {
            "title": f"Perf Conversation {random.randint(1000, 9999)}",
            "assistant_id": self.assistant_id,
        }

        with self.client.post(
            "/api/conversations",
            json=conversation_data,
            headers=headers,
        ) as response:
            if response.status_code == 201:
                conversation = response.json()
                self.conversation_id = conversation["id"]
            else:
                response.failure(f"Failed to create conversation: {response.status_code}")

    @task(4)
    def send_message(self):
        """Send message in conversation - high frequency task."""
        if not self.token or not self.conversation_id:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        # Generate random message
        messages = [
            "Hello, how are you?",
            "Can you help me with a question?",
            "What's the weather like?",
            "Tell me a joke",
            "Explain quantum physics",
            "Write a short story",
            "Calculate 2+2",
            "What's the capital of France?",
        ]

        message_data = {
            "content": random.choice(messages),
            "role": "user",
        }

        with self.client.post(
            f"/api/conversations/{self.conversation_id}/messages",
            json=message_data,
            headers=headers,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Failed to send message: {response.status_code}")

    @task(1)
    def upload_document(self):
        """Upload document - low frequency task."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        # Create a simple text file
        file_content = f"This is a test document for performance testing. Generated at {random.randint(1000, 9999)}."

        files = {
            "file": ("test_document.txt", file_content, "text/plain"),
        }

        with self.client.post(
            "/api/documents/upload",
            files=files,
            headers=headers,
        ) as response:
            if response.status_code != 201:
                response.failure(f"Failed to upload document: {response.status_code}")

    @task(1)
    def search_documents(self):
        """Search documents - low frequency task."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        search_terms = ["test", "document", "performance", "search", "query"]
        query = random.choice(search_terms)

        with self.client.get(
            f"/api/documents/search?q={query}",
            headers=headers,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Failed to search documents: {response.status_code}")

    @task(1)
    def get_system_health(self):
        """Get system health - low frequency task."""
        with self.client.get("/health") as response:
            if response.status_code != 200:
                response.failure(f"Health check failed: {response.status_code}")


class AdminUser(HttpUser):
    """Simulate an admin user with administrative tasks."""

    wait_time = between(5, 10)  # Longer wait time for admin tasks

    def on_start(self):
        """Setup admin session."""
        self.token = None
        self._admin_login()

    def _admin_login(self):
        """Login as admin user."""
        try:
            login_data = {
                "username": "admin@example.com",
                "password": "adminpassword123",
            }

            with self.client.post(
                "/api/auth/login",
                data=login_data,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    login_response = response.json()
                    self.token = login_response.get("access_token")
                else:
                    response.failure(f"Admin login failed: {response.status_code}")

        except Exception as e:
            print(f"Error in admin login: {e}")

    @task(1)
    def get_all_users(self):
        """Get all users - admin task."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        with self.client.get("/api/admin/users", headers=headers) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get users: {response.status_code}")

    @task(1)
    def get_system_stats(self):
        """Get system statistics - admin task."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        with self.client.get("/api/admin/stats", headers=headers) as response:
            if response.status_code != 200:
                response.failure(f"Failed to get stats: {response.status_code}")


class APIUser(HttpUser):
    """Simulate API-only usage (no UI interaction)."""

    wait_time = between(0.5, 2)  # Faster requests for API testing

    def on_start(self):
        """Setup API session."""
        self.token = None
        self._api_login()

    def _api_login(self):
        """Login for API access."""
        try:
            login_data = {
                "username": "api_user@test.com",
                "password": "apipassword123",
            }

            with self.client.post(
                "/api/auth/login",
                data=login_data,
                catch_response=True,
            ) as response:
                if response.status_code == 200:
                    login_response = response.json()
                    self.token = login_response.get("access_token")
                else:
                    # Create API user if doesn't exist
                    self._create_api_user()

        except Exception as e:
            print(f"Error in API login: {e}")

    def _create_api_user(self):
        """Create API user if doesn't exist."""
        try:
            user_data = {
                "email": "api_user@test.com",
                "username": "api_user",
                "password": "apipassword123",
                "first_name": "API",
                "last_name": "User",
            }

            with self.client.post("/api/auth/register", json=user_data) as response:
                if response.status_code == 201:
                    self._api_login()  # Try login again

        except Exception as e:
            print(f"Error creating API user: {e}")

    @task(5)
    def api_chat_completion(self):
        """Test chat completion API - high frequency."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        chat_data = {
            "messages": [
                {"role": "user", "content": "Hello, this is a performance test."},
            ],
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 100,
        }

        with self.client.post(
            "/api/chat/completions",
            json=chat_data,
            headers=headers,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Chat completion failed: {response.status_code}")

    @task(3)
    def api_embedding(self):
        """Test embedding API - medium frequency."""
        if not self.token:
            return

        headers = {"Authorization": f"Bearer {self.token}"}

        embedding_data = {
            "input": "This is a test text for embedding generation.",
            "model": "text-embedding-ada-002",
        }

        with self.client.post(
            "/api/embeddings",
            json=embedding_data,
            headers=headers,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Embedding failed: {response.status_code}")


# Event handlers for monitoring
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when a test is starting."""
    print("Performance test starting...")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when a test is ending."""
    print("Performance test ending...")

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, start_time, url, **kwargs):
    """Called for every request."""
    if exception:
        print(f"Request failed: {name} - {exception}")
    elif response.status_code >= 400:
        print(f"Request error: {name} - {response.status_code}")
