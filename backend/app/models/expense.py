# app/models/expense.py
class ExpenseCategory(str, enum.Enum):
    FUEL = "fuel"
    MAINTENANCE = "maintenance"
    TOLL = "toll"
    INSURANCE = "insurance"
    OTHER = "other"

class Expense(Base, BaseModel):
    __tablename__ = "expenses"
    vehicle_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("vehicles.id", ondelete="RESTRICT"), nullable=False, index=True)
    category: Mapped[ExpenseCategory] = mapped_column(PG_ENUM(ExpenseCategory, name="expense_category_enum", create_type=False), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    liters: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)  # only for FUEL
    expense_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vehicle: Mapped["Vehicle"] = relationship()