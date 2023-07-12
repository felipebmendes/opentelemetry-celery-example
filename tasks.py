import os
from celery import Celery
from celery.signals import worker_process_init
from datetime import datetime

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat

app = Celery(
    broker=os.environ['BROKER_URL'],
    backend=os.environ['RESULT_BACKEND'],
)


@worker_process_init.connect
def init_worker(**kwargs):

    resource = Resource(attributes={
    "service.name": os.environ.get("OTEL_SERVICE_NAME", "worker"),
      })
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(TracerProvider(resource=resource))
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    CeleryInstrumentor().instrument()
    propagator = B3MultiFormat()
    set_global_textmap(propagator)



@app.task
def current_datetime_async():
    print(f'Trace id inside task: {trace.format_trace_id(trace.get_current_span().get_span_context().trace_id)} ---')
    now = datetime.now().isoformat()
    print(now)
    return now
