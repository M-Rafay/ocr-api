# Deploy OCR API to Render

This guide will walk you through deploying the OCR API to Render, a cloud platform that makes it easy to deploy web services.

## Prerequisites

- A Render account (free tier available)
- Your OCR API code in a Git repository (GitHub, GitLab, etc.)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository contains these files:
- `render.yaml` - Render configuration
- `requirements.txt` - Python dependencies
- `Procfile` - Process definition
- `runtime.txt` - Python version specification
- `app/` directory with all your application code

### 2. Connect to Render

1. **Sign up/Login** to [Render](https://render.com)
2. **Connect your Git repository**:
   - Click "New +" → "Web Service"
   - Connect your GitHub/GitLab account
   - Select your OCR API repository

### 3. Configure the Service

#### Option A: Using render.yaml (Recommended)

If you have the `render.yaml` file in your repository:

1. **Select "Use render.yaml"** when creating the service
2. **Render will automatically detect** the configuration
3. **Click "Create Web Service"**

#### Option B: Manual Configuration

If not using render.yaml:

1. **Name**: `ocr-api`
2. **Environment**: `Python`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Health Check Path**: `/health`

### 4. Environment Variables

The `render.yaml` file already configures SQLite automatically. If you need to set environment variables manually:

| Key | Value | Description |
|-----|-------|-------------|
| `PYTHON_VERSION` | `3.10.0` | Python version |
| `DATABASE_URL` | `sqlite:///./ocr.db` | SQLite database (file-based, no external dependencies) |

### 5. Deploy

1. **Click "Create Web Service"**
2. **Wait for build** (5-10 minutes for first deployment)
3. **Monitor the logs** for any issues

## Configuration Files

### render.yaml
```yaml
services:
  - type: web
    name: ocr-api
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: DATABASE_URL
        value: sqlite:///./ocr.db
    healthCheckPath: /health
```

### Procfile
```
web: gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### runtime.txt
```
python-3.10.0
```

## Deployment Options

### Free Tier (Starter Plan)
- **Cost**: Free
- **Limitations**: 
  - 750 hours/month
  - Sleeps after 15 minutes of inactivity
  - 512MB RAM
  - Shared CPU
- **Database**: SQLite (file-based, no external dependencies)
- **Storage**: Persistent file storage for SQLite database

### Paid Plans
- **Standard**: $7/month
  - Always on
  - 1GB RAM
  - Dedicated CPU
  - Can still use SQLite or upgrade to PostgreSQL

## Post-Deployment

### 1. Test Your API

Once deployed, test your endpoints:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Extract text from image URL
curl -X POST https://your-app-name.onrender.com/extract-text \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/image.png",
    "user_id": "test-user",
    "language": "en"
  }'
```

### 2. Monitor Your Service

- **Logs**: View real-time logs in Render dashboard
- **Metrics**: Monitor CPU, memory, and response times
- **Health**: Automatic health checks at `/health`

### 3. Custom Domain (Optional)

1. **Add custom domain** in Render dashboard
2. **Configure DNS** to point to your Render service
3. **SSL certificate** is automatically provisioned

## Troubleshooting

### Common Issues

#### 1. Build Failures
**Symptoms**: Build fails during dependency installation

**Solutions**:
- Check `requirements.txt` for correct package names
- Ensure all dependencies are compatible
- Monitor build logs for specific errors

#### 2. Runtime Errors
**Symptoms**: Service starts but fails during requests

**Solutions**:
- Check application logs in Render dashboard
- Verify environment variables are set correctly
- Test locally before deploying

#### 3. Memory Issues
**Symptoms**: Service crashes or becomes unresponsive

**Solutions**:
- Upgrade to paid plan for more memory
- Optimize image processing (reduce image size)
- Implement better error handling

#### 4. OpenCV Issues
**Symptoms**: `libGL.so.1` or similar errors

**Solutions**:
- The Dockerfile includes necessary system dependencies
- For Render, the build process should handle this automatically
- If issues persist, check the build logs

### Debugging Steps

1. **Check Build Logs**:
   - Go to your service in Render dashboard
   - Click on "Logs" tab
   - Look for error messages during build

2. **Check Runtime Logs**:
   - Monitor logs during API requests
   - Look for Python exceptions or errors

3. **Test Locally**:
   - Ensure everything works locally first
   - Use the same Python version (3.10.0)

4. **Verify Dependencies**:
   - Check that all packages in `requirements.txt` are compatible
   - Ensure no conflicting versions

## Performance Optimization

### For Free Tier
- **Image size**: Keep images under 5MB
- **Processing time**: Optimize for faster processing
- **Memory usage**: Monitor memory consumption

### For Paid Plans
- **Concurrent requests**: Handle multiple requests efficiently
- **Database optimization**: Use PostgreSQL for better performance
- **Caching**: Implement result caching for repeated requests

## Security Considerations

### Production Deployment
1. **CORS Configuration**: Update CORS settings for your domain
2. **Rate Limiting**: Implement proper rate limiting
3. **Input Validation**: Validate all inputs thoroughly
4. **Error Handling**: Don't expose sensitive information in errors

### Environment Variables
- **Database URLs**: Use environment variables for database connections
- **API Keys**: Store sensitive data in environment variables
- **CORS Origins**: Configure allowed origins properly

## Monitoring and Maintenance

### Health Checks
- **Automatic**: Render checks `/health` endpoint
- **Manual**: Monitor response times and success rates

### Logs
- **Application logs**: Monitor for errors and performance issues
- **Access logs**: Track API usage and patterns

### Updates
- **Automatic**: Render deploys on Git pushes
- **Manual**: Trigger deployments from dashboard

## Cost Optimization

### Free Tier
- **Sleep mode**: Service sleeps after inactivity
- **Wake time**: 30-60 seconds to wake up
- **Usage limits**: Monitor your 750 hours/month

### Paid Plans
- **Right-sizing**: Choose appropriate plan for your needs
- **Database costs**: PostgreSQL costs extra
- **Bandwidth**: Monitor data transfer costs

## Next Steps

1. **Deploy your service** following the steps above
2. **Test all endpoints** to ensure they work
3. **Monitor performance** and adjust as needed
4. **Set up monitoring** for production use
5. **Configure custom domain** if needed
6. **Implement proper security** measures

Your OCR API should now be live and accessible via your Render URL! 