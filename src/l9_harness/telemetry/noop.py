class NoopTelemetry:
    def increment(self, name: str, value: int = 1, **labels: str) -> None:
        return None

    def timing(self, name: str, seconds: float, **labels: str) -> None:
        return None
