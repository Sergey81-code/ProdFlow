# from datetime import date, datetime

# import sqlalchemy
# from .core import Base, uuid_pk
# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy import (
#     ARRAY,
#     UUID,
#     CheckConstraint,
#     Date,
#     DateTime,
#     ForeignKey,
#     Index,
#     Integer,
#     String,
#     Boolean,
#     func,
# )


# class Detail(Base):
#     __tablename__ = "detail"

#     id: Mapped[uuid_pk]
#     name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
#     code: Mapped[str | None] = mapped_column(String(256), unique=True, nullable=True)
#     description: Mapped[str | None] = mapped_column(String, nullable=True)

#     __table_args__ = (
#         Index("ix_details_name", "name"),
#         Index("ix_details_code", "code", postgresql_using="hash"),
#     )


# class OperationStage(Base):
#     __tablename__ = "operation_stages"

#     id: Mapped[uuid_pk]
#     name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)


# class Operation(Base):
#     __tablename__ = "operations"

#     id: Mapped[uuid_pk]
#     name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
#     code: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
#     description: Mapped[str | None] = mapped_column(String, nullable=True)

#     __table_args__ = (
#         Index("ix_operations_name", "name"),
#         Index("ix_operations_code_hash", "code", postgresql_using="hash"),
#     )

#     # production_orders: Mapped[list["ProductionOrder"]] = relationship(
#     #     secondary="product_order_operations",
#     #     back_populates="operations",
#     #     lazy="selectin",
#     #     passive_deletes=True,
#     # )


# class ProductionOrder(Base):
#     __tablename__ = "production_orders"

#     id: Mapped[uuid_pk]
#     detail_id: Mapped[uuid_pk] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("details.id", ondelete="SET NULL"),
#         nullable=False,
#     )
#     quantity_details: Mapped[int] = mapped_column(Integer, nullable=False)
#     quantity_operations: Mapped[int] = mapped_column(Integer, nullable=False)
#     code: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
#     name: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
#     department_id: Mapped[str | None] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("departments.id", ondelete="SET NULL"),
#         nullable=True,
#     )
#     description: Mapped[str | None] = mapped_column(String, nullable=True)
#     is_finished: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
#     is_started: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
#     finished_date: Mapped[date | None] = mapped_column(Date, nullable=True)

#     operation_ids: Mapped[list[uuid_pk]] = mapped_column(ARRAY(UUID(as_uuid=True)))

#     __table_args__ = (
#         CheckConstraint("quantity_details >= 1", name="check_quantity_details_min_1"),
#         CheckConstraint(
#             "quantity_operations >= 1", name="check_quantity_operations_min_1"
#         ),
#         Index("ix_production_orders_code_hash", "code", postgresql_using="hash"),
#         Index(
#             "ix_production_orders_dep_finished_date",
#             "department_id",
#             sqlalchemy.asc("is_finished"),
#             sqlalchemy.asc("is_started"),
#             sqlalchemy.desc("finished_date"),
#         ),
#         Index("ix_production_orders_is_finished", "is_finished"),
#         Index("ix_production_orders_is_started", "is_started"),
#     )

#     # operations: Mapped[list["Operation"]] = relationship(
#     #     secondary="product_order_operations",
#     #     back_populates="production_orders",
#     #     lazy="selectin",
#     #     passive_deletes=True,
#     #     order_by="ProductOrderOperation.order",
#     # )


# class Action(Base):
#     __tablename__ = "actions"

#     id: Mapped[uuid_pk]
#     user_id: Mapped[uuid_pk] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("users.id", ondelete="SET NULL"),
#         nullable=False,
#     )
#     production_order_id: Mapped[uuid_pk] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("production_orders.id", ondelete="SET NULL"),
#         nullable=False,
#     )
#     operation_stage_id: Mapped[uuid_pk] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("operation_stages.id", ondelete="SET NULL"),
#         nullable=False,
#     )
#     operation_id: Mapped[uuid_pk] = mapped_column(
#         UUID(as_uuid=True),
#         ForeignKey("operations.id", ondelete="SET NULL"),
#         nullable=True,
#     )

#     timestamp: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         nullable=False,
#         server_default=func.now(),
#     )


# # class ProductionOrderOperation(Base):
# #     __tablename__ = "product_order_operations"

# #     operation_id: Mapped[uuid_pk] = mapped_column(
# #         ForeignKey("operations.id", ondelete="CASCADE"), primary_key=True
# #     )

# #     production_order_id: Mapped[uuid_pk] = mapped_column(
# #         ForeignKey("production_orders.id", ondelete="CASCADE"), primary_key=True
# #     )

# #     order: Mapped[int] = mapped_column(Integer, nullable=False)
# #     __table_args__ = (
# #         CheckConstraint("order >= 1", name="check_order_min_1"),
# #         Index(
# #             "ix_product_order_operations_order_by_po", "production_order_id", "order"
# #         ),
# #     )
