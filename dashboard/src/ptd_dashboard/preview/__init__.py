"""Preview adaptation services for dashboard-host display models."""

from ptd_dashboard.preview.models import DashboardPreview
from ptd_dashboard.preview.service import adapt_preview_response

__all__ = [
    "DashboardPreview",
    "adapt_preview_response",
]
