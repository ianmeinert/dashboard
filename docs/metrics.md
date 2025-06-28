# Metrics and Monitoring

The Family Dashboard API includes comprehensive Prometheus metrics for monitoring application health, performance, and business metrics.

## Metrics Endpoint

The `/metrics` endpoint provides Prometheus-formatted metrics that can be scraped by monitoring systems.

### Accessing Metrics

```bash
# Get all metrics
curl http://localhost:8000/metrics

# Example response:
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
# http_requests_total{method="GET",endpoint="/health",status="200"} 42
```

## Available Metrics

### HTTP Request Metrics

- `http_requests_total` - Total number of HTTP requests by method, endpoint, and status
- `http_request_duration_seconds` - Request duration histogram
- `http_requests_inprogress` - Currently in-progress requests

### Business Logic Metrics

- `calendar_events_total` - Calendar events processed by operation and status
- `weather_requests_total` - Weather API requests by status and location
- `grocery_items_total` - Grocery items processed by operation and status

### External API Metrics

- `external_api_requests_total` - External API calls by API name, endpoint, and status
- `external_api_duration_seconds` - External API response time histogram

### Database Metrics

- `database_operations_total` - Database operations by operation, table, and status
- `database_operation_duration_seconds` - Database operation duration histogram

### System Health Metrics

- `active_connections` - Number of active database connections
- `memory_usage_bytes` - Current memory usage

### Error Metrics

- `errors_total` - Error counts by error type and endpoint

### Rate Limiting Metrics

- `rate_limit_hits_total` - Rate limit hits by client ID

## Configuration

Metrics can be enabled/disabled using the `METRICS_ENABLED` environment variable:

```bash
# Enable metrics (default)
METRICS_ENABLED=true

# Disable metrics
METRICS_ENABLED=false
```

## Prometheus Configuration

Add the following to your `prometheus.yml` configuration:

```yaml
scrape_configs:
  - job_name: 'family-dashboard'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 15s
```

## Grafana Dashboard

Create a Grafana dashboard to visualize the metrics:

### Key Panels

1. **Request Rate**

   ```
   rate(http_requests_total[5m])
   ```

2. **Response Time (95th percentile)**

   ```
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   ```

3. **Error Rate**

   ```
   rate(errors_total[5m])
   ```

4. **Weather API Success Rate**

   ```
   rate(weather_requests_total{status="success"}[5m]) / rate(weather_requests_total[5m])
   ```

5. **Database Operation Duration**

   ```
   histogram_quantile(0.95, rate(database_operation_duration_seconds_bucket[5m]))
   ```

## Alerting Rules

Example Prometheus alerting rules:

```yaml
groups:
  - name: family-dashboard
    rules:
      - alert: HighErrorRate
        expr: rate(errors_total[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Response time is slow"
          
      - alert: WeatherAPIDown
        expr: rate(weather_requests_total{status="error"}[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Weather API is failing"
```

## Custom Metrics

You can add custom metrics using the provided functions:

```python
from backend.metrics import (
    record_calendar_event,
    record_weather_request,
    record_grocery_operation,
    record_external_api_request,
    record_database_operation,
    record_error,
    record_rate_limit_hit
)

# Record a successful calendar event
record_calendar_event("create", "success")

# Record a weather API request
record_weather_request("success", "New York,NY")

# Record a database operation
record_database_operation("select", "grocery_items", "success", 0.05)

# Record an error
record_error("ValidationError", "/api/weather/current")
```

## Performance Monitoring Decorators

Use the provided decorators to automatically monitor function performance:

```python
from backend.metrics import monitor_performance_async

@monitor_performance_async("get_weather_data", "external_api")
async def get_weather_data(lat: float, lon: float):
    # Your function implementation
    pass

@monitor_performance_async("save_grocery_item", "database")
async def save_grocery_item(item: dict):
    # Your function implementation
    pass
```

## Health Check Integration

The `/health` endpoint automatically records metrics:

- Records health check status and duration
- Provides response time information
- Integrates with monitoring systems

## Best Practices

1. **Monitor Key Metrics**: Focus on request rate, error rate, and response time
2. **Set Appropriate Alerts**: Configure alerts for critical failures and performance degradation
3. **Use Histograms**: Use histograms for response time metrics to understand distribution
4. **Label Metrics**: Use meaningful labels to filter and group metrics
5. **Regular Review**: Regularly review metrics to identify trends and issues

## Troubleshooting

### Metrics Not Available

1. Check if metrics are enabled: `METRICS_ENABLED=true`
2. Verify the `/metrics` endpoint is accessible
3. Check application logs for metrics-related errors

### High Memory Usage

Monitor the `memory_usage_bytes` metric and set alerts for unusual patterns.

### External API Issues

Use the `external_api_requests_total` and `external_api_duration_seconds` metrics to monitor external service health.
