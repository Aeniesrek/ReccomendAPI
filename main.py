import os
from fastapi import FastAPI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.cloud import secretmanager

app = FastAPI()

@app.get("/")
async def index():
    # 環境変数からJSONファイルのパスを取得する
    json_file_path = get_secret("GOOGLE_APPLICATION_CREDENTIALS")
    spread_sheet_key = get_secret("SPREADSHEET_KEY")
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

def get_secret(key):
    if os.getenv('ENV') == 'production':
        # 本番環境用のシークレット取得処理
        return access_secret_version('hellowebapi-415301', key)
    else:
        # ローカル環境用の処理
        return os.getenv(key,"")

def access_secret_version(project_id, secret_id, version_id="latest"):
    """
    GCP Secret Managerからシークレットの値を取得します。
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")