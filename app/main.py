from fastapi import FastAPI
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import posting_service

app = FastAPI(
    title="Automated Multi-Platform Posting API",
    description="Publishes one validated message to configured platforms independently.",
    version="1.0.0",
)


@app.get("/")
async def health_check():
    return {"message": "Automated Posting API is running", "docs": "/docs"}


@app.post("/posting", response_model=PostingResponse)
async def create_post(request: PostingRequest):
    results = await posting_service.publish_everywhere(request.message)
    succeeded = sum(result.status == "success" for result in results)
    if succeeded == len(results):
        overall = "success"
    elif succeeded:
        overall = "partial_success"
    else:
        overall = "failed"
    return PostingResponse(success=succeeded > 0, overall_status=overall, results=results)
