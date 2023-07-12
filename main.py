import os
from celery import group, Celery
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from tasks import current_datetime_async


c = Celery(
    broker=os.environ['BROKER_URL'],
    backend=os.environ['RESULT_BACKEND'],
)

app = FastAPI()

def _configure_tracer(app):
    FastAPIInstrumentor.instrument_app(app)
    CeleryInstrumentor().instrument()
    propagator = B3MultiFormat()
    set_global_textmap(propagator)

def _init_tracer(): 
    resource = Resource(attributes={
    "service.name": os.environ.get("OTEL_SERVICE_NAME", "api"),
      })
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)


_init_tracer()
_configure_tracer(app)



@app.get("/")
async def root():
    return {"message": "I'm Alive!"}


@app.get("/current_datetime")
async def current_datetime():
    
    print(f'Trace id: {trace.format_trace_id(trace.get_current_span().get_span_context().trace_id)} ---')

    future = current_datetime_async.apply_async()
    result = future.get(timeout=2)
    return {"message": {"result": result}}
