from fastapi import FastAPI
from app.routers import accounts, contacts, opportunities, cases
from app.config import get_settings
import logging

logging.basicConfig(level=get_settings().log_level)

app = FastAPI(
    title="SalesforceSync",
    description=(
        "Python REST service integrating with Salesforce APIs. "
        "Manages Accounts, Contacts, Opportunities, and Cases "
        "via simple-salesforce with full OOP service design."
    ),
    version="0.1.0",
)

app.include_router(accounts.router)
app.include_router(contacts.router)
app.include_router(opportunities.router)
app.include_router(cases.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": "salesforce-sync"}


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "SalesforceSync",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": [
            "/accounts",
            "/contacts",
            "/opportunities",
            "/cases",
        ],
    }
