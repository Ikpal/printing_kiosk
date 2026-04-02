from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from .upload import upload_sessions, handle_upload_logic

router = APIRouter()

MOBILE_HTML = """
<!DOCTYPE html>
<html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Upload Document</title>
<style>
body { font-family: sans-serif; padding: 20px; background: #0f172a; color: white; text-align: center; }
.btn { background: #4F46E5; color: white; padding: 15px 30px; border-radius: 10px; border: none; font-size: 1.2rem; margin-top: 20px; width: 100%; cursor: pointer; }
input[type=file] { padding: 20px; background: #1e293b; border-radius: 10px; width: 100%; box-sizing: border-box; }
</style>
</head>
<body>
  <div style="max-width: 400px; margin: 0 auto">
      <h2>Send to Kiosk</h2>
      <p style="color: #94a3b8">Select a document to instantly send it to the printing kiosk screen.</p>
      <form id="uploadForm" action="/mobile/{session_id}" method="post" enctype="multipart/form-data">
         <input type="file" name="file" accept=".pdf,.docx,.jpg,.jpeg,.png" required />
         <button class="btn" type="submit" id="submitBtn">Upload File</button>
      </form>
      <div id="status" style="margin-top: 20px;"></div>
  </div>
  <script>
    document.getElementById('uploadForm').onsubmit = async (e) => {
      e.preventDefault();
      document.getElementById('submitBtn').disabled = true;
      document.getElementById('submitBtn').innerText = 'Uploading...';
      const formData = new FormData(e.target);
      try {
          const res = await fetch(e.target.action, { method: 'POST', body: formData });
          if (res.ok) {
             document.getElementById('status').innerHTML = '<h3 style="color:#10b981">Success! Check the kiosk screen.</h3>';
             document.getElementById('uploadForm').style.display = 'none';
          } else {
             const err = await res.json();
             document.getElementById('status').innerHTML = '<h3 style="color:#ef4444">Error: ' + err.detail + '</h3>';
             document.getElementById('submitBtn').disabled = false;
             document.getElementById('submitBtn').innerText = 'Try Again';
          }
      } catch (e) {
             document.getElementById('status').innerHTML = '<h3 style="color:#ef4444">Network Error</h3>';
             document.getElementById('submitBtn').disabled = false;
             document.getElementById('submitBtn').innerText = 'Try Again';
      }
    };
  </script>
</body>
</html>
"""

@router.get("/{session_id}")
async def get_mobile_page(session_id: str):
    if session_id not in upload_sessions:
        return HTMLResponse("<h1>Invalid or expired session. Please scan the QR code again.</h1>", status_code=404)
    return HTMLResponse(MOBILE_HTML.replace("{session_id}", session_id))

@router.post("/{session_id}")
async def post_mobile_upload(request: Request, session_id: str, file: UploadFile = File(...)):
    if session_id not in upload_sessions:
        raise HTTPException(status_code=404, detail="Invalid session")
    
    job_id = await handle_upload_logic(request, file)
    upload_sessions[session_id] = job_id
    return {"status": "success", "job_id": job_id}
