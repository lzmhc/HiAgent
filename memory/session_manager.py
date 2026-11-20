import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from memory.message import JsonlMessage, Message


class SessionManager:
    def __init__(self, base_dir: str = "~/.agents"):
        self.base_dir = Path(base_dir).expanduser()
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, session_id: str) -> str:
        if session_id is None:
            from datetime import datetime
            now = datetime.now()
            session_id = now.strftime("%Y%m%d%H%M%S")
        print(self.sessions_dir)
        session_file = self.sessions_dir / f"{session_id}.jsonl"
        session_file.touch()
        return session_id

    def get_session_file(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.jsonl"

    def append_jsonl_message(self, session_id: str, id: str, type: str, parentId: str, message: Dict):
        session_file = self.get_session_file(session_id)
        if not session_file.exists():
            self.create_session(session_id)
        jsonl_message = JsonlMessage(id, type, parentId, message)
        with open(session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(jsonl_message.to_dict(), ensure_ascii=False) + "\n")

    def load_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        session_file = self.get_session_file(session_id)
        if not session_file.exists():
            return []
        messages = []
        with open(session_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    messages.append(record)
        return messages[-limit:]

    def list_sessions(self) -> List[Dict]:
        files = self.sessions_dir.glob("*.jsonl")
        sorted_files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
        sessions = [{"session_id": f.stem} for f in sorted_files]
        return sessions
