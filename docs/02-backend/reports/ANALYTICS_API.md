# Analytics API Documentation

## Overview

The Analytics layer provides comprehensive metrics and aggregations for DailyTaskReport data. All endpoints support date filtering and multi-tenant isolation.

---

## Core Concepts

### Data Aggregation

- **SUM**: Total workers, hours, productivity
- **AVG**: Average hours, productivity per report
- **COUNT**: Number of reports, unique operations/engineers/locations
- **GROUP BY**: operation, location (LocationNode), date, engineer

### Query Optimization

All endpoints use:
- `select_related()` for foreign keys (operation, engineer, location, farm)
- `prefetch_related()` for reverse relations (labor_entries, attachments)
- Database indexes on company, report_date, operation, engineer

### Multi-Tenant

All analytics are company-scoped automatically via `for_company()` filter.

---

## Endpoints

### 1. GET `/analytics/kpi`

**Comprehensive KPI Dashboard**

Provides summary metrics across all time or date range.

#### Query Parameters

- `start_date` (optional): YYYY-MM-DD format
- `end_date` (optional): YYYY-MM-DD format

#### Example Request

```
GET /analytics/kpi?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

#### Response Schema

```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "summary": {
    "total_reports": 150,
    "total_workers": 2450,
    "company_workers": 1800,
    "contractor_workers": 650,
    "avg_workers_per_report": 16.3
  },
  "operations": {
    "total_unique_operations": 8,
    "total_operation_records": 150,
    "avg_productivity": 125.5
  }
}
```

#### Metrics Explained

| Metric | Type | Description |
|--------|------|-------------|
| `total_reports` | integer | Number of DailyTaskReport records |
| `total_workers` | integer | Sum of company_workers + contractor_workers |
| `company_workers` | integer | Sum of company_workers field |
| `contractor_workers` | integer | Sum of contractor_workers field |
| `avg_workers_per_report` | float | Average workers per report |
| `total_unique_operations` | integer | Count of distinct Operation records |
| `total_operation_records` | integer | Total number of operation entries |
| `avg_productivity` | float | Average of actual_productivity field |

#### Database Queries

```python
# Optimized query pattern
reports = DailyTaskReport.objects.for_company(company) \
    .select_related('operation', 'farm', 'engineer', 'location') \
    .prefetch_related('labor_entries')

# Count total
reports.count()

# Aggregate workers
reports.aggregate(
    company_workers=Sum('company_workers'),
    contractor_workers=Sum('contractor_workers'),
    avg_workers=Avg(F('company_workers') + F('contractor_workers'))
)

# Count operations
reports.aggregate(unique_operations=Count('operation', distinct=True))
```

---

### 2. GET `/analytics/productivity`

**Productivity Metrics with Multi-dimensional Grouping**

Shows productivity aggregation by operation, location, and date separately.

#### Query Parameters

- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

#### Example Request

```
GET /analytics/productivity?start_date=2024-01-01
Authorization: Bearer {token}
```

#### Response Schema

```json
{
  "by_operation": [
    {
      "operation__id": 5,
      "operation__name": "Pollination",
      "total_productivity": 2450,
      "avg_productivity": 163.3,
      "count_reports": 15,
      "min_productivity": 80,
      "max_productivity": 250
    },
    {
      "operation__id": 3,
      "operation__name": "Maintenance",
      "total_productivity": 1890,
      "avg_productivity": 135.0,
      "count_reports": 14,
      "min_productivity": 90,
      "max_productivity": 200
    }
  ],
  "by_location": [
    {
      "location__id": 12,
      "location__name": "North Field - Stage A",
      "location__type": "ENCLOSURE",
      "total_productivity": 1200,
      "avg_productivity": 150.0,
      "count_reports": 8
    },
    {
      "location__id": 45,
      "location__name": "South Field - Stage B",
      "location__type": "SECTOR",
      "total_productivity": 980,
      "avg_productivity": 122.5,
      "count_reports": 8
    }
  ],
  "by_date": [
    {
      "report_date": "2024-01-31",
      "total_productivity": 450,
      "avg_productivity": 112.5,
      "count_reports": 4
    },
    {
      "report_date": "2024-01-30",
      "total_productivity": 520,
      "avg_productivity": 130.0,
      "count_reports": 4
    }
  ]
}
```

#### Metrics Explained

- **total_productivity**: Sum of actual_productivity for group
- **avg_productivity**: Average actual_productivity for group
- **count_reports**: Number of reports in group
- **min_productivity**: Minimum productivity (operation grouping only)
- **max_productivity**: Maximum productivity (operation grouping only)

#### Database Queries

```python
# By operation
reports.values('operation__id', 'operation__name').annotate(
    total_productivity=Sum('actual_productivity'),
    avg_productivity=Avg('actual_productivity'),
    count_reports=Count('id'),
    min_productivity=Min('actual_productivity'),
    max_productivity=Max('actual_productivity'),
).order_by('-total_productivity')

