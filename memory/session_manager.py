import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class SessionManager:
    def __init__(self, base_dir: str = "~/.hiagent"):
        self.base_dir = Path(base_dir).expanduser()
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, session_id: str) -> str:
        if session_id is None:
            import uuid
            session_id = str(uuid.uuid4())
        session_file = self.sessions_dir / f"{session_id}.jsonl"
        session_file.touch()
        return session_id

    def get_session_file(self, session_id: str) -> Path:
        return self.sessions_dir / f"{session_id}.jsonl"

    def append_message(self, session_id: str, message: Dict):
        session_file = self.get_session_file(session_id)
        if not session_file.exists():
            self.create_session(session_id)
        message["timestamp"] = datetime.now().timestamp()
        with open(session_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(message, ensure_ascii=False) + "\n")

    def load_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        session_file = self.get_session_file(session_id)
        if not session_file.exists():
            return []
        messages = []
        with open(session_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    messages.append(json.loads(line))
        return messages[-limit:]

    def list_sessions(self) -> List[Dict]:
        sessions = []
        for file in self.sessions_dir.glob("*.jsonl"):
            session_id = file.stem
            first_message = self._read_first_message(file)
            sessions.append({
                "session_id": session_id,
                "created_at": first_message.get("timestamp") if first_message else None,
                "first_message": first_message.get("content", "")[:50] if first_message else ""
            })
        return sessions

    def _read_first_message(self, file_path: Path) -> Optional[Dict]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                first_line = f.readline()
                if first_line.strip():
                    return json.loads(first_line)
        except:
            pass
        return None