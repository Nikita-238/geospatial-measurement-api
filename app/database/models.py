from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class File(Base):
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    crs: Mapped[str | None] = mapped_column(String(100), nullable=True)
    feature_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(
        String(20),
        default="uploaded"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    measurements: Mapped[list["Measurement"]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan"
    )


class Measurement(Base):
    __tablename__ = "measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    file_id: Mapped[int] = mapped_column(
        ForeignKey("files.id", ondelete="CASCADE"),
        nullable=False
    )

    feature_id: Mapped[int] = mapped_column(Integer, nullable=False)

    geometry_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    area: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    length: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    measurement_unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="success"
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    file: Mapped["File"] = relationship(
        back_populates="measurements"
    )