from datetime import date
from app.schemas import ShipmentRecord
from app.workflow import Workflow

def sample_record(confidence: float = 0.95) -> ShipmentRecord:
    return ShipmentRecord(shipment_reference="SHP-2048", shipper_name="Northwind Parts",
        pickup_location="Chicago, IL", delivery_location="Dallas, TX",
        pickup_date=date(2026, 11, 2), package_count=3, confidence=confidence)

def test_valid_record_processed_without_forwarding():
    workflow = Workflow(extractor=lambda _: sample_record())
    result = workflow.process("Synthetic sample shipment document.")
    assert result.status == "processed"
    assert result.record.shipment_reference == "SHP-2048"

def test_low_confidence_requires_review():
    workflow = Workflow(extractor=lambda _: sample_record(0.4), confidence_threshold=0.8)
    result = workflow.process("Synthetic sample shipment document.", True)
    assert result.status == "review_required"
    assert len(workflow.review_queue) == 1

def test_confident_record_forwarded_when_requested():
    calls = []
    def fake_forwarder(record):
        calls.append(record.shipment_reference)
        return 201
    workflow = Workflow(extractor=lambda _: sample_record(), forwarder=fake_forwarder)
    result = workflow.process("Synthetic sample shipment document.", True)
    assert result.status == "processed"
    assert result.downstream_status_code == 201
    assert calls == ["SHP-2048"]

def test_forwarding_failure_reported():
    from app.downstream import DownstreamError
    def fail(_):
        raise DownstreamError("service unavailable")
    workflow = Workflow(extractor=lambda _: sample_record(), forwarder=fail)
    result = workflow.process("Synthetic sample shipment document.", True)
    assert result.status == "downstream_failed"
