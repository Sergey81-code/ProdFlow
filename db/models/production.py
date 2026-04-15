from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    String,
    Time,
    UniqueConstraint,
    and_,
    func,
)
from sqlalchemy.orm import relationship, foreign

from .core import Base


class ProdOrder(Base):
    __tablename__ = "ProdOrder"

    id = Column("RecId", BigInteger, primary_key=True)

    prod_id = Column("ProdId", String(60), index=True, nullable=False)
    item_id = Column("ItemId", String(60), index=True, nullable=True)
    name = Column("Name", String(250), nullable=True)
    prod_group_id = Column("ProdGroupId", String(60), nullable=True)
    prod_status = Column("ProdStatus", Integer, nullable=True)
    prod_prio = Column("ProdPrio", Integer, nullable=True)
    prod_locked = Column("ProdLocked", Boolean, nullable=True)
    prod_type = Column("ProdType", String(50), nullable=True)
    sched_status = Column("SchedStatus", String(50), nullable=True)
    sched_date = Column("SchedDate", Date, nullable=True)
    sched_start = Column("SchedStart", DateTime, nullable=True)
    sched_end = Column("SchedEnd", DateTime, nullable=True)
    sched_from_time = Column("SchedFromTime", Time, nullable=True)
    sched_to_time = Column("SchedToTime", Time, nullable=True)
    qty_sched = Column("QtySched", Numeric(18, 6), nullable=True)
    qty_st_up = Column("QtyStUp", Numeric(18, 6), nullable=True)
    finished_date = Column("FinishedDate", Date, nullable=True)
    st_up_date = Column("StUpDate", Date, nullable=True)
    dlv_date = Column("DlvDate", Date, nullable=True)
    prod_pool_id = Column("ProdPoolId", String(60), nullable=True)
    bom_id = Column("BOMId", String(100), nullable=True)
    route_id = Column("RouteId", String(100), nullable=True)
    invent_location_id = Column("InventLocationId", String(60), nullable=True)
    invent_batch_id = Column("InventBatchId", String(60), nullable=True)
    invent_serial_id = Column("InventSerialId", String(60), nullable=True)
    remark = Column("Remark", String(250), nullable=True)

    created_date_time = Column("createdDateTime", DateTime, nullable=True)
    modified_date_time = Column("modifiedDateTime", DateTime, nullable=True)

    routes = relationship(
        "ProdRoute",
        back_populates="prod_table",
        cascade="save-update, merge",
        lazy="selectin",
    )

    journals = relationship(
        "ProdJournal",
        back_populates="prod_table",
        cascade="save-update, merge",
        lazy="selectin",
    )

    journal_entries = relationship(
        "ProdJournalRoute",
        back_populates="prod_table",
        cascade="save-update, merge",
        lazy="selectin",
    )

    journal_tables = relationship(
        "ProdJournal",
        back_populates="prod_table",
        primaryjoin="ProdOrder.prod_id==ProdJournal.prod_id",
        viewonly=True,
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint("ProdId", name="uq_prodorder_prodid"),)


class ProdJournal(Base):
    __tablename__ = "ProdJournal"

    rec_id = Column("RecId", BigInteger, primary_key=True)
    journal_id = Column("JournalId", String(80), nullable=False, index=True)
    description = Column("Description", String(250), nullable=True)
    prod_id = Column(
        "ProdId", String(60), ForeignKey("ProdOrder.ProdId"), index=True, nullable=True
    )
    opr_num = Column("OprNum", Integer, nullable=True)
    journal_type = Column("JournalType", String(50), nullable=True)
    posted = Column("Posted", Boolean, nullable=True)
    qty_good = Column("qtyGood", Numeric(18, 6), nullable=True)
    qty_error = Column("qtyError", Numeric(18, 6), nullable=True)
    end_job = Column("EndJob", Boolean, nullable=True)
    auto_report_finished = Column("AutoReportFinished", Boolean, nullable=True)
    route_auto_pick_list = Column("RouteAutoPickList", Boolean, nullable=True)
    prod_auto_pick_list = Column("ProdAutoPickList", Boolean, nullable=True)

    created_date_time = Column("createdDateTime", DateTime, nullable=True)
    modified_date_time = Column("modifiedDateTime", DateTime, nullable=True)

    prod_table = relationship(
        "ProdOrder",
        back_populates="journals",
        primaryjoin="ProdJournal.prod_id==ProdOrder.prod_id",
        viewonly=True,
    )

    journal_routes = relationship(
        "ProdJournalRoute",
        back_populates="journal_table",
        primaryjoin="ProdJournal.journal_id==ProdJournalRoute.journal_id",
        viewonly=True,
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint("JournalId", name="uq_prodjournal_journalid"),)


