"""
Utility functions for the SabiTax application.
Nigerian tax calculations, formatting, and helpers.
"""
import random
import string
from datetime import date
from decimal import Decimal
from typing import TypeVar

T = TypeVar("T")


def format_naira(amount: Decimal | float | int, show_sign: bool = False) -> str:
    """
    Format an amount as Nigerian Naira.

    Args:
        amount: Amount to format
        show_sign: Whether to show + for positive amounts

    Returns:
        Formatted string like "₦1,234,567" or "+₦1,234,567"
    """
    amount_decimal = Decimal(str(amount))
    sign = ""

    if show_sign and amount_decimal > 0:
        sign = "+"
    elif amount_decimal < 0:
        sign = "-"
        amount_decimal = abs(amount_decimal)

    formatted = f"{amount_decimal:,.0f}"
    return f"{sign}₦{formatted}"


def generate_referral_code(name: str) -> str:
    """
    Generate a unique referral code based on user's name.

    Args:
        name: User's name

    Returns:
        Referral code like "SABI-JOE123"
    """
    # Take first 3 chars of name (uppercase)
    name_part = "".join(c for c in name.upper() if c.isalpha())[:3]
    if len(name_part) < 3:
        name_part = name_part.ljust(3, "X")

    # Random alphanumeric suffix
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))

    return f"SABI-{name_part}{suffix}"


def generate_tin_reference() -> str:
    """
    Generate a TIN application reference number.

    Returns:
        Reference like "TIN-2025-ABC12345"
    """
    year = date.today().year
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"TIN-{year}-{suffix}"


def generate_filing_reference() -> str:
    """
    Generate a tax filing reference number.

    Returns:
        Reference like "FIRS-2025-XXXXXX"
    """
    year = date.today().year
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"FIRS-{year}-{suffix}"


def mask_tin(tin: str) -> str:
    """
    Mask a TIN for display, showing only first 3 and last 2 digits.

    Args:
        tin: Full TIN number

    Returns:
        Masked TIN like "221***90"
    """
    if not tin or len(tin) < 6:
        return tin
    return f"{tin[:3]}***{tin[-2:]}"


def mask_account_number(account_number: str) -> str:
    """
    Mask a bank account number for display.

    Args:
        account_number: Full account number

    Returns:
        Masked account like "***4567"
    """
    if not account_number or len(account_number) < 4:
        return account_number
    return f"***{account_number[-4:]}"


# Nigerian Personal Income Tax (PIT) Brackets
# Based on FIRS guidelines
NIGERIAN_TAX_BRACKETS: list[tuple[Decimal, Decimal, Decimal]] = [
    # (Upper Limit, Rate, Previous Bracket Tax)
    (Decimal("300000"), Decimal("0.07"), Decimal("0")),
    (Decimal("600000"), Decimal("0.11"), Decimal("21000")),
    (Decimal("1100000"), Decimal("0.15"), Decimal("54000")),
    (Decimal("1600000"), Decimal("0.19"), Decimal("129000")),
    (Decimal("3200000"), Decimal("0.21"), Decimal("224000")),
    (Decimal("999999999999"), Decimal("0.24"), Decimal("560000")),
]

# Consolidated Relief Allowance (CRA)
CRA_FIXED_AMOUNT = Decimal("200000")
CRA_PERCENTAGE = Decimal("0.20")  # 20% of gross income


def calculate_cra(gross_income: Decimal | float | int) -> Decimal:
    """
    Calculate Consolidated Relief Allowance (CRA).
    
    Args:
        gross_income: Annual gross income
        
    Returns:
        CRA amount
    """
    gross = Decimal(str(gross_income))
    cra_minimum = max(CRA_FIXED_AMOUNT, gross * Decimal("0.01"))
    cra = cra_minimum + (gross * CRA_PERCENTAGE)
    return cra.quantize(Decimal("0.01"))


