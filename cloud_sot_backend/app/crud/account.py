from sqlalchemy.orm import Session
from app.models.account import Account
from app.schemas.account import AccountCreate

def create_account(db: Session, account: AccountCreate):
    db_account = Account(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


def get_accounts(db: Session):
    return db.query(Account).all()


def get_account(db: Session, account_id: int):
    return db.query(Account).filter(
        Account.account_id == account_id
    ).first()


def update_account(db: Session, account_id: int, account_update):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return None

    update_data = account_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account_id: int):
    account = db.query(Account).filter(
        Account.account_id == account_id
    ).first()

    if not account:
        return False

    db.delete(account)
    db.commit()
    return True