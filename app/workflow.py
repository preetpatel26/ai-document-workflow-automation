from collections.abc import Callable
from app.config import settings
from app.downstream import DownstreamError, forward_record
from app.schemas import ProcessResponse, ShipmentRecord

class Workflow:
    def __init__(self, extractor: Callable[[str], ShipmentRecord],
                 forwarder: Callable[[ShipmentRecord], int] | None = None,
                 confidence_threshold: float | None = None):
        self.extractor = extractor
        self.forwarder = forwarder or forward_record
        self.confidence_threshold = settings.review_confidence_threshold if confidence_threshold is None else confidence_threshold
        self.review_queue: list[dict] = []

    def process(self, document_text: str, send_to_downstream: bool = False) -> ProcessResponse:
        record = self.extractor(document_text)
        reasons = []
        if record.confidence < self.confidence_threshold:
            reasons.append(f"Confidence {record.confidence:.2f} is below threshold {self.confidence_threshold:.2f}.")
        if reasons:
            self.review_queue.append({"record": record.model_dump(mode="json"), "reasons": reasons})
            return ProcessResponse(status="review_required", record=record, review_reasons=reasons,
                                   message="Record requires human review before downstream submission.")
        if send_to_downstream:
            try:
                code = self.forwarder(record)
            except DownstreamError as exc:
                return ProcessResponse(status="downstream_failed", record=record, message=str(exc))
            return ProcessResponse(status="processed", record=record, downstream_status_code=code,
                                   message="Record validated and forwarded successfully.")
        return ProcessResponse(status="processed", record=record,
                               message="Record extracted and validated; downstream forwarding was not requested.")
