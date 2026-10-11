from fastapi import FastAPI, HTTPException
from app.extractor import ExtractionConfigurationError, LLMExtractor
from app.schemas import ProcessRequest, ProcessResponse
from app.workflow import Workflow

app = FastAPI(title="AI Document Workflow Automation",
              description="LLM extraction, schema validation, human review, and optional REST forwarding.",
              version="0.1.0")
workflow = Workflow(extractor=LLMExtractor().extract)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.post("/process", response_model=ProcessResponse)
def process_document(request: ProcessRequest) -> ProcessResponse:
    try:
        return workflow.process(request.document_text, request.send_to_downstream)
    except ExtractionConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Document extraction failed.") from exc

@app.get("/review-queue")
def get_review_queue() -> dict:
    return {"items": workflow.review_queue, "count": len(workflow.review_queue)}
