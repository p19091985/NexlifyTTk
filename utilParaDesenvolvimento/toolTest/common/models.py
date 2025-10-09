# common/models.py
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Dict, Any

class TestStatus(Enum):
    SUCCESS = "✅ SUCCESS"
    FAIL = "❌ FAIL"
    ERROR = "💥 ERROR"
    SKIPPED = "⏭️ SKIPPED"
    TIMEOUT = "⏰ TIMEOUT"
    DIVINE_PASS = "✨ DIVINE"
    GODLIKE = "⚡ GODLIKE"

class TestSeverity(Enum):
    CRITICAL = "🔥 CRITICAL"
    HIGH = "🔴 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"

@dataclass
class TestResult:
    suite_name: str
    class_name: str
    method_name: str
    status: TestStatus
    duration: float
    details: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    severity: TestSeverity = TestSeverity.MEDIUM
    retry_count: int = 0
    performance_score: float = 0.0

    def __post_init__(self):
        if self.duration > 0:
            base_score = 100
            if self.duration > 1.0: base_score = 60
            elif self.duration > 0.1: base_score = 80
            elif self.duration > 0.01: base_score = 95
            self.performance_score = base_score