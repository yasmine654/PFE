from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base

# ✅ IMPORT MODELS
from app.models import (
    tenant, provider, region, availability_zone,
    vpc, subnet, vm, vpc_peering,
    acl, elastic_ip, nat_gateway,
    load_balancer, vpn_gateway,
    volume, security_group, waf, account
)

# ✅ IMPORT ROUTERS
from app.api import tenant as tenant_api
from app.api import provider as provider_api
from app.api import account as account_api
from app.api import region as region_api
from app.api import vpc as vpc_api
from app.api import availability_zone as az_api
from app.api import subnet as subnet_api
from app.api import vm as vm_api
from app.api import vpc_peering as peering_api
from app.api import acl as acl_api
from app.api import elastic_ip as eip_api
from app.api import load_balancer as lb_api
from app.api import nat_gateway as nat_api
from app.api import security_group as sg_api
from app.api import volume as volume_api
from app.api import vpn_gateway as vpn_api
from app.api import waf as waf_api
from app.api import vip as vip_api
from app.api.conflicts import router as conflict_router

# 🔥 CREATE APP
app = FastAPI(title="Cloud Source of Truth")

# 🔥 CORS (version plus propre)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ CREATE TABLES
Base.metadata.create_all(bind=engine)

# ✅ ROOT TEST
@app.get("/")
def root():
    return {"message": "Backend is running 🚀"}


# ✅ INCLUDE ROUTERS
app.include_router(tenant_api.router)
app.include_router(provider_api.router)
app.include_router(account_api.router)
app.include_router(region_api.router)
app.include_router(vpc_api.router)
app.include_router(az_api.router)
app.include_router(subnet_api.router)
app.include_router(vm_api.router)
app.include_router(peering_api.router)
app.include_router(acl_api.router)
app.include_router(eip_api.router)
app.include_router(lb_api.router)
app.include_router(nat_api.router)
app.include_router(sg_api.router)
app.include_router(volume_api.router)
app.include_router(vpn_api.router)
app.include_router(waf_api.router)
app.include_router(vip_api.router)
app.include_router(conflict_router)