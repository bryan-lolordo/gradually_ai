"""
Routes package for the API.
Each module in this package represents a group of related endpoints.
"""

from .routes import auth, baseline_schedule, daily_schedule, tasks, habits

__all__ = [
    'auth',
    'baseline_schedule',
    'daily_schedule',
    'tasks',
    'habits'
] 