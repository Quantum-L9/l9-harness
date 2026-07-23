from enum import StrEnum

class RunState(StrEnum):
    CREATED = 'created'
    SUBJECT_LOCKED = 'subject_locked'
    PLANNED = 'planned'
    RUNNING = 'running'
    COLLECTED = 'collected'
    EXPORTED = 'exported'
    BUNDLED = 'bundled'
    VERIFIED = 'verified'
    COMPLETED = 'completed'
    PARTIAL = 'partial'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
TERMINAL_STATES = {RunState.COMPLETED, RunState.PARTIAL, RunState.FAILED, RunState.CANCELLED}
