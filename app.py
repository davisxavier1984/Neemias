# app.py (Completo e Corrigido)
from flask import Flask, render_template, request, redirect, url_for, flash, session
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configuração do Google Sheets
def setup_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet_id = "1kZB9Pa0W3u-UXcvn4Cq1O9ypQdUtmxoSR2HHrsoqZ-8"  # Substitua pelo ID da sua planilha PRINCIPAL
    sheet = client.open_by_key(spreadsheet_id)
    worksheet_solicitacoes = sheet.get_worksheet(0) # Aba de Solicitações
    worksheet_produtos = sheet.worksheet("Produtos") # Assume que você tem uma aba chamada "Produtos"
    return worksheet_solicitacoes, worksheet_produtos # Retorna ambos os worksheets

# Funções para Solicitações
def load_market_list():
    worksheet_solicitacoes, _ = setup_google_sheets()
    all_values = worksheet_solicitacoes.get_all_values()
    if not all_values:
        return [], []
    headers = all_values[0]
    records = []
    for row in all_values[1:]:
        record = {}
        for i, header in enumerate(headers):
            record[header] = row[i] if i < len(row) else ''
        records.append(record)
    return headers, records

def generate_unique_solicitation_number():
    worksheet_solicitacoes, _ = setup_google_sheets()
    solicitation_numbers = worksheet_solicitacoes.col_values(1)[1:]

    if not solicitation_numbers:
        return 1000
    else:
        max_number = 0
        for number_str in solicitation_numbers:
            try:
                number = int(number_str)
                if number > max_number:
                    max_number = number
            except ValueError:
                pass
        return max_number + 1

def add_item(data, sec_solicitante, destino, colaborador, status, descricao_item, und, quantidade):
    worksheet_solicitacoes, _ = setup_google_sheets()
    solicitation_number = generate_unique_solicitation_number()
    if not worksheet_solicitacoes.get_all_records():
        worksheet_solicitacoes.append_row(["Nº DA SOLICITAÇÃO", "DATA", "SEC. SOLICITANTE", "DESTINO", "COLABORADOR", "STATUS", "DESCRIÇÃO DO ITEM", "UND", "QUANTIDADE"])
    worksheet_solicitacoes.append_row([solicitation_number, data, sec_solicitante, destino, colaborador, status, descricao_item, und, quantidade])

def remove_item(item_name):
    worksheet_solicitacoes, _ = setup_google_sheets()
    records = worksheet_solicitacoes.get_all_records()
    for i, record in enumerate(records):
        if record.get("DESCRIÇÃO DO ITEM") == item_name:
            worksheet_solicitacoes.delete_rows(i + 2)
            break

# Funções para Produtos
def load_product_list():
    _, worksheet_produtos = setup_google_sheets()
    records = worksheet_produtos.get_all_records()
    product_dict = {}
    for record in records:
        # Use 'Descrição' como chave.  Se 'Item' for o identificador único, use 'Item'.
        product_dict[record['Descrição']] = record
    return product_dict

def generate_unique_product_number():
    _, worksheet_produtos = setup_google_sheets()
    product_numbers = worksheet_produtos.col_values(1)[1:]

    if not product_numbers:
        return 1
    else:
        max_number = 0
        for number_str in product_numbers:
            try:
                number = int(number_str)
                if number > max_number:
                    max_number = number
            except ValueError:
                pass
        return max_number + 1

def add_product(descricao, unidade, classificacao):
    _, worksheet_produtos = setup_google_sheets()
    product_number = generate_unique_product_number()
    if not worksheet_produtos.get_all_records():
        worksheet_produtos.append_row(["Nº do Produto", "Descrição", "Unidade", "Classificação"])
    worksheet_produtos.append_row([product_number, descricao, unidade, classificacao])

def remove_product(product_number):
    _, worksheet_produtos = setup_google_sheets()
    records = worksheet_produtos.get_all_records()
    for i, record in enumerate(records):
        if record.get("Nº do Produto") == int(product_number):
            worksheet_produtos.delete_rows(i + 2)
            break

# Rotas Flask
@app.route('/')
def index():
    headers, market_list = load_market_list()
    product_list = load_product_list()  # Agora retorna um dicionário
    return render_template('index.html', market_list=market_list, headers=headers, product_list=product_list)

@app.route('/products')
def products():
    product_list = load_product_list()
    return render_template('products.html', product_list=product_list)

@app.route('/add', methods=['POST'])
def add():
    data = request.form.get('data')
    sec_solicitante = request.form.get('sec_solicitante')
    destino = request.form.get('destino')
    colaborador = request.form.get('colaborador')
    status = request.form.get('status')
    descricao_item = request.form.get('descricao_item')
    und = request.form.get('und')
    quantidade = request.form.get('quantidade')

    if data and sec_solicitante and destino and colaborador and status and descricao_item and und and quantidade:
        add_item(data, sec_solicitante, destino, colaborador, status, descricao_item, und, quantidade)
        flash(f"Solicitação para '{descricao_item}' adicionada com sucesso com Nº de Solicitação gerado!", 'success')
    else:
        flash("Por favor, preencha todos os campos da solicitação.", 'error')
    print("Sessão do Flask (rota /add):", session) # Debug
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete():
    item_to_remove = request.form.get('item_to_remove')
    if item_to_remove:
        remove_item(item_to_remove)
        flash(f"Item '{item_to_remove}' removido com sucesso da lista!", 'success')
    else:
        flash("Erro ao tentar remover o item.", 'error')
    return redirect(url_for('index'))

@app.route('/add_product', methods=['POST'])
def add_product_route():
    descricao = request.form.get('descricao')
    unidade = request.form.get('unidade')
    classificacao = request.form.get('classificacao')

    if descricao and unidade and classificacao:
        add_product(descricao, unidade, classificacao)
        flash("Produto cadastrado com sucesso!", 'success')
    else:
        flash("Por favor, preencha todos os campos do produto.", 'error')

    return redirect(url_for('products'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
    product_number = request.form.get('product_number')
    if product_number:
        remove_product(product_number)
        flash(f"Produto '{product_number}' removido com sucesso da lista!", 'success')
    else:
        flash("Erro ao tentar remover o produto.", 'error')
    return redirect(url_for('products'))

if __name__ == '__main__':
    app.run(debug=True)