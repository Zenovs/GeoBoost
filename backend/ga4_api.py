"""
GeoBoost – Google Analytics 4 API Integration
Mit Quota-Management (exponentielles Backoff)
"""

import json
import time
from typing import List, Dict, Any, Optional


BACKOFF_DELAYS = [10, 30, 60, 300]


class GA4API:
    def __init__(self, property_id: str, credentials_path: str):
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.oauth2 import service_account

        self.property_id = str(property_id)
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=["https://www.googleapis.com/auth/analytics.readonly"],
        )
        self.client = BetaAnalyticsDataClient(credentials=creds)

    def _run_report(
        self,
        dimensions: List[str],
        metrics: List[str],
        start_date: str,
        end_date: str,
        limit: int = 50,
        order_by: Optional[str] = None,
        retry: int = 0,
    ) -> list:
        from google.analytics.data_v1beta.types import (
            DateRange, Dimension, Metric, RunReportRequest,
        )
        try:
            req = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[Dimension(name=d) for d in dimensions],
                metrics=[Metric(name=m) for m in metrics],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                limit=limit,
            )
            response = self.client.run_report(req)
            return response.rows
        except Exception as e:
            err = str(e)
            if ("RESOURCE_EXHAUSTED" in err or "429" in err) and retry < len(BACKOFF_DELAYS):
                wait = BACKOFF_DELAYS[retry]
                print(f"GA4 Quota-Fehler – warte {wait}s (Versuch {retry+1}/4)...")
                time.sleep(wait)
                return self._run_report(dimensions, metrics, start_date, end_date, limit, order_by, retry + 1)
            raise

    def _rows_to_dicts(self, rows, dim_names: List[str], metric_names: List[str]) -> List[Dict]:
        result = []
        for row in rows:
            entry = {}
            for i, name in enumerate(dim_names):
                entry[name] = row.dimension_values[i].value
            for i, name in enumerate(metric_names):
                val = row.metric_values[i].value
                try:
                    entry[name] = float(val) if "." in val else int(val)
                except (ValueError, TypeError):
                    entry[name] = val
            result.append(entry)
        return result

    def get_traffic_overview(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Gesamtübersicht: Users, Sessions, Conversions mit Trend"""
        rows = self._run_report(
            dimensions=[],
            metrics=["totalUsers", "sessions", "conversions", "bounceRate", "averageSessionDuration"],
            start_date=start_date,
            end_date=end_date,
        )
        if not rows:
            return {}
        row = rows[0]
        return {
            "total_users": int(row.metric_values[0].value),
            "sessions": int(row.metric_values[1].value),
            "conversions": int(row.metric_values[2].value),
            "bounce_rate": round(float(row.metric_values[3].value) * 100, 1),
            "avg_session_duration": round(float(row.metric_values[4].value), 0),
        }

    def get_channel_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Traffic nach Kanal"""
        rows = self._run_report(
            dimensions=["sessionDefaultChannelGrouping"],
            metrics=["sessions", "totalUsers", "conversions", "bounceRate"],
            start_date=start_date,
            end_date=end_date,
            limit=20,
        )
        data = []
        for row in rows:
            sessions = int(row.metric_values[0].value)
            conversions = int(row.metric_values[2].value)
            data.append({
                "channel": row.dimension_values[0].value,
                "sessions": sessions,
                "users": int(row.metric_values[1].value),
                "conversions": conversions,
                "conversion_rate": round((conversions / sessions * 100) if sessions > 0 else 0, 2),
                "bounce_rate": round(float(row.metric_values[3].value) * 100, 1),
            })
        return sorted(data, key=lambda x: x["sessions"], reverse=True)

    def get_landingpage_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Top 10 Landing Pages"""
        rows = self._run_report(
            dimensions=["landingPagePlusQueryString"],
            metrics=["sessions", "totalUsers", "conversions", "bounceRate"],
            start_date=start_date,
            end_date=end_date,
            limit=10,
        )
        data = []
        for row in rows:
            sessions = int(row.metric_values[0].value)
            conversions = int(row.metric_values[2].value)
            data.append({
                "page": row.dimension_values[0].value,
                "sessions": sessions,
                "users": int(row.metric_values[1].value),
                "conversions": conversions,
                "conversion_rate": round((conversions / sessions * 100) if sessions > 0 else 0, 2),
                "bounce_rate": round(float(row.metric_values[3].value) * 100, 1),
            })
        return sorted(data, key=lambda x: x["sessions"], reverse=True)

    def get_device_data(self, start_date: str, end_date: str) -> List[Dict]:
        """Device-Split: Mobile, Desktop, Tablet"""
        rows = self._run_report(
            dimensions=["deviceCategory"],
            metrics=["sessions", "totalUsers", "conversions"],
            start_date=start_date,
            end_date=end_date,
        )
        data = []
        for row in rows:
            sessions = int(row.metric_values[0].value)
            conversions = int(row.metric_values[2].value)
            data.append({
                "device": row.dimension_values[0].value,
                "sessions": sessions,
                "users": int(row.metric_values[1].value),
                "conversions": conversions,
                "conversion_rate": round((conversions / sessions * 100) if sessions > 0 else 0, 2),
            })
        return sorted(data, key=lambda x: x["sessions"], reverse=True)
