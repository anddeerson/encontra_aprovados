import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
import unicodedata


def normalizar_texto(texto):
    """Remove acentos e converte para minúsculas."""
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    return texto.lower().strip()


def extrair_nomes_pdf(pdf_file):
    """Extrai nomes completos do PDF, normalizando-os."""
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    matches = re.findall(r'\b[A-ZÀ-Ú][A-ZÀ-Ú]+\s[A-ZÀ-Ú ]+\b', text)
    return {normalizar_texto(name) for name in matches}


def main():
    st.title("Encontra Aprovados Versão 0.6")
    st.write("Carregue o arquivo CSV com os nome(s) do(s) aluno(s) e um ou mais PDFs com o(s) aprovado(s).")

    csv_file = st.file_uploader("Carregar arquivo CSV", type=["csv"])
    pdf_files = st.file_uploader("Carregar arquivo(s) PDF", type=["pdf"], accept_multiple_files=True)

    if csv_file and pdf_files:
        df_csv = pd.read_csv(csv_file)
        colunas = df_csv.columns.tolist()
        coluna_nomes = st.selectbox("Selecione a coluna que contém os nomes:", colunas)
        csv_names = {normalizar_texto(name) for name in df_csv[coluna_nomes].dropna().tolist()}

        results = []
        for pdf_file in pdf_files:
            approved_names = extrair_nomes_pdf(pdf_file)
            common_names = csv_names.intersection(approved_names)
            for name in common_names:
                results.append({"Nome": name, "Arquivo PDF": pdf_file.name})

        if results:
            st.success("Alunos aprovados encontrados!")
            results_df = pd.DataFrame(results)
            st.dataframe(results_df)
            csv_download = results_df.to_csv(index=False).encode("utf-8")
            st.download_button("Baixar resultados como CSV", data=csv_download, file_name="alunos_aprovados.csv")
        else:
            st.warning("Nenhum aluno aprovado foi encontrado nos PDFs enviados.")


if __name__ == "__main__":
    main()