class ProdRoute(Base):
    __tablename__ = "ProdRoute"

    id = Column("RecId", BigInteger, primary_key=True)

    prod_id = Column(
        "ProdId", String(60), ForeignKey("ProdOrder.ProdId"), index=True, nullable=False
    )
    opr_num = Column("OprNum", Integer, nullable=False)
    level = Column("Level", Integer, nullable=True)
    opr_id = Column("OprId", String(100), nullable=True)
    wrkctr_id = Column("WrkCtrId", String(80), nullable=True)
    setup_time = Column("SetupTime", Numeric(12, 3), nullable=True)
    process_time = Column("ProcessTime", Numeric(12, 3), nullable=True)
    process_per_qty = Column("ProcessPerQty", Numeric(18, 6), nullable=True)
    transp_time = Column("TranspTime", Numeric(12, 3), nullable=True)
    queue_time_before = Column("QueueTimeBefore", Numeric(12, 3), nullable=True)
    queue_time_after = Column("QueueTimeAfter", Numeric(12, 3), nullable=True)
    calc_qty = Column("CalcQty", Numeric(18, 6), nullable=True)
    opr_finished = Column("OprFinished", Boolean, nullable=True)
    from_date = Column("FromDate", Date, nullable=True)
    to_date = Column("ToDate", Date, nullable=True)
    from_time = Column("FromTime", Time, nullable=True)
    to_time = Column("ToTime", Time, nullable=True)
    opr_priority = Column("OprPriority", Integer, nullable=True)
    job_id_process = Column("JobIdProcess", String(100), nullable=True)

    created_date_time = Column("createdDateTime", DateTime, nullable=True)
    modified_date_time = Column("modifiedDateTime", DateTime, nullable=True)

    prod_table = relationship(
        "ProdOrder",
        back_populates="routes",
        primaryjoin="ProdRoute.prod_id==ProdOrder.prod_id",
        viewonly=False,
    )
    journal_entries = relationship(
        "ProdJournalRoute",
        primaryjoin=lambda: ProdRoute.prod_id == foreign(ProdJournalRoute.prod_id),
        viewonly=True,
        lazy="joined",
    )

    __table_args__ = (
        UniqueConstraint("ProdId", "OprNum", name="uq_prodrt_prodid_oprnum"),
    )


