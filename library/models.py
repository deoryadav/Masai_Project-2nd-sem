from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class Book:
    ISBN: str
    Title: str
    Author: str
    CopiesTotal: int
    CopiesAvailable: int

@dataclass
class Member:
    MemberID: int
    Name: str
    PasswordHash: str
    Email: str
    JoinDate: date

@dataclass
class Loan:
    LoanID: int
    MemberID: int
    ISBN: str
    IssueDate: date
    DueDate: date
    ReturnDate: Optional[date] = field(default=None)
