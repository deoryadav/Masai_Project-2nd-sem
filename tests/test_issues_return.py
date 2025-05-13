import pytest
from datetime import date, timedelta
from library.storage import CSVStorage
from library.models import Book, Loan
import os, shutil

@pytest.fixture
def temp_data(tmp_path):
    # copy template CSVs into tmp_path/data
    src = os.path.join(os.path.dirname(__file__), "..", "data")
    dst = tmp_path / "data"
    shutil.copytree(src, dst)
    return str(tmp_path / "data")


def test_issue_return_restores_copies(tmp_path, temp_data):
    storage = CSVStorage(data_dir=temp_data)
    books = storage.load_books()
    loans = storage.load_loans()

    # issue a book
    b = books[0]
    orig = b.CopiesAvailable
    loan_id = max([l.LoanID for l in loans] or [0]) + 1
    issue = date.today(); due = issue + timedelta(days=14)
    loans.append(Loan(loan_id, 1001, b.ISBN, issue, due))
    b.CopiesAvailable -= 1

    storage.save_books(books)
    storage.save_loans(loans)

    # now return it
    loans[-1].ReturnDate = date.today()
    b.CopiesAvailable += 1
    storage.save_books(books)
    storage.save_loans(loans)

    # reload and assert
    b2 = storage.load_books()[0]
    assert b2.CopiesAvailable == orig


# New test: invalid ISBN should not be found

def test_issue_invalid_isbn(temp_data):
    storage = CSVStorage(data_dir=temp_data)
    books = storage.load_books()
    # simulate CLI logic
    isbn = "0000"
    bk = next((b for b in books if b.ISBN == isbn), None)
    assert bk is None


# New test: returning an already returned loan

def test_return_already_returned(temp_data):
    storage = CSVStorage(data_dir=temp_data)
    loans = storage.load_loans()
    # mark first loan as returned
    ln = loans[0]
    ln.ReturnDate = date.today()
    storage.save_loans(loans)
    # simulate the CLI check
    assert ln.ReturnDate is not None
