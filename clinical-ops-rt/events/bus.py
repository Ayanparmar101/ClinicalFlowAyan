from datetime import datetime
from typing import List, Dict

class Event:
    def __init__(self, subject_id, site_id, event_type, msg):
        self.timestamp = datetime.now()
        self.subject_id = subject_id
        self.site_id = site_id
        self.event_type = event_type
        self.msg = msg

    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "subject_id": self.subject_id,
            "site_id": self.site_id,
            "event_type": self.event_type,
            "message": self.msg
        }

    @classmethod
    def from_dict(cls, data: Dict):
        """Helper to convert the dictionary-based events from metrics into proper Event objects"""
        # Map 'type' to 'event_type' and handle the message consolidation
        event_type = data.get("type", "UNKNOWN")
        subject_id = data.get("subject_id")
        site_id = data.get("site_id")
        
        # Build message from remaining keys
        msg_parts = []
        for k, v in data.items():
            if k not in ["type", "subject_id", "site_id"]:
                msg_parts.append(f"{k}: {v}")
        msg = " | ".join(msg_parts)
        
        return cls(subject_id, site_id, event_type, msg)

class EventBus:
    def __init__(self):
        self.events = []

    def emit(self, subject_id, site_id, event_type, msg):
        self.events.append(Event(subject_id, site_id, event_type, msg))

    def extend(self, events: List):
        if events:
            for e in events:
                if isinstance(e, dict):
                    self.events.append(Event.from_dict(e))
                else:
                    self.events.append(e)

    def get_events(self) -> List[Event]:
        return self.events

