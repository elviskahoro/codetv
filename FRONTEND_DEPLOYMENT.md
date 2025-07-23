# CodeTV Frontend Deployment Guide

## Overview

This guide covers deploying the CodeTV frontend application to Render.com. The frontend is built with Reflex (Python) and provides a visual interface for the CodeTV AI Learning Path Generator.

## Features

- **Interactive UI**: Clean, modern interface built with Reflex
- **Process Visualization**: Real-time step-by-step progress tracking
- **Demo Mode**: Simulated processing for demonstration purposes
- **Responsive Design**: Works on desktop and mobile devices
- **Easy Deployment**: Optimized for Render.com with one-click deployment

## Quick Deployment to Render.com

### Option 1: Using Render.com Dashboard

1. **Connect Repository**:
   - Go to [Render.com](https://render.com) and sign in
   - Click "New" → "Web Service"
   - Connect your GitHub repository containing this code

2. **Configure Service**:
   - **Name**: `codetv-frontend`
   - **Environment**: `Python 3`
   - **Region**: Choose your preferred region
   - **Branch**: `main` (or your deployment branch)
   - **Root Directory**: `.` (root of repository)

3. **Build Settings**:
   ```bash
   # Build Command
   pip install uv && \
   uv pip install --system -r requirements.txt && \
   reflex init --name codetv --template blank --loglevel INFO && \
   reflex export --frontend-only --no-zip
   ```

   ```bash
   # Start Command
   reflex run --env prod --port $PORT --host 0.0.0.0
   ```

4. **Environment Variables**:
   - `PYTHON_VERSION`: `3.11.8`
   - `NODE_VERSION`: `18.19.0`
   - `REFLEX_ENV`: `prod`

### Option 2: Using render.yaml (Infrastructure as Code)

1. Place the provided `render.yaml` file in your repository root
2. In Render.com dashboard, create a new "Blueprint"
3. Connect your repository and Render will automatically use the configuration

### Option 3: Using Render CLI

```bash
# Install Render CLI
curl -fsSL https://cli.render.com/install | sh

# Deploy from command line
render deploy --service-type web \
  --name codetv-frontend \
  --env python \
  --build-cmd "pip install uv && uv pip install --system -r requirements.txt && reflex init --name codetv --template blank --loglevel INFO && reflex export --frontend-only --no-zip" \
  --start-cmd "reflex run --env prod --port \$PORT --host 0.0.0.0"
```

## Docker Deployment (Alternative)

If you prefer Docker deployment, use the provided `Dockerfile.frontend`:

```bash
# Build the image
docker build -f Dockerfile.frontend -t codetv-frontend .

# Run locally for testing
docker run -p 3000:3000 codetv-frontend

# Deploy to Render using Docker
# (Configure in Render dashboard to use Dockerfile.frontend)
```

## Application Structure

```
app/
├── __init__.py
├── app.py              # Main Reflex application
└── pages/
    └── index/
        ├── __init__.py
        └── page.py     # Main page component with UI logic
```

## Key Features

### Process Step Visualization

The application shows real-time progress through these steps:

1. **Initializing Agent** - Setting up AI agent and tools
2. **Processing URL** - Fetching and parsing awesome list content  
3. **Analyzing Resources** - Categorizing and evaluating learning resources
4. **Generating Learning Paths** - Creating personalized learning pathways
5. **Finalizing Output** - Preparing results and recommendations

### Demo Data

The frontend includes realistic demo data for:
- Resource analysis (topic, language, item count)
- Learning categories with badges
- Recommended learning paths with difficulty levels
- Time estimates and prerequisites

### Responsive Interface

- Mobile-friendly design
- Progress indicators and loading states
- Error handling and validation
- Clean, modern UI with proper spacing

## Environment Configuration

### Production Settings

```python
# rxconfig.py
import reflex as rx

config = rx.Config(
    app_name=\"codetv\",
    # Production optimizations
    db_url=\"sqlite:///reflex.db\",  # Use PostgreSQL in production if needed
)
```

### Environment Variables

- `REFLEX_ENV=prod` - Enables production optimizations
- `PORT` - Automatically set by Render.com
- `PYTHON_VERSION=3.11.8` - Python runtime version
- `NODE_VERSION=18.19.0` - Node.js for frontend assets

## Performance Optimizations

### Docker Multi-stage Build

The `Dockerfile.frontend` uses multi-stage builds to:
- Reduce final image size
- Separate build and runtime dependencies
- Improve security with non-root user
- Enable health checks

### UV Package Manager

Uses UV for faster Python package installation:
- Significantly faster than pip
- Better dependency resolution
- Improved caching

### .dockerignore

Optimized `.dockerignore.frontend` excludes:
- Development files and logs
- Test files and outputs
- IDE configurations
- Git history
- Unnecessary documentation

## Monitoring and Debugging

### Health Checks

The application includes health check endpoints:
- HTTP health check on `/` 
- 30-second intervals with 3 retries
- Proper error handling and logging

### Logs

Access logs through Render.com dashboard:
- Application logs for debugging
- Build logs for deployment issues
- Runtime logs for monitoring

## Scaling and Upgrades

### Render.com Plans

- **Free Tier**: Limited resources, sleeps after inactivity
- **Starter**: \$7/month, no sleep, better performance
- **Standard**: \$25/month, more resources, better SLA

### Upgrade Path

Future enhancements can include:
- Backend API integration
- User authentication
- Database persistence
- Custom domain
- CDN integration

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check Python version compatibility
   - Verify UV installation
   - Review dependency conflicts

2. **Runtime Errors**:
   - Check logs in Render dashboard
   - Verify environment variables
   - Test locally with Docker

3. **Performance Issues**:
   - Upgrade Render plan
   - Optimize dependencies
   - Enable caching

### Support

- Render.com documentation: https://render.com/docs
- Reflex documentation: https://reflex.dev/docs/
- GitHub issues for CodeTV-specific problems

## Security Considerations

- Uses non-root user in Docker container
- No sensitive data stored in frontend
- Environment variables for configuration
- HTTPS enabled by default on Render.com
- Regular dependency updates recommended

## Cost Estimation

### Render.com Pricing

- **Free**: \$0/month (with limitations)
- **Starter**: \$7/month (recommended for demos)
- **Standard**: \$25/month (production ready)

### Monthly Costs for Demo Deployment

- Frontend service: \$0 (Free tier) or \$7 (Starter)
- Custom domain: \$0 (Free with *.onrender.com)
- SSL certificate: \$0 (Included)

**Total**: \$0-7/month depending on performance requirements

## Next Steps

1. Deploy the frontend using one of the methods above
2. Test the demo functionality
3. Customize the UI/UX as needed
4. Consider integrating with the actual backend
5. Add authentication and user management
6. Implement result persistence if required
