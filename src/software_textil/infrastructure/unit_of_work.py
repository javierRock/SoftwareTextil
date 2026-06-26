"""Implementaciones de UnitOfWork de infraestructura."""

from software_textil.application.unit_of_work import NoOpUnitOfWork
from software_textil.infrastructure.persistence.database import db


class InMemoryUnitOfWork(NoOpUnitOfWork):
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


class SQLAlchemyUnitOfWork(NoOpUnitOfWork):
    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()
