"""
Celery worker for CPU-only meaisínfhoghlaim modules.

Workers: alignment (Irish G2P, ColPali), quality (canuint_validator,
         completeness, content_quality), evaluation (RAGAS pipeline).
"""
from celery import Celery
app = Celery("meaisínfhoghlaim", broker="redis://dragonfly:6379/0")
app.conf.task_routes = {"alignment.*": {"queue": "alignment"}, "quality.*": {"queue": "quality"}, "evaluation.*": {"queue": "evaluation"}}
