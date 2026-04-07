import json
import time
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from google.oauth2 import service_account

class GA4API:
    def __init__(self, property_id, credentials_path):
        self.property_id = property_id
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.client = BetaAnalyticsDataClient(credentials=self.credentials)

    def run_report(self, dimensions, metrics, date_ranges, retry_count=0):
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=dimensions,
                metrics=metrics,
                date_ranges=date_ranges,
            )
            response = self.client.run_report(request)
            return response
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) and retry_count < 4:
                wait_time = [10, 30, 60, 300][retry_count]
                print(f"Quota exceeded, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                return self.run_report(dimensions, metrics, date_ranges, retry_count + 1)
            else:
                raise e

    def get_traffic_data(self, start_date, end_date):
        dimensions = [Dimension(name="sessionDefaultChannelGrouping")]
        metrics = [Metric(name="sessions"), Metric(name="conversions"), Metric(name="conversionRate")]
        date_ranges = [DateRange(start_date=start_date, end_date=end_date)]
        
        response = self.run_report(dimensions, metrics, date_ranges)
        
        data = []
        for row in response.rows:
            data.append({
                'channel': row.dimension_values[0].value,
                'sessions': int(row.metric_values[0].value),
                'conversions': int(row.metric_values[1].value),
                'conversion_rate': float(row.metric_values[2].value)
            })
        
        return data

# Example usage
if __name__ == "__main__":
    ga4 = GA4API("YOUR_PROPERTY_ID", "path/to/credentials.json")
    data = ga4.get_traffic_data("2023-01-01", "2023-12-31")
    print(json.dumps(data, indent=2))