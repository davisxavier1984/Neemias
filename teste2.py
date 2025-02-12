import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Configuração do Google Sheets
def setup_google_sheets():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file("credentials.json", scopes=scope)
    client = gspread.authorize(creds)
    spreadsheet_id = "1kZB9Pa0W3u-UXcvn4Cq1O9ypQdUtmxoSR2HHrsoqZ-8"  # Substitua pelo ID da sua planilha
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.get_worksheet(0)  # Acessa a primeira aba
    print("Planilha acessada com sucesso")  # Mensagem de depuração
    return worksheet

# Função para carregar a lista de mercado
def load_market_list(worksheet):
    records = worksheet.get_all_records()
    return records

# Função para adicionar um item à lista
def add_item(worksheet, item, quantity):
    # Verifica se a planilha está vazia (sem cabeçalhos)
    if not worksheet.get_all_records():
        worksheet.append_row(["Item", "Quantidade"])  # Adiciona cabeçalhos se a planilha estiver vazia
    worksheet.append_row([item, quantity])

# Função para remover um item da lista
def remove_item(worksheet, item_name):
    records = worksheet.get_all_records()
    for i, record in enumerate(records):
        if record.get("Item") == item_name:  # Usar .get() para evitar KeyError
            worksheet.delete_rows(i + 2)  # +2 porque a primeira linha é o cabeçalho
            break

# Interface do Streamlit
def main():
    st.title("Lista de Mercado 🛒")

    # Configuração do Google Sheets
    worksheet = setup_google_sheets()

    # Carregar a lista de mercado
    market_list = load_market_list(worksheet)

    # Exibir a lista de mercado
    st.header("Itens na Lista de Mercado")
    if market_list:
        for item in market_list:
            # Usar .get() para evitar KeyError
            item_name = item.get("Item", "Desconhecido")
            item_quantity = item.get("Quantidade", "N/A")
            st.write(f"- {item_name}: {item_quantity}")
    else:
        st.write("A lista de mercado está vazia.")

    # Adicionar um novo item
    st.header("Adicionar Item")
    new_item = st.text_input("Nome do Item")
    new_quantity = st.text_input("Quantidade")
    if st.button("Adicionar"):
        if new_item and new_quantity:
            add_item(worksheet, new_item, new_quantity)
            st.success(f"Item '{new_item}' adicionado com sucesso!")
            st.rerun()  # Recarrega a página para atualizar a lista
        else:
            st.error("Por favor, preencha todos os campos.")

    # Remover um item
    st.header("Remover Item")
    item_to_remove = st.text_input("Nome do Item para Remover")
    if st.button("Remover"):
        if item_to_remove:
            remove_item(worksheet, item_to_remove)
            st.success(f"Item '{item_to_remove}' removido com sucesso!")
            st.experimental_rerun()  # Recarrega a página para atualizar a lista
        else:
            st.error("Por favor, insira o nome do item.")

if __name__ == "__main__":
    main()
