from collections.abc import Mapping, Set
from enum import StrEnum


class DocumentStatus(StrEnum):
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    DELETING = "DELETING"


DOCUMENT_STATUS_TRANSITIONS: Mapping[DocumentStatus, Set[DocumentStatus]] = {
    DocumentStatus.PROCESSING: {
        DocumentStatus.READY,
        DocumentStatus.FAILED,
        DocumentStatus.DELETING,
    },
    DocumentStatus.READY: {
        DocumentStatus.PROCESSING,
        DocumentStatus.DELETING,
    },
    DocumentStatus.FAILED: {
        DocumentStatus.PROCESSING,
        DocumentStatus.DELETING,
    },
    DocumentStatus.DELETING: set(),
}


class InvalidDocumentStatusTransition(ValueError):
    def __init__(self, from_status: DocumentStatus, to_status: DocumentStatus) -> None:
        super().__init__(f"invalid document status transition: {from_status} -> {to_status}")
        self.from_status = from_status
        self.to_status = to_status


def can_transition_document_status(
    from_status: DocumentStatus,
    to_status: DocumentStatus,
) -> bool:
    if from_status == to_status:
        return True

    return to_status in DOCUMENT_STATUS_TRANSITIONS[from_status]


def require_document_status_transition(
    from_status: DocumentStatus,
    to_status: DocumentStatus,
) -> None:
    if not can_transition_document_status(from_status, to_status):
        raise InvalidDocumentStatusTransition(from_status, to_status)
