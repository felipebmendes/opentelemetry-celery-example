import os
from celery import Celery
from celery.signals import worker_process_init
from datetime import datetime

from opentelemetry import trace
from opentelemetry.instrumentation.celery import CeleryInstrumentor

app = Celery(
    broker=os.environ['BROKER_URL'],
    backend=os.environ['RESULT_BACKEND'],
)


@worker_process_init.connect
def init_worker(**kwargs):
    trace.get_tracer_provider()
    CeleryInstrumentor().instrument()


@app.task
def current_datetime_async():
    print(f'Trace id inside task: {trace.format_trace_id(trace.get_current_span().get_span_context().trace_id)} ---')
    now = datetime.now().isoformat()
    print(now)
    return now
