import bcrypt
from typing import Optional
from library.models import Member
from library.storage import CSVStorage

class AuthService:
    def __init__(self, storage: CSVStorage):
        self.storage = storage
        self._members = self.storage.load_members()
        self.logged_in: Optional[Member] = None

    def register_member(self, name: str, password: str, email: str):
        pwd_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        new_id = max((m.MemberID for m in self._members), default=1000) + 1
        from datetime import date
        member = Member(new_id, name, pwd_hash, email, date.today())
        self._members.append(member)
        self.storage.save_members(self._members)
        return member

    def login(self, member_id: int, password: str) -> bool:
        found = next((m for m in self._members if m.MemberID==member_id), None)
        if found and bcrypt.checkpw(password.encode(), found.PasswordHash.encode()):
            self.logged_in = found
            return True
        return False
