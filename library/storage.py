import csv, os
from datetime import datetime
from typing import List
from library.models import Book, Member, Loan

DATE_FMT = "%Y-%m-%d"

class CSVStorage:
    def __init__(self, data_dir: str = None):
        # Determine effective data directory
        if data_dir and str(data_dir).strip().lower() != "none":
            # Use provided non-empty path
            self.data_dir = os.path.abspath(data_dir)
        else:
            # Default to the data/ folder at the project root
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            self.data_dir = os.path.join(project_root, "data")

        # DEBUG: show configured data directory
        # print(f"[DEBUG] CSVStorage using data_dir = {self.data_dir}")

    def _load(self, fname: str) -> List[dict]:
        path = os.path.join(self.data_dir, fname)
        with open(path, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def _save(self, fname: str, rows: List[dict], fieldnames: List[str]):
        path = os.path.join(self.data_dir, fname)
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    # --- Books ---
    def load_books(self) -> List[Book]:
        rows = self._load("books.csv")
        return [
            Book(
                ISBN=r["ISBN"],
                Title=r["Title"],
                Author=r["Author"],
                CopiesTotal=int(r["CopiesTotal"]),
                CopiesAvailable=int(r["CopiesAvailable"])
            ) for r in rows
        ]

    def save_books(self, books: List[Book]):
        rows = [b.__dict__ for b in books]
        fieldnames = ["ISBN", "Title", "Author", "CopiesTotal", "CopiesAvailable"]
        self._save("books.csv", rows, fieldnames)

    # --- Members ---
    def load_members(self) -> List[Member]:
        rows = self._load("members.csv")
        members = []
        for r in rows:
            members.append(Member(
                MemberID=int(r["MemberID"]),
                Name=r["Name"],
                PasswordHash=r["PasswordHash"],
                Email=r["Email"],
                JoinDate=datetime.strptime(r["JoinDate"], DATE_FMT).date()
            ))
        return members

    def save_members(self, members: List[Member]):
        rows = []
        for m in members:
            row = m.__dict__.copy()
            row["JoinDate"] = m.JoinDate.strftime(DATE_FMT)
            rows.append(row)
        self._save("members.csv", rows, ["MemberID","Name","PasswordHash","Email","JoinDate"])

    # --- Loans ---
    def load_loans(self) -> List[Loan]:
        rows = self._load("loans.csv")
        loans = []
        for r in rows:
            loans.append(
                Loan(
                    LoanID=int(r["LoanID"]),
                    MemberID=int(r["MemberID"]),
                    ISBN=r["ISBN"],
                    IssueDate=datetime.strptime(r["IssueDate"], DATE_FMT).date(),
                    DueDate=datetime.strptime(r["DueDate"], DATE_FMT).date(),
                    ReturnDate=(datetime.strptime(r["ReturnDate"], DATE_FMT).date()
                                if r.get("ReturnDate") else None)
                )
            )
        return loans

    def save_loans(self, loans: List[Loan]):
        rows = []
        for ln in loans:
            row = {
                "LoanID": ln.LoanID,
                "MemberID": ln.MemberID,
                "ISBN": ln.ISBN,
                "IssueDate": ln.IssueDate.strftime(DATE_FMT),
                "DueDate": ln.DueDate.strftime(DATE_FMT),
                "ReturnDate": ln.ReturnDate.strftime(DATE_FMT) if ln.ReturnDate else ""
            }
            rows.append(row)
        self._save("loans.csv", rows, ["LoanID","MemberID","ISBN","IssueDate","DueDate","ReturnDate"])
