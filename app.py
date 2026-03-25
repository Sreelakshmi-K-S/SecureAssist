from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import os

from rules import rule_based_check
from score_engine import final_decision
from advisor import advisory_message
from input_detector import detect_input_type
from scraper import scrape_url

app = FastAPI(title="SecureAssist Threat Scanner")

app.add_middleware(
    SessionMiddleware, secret_key=os.environ.get("SECRET_KEY", "your-secret-key-here")
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

class AnalyzeRequest(BaseModel):
    input: str

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Display the main input page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze")
async def analyze(request: Request, input: str = Form(None)):
    """Process the input and redirect to results page"""
    user_input = input.strip() if input else ""
    
    if not user_input:
        return RedirectResponse(url=app.url_path_for("index"), status_code=303)
        
    # Get enhanced detection with detailed analysis
    detection_result = detect_input_type(user_input)
    input_type = detection_result['type']
    
    # If the input is a URL, also scrape its content for preview and enhanced analysis
    scraped = None
    if input_type and input_type.upper() == "URL":
        scraped = scrape_url(user_input)
        
    # Pass detection data and scraped content to rule_based_check for comprehensive analysis
    score, reasons = rule_based_check(user_input, input_type, detection_result, scraped)
    score = max(0, min(score, 100))
    result = final_decision(score)
    advice = advisory_message(result)
    
    # Slim down scraped data before storing in session cookie.
    # The full 'text' field can push the cookie over the 4096-byte limit,
    # causing the write to fail silently and old results to persist.
    session_scraped = None
    if scraped:
        session_scraped = {
            'title':       (scraped.get('title') or '')[:120],
            'description': (scraped.get('description') or '')[:200],
            'image_url':   scraped.get('image_url'),
            'links':       scraped.get('links', {'internal': 0, 'external': 0}),
            'forms':       scraped.get('forms', [])[:5],
            'status':      scraped.get('status', 'error'),
        }

    request.session['analysis'] = {
        'user_input': user_input[:300],
        'input_type': input_type,
        'result':     result,
        'score':      score,
        'advice':     advice,
        'reasons':    reasons[:10],
        'scraped':    session_scraped,
    }
    
    return RedirectResponse(url=app.url_path_for("result"), status_code=303)

@app.get("/result", response_class=HTMLResponse)
async def result(request: Request):
    """Display the analysis results"""
    analysis = request.session.get('analysis')
    
    if not analysis:
        return RedirectResponse(url=app.url_path_for("index"), status_code=303)
        
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "user_input": analysis['user_input'],
            "input_type": analysis['input_type'],
            "result": analysis['result'],
            "score": analysis['score'],
            "advice": analysis['advice'],
            "reasons": analysis['reasons'],
            "scraped": analysis['scraped']
        }
    )

@app.post("/api/analyze")
async def api_analyze(payload: AnalyzeRequest):
    """API endpoint for the browser extension"""
    user_input = payload.input.strip()
    
    if not user_input:
        return JSONResponse({"error": "No input provided"}, status_code=400)
        
    detection_result = detect_input_type(user_input)
    input_type = detection_result['type']
    
    scraped = None
    if input_type and input_type.upper() == "URL":
        scraped = scrape_url(user_input)
        
    score, reasons = rule_based_check(user_input, input_type, detection_result, scraped)
    score = max(0, min(score, 100))
    result = final_decision(score)
    advice = advisory_message(result)
    
    return {
        "user_input": user_input,
        "input_type": input_type,
        "result": result,
        "score": score,
        "advice": advice,
        "reasons": reasons
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=True)