import os
from celery import group, Celery
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from tasks import current_datetime_async

app = FastAPI()

tracer = trace.get_tracer(__name__)
trace_provider = TracerProvider(resource=Resource.create({"service.name": "carol-sql-orchestration"}))
trace.set_tracer_provider(trace_provider)
set_global_textmap(B3MultiFormat())
FastAPIInstrumentor.instrument_app(app)
# CeleryInstrumentor().instrument()
LoggingInstrumentor().instrument(set_logging_format=True)

c = Celery(
    broker=os.environ['BROKER_URL'],
    backend=os.environ['RESULT_BACKEND'],
)


@app.get("/")
async def root():
    return {"message": "I'm Alive!"}


@app.get("/current_datetime")
async def current_datetime():
    
    print(f'Trace id: {trace.format_trace_id(trace.get_current_span().get_span_context().trace_id)} ---')

    future = current_datetime_async.apply_async()
    result = future.get(timeout=2)
    return {"message": {"result": result}}