class ProdJournalRoute(Base):
    __tablename__ = "ProdJournalRoute"

    rec_id = Column(
        "RecId",
        BigInteger,
        Identity(always=False),
        primary_key=True,
    )

    journal_id = Column(
        "JournalId",
        String(80),
        ForeignKey("ProdJournal.JournalId"),
        nullable=True,
        index=True,
    )
    voucher = Column("Voucher", String(80), nullable=True)
    line_num = Column("LineNum", Integer, nullable=False, default=1)
    trans_date = Column("TransDate", Date, nullable=True)

    prod_id = Column(
        "ProdId", String(60), ForeignKey("ProdOrder.ProdId"), index=True, nullable=False
    )
    opr_num = Column("OprNum", Integer, nullable=True)
    job_type = Column("JobType", String(60), nullable=True)
    wrkctr_id = Column("WrkCtrId", String(80), nullable=True)
    hours = Column("Hours", Numeric(12, 3), nullable=True)
    hour_price = Column("HourPrice", Numeric(18, 6), nullable=True)
    qty_good = Column("QtyGood", Numeric(18, 6), nullable=True)
    qty_error = Column("QtyError", Numeric(18, 6), nullable=True)
    empl_id = Column("EmplId", String(80), nullable=True)
    opr_finished = Column("OprFinished", Boolean, nullable=True)
    job_finished = Column("JobFinished", Boolean, nullable=True)
    executed_pct = Column("ExecutedPct", Numeric(5, 2), nullable=True)
    from_time = Column("FromTime", Time, nullable=True)
    to_time = Column("ToTime", Time, nullable=True)
    opr_id = Column("OprId", String(100), nullable=True)
    cancelled = Column("Cancelled", Boolean, nullable=True)
    error_cause = Column("ErrorCause", String(250), nullable=True)
    created_date_time = Column("createdDateTime", DateTime, nullable=True)
    modified_date_time = Column("modifiedDateTime", DateTime, nullable=True)

    user_id = Column(
        ForeignKey("users.id", ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )

    prod_table = relationship(
        "ProdOrder",
        back_populates="journal_entries",
        primaryjoin="ProdJournalRoute.prod_id==ProdOrder.prod_id",
        viewonly=False,
    )
    prod_routes = relationship(
        "ProdRoute",
        primaryjoin=lambda: and_(
            foreign(ProdJournalRoute.prod_id) == ProdRoute.prod_id,
            foreign(ProdJournalRoute.opr_num) == ProdRoute.opr_num,
        ),
        viewonly=True,
        lazy="selectin",
    )

    journal_table = relationship(
        "ProdJournal",
        back_populates="journal_routes",
        primaryjoin="ProdJournalRoute.journal_id==ProdJournal.journal_id",
        viewonly=True,
    )

    user = relationship("User", lazy="joined")

    __table_args__ = (
        UniqueConstraint(
            "ProdId",
            "JournalId",
            "OprNum",
            "LineNum",
            name="uq_prodjournalroute_business",
        ),
    )


class ProdJournalRouteRecords(Base):
    __tablename__ = "ProdJournalRouteRecords"

    id = Column(
        "Id",
        BigInteger,
        Identity(always=False),
        primary_key=True,
    )
    action = Column("Action", String(30), nullable=False)

    user_id = Column(
        ForeignKey("users.id", ondelete="NO ACTION"),
        nullable=False,
        index=True,
    )
    journal_id = Column(
        "JournalId",
        String(80),
        ForeignKey("ProdJournal.JournalId", ondelete="NO ACTION"),
        nullable=True,
        index=True,
    )
    line_num = Column("LineNum", Integer, nullable=False, default=1)

    prod_id = Column(
        "ProdId",
        String(60),
        ForeignKey("ProdOrder.ProdId", ondelete="NO ACTION"),
        index=True,
        nullable=False,
    )
    opr_num = Column("OprNum", Integer, nullable=True)
    record_date = Column(
        "RecordDate",
        Date,
        nullable=False,
        server_default=func.current_date(),
    )

    record_time = Column(
        "RecordTime",
        Time,
        nullable=False,
        server_default=func.current_time(),
    )

    created_date_time = Column(
        "createdDateTime",
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        UniqueConstraint(
            "ProdId",
            "JournalId",
            "OprNum",
            "LineNum",
            "Action",
            "user_id",
            "createdDateTime",
            name="uq_prodjournalrouterecord_business",
        ),
    )


class ProdBOM(Base):
    __tablename__ = "ProdBOM"

    rec_id = Column("RecId", BigInteger, primary_key=True)

    prod_id = Column(
        "ProdId", String(60), ForeignKey("ProdOrder.ProdId"), index=True, nullable=False
    )
    line_num = Column("LineNum", Integer, nullable=False)
    item_id = Column("ItemId", String(60), nullable=True)
    bom_qty = Column("BOMQty", Numeric(18, 6), nullable=True)
    opr_num = Column("OprNum", Integer, nullable=True)
    unit_id = Column("UnitId", String(60), nullable=True)
    invent_trans_id = Column("InventTransId", String(80), nullable=True)
    raw_material_date = Column("RawMaterialDate", Date, nullable=True)

    created_date_time = Column("createdDateTime", DateTime, nullable=True)
    modified_date_time = Column("modifiedDateTime", DateTime, nullable=True)

    prod_table = relationship("ProdOrder", viewonly=True)


class Invent(Base):
    __tablename__ = "InventTable"

    rec_id = Column("RecId", BigInteger, primary_key=True)
    item_id = Column("ItemId", String(60), unique=True, index=True, nullable=False)
    item_name = Column("ItemName", String(250), nullable=True)
    item_group_id = Column("ItemGroupId", String(60), nullable=True)
    item_type = Column("ItemType", String(80), nullable=True)
    primary_vendor_id = Column("PrimaryVendorId", String(80), nullable=True)
    net_weight = Column("NetWeight", Numeric(18, 6), nullable=True)
    unit_volume = Column("UnitVolume", Numeric(18, 6), nullable=True)
    bom_unit_id = Column("BOMUnitId", String(60), nullable=True)
    minimum_pallet_quantity = Column("MinimumPalletQuantity", Integer, nullable=True)

    created_date_time = Column("createdDateTime", DateTime, nullable=True)
    modified_date_time = Column("modifiedDateTime", DateTime, nullable=True)

    prod_tables = relationship(
        "ProdOrder",
        primaryjoin=lambda: Invent.item_id == foreign(ProdOrder.item_id),
        viewonly=True,
    )
