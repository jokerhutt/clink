from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.shared.database import Base

class MemoryCategory(Base):

    __tablename__ = "memory_categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique = True,
        index = True
    )

    description: Mapped[str] = mapped_column(
        Text()
    )

    entries: Mapped[list["MemoryEntry"]] = relationship(
        back_populates="category",
        cascade="all, delete_orphan"
    )

class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id: Mapped[int] = mapped_column(primary_key=True)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("memory_categories.id")
    )

    title: Mapped[str] = mapped_column(
        String(255),
        index = True
    )

    summary: Mapped[str] = mapped_column(
        Text()
    )

    category: Mapped["MemoryCategory"] = relationship(
        back_populates="entries"
    )
