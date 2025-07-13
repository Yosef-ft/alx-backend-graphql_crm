# Setup CRM with Celery and Redis
1. Install redis and required libraries
2. Database migration
3. Run service:
```
celery -A graphql_crm worker -l info
```
4. start celery beat scheduler
```
celery -A graphql_crm beat -l info
```
5. Verify output:
```
cat /tmp/crm_report_log.txt
```