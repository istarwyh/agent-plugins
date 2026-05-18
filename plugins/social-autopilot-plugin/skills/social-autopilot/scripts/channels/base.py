from dataclasses import dataclass, field


@dataclass
class ChannelResult:
    channel: str
    attempted: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    messages: list[str] = field(default_factory=list)

    def add_message(self, message: str):
        if message:
            self.messages.append(message)

    def print_summary(self):
        print(
            f"[{self.channel}] attempted={self.attempted}, "
            f"succeeded={self.succeeded}, failed={self.failed}, skipped={self.skipped}"
        )
        for message in self.messages:
            print(f"  - {message}")
