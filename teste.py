import gspread
from google.oauth2.service_account import Credentials

# 1. Definir escopo correto
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# 2. Carregar credenciais
credenciais_arquivo = "credentials.json"
creds = Credentials.from_service_account_file(credenciais_arquivo, scopes=scope)

# 3. Autorizar o cliente
client = gspread.authorize(creds)

# 4. Acessar a planilha
spreadsheet_id = "1kZB9Pa0W3u-UXcvn4Cq1O9ypQdUtmxoSR2HHrsoqZ-8"
sheet = client.open_by_key(spreadsheet_id)

# 5. Ler os registros
worksheet = sheet.get_worksheet(0)
records = worksheet.get_all_records()
print(records)
