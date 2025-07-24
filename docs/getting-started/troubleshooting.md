# Troubleshooting Guide

This guide helps you resolve common issues when setting up and running the AI Chat Application.

## 🚨 Common Issues

### Application Won't Start

**Symptoms:**
- Services fail to start
- Port conflicts
- Environment variable errors

**Solutions:**

1. **Check Port Availability**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep :8000
   netstat -tulpn | grep :3000
   ```

2. **Verify Environment Variables**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Verify required variables
   cat .env | grep -E "(API_KEY|DATABASE_URL|SECRET_KEY)"
   ```

3. **Check Service Logs**
   ```bash
   # Backend logs
   docker logs ai-chat-backend
   
   # Frontend logs
   docker logs ai-chat-frontend
   ```

### Database Connection Issues

**Symptoms:**
- Database connection errors
- Migration failures
- Data persistence issues

**Solutions:**

1. **Verify Database Service**
   ```bash
   # Check if PostgreSQL is running
   docker ps | grep postgres
   
   # Test connection
   docker exec -it ai-chat-postgres psql -U postgres -d ai_chat
   ```

2. **Check Database Configuration**
   ```bash
   # Verify DATABASE_URL format
   echo $DATABASE_URL
   # Should be: postgresql://username:password@host:port/database
   ```

3. **Reset Database (if needed)**
   ```bash
   # Drop and recreate database
   docker exec -it ai-chat-postgres psql -U postgres -c "DROP DATABASE IF EXISTS ai_chat;"
   docker exec -it ai-chat-postgres psql -U postgres -c "CREATE DATABASE ai_chat;"
   ```

### AI Provider Issues

**Symptoms:**
- AI responses fail
- Authentication errors
- Rate limit errors

**Solutions:**

1. **Verify API Keys**
   ```bash
   # Check if API key is set
   echo $OPENAI_API_KEY
   echo $ANTHROPIC_API_KEY
   ```

2. **Test API Connection**
   ```bash
   # Test OpenAI API
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

3. **Check Rate Limits**
   - Monitor your API usage
   - Implement rate limiting if needed
   - Consider upgrading your plan

### Frontend Issues

**Symptoms:**
- Page won't load
- JavaScript errors
- Styling issues

**Solutions:**

1. **Clear Browser Cache**
   - Hard refresh (Ctrl+F5)
   - Clear browser cache
   - Try incognito mode

2. **Check Console Errors**
   - Open browser developer tools
   - Check Console tab for errors
   - Check Network tab for failed requests

3. **Verify Frontend Build**
   ```bash
   # Rebuild frontend
   cd frontend-react
   npm run build
   ```

### Docker Issues

**Symptoms:**
- Container won't start
- Volume mounting errors
- Network connectivity issues

**Solutions:**

1. **Check Docker Status**
   ```bash
   # Verify Docker is running
   docker --version
   docker-compose --version
   ```

2. **Clean Up Containers**
   ```bash
   # Stop and remove containers
   docker-compose down
   docker system prune -f
   ```

3. **Rebuild Images**
   ```bash
   # Rebuild all images
   docker-compose build --no-cache
   ```

## 🔧 Configuration Issues

### Environment Variables

**Common Problems:**
- Missing required variables
- Incorrect format
- Permission issues

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/ai_chat

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret

# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Optional
REDIS_URL=redis://localhost:6379
WEAVIATE_URL=http://localhost:8080
```

### File Permissions

**Symptoms:**
- Upload failures
- File access errors
- Permission denied messages

**Solutions:**

1. **Check Directory Permissions**
   ```bash
   # Verify upload directory permissions
   ls -la uploads/
   chmod 755 uploads/
   ```

2. **Fix Ownership**
   ```bash
   # Change ownership to application user
   sudo chown -R $USER:$USER uploads/
   ```

## 📊 Performance Issues

### Slow Response Times

**Causes:**
- High system load
- Database performance
- Network latency
- AI provider delays

**Solutions:**

1. **Monitor System Resources**
   ```bash
   # Check CPU and memory usage
   htop
   free -h
   ```

2. **Optimize Database**
   ```bash
   # Check database performance
   docker exec -it ai-chat-postgres psql -U postgres -d ai_chat -c "SELECT * FROM pg_stat_activity;"
   ```

3. **Enable Caching**
   - Configure Redis caching
   - Implement response caching
   - Use CDN for static assets

### Memory Issues

**Symptoms:**
- Out of memory errors
- Slow performance
- Service crashes

**Solutions:**

1. **Increase Memory Limits**
   ```yaml
   # In docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             memory: 2G
   ```

2. **Optimize Application**
   - Reduce concurrent connections
   - Implement connection pooling
   - Use streaming for large files

## 🔍 Debugging Tools

### Logging

**Enable Debug Logging:**
```bash
# Set log level
export LOG_LEVEL=DEBUG

# View logs in real-time
docker-compose logs -f backend
```

### Health Checks

**Test Application Health:**
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000/health
```

### Database Debugging

**Common Queries:**
```sql
-- Check active connections
SELECT * FROM pg_stat_activity;

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🆘 Getting Help

### Before Asking for Help

1. **Check this guide** for your specific issue
2. **Search existing issues** on GitHub
3. **Check the logs** for error messages
4. **Try the solutions** listed above

### When to Ask for Help

- You've tried all solutions in this guide
- You have a unique error message
- The issue affects multiple users
- You need clarification on a solution

### How to Ask for Help

**Include in your request:**
- Error messages (full text)
- Steps to reproduce
- Environment details
- What you've already tried
- Logs (if relevant)

**Channels:**
- [GitHub Issues](https://github.com/your-org/ai-chat-app/issues)
- [Discord Community](https://discord.gg/your-server)
- [Documentation](../user-guide/troubleshooting.md)

## 📚 Additional Resources

- [User Guide Troubleshooting](../user-guide/troubleshooting.md) - More detailed troubleshooting
- [FAQ](../user-guide/faq.md) - Common questions and answers
- [API Documentation](../api/overview.md) - API reference
- [Architecture Overview](../architecture/overview.md) - System design

---

**Still having issues?** Don't hesitate to reach out to the community for help! 🚀