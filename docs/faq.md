# FAQ - Frequently Asked Questions

## 🚀 Getting Started

### How do I start ConvoSphere?
```bash
git clone https://github.com/your-org/convosphere.git
cd convosphere
docker-compose up --build
```
Then open [http://localhost:5173](http://localhost:5173).

### What are the system requirements?
- **Browser**: Chrome, Firefox, Safari, Edge (latest versions)
- **Internet**: Stable connection for AI features
- **Storage**: 1GB free space for Docker
- **RAM**: 4GB minimum, 8GB recommended

### Can I use ConvoSphere without Docker?
Yes! See [Manual Setup](quick-start.md#alternative-manual-setup) in the Quick Start guide.

### How do I register an account?
1. Click "Register" in the top right corner
2. Fill out the form with your email and password
3. Confirm your email address
4. Log in and start chatting!

## 💬 Chat & Conversations

### How do I start a new conversation?
- Click "New Chat" on the dashboard
- Use the "+" button in the chat sidebar
- Navigate directly to `/chat`

### Can I attach files to messages?
Yes! Supported formats:
- **PDF** (.pdf) - Up to 50MB
- **Word** (.docx) - Up to 50MB  
- **Text** (.txt) - Up to 10MB
- **Markdown** (.md) - Up to 10MB

### How do I search my chat history?
- Use the search bar in the top navigation
- Type keywords to find specific conversations
- Filter by date range or AI assistant

### Can I export my conversations?
Currently, conversations are stored in the database. Export functionality is planned for future releases.

### Why isn't the AI responding?
Common causes:
- **Internet connection** - Check your connection
- **API limits** - You may have reached usage limits
- **AI provider issues** - The AI service might be down
- **Configuration** - Check if API keys are set correctly

## 📚 Knowledge Base

### What file types can I upload?
- **PDF** (.pdf) - Documents, reports, manuals
- **Word** (.docx) - Office documents
- **Text** (.txt) - Plain text files
- **Markdown** (.md) - Documentation files

### How do I organize my documents?
- **Tags** - Add tags to categorize documents
- **Folders** - Create folders for different topics
- **Search** - Use full-text search to find documents
- **Metadata** - Add descriptions and keywords

### Can I share documents with others?
Currently, documents are private to your account. Sharing functionality is planned for future releases.

### How does the AI use my documents?
The AI can:
- **Reference** specific documents when you ask
- **Search** through your documents for relevant information
- **Summarize** document content
- **Answer questions** based on your documents

### What happens to my documents if I delete my account?
All your documents and data are permanently deleted when you delete your account.

## 🤖 AI & Assistants

### Which AI models are available?
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude-3, Claude-2
- **Local models**: Llama, Mistral (if configured)

### How do I create a custom AI assistant?
1. Go to "Assistants" section
2. Click "Create Assistant"
3. Configure:
   - Name and description
   - Choose AI model
   - Define personality
   - Link knowledge base
4. Save and start using

### Can I use multiple AI assistants in one conversation?
Currently, you can use one assistant per conversation. Multi-assistant conversations are planned for future releases.

### How do I change the AI's personality?
- Edit your assistant's configuration
- Modify the system prompt
- Adjust response parameters
- Link specific knowledge base documents

## 🛠️ Tools & Features

### What tools are available?
- **Web Search** - Find current information online
- **Calculator** - Perform mathematical calculations
- **Code Interpreter** - Execute and debug code
- **File Operations** - Edit and manage files

### How do I use tools in conversations?
1. Select a tool from the tool palette
2. Enter required parameters
3. The tool executes automatically
4. Results appear in the chat

### Can I create my own tools?
Yes! Developers can create custom tools using the MCP (Model Context Protocol) framework. See the [Developer Guide](developer-guide.md) for details.

### Are tools safe to use?
All tools run in a sandboxed environment with security restrictions. File operations are limited to your workspace.

## 👥 Users & Roles

### What user roles are available?
- **Standard User** - Basic chat and knowledge base features
- **Premium User** - Extended features and priority support
- **Moderator** - Community management capabilities
- **Admin** - Full system access and configuration

### How do I upgrade to Premium?
Contact support or check the pricing page for upgrade options.

### Can I change my role?
Role changes must be approved by an administrator. Contact support for role modification requests.

### What are the differences between roles?
- **Standard**: Basic features, limited storage
- **Premium**: Extended features, more storage, priority support
- **Moderator**: Community management, content moderation
- **Admin**: Full system access, user management, configuration

## 🔒 Security & Privacy

### Is my data secure?
Yes! We use:
- **End-to-end encryption** for messages
- **Secure HTTPS** connections
- **Regular security audits**
- **GDPR compliance** for data protection

### Who can see my conversations?
Only you can see your conversations. Administrators can access system logs for security purposes only.

### Can I delete my data?
Yes! You can:
- **Delete individual messages**
- **Delete entire conversations**
- **Delete your account** (permanently removes all data)

### How long is my data stored?
- **Active conversations** - Stored until you delete them
- **Account data** - Stored until account deletion
- **System logs** - Retained for security and debugging

## 🐛 Technical Issues

### The page won't load
Try these steps:
1. **Refresh the browser** (F5)
2. **Clear browser cache**
3. **Try a different browser**
4. **Check your internet connection**

### Chat is not working
- **Check WebSocket connection**
- **Refresh the page**
- **Try logging out and back in**
- **Contact support** if the issue persists

### File upload failed
Common causes:
- **File too large** (max 50MB)
- **Unsupported format**
- **Network interruption**
- **Server storage full**

### Performance is slow
- **Close other browser tabs**
- **Clear browser cache**
- **Try a different browser**
- **Check your internet speed**

## 📱 Mobile & Browser

### Does ConvoSphere work on mobile?
Yes! The interface is fully responsive and works on:
- **Smartphones** (iOS, Android)
- **Tablets** (iPad, Android tablets)
- **All modern browsers**

### Which browsers are supported?
- **Chrome** (recommended)
- **Firefox**
- **Safari**
- **Edge**
- **Opera**

### Can I use ConvoSphere offline?
Basic features work offline, but AI responses and file uploads require an internet connection.

### Is there a mobile app?
Currently, ConvoSphere is web-based only. A mobile app is planned for future releases.

## 💰 Costs & Limits

### Is ConvoSphere free?
Basic features are free. Premium features require a subscription.

### What are the usage limits?
- **Standard users**: 100 messages/day, 1GB storage
- **Premium users**: 1000 messages/day, 10GB storage
- **File uploads**: 50MB per file

### How do I check my usage?
Go to Settings → Usage to see your current limits and usage.

### What happens when I reach limits?
- **Message limits**: You'll need to wait until the next day
- **Storage limits**: You'll need to delete files or upgrade

## 🆘 Support & Help

### How do I get help?
- **Documentation**: This FAQ and user guides
- **Community**: Discord server and GitHub discussions
- **Support**: Email support for premium users
- **Issues**: GitHub Issues for bug reports

### Where can I report bugs?
- **GitHub Issues**: [Report a bug](https://github.com/your-org/convosphere/issues)
- **Email**: support@convosphere.com
- **Discord**: Community support channel

### How do I request new features?
- **GitHub Discussions**: [Feature requests](https://github.com/your-org/convosphere/discussions)
- **Discord**: Feature request channel
- **Email**: feedback@convosphere.com

### Is there a community?
Yes! Join our:
- **Discord Server**: [Community chat](https://discord.gg/your-server)
- **GitHub Discussions**: [Technical discussions](https://github.com/your-org/convosphere/discussions)
- **Blog**: [Updates and tutorials](https://blog.convosphere.com)

## 🔮 Future Features

### What's coming next?
Planned features include:
- **Document sharing** between users
- **Multi-assistant conversations**
- **Mobile app** for iOS and Android
- **Advanced analytics** and insights
- **API access** for integrations
- **Custom themes** and branding

### When will new features be released?
We release updates regularly. Check our [GitHub repository](https://github.com/lichtbaer/ai-chat-app) for the latest updates.

### Can I suggest features?
Absolutely! We welcome feature suggestions through:
- **GitHub Discussions**
- **Discord community**
- **Email feedback**

---

**Still have questions?** [User Guide](user-guide.md) | [Developer Guide](developer-guide.md) | [GitHub Issues](https://github.com/lichtbaer/ai-chat-app/issues)