def calculate_nigerian_pit(annual_income: Decimal | float | int) -> dict:
    """
    Calculate Nigerian Personal Income Tax based on FIRS guidelines.

    Args:
        annual_income: Annual gross income in Naira

    Returns:
        Dict with tax calculation details
    """
    gross = Decimal(str(annual_income))

    if gross <= 0:
        return {
            "gross_income": gross,
            "cra": Decimal("0"),
            "taxable_income": Decimal("0"),
            "tax_amount": Decimal("0"),
            "effective_rate": Decimal("0"),
        }

    # Calculate Consolidated Relief Allowance (CRA)
    # Higher of ₦200,000 or 1% of gross, PLUS 20% of gross
    cra_minimum = max(CRA_FIXED_AMOUNT, gross * Decimal("0.01"))
    cra = cra_minimum + (gross * CRA_PERCENTAGE)

    # Taxable income
    taxable = max(gross - cra, Decimal("0"))

    # Calculate tax using progressive brackets
    tax = Decimal("0")
    remaining = taxable
    previous_limit = Decimal("0")

    for upper_limit, rate, _ in NIGERIAN_TAX_BRACKETS:
        if remaining <= 0:
            break

        bracket_size = upper_limit - previous_limit
        taxable_in_bracket = min(remaining, bracket_size)
        tax += taxable_in_bracket * rate

        remaining -= taxable_in_bracket
        previous_limit = upper_limit

    # Effective tax rate
    effective_rate = (tax / gross * 100) if gross > 0 else Decimal("0")

    return {
        "gross_income": gross,
        "cra": cra,
        "taxable_income": taxable,
        "tax_amount": tax.quantize(Decimal("0.01")),
        "effective_rate": effective_rate.quantize(Decimal("0.01")),
    }


def calculate_monthly_paye(monthly_salary: Decimal | float | int) -> Decimal:
    """
    Calculate monthly PAYE (Pay As You Earn) tax.

    Args:
        monthly_salary: Monthly gross salary in Naira

    Returns:
        Monthly PAYE amount
    """
    annual = Decimal(str(monthly_salary)) * 12
    result = calculate_nigerian_pit(annual)
    monthly_tax = result["tax_amount"] / 12
    return monthly_tax.quantize(Decimal("0.01"))


# VAT Rate (Nigeria)
VAT_RATE = Decimal("0.075")  # 7.5%


def calculate_vat(amount: Decimal | float | int) -> Decimal:
    """
    Calculate Nigerian VAT (7.5%).

    Args:
        amount: Base amount

    Returns:
        VAT amount
    """
    return (Decimal(str(amount)) * VAT_RATE).quantize(Decimal("0.01"))


def get_next_tax_due_date() -> date:
    """
    Get the next tax filing due date.

    Returns:
        Next January 31st (annual PIT deadline)
    """
    today = date.today()
    current_year_deadline = date(today.year, 1, 31)

    if today <= current_year_deadline:
        return current_year_deadline
    return date(today.year + 1, 1, 31)


def get_tax_year() -> int:
    """
    Get the current tax year.

    Returns:
        Tax year (previous calendar year if before deadline)
    """
    today = date.today()
    deadline = date(today.year, 1, 31)

    if today <= deadline:
        return today.year - 1
    return today.year


def calculate_compliance_score(
    documented_income: Decimal | float,
    estimated_income: Decimal | float,
    has_tin: bool = False,
    filings_on_time: int = 0,
    total_filings: int = 0,
) -> int:
    """
    Calculate a user's tax compliance score (0-100).

    Args:
        documented_income: Income with receipts/records
        estimated_income: Estimated total income
        has_tin: Whether user has a TIN
        filings_on_time: Number of on-time filings
        total_filings: Total filings made

    Returns:
        Compliance score percentage
    """
    score = 0

    # Income documentation weight: 50%
    if estimated_income > 0:
        doc_ratio = min(float(documented_income) / float(estimated_income), 1.0)
        score += int(doc_ratio * 50)

    # TIN registration weight: 20%
    if has_tin:
        score += 20

    # Filing history weight: 30%
    if total_filings > 0:
        filing_ratio = filings_on_time / total_filings
        score += int(filing_ratio * 30)
    elif has_tin:
        # Neutral if no filings yet but has TIN
        score += 15

    return min(score, 100)
