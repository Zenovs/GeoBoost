"""
GeoBoost – PDF Generator
Nutzt Jinja2 für HTML-Templates und WeasyPrint für PDF-Rendering.
Charts werden mit matplotlib als base64-Bilder generiert.
"""

from pathlib import Path
from typing import Dict, Any, List

from jinja2 import Environment, FileSystemLoader


class PDFGenerator:
    def __init__(self, template_dir: str = "templates", config: Dict = None):
        self.template_dir = template_dir
        self.config = config or {}
        self.primary_color = config.get("primary_color", "#1a56db")
        self.accent_color = config.get("accent_color", "#7e3af2")
        self.company_name = config.get("company_name", "GeoBoost")
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters["fmt_num"] = lambda v: f"{int(v):,}".replace(",", "'") if v else "–"
        self.env.filters["fmt_pct"] = lambda v: f"{float(v):.1f}%" if v else "–"

    def generate_pdf(self, data: Dict[str, Any], output_path: str):
        import weasyprint
        charts = self._generate_charts(data)
        template = self.env.get_template("report.html")
        html = template.render(
            **data,
            charts=charts,
            primary_color=self.primary_color,
            accent_color=self.accent_color,
            company_name=self.company_name,
        )
        weasyprint.HTML(string=html, base_url=self.template_dir).write_pdf(output_path)

    def _generate_charts(self, data: Dict) -> Dict[str, str]:
        charts = {}
        results = data.get("results", {})

        # Channel chart
        channels = results.get("ga4_channels", [])
        if not channels and results.get("ga4_traffic", {}).get("rows"):
            channels = results["ga4_traffic"]["rows"]
        if channels:
            charts["channels"] = self._channel_bar_chart(channels)

        # Device chart
        devices = results.get("ga4_devices", [])
        if devices:
            charts["devices"] = self._device_pie_chart(devices)

        # PageSpeed chart
        ps = results.get("pagespeed", {})
        if ps and not ps.get("error"):
            charts["pagespeed"] = self._pagespeed_chart(ps)

        # Speed test waterfall chart
        speedtest = results.get("speedtest", {})
        if speedtest and speedtest.get("pages"):
            charts["speedtest"] = self._speedtest_waterfall(speedtest["pages"])

        return charts

    def _fig_to_base64(self, fig) -> str:
        import io, base64
        import matplotlib.pyplot as plt
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="white")
        buf.seek(0)
        b64 = base64.b64encode(buf.read()).decode()
        plt.close(fig)
        return f"data:image/png;base64,{b64}"

    def _channel_bar_chart(self, channels: List[Dict]) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        channels = sorted(channels, key=lambda x: x.get("sessions", 0), reverse=True)[:8]
        labels = [c.get("channel", "?")[:20] for c in channels]
        sessions = [c.get("sessions", 0) for c in channels]
        conversions = [c.get("conversions", 0) for c in channels]

        x = np.arange(len(labels))
        width = 0.45
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.bar(x - width / 2, sessions, width, label="Sessions", color=self.primary_color, alpha=0.85)
        ax.bar(x + width / 2, conversions, width, label="Conversions", color=self.accent_color, alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
        ax.yaxis.grid(True, alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, fontsize=9)
        ax.set_title("Traffic nach Kanal", fontsize=12, fontweight="bold", pad=10)
        fig.tight_layout()
        return self._fig_to_base64(fig)

    def _device_pie_chart(self, devices: List[Dict]) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        labels = [d.get("device", "?") for d in devices]
        sizes = [d.get("sessions", 0) for d in devices]
        colors = [self.primary_color, "#e5e7eb", self.accent_color][:len(labels)]
        fig, ax = plt.subplots(figsize=(5, 4))
        wedges, _, autotexts = ax.pie(
            sizes, labels=None, colors=colors,
            autopct="%1.0f%%", startangle=90,
            pctdistance=0.75, wedgeprops={"linewidth": 1, "edgecolor": "white"}
        )
        for at in autotexts:
            at.set_fontsize(10)
        ax.legend(wedges, labels, loc="lower center", bbox_to_anchor=(0.5, -0.12),
                  ncol=3, frameon=False, fontsize=9)
        ax.set_title("Gerätekategorien (Sessions)", fontsize=11, fontweight="bold", pad=10)
        fig.tight_layout()
        return self._fig_to_base64(fig)

    def _speedtest_waterfall(self, pages: List[Dict]) -> str:
        """Stacked horizontal bar chart: DNS + TCP + TLS + TTFB + Transfer per page."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        valid = [p for p in pages if p.get("total_ms") and not p.get("error")][:8]
        if not valid:
            return ""

        labels = []
        for p in valid:
            url = p.get("url", "")
            # shorten URL for display
            label = url.replace("https://", "").replace("http://", "")
            label = label.rstrip("/")
            labels.append(label[:35] + "…" if len(label) > 35 else label)

        dns    = np.array([p.get("dns_ms") or 0 for p in valid])
        tcp    = np.array([p.get("connect_ms") or 0 for p in valid])
        tls    = np.array([p.get("tls_ms") or 0 for p in valid])
        ttfb   = np.array([p.get("ttfb_ms") or 0 for p in valid])
        transf = np.array([p.get("transfer_ms") or 0 for p in valid])

        fig, ax = plt.subplots(figsize=(10, max(3, len(valid) * 0.65)))
        y = np.arange(len(labels))
        h = 0.55

        segments = [
            (dns,    "#93c5fd", "DNS"),
            (tcp,    "#6ee7b7", "TCP"),
            (tls,    "#fcd34d", "TLS"),
            (ttfb,   self.primary_color, "TTFB"),
            (transf, self.accent_color,  "Transfer"),
        ]

        left = np.zeros(len(valid))
        for vals, color, label_seg in segments:
            ax.barh(y, vals, h, left=left, color=color, label=label_seg, alpha=0.9)
            left += vals

        # Benchmark lines
        ax.axvline(200, color="#10b981", linestyle="--", linewidth=1, alpha=0.6, label="TTFB Gut (200ms)")
        ax.axvline(1500, color="#f97316", linestyle="--", linewidth=1, alpha=0.6, label="Total Gut (1.5s)")

        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel("Zeit in ms", fontsize=9)
        ax.xaxis.grid(True, alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, fontsize=8, loc="lower right")
        ax.set_title("HTTP Speed-Test – Timing Waterfall", fontsize=11, fontweight="bold", pad=10)
        fig.tight_layout()
        return self._fig_to_base64(fig)

    def _pagespeed_chart(self, ps: Dict) -> str:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        mob = ps.get("mobile", {})
        desk = ps.get("desktop", {})
        categories = ["Performance", "SEO", "Accessibility", "Best Practices"]
        mobile_scores = [mob.get("performance_score") or 0, mob.get("seo_score") or 0,
                         mob.get("accessibility_score") or 0, mob.get("best_practices_score") or 0]
        desktop_scores = [desk.get("performance_score") or 0, desk.get("seo_score") or 0,
                          desk.get("accessibility_score") or 0, desk.get("best_practices_score") or 0]
        x = np.arange(len(categories))
        width = 0.35
        fig, ax = plt.subplots(figsize=(9, 3.5))
        ax.bar(x - width / 2, mobile_scores, width, label="Mobile", color=self.primary_color, alpha=0.85)
        ax.bar(x + width / 2, desktop_scores, width, label="Desktop", color=self.accent_color, alpha=0.85)
        ax.set_ylim(0, 110)
        ax.axhline(90, color="#10b981", linestyle="--", alpha=0.5, linewidth=1, label="Ziel: 90+")
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=10)
        ax.yaxis.grid(True, alpha=0.3, linestyle="--")
        ax.set_axisbelow(True)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.legend(frameon=False, fontsize=9)
        ax.set_title("PageSpeed Scores", fontsize=12, fontweight="bold", pad=10)
        fig.tight_layout()
        return self._fig_to_base64(fig)
