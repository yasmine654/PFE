from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.tenant import Tenant
from app.models.provider import Provider
from app.core.validators import validate_fk_exists

from app.core.database import get_db
from app.schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate
)
from app.crud import account as crud_account
from app.models.account import Account

router = APIRouter(prefix="/accounts", tags=["Accounts"])


# ✅ CREATE
@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):

    validate_fk_exists(db, Tenant, "Tenant", account.tenant_id)
    validate_fk_exists(db, Provider, "Provider", account.provider_id)

    return crud_account.create_account(db, account)


# ✅ GET ALL
@router.get("/", response_model=list[AccountResponse])
def read_accounts(db: Session = Depends(get_db)):
    return crud_account.get_accounts(db)


# ✅ GET ONE
@router.get("/{account_id}", response_model=AccountResponse)
def read_account(account_id: int, db: Session = Depends(get_db)):
    account = crud_account.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


# ✅ UPDATE
@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, account: AccountUpdate, db: Session = Depends(get_db)):
    updated = crud_account.update_account(db, account_id, account)
    if not updated:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated


# ✅ DELETE (simple enfant)
@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):

    account_obj = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account_obj:
        raise HTTPException(status_code=404, detail="Account not found")

    db.delete(account_obj)
    db.commit()

    return {"message": "Account deleted"}