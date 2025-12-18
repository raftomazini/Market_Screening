import os
import sys
import pandas as pd
from binance.spot import Spot
import yfinance as yf
from dotenv import load_dotenv
from lib import smtp
from ta.momentum import RSIIndicator

# Carrega variáveis de ambiente
load_dotenv()

# Parâmetros
rsi_janela = 9
dias_crypto = 30
intervalo_b3 = '1d'
periodo_b3 = '1mo'
hoje = pd.to_datetime('today').strftime('%d/%m/%Y')

def calcular_rsi(close_series, janela=rsi_janela):
    if len(close_series.dropna()) < janela + 1:
        return None
    rsi = RSIIndicator(close=close_series, window=janela).rsi()
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None

# === 1. AÇÕES/ETFS (YFinance apenas) ===
def processar_acoes(filepath='tickers/br_tickers.txt'):
    oportunidades = []
    with open(filepath, 'r', encoding='utf-8') as f:
        tickers = [line.strip() for line in f if line.strip()]

    for ticker in tickers:
        print(f"\n🇧🇷 Processando {ticker} (B3)...")
        try:
            data = yf.Ticker(ticker).history(period=periodo_b3, interval=intervalo_b3, auto_adjust=True)
            if data.empty or 'Close' not in data.columns:
                print(f"⚠️ Sem dados para {ticker}")
                continue
            close = data['Close'].dropna()
        except Exception as e:
            print(f"❌ Erro ao obter dados para {ticker}: {e}")
            continue

        rsi = calcular_rsi(close)
        print(data)
        print(rsi)
        if rsi is not None and rsi <= 30:
            oportunidades.append({"Ticker": ticker, "Close": round(close.iloc[-1], 2), "RSI": round(rsi, 2)})

    return oportunidades

# === 3. CRIPTOMOEDAS (Binance) ===
def processar_crypto(filepath='tickers/crypto_tickers.txt'):
    binance_client = Spot(api_key=os.getenv("API_KEY"), api_secret=os.getenv("SECRET_KEY"))
    oportunidades = []
    with open(filepath, 'r', encoding='utf-8') as f:
        pairs = [line.strip().upper() for line in f if line.strip()]

    for pair in pairs:
        print(f"\n🪙 Processando {pair} (Binance)…")
        try:
            klines = binance_client.klines(pair, "1d", limit=30)
            cols = ['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime',
                    'QuoteAssetVolume', 'NumberOfTrades', 'TakerBuyBaseVolume',
                    'TakerBuyQuoteVolume', 'Ignore']
            df = pd.DataFrame(klines, columns=cols)
            close = df['Close'].astype(float)
        except Exception as e:
            print(f"❌ Erro ao processar {pair}: {e}")
            continue

        rsi = calcular_rsi(close)
        print(df)
        print(rsi)
        if rsi is not None and rsi <= 30:
            oportunidades.append({"Ticker": pair, "Close": round(close.iloc[-1], 2), "RSI": round(rsi, 2)})

    return oportunidades

# === EXECUÇÃO via CLI ===
def main():
    if len(sys.argv) < 2:
        print("Uso: python rsi_scanner.py [acoes | crypto]")
        sys.exit(1)

    tipo = sys.argv[1].lower()
    if tipo not in ['acoes', 'crypto']:
        print("❌ Tipo inválido. Use: acoes | crypto")
        sys.exit(1)

    if tipo == 'acoes':
        oportunidades = processar_acoes()
        titulo = "Oportunidades RSI - Ações/ETFs"
    elif tipo == 'crypto':
        oportunidades = processar_crypto()
        titulo = "Oportunidades RSI - Criptomoedas"

    if oportunidades:
        df = pd.DataFrame(oportunidades)
        html = df.to_html(index=False)
    else:
        html = f"Nenhuma oportunidade de RSI <= 30 encontrada para tipo: {tipo}"

    destinations = os.getenv("MAIL_RECEIVER").split(',')

    for destination in destinations:
        smtp.send_ssl_email(
            os.getenv("MAIL_SMTP"),
            os.getenv("MAIL_PORT"),
            os.getenv("MAIL_USER"),
            os.getenv("MAIL_PASS"),
            os.getenv("MAIL_SENDER"),
            destination,
            titulo,
            html
        )

    print(f"\n✅ Relatório enviado: {titulo}")

if __name__ == "__main__":
    main()
