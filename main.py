import asyncio
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import StreamingResponse
import edge_tts

app = FastAPI(title="Edge TTS Fast Proxy")

async def tts_streaming_generator(text: str, voice: str):
    try:
        # Microsoft ko lagna chahiye ki request sach me Edge Browser se aa rahi hai
        # Isliye hum custom headers aur connect_options pass karenge
        communicate = edge_tts.Communicate(text, voice)
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
                
    except Exception as e:
        print(f"Error in streaming: {e}")

@app.get("/v1/tts")
async def text_to_speech(
    text: str = Query(..., description="Jo text bolna hai"),
    voice: str = Query("hi-IN-MadhurNeural", description="Voice name")
):
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
        
    # Extra Safety: Kuch voices ke naam change hue hain, unhe filter karna
    # Agar sirf 'Madhur' pass ho toh use neural me convert karna
    if voice == "Madhur":
        voice = "hi-IN-MadhurNeural"
    elif voice == "Swara":
        voice = "hi-IN-SwaraNeural"

    return StreamingResponse(
        tts_streaming_generator(text, voice), 
        media_type="audio/mpeg"
    )

@app.get("/")
def home():
    return {"status": "Edge TTS Proxy is Running Successfully!"}
