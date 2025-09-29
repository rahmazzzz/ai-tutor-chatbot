from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from app.deps import get_current_user
from app.services.notes_service import NotesService

router = APIRouter()
notes_service = NotesService()

@router.post("/notes/from-audio")
async def generate_notes_from_audio(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """
    Accepts lecture audio, generates transcript and notes.
    """
    try:
        # Generate transcript and notes
        transcript, notes = await notes_service.generate_from_audio(file)
        response = {"transcript": transcript, "notes": notes}
        return JSONResponse(response)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
