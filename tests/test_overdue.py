import pytest
from datetime import date, timedelta
from library.storage import CSVStorage
from library.models import Loan, Book
import os, shutil

@pytest.fixture
def temp_env(tmp_path):
    # copy data folder
    src = os.path.join(os.path.dirname(__file__), "..", "data")
    dst = tmp_path / "data"
    shutil.copytree(src, dst)
    return str(dst)

def test_overdue_detection(tmp_path, temp_env, capsys):
    storage = CSVStorage(data_dir=temp_env)
    # create one overdue loan
    loans = storage.load_loans()
    loans.append(Loan(
        LoanID=999,
        MemberID=1001,
        ISBN=storage.load_books()[0].ISBN,
        IssueDate=date.today() - timedelta(days=30),
        DueDate=date.today() - timedelta(days=16),
        ReturnDate=None
    ))
    storage.save_loans(loans)

    # run the overdue block
    from library.main import _get_overdue_loans, _print_overdue  # you’d factor these out
    overdue = _get_overdue_loans(storage)
    assert any(l.LoanID == 999 for l in overdue)

    _print_overdue(overdue, storage)  # prints the table
    captured = capsys.readouterr()
    assert "LoanID" in captured.out
    assert "999" in captured.out
