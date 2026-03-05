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
from app.api import region
from app.api import vpc
from app.api import availability_zone
from app.api import subnet
from app.api import vm
from app.api import vpc_peering
from app.api import acl
from app.api import elastic_ip
from app.api import load_balancer
from app.api import nat_gateway
from app.api import security_group
from app.api import volume
from app.api import vpn_gateway
from app.api import waf

app = FastAPI(title="Cloud Source of Truth")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}

app.include_router(tenant.router)
app.include_router(provider.router)
app.include_router(account.router)
app.include_router(region.router)
app.include_router(vpc.router)
app.include_router(availability_zone.router)
app.include_router(subnet.router)
app.include_router(vm.router)
app.include_router(vpc_peering.router)
app.include_router(acl.router)
app.include_router(elastic_ip.router)
app.include_router(load_balancer.router)
app.include_router(nat_gateway.router)
app.include_router(security_group.router)
app.include_router(volume.router)
app.include_router(vpn_gateway.router)
app.include_router(waf.router)