# By location
reports.values('location__id', 'location__name', 'location__type').annotate(
    total_productivity=Sum('actual_productivity'),
    avg_productivity=Avg('actual_productivity'),
    count_reports=Count('id'),
).order_by('-total_productivity')

# By date
reports.values('report_date').annotate(
    total_productivity=Sum('actual_productivity'),
    avg_productivity=Avg('actual_productivity'),
    count_reports=Count('id'),
).order_by('-report_date')
```

---

### 3. GET `/analytics/operations-summary`

**Operations Summary with Worker Breakdown**

Comprehensive view of each operation with workers, hours, and locations.

#### Query Parameters

- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

#### Example Request

```
GET /analytics/operations-summary?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

#### Response Schema

```json
{
  "total_operations": 8,
  "operations": [
    {
      "operation__id": 5,
      "operation__name": "Pollination",
      "operation__category": "pollination",
      "total_reports": 45,
      "total_company_workers": 720,
      "total_contractor_workers": 180,
      "total_workers": 900,
      "total_work_hours": 360.5,
      "avg_work_hours": 8.0,
      "total_productivity": 5850,
      "avg_productivity": 130.0,
      "unique_engineers": 5,
      "unique_locations": 12
    },
    {
      "operation__id": 3,
      "operation__name": "Maintenance",
      "operation__category": "maintenance",
      "total_reports": 38,
      "total_company_workers": 570,
      "total_contractor_workers": 150,
      "total_workers": 720,
      "total_work_hours": 304.0,
      "avg_work_hours": 8.0,
      "total_productivity": 4560,
      "avg_productivity": 120.0,
      "unique_engineers": 4,
      "unique_locations": 8
    }
  ]
}
```

#### Metrics Explained

| Metric | Description |
|--------|-------------|
| `total_reports` | Count of reports for operation |
| `total_company_workers` | Sum of company_workers |
| `total_contractor_workers` | Sum of contractor_workers |
| `total_workers` | Sum of both worker types |
| `total_work_hours` | Sum of work_hours |
| `avg_work_hours` | Average work_hours per report |
| `total_productivity` | Sum of actual_productivity |
| `avg_productivity` | Average actual_productivity |
| `unique_engineers` | Count of distinct engineers |
| `unique_locations` | Count of distinct LocationNodes |

#### Database Query

```python
reports.values('operation__id', 'operation__name', 'operation__category').annotate(
    total_reports=Count('id'),
    total_company_workers=Sum('company_workers'),
    total_contractor_workers=Sum('contractor_workers'),
    total_work_hours=Sum('work_hours'),
    avg_work_hours=Avg('work_hours'),
    total_productivity=Sum('actual_productivity'),
    avg_productivity=Avg('actual_productivity'),
    unique_engineers=Count('engineer', distinct=True),
    unique_locations=Count('location', distinct=True),
).order_by('-total_reports')
```

---

### 4. GET `/analytics/workers-by-location`

**Worker Distribution by LocationNode**

Shows workforce allocation across farm locations.

#### Query Parameters

- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

#### Example Request

```
GET /analytics/workers-by-location?start_date=2024-01-15
Authorization: Bearer {token}
```

#### Response Schema

```json
{
  "total_locations": 15,
  "locations": [
    {
      "location__id": 12,
      "location__name": "North Field - Stage A",
      "location__type": "ENCLOSURE",
      "location__farm__id": 1,
      "location__farm__name": "Main Farm",
      "total_company_workers": 280,
      "total_contractor_workers": 70,
      "total_workers": 350,
      "total_reports": 14,
      "unique_engineers": 3,
      "unique_operations": 4
    },
    {
      "location__id": 45,
      "location__name": "South Field - Stage B",
      "location__type": "SECTOR",
      "location__farm__id": 1,
      "location__farm__name": "Main Farm",
      "total_company_workers": 240,
      "total_contractor_workers": 60,
      "total_workers": 300,
      "total_reports": 12,
      "unique_engineers": 2,
      "unique_operations": 3
    }
  ]
}
```

#### Metrics Explained

- **location__type**: STAGE, SECTOR, or ENCLOSURE (LocationNode hierarchy)
- **total_workers**: Company + contractor workers at location
- **unique_engineers**: Distinct engineers working at location
- **unique_operations**: Distinct operations performed at location

#### Database Query

```python
reports.values(
    'location__id', 'location__name', 'location__type',
    'location__farm__id', 'location__farm__name'
).annotate(
    total_company_workers=Sum('company_workers'),
    total_contractor_workers=Sum('contractor_workers'),
    total_workers=F('total_company_workers') + F('total_contractor_workers'),
    total_reports=Count('id'),
    unique_engineers=Count('engineer', distinct=True),
    unique_operations=Count('operation', distinct=True),
).order_by('-total_workers')
```

---

### 5. GET `/analytics/operation-location-matrix`

**Operation × Location Cross-Tabulation**

Shows worker allocation at each operation-location combination.

#### Query Parameters

