# Coolify Deployment Guide

## Deployment as Application + API Scheduling

Deploy as a regular **Application** that runs once and exits, triggered weekly via Coolify's API.

### Setup Steps:

1. **Push to Private GitHub Repository**
   ```bash
   git add .
   git commit -m "Prepare for Coolify deployment"
   git push origin main
   ```

2. **Create New Application in Coolify**:
   - Go to your existing Project (where website & DB are)
   - **Add New Resource** → **Application**
   - **Name**: `lego-data-updater`
   - **Repository**: Your private GitHub repo URL
   - **Branch**: `main`

3. **Configure Environment Variables**:
   ```
   SQL_DB_HOST=<your-database-service-name>
   SQL_DB_USER=<your-database-user>
   SQL_DB_PASS=<your-database-password>
   SQL_DB_NAME=mybricklogdb
   ```
   
   💡 **Database Connection**: Use the internal service name from your existing database in the same project.

4. **Build Configuration**:
   - **Dockerfile**: `./Dockerfile`
   - **Build Context**: `/`
   - **Port**: Not needed (batch job)
   - **Health Check**: Disabled

5. **Deploy and Test**:
   - Deploy the application
   - Use "Restart" button to test execution
   - Check logs to verify it runs successfully

### Weekly Scheduling via API

1. **Get API Details** from Coolify:
   - Go to your application settings
   - Find the **API endpoint** for restarting
   - Get your **API token** from Coolify settings

2. **Set up Cron Job** on your server:
   ```bash
   # Edit crontab
   crontab -e
   
   # Add weekly execution (Sunday at 2 AM)
   0 2 * * 0 curl -X POST "https://your-coolify-instance.com/api/v1/applications/{app-id}/restart" \
     -H "Authorization: Bearer YOUR_API_TOKEN" \
     -H "Content-Type: application/json"
   ```

### Alternative: GitHub Actions Scheduler

Create `.github/workflows/weekly-trigger.yml`:
```yaml
name: Weekly LEGO Data Update
on:
  schedule:
    - cron: '0 2 * * 0'  # Sunday at 2 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  trigger-update:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Coolify Deployment
        run: |
          curl -X POST "${{ secrets.COOLIFY_RESTART_URL }}" \
            -H "Authorization: Bearer ${{ secrets.COOLIFY_API_TOKEN }}" \
            -H "Content-Type: application/json"
```

Add these secrets to your GitHub repository:
- `COOLIFY_RESTART_URL`: Your app's restart endpoint
- `COOLIFY_API_TOKEN`: Your Coolify API token

### Advantages:
- ✅ Runs once and exits (no resource waste)
- ✅ Integrated with existing project
- ✅ Automatic database connection
- ✅ CI/CD via GitHub
- ✅ Flexible scheduling options
- ✅ Easy manual triggering for testing

### Database Connection

Your database service in the same Coolify project will be accessible via internal hostname:

```bash
SQL_DB_HOST=your-database-service-name  # e.g., "mybricklogdb" or "database"
SQL_DB_USER=root  # or your configured user
SQL_DB_PASS=your-database-password
SQL_DB_NAME=mybricklogdb
```

### Testing & Monitoring

1. **Initial Test**: Use Coolify's "Restart" button
2. **Check Logs**: Monitor execution in Coolify's log viewer
3. **Verify Database**: Check for updated LEGO data
4. **Test Scheduling**: Verify your cron job or GitHub Action works

### Troubleshooting

- **Connection Issues**: Verify database service name and credentials
- **Download Failures**: Check logs for Rebrickable blocking (should be resolved with anti-blocking measures)
- **SQL Errors**: Check database permissions and foreign key constraints
