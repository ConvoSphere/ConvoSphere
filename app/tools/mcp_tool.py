                if response.status == 200:
                    await response.json()
                    logger.info(f"Connected to MCP server: {self.server_name}")
                    self.is_connected = True 