import gdown
import os
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

# --- مدل داده برای ورودی درخواست ---
# با استفاده از Pydantic، ورودی‌ها را اعتبارسنجی می‌کنیم
class DownloadRequest(BaseModel):
    drive_link: str = Field(..., description="لینک اشتراک‌گذاری فایل در گوگل درایو")
    destination_path: str = Field(..., description="مسیر نسبی برای ذخیره فایل روی دیسک")

# --- ساخت اپلیکیشن FastAPI ---
app = FastAPI(
    title="Google Drive Downloader API",
    description="یک سرویس برای دانلود فایل از گوگل درایو و ذخیره آن روی دیسک.",
    version="1.0.0"
)

# --- پوشه پایه برای امنیت ---
# تمام دانلودها برای امنیت بیشتر، داخل این پوشه انجام می‌شوند
BASE_DOWNLOAD_DIR = Path("/data")

def start_download(url: str, output_path: Path):
    """
    تابع اصلی دانلود که در پس‌زمینه اجرا می‌شود.
    """
    print(f"🚀 Starting download...")
    print(f"   - From: {url}")
    print(f"   - To: {output_path}")
    
    try:
        # ساختن پوشه‌های والد در صورت عدم وجود
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # استفاده از gdown برای دانلود فایل با تشخیص هوشمند نام
        gdown.download(url=url, output=str(output_path), quiet=False, fuzzy=True)
        
        print(f"✅ Download complete for: {output_path.name}")
        
    except Exception as e:
        print(f"❌ Error downloading file {url}. Reason: {e}")

@app.post("/download/")
def schedule_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """
    اندپوینت اصلی برای دریافت درخواست دانلود.
    این اندپوینت بلافاصله پاسخ می‌دهد و دانلود را در پس‌زمینه شروع می‌کند.
    """
    # --- بررسی امنیتی مسیر ---
    # ترکیب مسیر پایه با مسیر درخواستی کاربر
    full_path = BASE_DOWNLOAD_DIR.joinpath(request.destination_path).resolve()

    # جلوگیری از حملات Path Traversal (مانند ../../)
    if BASE_DOWNLOAD_DIR not in full_path.parents and full_path != BASE_DOWNLOAD_DIR:
        raise HTTPException(
            status_code=400,
            detail="Error: Invalid destination path. Path must be inside the base data directory."
        )

    # --- افزودن وظیفه به پس‌زمینه ---
    # این کار باعث می‌شود سرور منتظر اتمام دانلود نماند و بلافاصله پاسخ دهد
    background_tasks.add_task(start_download, request.drive_link, full_path)

    return {
        "status": "success",
        "message": "Download task has been scheduled successfully.",
        "details": {
            "drive_link": request.drive_link,
            "save_location": str(full_path)
        }
    }

@app.get("/")
def read_root():
    """
    یک اندپوینت ساده برای اطمینان از سلامت سرویس.
    """
    return {"message": "Google Drive Downloader API is running."}
