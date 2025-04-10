from fastapi import FastAPI
from app.services import eql_index_api, data_exporter

app = FastAPI(
    title="Index Tracker",
    description="Top 100 US stocks Index Tracker backend service",
    version="1.0.0"
)

# Register routers
app.include_router(eql_index_api.router, prefix="/services")
app.include_router(data_exporter.router, prefix="/services")

@app.get("/")
def root():
    return {"message": "API service is up & running!"}