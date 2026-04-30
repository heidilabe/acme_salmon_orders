import time
from dataclasses import dataclass,field
from typing import Dict, Optional
from datetime import datetime, timedelta

@dataclass
class Session:
    username:str
    role: str
    login_time: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    def update_activity(self) ->None:
        self.last_activity = datetime.now()
    def is_expired(self,timeout_minutes: int = 30) -> bool:
        expiration = self.last_activity + timedelta(minutes=timeout_minutes)
        return datetime.now() > expiration
class LoginAttemptTracker:
    _attempts: Dict[str,list] = {}
    MAX_ATTEMPTS = 3
    WINDOW_SECONDS = 300
    @classmethod
    def record_attempt(cls, username: str)-> bool:
        now = time.time()
        if username not in cls._attempts:
            cls._attempts[username] = []
        cls._attempts[username] = [
            ts for ts in cls._attempts[username]
                if now - ts < cls.WINDOW_SECONDS
            ]
        cls._attempts[username].append(now)
        return len(cls._attempts[username]) >= cls.MAX_ATTEMPTS
    @classmethod
    def is_blocked(cls,username: str) -> bool:
        if username not in cls._attempts:
            return False
        
        now = time.time()
        recent = [ts for ts in cls._attempts[username] if now - ts <
    cls.WINDOW_SECONDS]
        return len(recent) >= cls.MAX_ATTEMPTS
    @classmethod
    def reset(cls, username: str)-> None:
        cls._attempts.pop(username, None)
class AuditLogger:
    @staticmethod
    def log_action(username: str,action: str, details:str = "")-> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[AUDIT] {timestamp} | User: {username} |Action:{action} |{details}")




            

                

    


            

