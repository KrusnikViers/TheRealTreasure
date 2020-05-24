from sqlalchemy import orm


def get_with_update(session: orm.Session, model, db_id: int, **kwargs):
    instance = session.query(model).filter(model.id == db_id).first()
    if not instance:
        instance = model(id=db_id, **kwargs)
        session.add(instance)
        return instance
    for key, value in kwargs.items():
        if getattr(instance, key) != value:
            setattr(instance, key, value)
    return instance
