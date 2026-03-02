from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.account import (
    AccountCreate,
    AccountResponse,
    AccountUpdate
)
from app.crud import account as crud_account

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.post("/", response_model=AccountResponse)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    return crud_account.create_account(db, account)


@router.get("/", response_model=list[AccountResponse])
def read_accounts(db: Session = Depends(get_db)):
    return crud_account.get_accounts(db)


@router.get("/{account_id}", response_model=AccountResponse)
def read_account(account_id: int, db: Session = Depends(get_db)):
    account = crud_account.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, account: AccountUpdate, db: Session = Depends(get_db)):
    updated = crud_account.update_account(db, account_id, account)
    if not updated:
        raise HTTPException(status_code=404, detail="Account not found")
    return updated


@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    deleted = crud_account.delete_account(db, account_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted"}