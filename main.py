import os
from fastapi import FastAPI
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = FastAPI()

@app.get("/")
async def index():
    # 環境変数からJSONファイルのパスを取得する
    json_file_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    spread_sheet_key = os.getenv("SPREADSHEET_KEY", "")
    if not json_file_path or not spread_sheet_key:
        return {"error": "Missing environment variables"}

    ws = connect_gspread(json_file_path, spread_sheet_key)
    ds = ws.range('A1:G3')
    # ここでの返却値を適切な形式に変換する必要があるかもしれません
    return {"data": [cell.value for cell in ds]}

def connect_gspread(json_file_path, key):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_path, scope)
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_key(key).sheet1
    return worksheet