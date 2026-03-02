from fastapi import FastAPI
from app.core.database import engine
from app.models import (
    tenant, provider, region, availability_zone,
    vpc, subnet, vm, vpc_peering,
    acl, elastic_ip, nat_gateway,
    load_balancer, vpn_gateway,
    volume, security_group, waf,account
)
from app.core.database import Base
from app.api import tenant
from app.api import provider
from app.api import account


app = FastAPI(title="Cloud Source of Truth")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}

app.include_router(tenant.router)
app.include_router(provider.router)
app.include_router(account.router)