from sqlalchemy.orm import Session
from app.models.vm import VM


def create_vm(db: Session, vm):
    db_vm = VM(**vm.model_dump())
    db.add(db_vm)
    db.commit()
    db.refresh(db_vm)
    return db_vm


def get_vms(db: Session):
    return db.query(VM).all()


def get_vm(db: Session, vm_id: int):
    return db.query(VM).filter(
        VM.vm_id == vm_id
    ).first()


def update_vm(db: Session, vm_id: int, vm_update):
    vm = get_vm(db, vm_id)
    if not vm:
        return None

    update_data = vm_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(vm, key, value)

    db.commit()
    db.refresh(vm)
    return vm