- `start_date` (optional): YYYY-MM-DD
- `end_date` (optional): YYYY-MM-DD

#### Example Request

```
GET /analytics/operation-location-matrix?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer {token}
```

#### Response Schema

```json
{
  "matrix": [
    {
      "operation__id": 5,
      "operation__name": "Pollination",
      "location__id": 12,
      "location__name": "North Field - Stage A",
      "location__type": "ENCLOSURE",
      "total_workers": 280,
      "company_workers": 210,
      "contractor_workers": 70,
      "total_reports": 14
    },
    {
      "operation__id": 5,
      "operation__name": "Pollination",
      "location__id": 45,
      "location__name": "South Field - Stage B",
      "location__type": "SECTOR",
      "total_workers": 250,
      "company_workers": 190,
      "contractor_workers": 60,
      "total_reports": 12
    },
    {
      "operation__id": 3,
      "operation__name": "Maintenance",
      "location__id": 12,
      "location__name": "North Field - Stage A",
      "location__type": "ENCLOSURE",
      "total_workers": 150,
      "company_workers": 120,
      "contractor_workers": 30,
      "total_reports": 8
    }
  ]
}
```

#### Use Cases

- Identify labor-intensive operation-location combinations
- Resource allocation planning
- Performance comparison across locations
- Bottleneck identification

#### Database Query

```python
reports.values(
    'operation__id', 'operation__name',
    'location__id', 'location__name', 'location__type'
).annotate(
    company_workers=Sum('company_workers'),
    contractor_workers=Sum('contractor_workers'),
    total_workers=F('company_workers') + F('contractor_workers'),
    total_reports=Count('id'),
).order_by('operation__name', '-total_workers')
```

---

## Authentication

All endpoints require:

```
Authorization: Bearer {jwt_token}
```

---

## Error Responses

### 401 Unauthorized

```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 400 Bad Request (Invalid Date Format)

```json
{
  "error": "Invalid date format. Use YYYY-MM-DD"
}
```

---

## Performance Considerations

### Database Indexes

```python
# DailyTaskReport has indexes on:
indexes = [
    models.Index(fields=['company', 'report_date']),
    models.Index(fields=['company', 'operation', 'report_date']),
    models.Index(fields=['report_date']),
    models.Index(fields=['engineer', 'report_date']),
]
```

### Query Optimization

1. **select_related()** for foreign keys:
   - operation
   - farm
   - engineer
   - location
   - location.farm

2. **prefetch_related()** for reverse relations:
   - labor_entries
   - attachments

3. **Count distinct** uses database GROUP BY optimization

### Caching Strategy

Consider caching for high-traffic endpoints:

```python
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # 5 minutes
def kpi_view(request):
    ...
```

---

## Rate Limiting

Recommended rate limits per client:

- Public endpoints: 100 requests/hour
- Analytics endpoints: 500 requests/hour
- Admin endpoints: Unlimited

---

## Future Enhancements

- [ ] Export to CSV/Excel
- [ ] Scheduled report generation
- [ ] Trend analysis (YoY, MoM)
- [ ] Anomaly detection
- [ ] Custom metrics
- [ ] Real-time streaming updates

---

## Integration Examples

### Frontend React Hook

```javascript
const useAnalyticsKPI = (startDate, endDate) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchKPI = async () => {
      setLoading(true);
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response = await fetch(`/api/analytics/kpi?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const result = await response.json();
      setData(result);
      setLoading(false);
    };

    fetchKPI();
  }, [startDate, endDate]);

  return { data, loading };
};
```

### Python Client

```python
import requests
from datetime import datetime, timedelta

class AnalyticsClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {'Authorization': f'Bearer {token}'}

    def get_kpi(self, start_date=None, end_date=None):
        params = {}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()

        response = requests.get(
            f'{self.base_url}/analytics/kpi',
            headers=self.headers,
            params=params
        )
        return response.json()

    def get_productivity(self, start_date=None, end_date=None):
        params = {}
        if start_date:
            params['start_date'] = start_date.isoformat()
        if end_date:
            params['end_date'] = end_date.isoformat()

        response = requests.get(
            f'{self.base_url}/analytics/productivity',
            headers=self.headers,
            params=params
        )
        return response.json()

# Usage
client = AnalyticsClient('http://localhost:8000/api', 'your-token')
start = datetime.now() - timedelta(days=30)
end = datetime.now()

kpi_data = client.get_kpi(start, end)
print(f"Total Workers: {kpi_data['summary']['total_workers']}")
print(f"Avg Productivity: {kpi_data['operations']['avg_productivity']}")
```

---

## Troubleshooting

### No data returned

1. Check date range includes data
2. Verify company_id is set correctly
3. Ensure user has access to reports

### Slow queries

1. Check database indexes exist
2. Verify select_related/prefetch_related used
3. Consider date range filtering

### Authentication errors

1. Verify token is valid
2. Check Authorization header format
3. Ensure token has not expired

---
