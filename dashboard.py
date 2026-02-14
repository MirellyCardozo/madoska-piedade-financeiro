import streamlit as st
import pandas as pd
from sqlalchemy import text
from datetime import date
from fpdf import FPDF
from io import BytesIO
from database import engine


# ==========================
# PDF
# ==========================
class RelatorioPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Relatório Financeiro - Madoska Piedade", ln=True, align="C")
        self.ln(5)


def gerar_pdf(df, periodo, saldo_anterior, entradas, saidas, saldo_final):
    pdf = RelatorioPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 8, f"Período: {periodo}", ln=True)
    pdf.ln(3)

    pdf.cell(0, 8, f"Saldo anterior: R$ {saldo_anterior:.2f}", ln=True)
    pdf.cell(0, 8, f"Total de entradas: R$ {entradas:.2f}", ln=True)
    pdf.cell(0, 8, f"Total de saídas: R$ {saidas:.2f}", ln=True)
    pdf.cell(0, 8, f"Saldo final: R$ {saldo_final:.2f}", ln=True)

    pdf.ln(6)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Lançamentos do mês:", ln=True)
    pdf.ln(3)

    pdf.set_font("Arial", size=9)

    for _, row in df.iterrows():
        linha = (
            f"{row['data']} | {row['tipo']} | {row['categoria']} | "
            f"{row['pagamento']} | {row['descricao']} | R$ {row['valor']:.2f}"
        )
        pdf.multi_cell(0, 6, linha)

    buffer = BytesIO()
    buffer.write(pdf.output(dest="S").encode("latin-1"))
    buffer.seek(0)
    return buffer


# ==========================
# DASHBOARD
# ==========================
def tela_dashboard(usuario_id):
    st.title("Dashboard")

    mes_ref = st.date_input("Mês de referência", value=date.today())

    inicio_mes = date(mes_ref.year, mes_ref.month, 1)
    if mes_ref.month == 12:
        fim_mes = date(mes_ref.year + 1, 1, 1)
    else:
        fim_mes = date(mes_ref.year, mes_ref.month + 1, 1)

    # -------- SALDO ANTERIOR --------
    saldo_anterior = pd.read_sql(
        text(
            """
            SELECT COALESCE(SUM(
                CASE
                    WHEN tipo = 'Entrada' THEN valor
                    ELSE -valor
                END
            ), 0) AS saldo
            FROM lancamentos
            WHERE usuario_id = :usuario_id
            AND data < :inicio
            """
        ),
        engine,
        params={"usuario_id": usuario_id, "inicio": inicio_mes},
    ).iloc[0]["saldo"]

    # -------- MOVIMENTAÇÃO DO MÊS --------
    df = pd.read_sql(
        text(
            """
            SELECT data, tipo, categoria, pagamento, descricao, valor
            FROM lancamentos
            WHERE usuario_id = :usuario_id
            AND data >= :inicio
            AND data < :fim
            ORDER BY data
            """
        ),
        engine,
        params={
            "usuario_id": usuario_id,
            "inicio": inicio_mes,
            "fim": fim_mes,
        },
    )

    entradas = df.loc[df["tipo"] == "Entrada", "valor"].sum()
    saidas = df.loc[df["tipo"] == "Saída", "valor"].sum()
    saldo_final = saldo_anterior + entradas - saidas

    # -------- RESUMO --------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Saldo anterior", f"R$ {saldo_anterior:.2f}")
    col2.metric("Entradas", f"R$ {entradas:.2f}")
    col3.metric("Saídas", f"R$ {saidas:.2f}")
    col4.metric("Saldo final", f"R$ {saldo_final:.2f}")

    st.divider()

    st.subheader("Lançamentos do mês")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ==========================
    # BOTÃO QUE TINHA SUMIDO (AGORA VOLTOU)
    # ==========================
    st.divider()
    st.subheader("Exportar relatório")

    if st.button("Gerar Relatório PDF"):
        pdf_buffer = gerar_pdf(
            df=df,
            periodo=f"{mes_ref.month}/{mes_ref.year}",
            saldo_anterior=saldo_anterior,
            entradas=entradas,
            saidas=saidas,
            saldo_final=saldo_final,
        )

        st.download_button(
            label="Baixar PDF",
            data=pdf_buffer,
            file_name=f"relatorio_{mes_ref.month}_{mes_ref.year}.pdf",
            mime="application/pdf",
        )
