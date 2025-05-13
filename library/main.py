import argparse
from datetime import date, timedelta
from tabulate import tabulate

from library.storage import CSVStorage
from library.auth import AuthService
from library.models import Loan

# Helper functions for overdue logic and printing

def _get_overdue_loans(storage):
    loans = storage.load_loans()
    today = date.today()
    return [l for l in loans if l.IssueDate <= l.DueDate and not l.ReturnDate and l.DueDate < today]


def _print_overdue(overdue, storage):
    if overdue:
        rows = []
        members = {m.MemberID: m for m in storage.load_members()}
        for l in overdue:
            rows.append([l.LoanID, l.MemberID, l.ISBN, l.DueDate, members[l.MemberID].Email])
        print(tabulate(rows,
                       headers=["LoanID", "MemberID", "ISBN", "Due", "Email"],
                       tablefmt="grid"))
    else:
        print("No overdue loans.")

MENU_LIB = """
=== Librarian Dashboard ===
1. Add Book
2. Register Member
3. Issue Book
4. Return Book
5. Overdue List
6. Remove Book
7. Logout
> """

MENU_MEMBER = """
=== Member Dashboard ===
1. Search Catalogue
2. Borrow Book
3. My Loans
4. Logout
> """


def run():
    # CLI argument for data directory
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=None, help="path to CSV data folder")
    args = parser.parse_args()

    storage = CSVStorage(data_dir=args.data_dir)
    books = storage.load_books()
    loans = storage.load_loans()
    auth = AuthService(storage)

    role = input("Login as (librarian/member): ").strip().lower()
    if role == "librarian":
        password = input("Enter librarian password: ")
        if password != "libpass":
            print("❌ Invalid password.")
            return
        while True:
            choice = input(MENU_LIB).strip()
            if choice == "1":  # Add Book
                isbn = input("ISBN: ").strip()
                title = input("Title: ").strip()
                author = input("Author: ").strip()
                try:
                    total = int(input("Total copies: ").strip())
                except ValueError:
                    print("❌ Total copies must be a number.")
                    continue
                if total < 0:
                    print("❌ Total copies cannot be negative.")
                    continue
                new_book = type(books[0])(
                    ISBN=isbn, Title=title, Author=author,
                    CopiesTotal=total, CopiesAvailable=total
                )
                books.append(new_book)
                storage.save_books(books)
                print("✓ Book added.")

            elif choice == "2":  # Register Member
                name = input("Name: ").strip()
                email = input("Email: ").strip()
                pwd = input("Password: ")
                if any(m.Email.lower() == email.lower() for m in storage.load_members()):
                    print(f"❌ Email {email} is already registered.")
                    continue
                mem = auth.register_member(name, pwd, email)
                print(f"✓ Member {mem.MemberID} registered.")

            elif choice == "3":  # Issue Book
                isbn = input("ISBN to issue: ").strip()
                try:
                    mid = int(input("Member ID: ").strip())
                except ValueError:
                    print("❌ Invalid Member ID format.")
                    continue
                bk = next((b for b in books if b.ISBN == isbn), None)
                if not bk:
                    print(f"❌ ISBN {isbn} not found.")
                    continue
                if bk.CopiesAvailable <= 0:
                    print(f"❌ Book {isbn} has no available copies.")
                    continue
                loan_id = max((l.LoanID for l in loans), default=0) + 1
                issue_date = date.today()
                due_date = issue_date + timedelta(days=14)
                loans.append(Loan(loan_id, mid, isbn, issue_date, due_date))
                bk.CopiesAvailable -= 1
                storage.save_books(books)
                storage.save_loans(loans)
                print(f"✓ Book issued. Due on {due_date}.")

            elif choice == "4":  # Return Book
                try:
                    lid = int(input("Loan ID to return: ").strip())
                except ValueError:
                    print("❌ Invalid Loan ID format.")
                    continue
                ln = next((l for l in loans if l.LoanID == lid), None)
                if not ln:
                    print(f"❌ No loan found with ID {lid}.")
                    continue
                if ln.ReturnDate:
                    print(f"❌ Loan {lid} has already been returned on {ln.ReturnDate}.")
                    continue
                ln.ReturnDate = date.today()
                bk = next(b for b in books if b.ISBN == ln.ISBN)
                bk.CopiesAvailable += 1
                storage.save_books(books)
                storage.save_loans(loans)
                print("✓ Returned.")

            elif choice == "5":  # Overdue List
                # Spot corrupted records
                loans = storage.load_loans()
                bad = [l for l in loans if l.IssueDate > l.DueDate]
                if bad:
                    print("⚠️ Found loans with invalid dates:")
                    for l in bad:
                        print(f"  Loan {l.LoanID}: Issue {l.IssueDate}, Due {l.DueDate}")
                # Get overdue and print
                overdue = _get_overdue_loans(storage)
                _print_overdue(overdue, storage)

            elif choice == "6":  # Remove Book
                isbn = input("ISBN to remove: ").strip()
                books = storage.load_books()
                before = len(books)
                new_books = [b for b in books if b.ISBN != isbn]
                if len(new_books) < before:
                    storage.save_books(new_books)
                    books = new_books
                    print(f"✓ Book {isbn} removed.")
                else:
                    print(f"❌ No book found with ISBN {isbn}.")

            elif choice == "7":  # Logout
                break
            else:
                print("❌ Invalid choice.")

    elif role == "member":
        try:
            mid = int(input("Member ID: ").strip())
        except ValueError:
            print("❌ Invalid Member ID format.")
            return
        pwd = input("Password: ")
        if not auth.login(mid, pwd):
            print("❌ Member ID or password incorrect.")
            return
        while True:
            choice = input(MENU_MEMBER).strip()
            if choice == "1":  # Search Catalogue
                term = input("Search keyword: ").lower()
                for b in books:
                    if term in b.Title.lower() or term in b.Author.lower():
                        print(f"{b.ISBN}: {b.Title} ({b.CopiesAvailable} available)")

            elif choice == "2":  # Borrow Book
                isbn = input("ISBN to borrow: ").strip()
                b = next((x for x in books if x.ISBN == isbn), None)
                if not b:
                    print(f"❌ ISBN {isbn} not found.")
                    continue
                if b.CopiesAvailable <= 0:
                    print(f"❌ Book {isbn} has no available copies.")
                    continue
                lid = max((l.LoanID for l in loans), default=0) + 1
                issue_date = date.today()
                due_date = issue_date + timedelta(days=14)
                loans.append(Loan(lid, auth.logged_in.MemberID, isbn, issue_date, due_date))
                b.CopiesAvailable -= 1
                storage.save_books(books)
                storage.save_loans(loans)
                print(f"✓ Borrowed. Due {due_date}.")

            elif choice == "3":  # My Loans
                for l in loans:
                    if l.MemberID == auth.logged_in.MemberID:
                        status = "Returned" if l.ReturnDate else f"Due {l.DueDate}"
                        print(f"Loan {l.LoanID}: {l.ISBN} → {status}")

            elif choice == "4":  # Logout
                break
            else:
                print("❌ Invalid choice.")

    else:
        print("❌ Invalid role.")


if __name__ == "__main__":
    run()
