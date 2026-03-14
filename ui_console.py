from typing import List
# ----------------------------
# Console / Log (simple)
# ----------------------------
class ConsoleLog:
    def __init__(self, max_lines: int = 400):
        self.lines: List[str] = []
        self.max_lines = max_lines

    def add(self, msg: str) -> None:
        self.lines.append(msg)
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]

    def last(self, n: int) -> List[str]:
        return self.lines[-n:]