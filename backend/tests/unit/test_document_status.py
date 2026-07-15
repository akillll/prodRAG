import pytest

from documents.status import (
    DocumentStatus,
    InvalidDocumentStatusTransition,
    can_transition_document_status,
    require_document_status_transition,
)


@pytest.mark.parametrize(
    ("from_status", "to_status"),
    [
        (DocumentStatus.PROCESSING, DocumentStatus.READY),
        (DocumentStatus.PROCESSING, DocumentStatus.FAILED),
        (DocumentStatus.PROCESSING, DocumentStatus.DELETING),
        (DocumentStatus.READY, DocumentStatus.PROCESSING),
        (DocumentStatus.READY, DocumentStatus.DELETING),
        (DocumentStatus.FAILED, DocumentStatus.PROCESSING),
        (DocumentStatus.FAILED, DocumentStatus.DELETING),
        (DocumentStatus.READY, DocumentStatus.READY),
    ],
)
def test_document_status_allows_expected_transitions(
    from_status: DocumentStatus,
    to_status: DocumentStatus,
) -> None:
    assert can_transition_document_status(from_status, to_status) is True
    require_document_status_transition(from_status, to_status)


@pytest.mark.parametrize(
    ("from_status", "to_status"),
    [
        (DocumentStatus.READY, DocumentStatus.FAILED),
        (DocumentStatus.FAILED, DocumentStatus.READY),
        (DocumentStatus.DELETING, DocumentStatus.PROCESSING),
        (DocumentStatus.DELETING, DocumentStatus.READY),
        (DocumentStatus.DELETING, DocumentStatus.FAILED),
    ],
)
def test_document_status_rejects_invalid_transitions(
    from_status: DocumentStatus,
    to_status: DocumentStatus,
) -> None:
    assert can_transition_document_status(from_status, to_status) is False

    with pytest.raises(InvalidDocumentStatusTransition):
        require_document_status_transition(from_status, to_status)
