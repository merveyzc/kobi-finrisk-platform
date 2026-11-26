import os
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

BASE_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/"
TIMEOUT = 15


def _get_api_key():
    # 1. .env dosyasını yükle
    load_dotenv()

    # 2. "TCMB_EVDS_API_KEY" değişkenini os ile oku
    api_key =os.getenv("TCMB_EVDS_API_KEY")

    # 3. Eğer api_key yoksa veya boşsa açıklayıcı bir mesajla ValueError fırlat (raise)
    if not api_key:
        raise ValueError ("TCMB_EVDS_API_KEY .env dosyasında bulunamadı")

    # 4. Bulunan anahtarı döndür
    return api_key


def fetch_evds_series(series_codes, lookback_days=45):
    # 1. Yukarıdaki yardımcı fonksiyondan API anahtarını al
    api_key = _get_api_key()

    # 2. Bugünün tarihini ve lookback_days gün öncesini hesapla
    # İpucu: datetime.now() ve timedelta(days=...) kullan
    end_dt = datetime.now()
    start_dt = end_dt-timedelta(days=lookback_days)

    # 3. İki tarihi de EVDS'nin istediği "GG-AA-YYYY" metnine çevir (.strftime("%d-%m-%Y"))
    start_date = start_dt.strftime("%d-%m-%Y")
    end_date = end_dt.strftime("%d-%m-%Y")

    # 4. series_codes listesini aralarına "-" koyarak tek metin yap ("-".join(...))
    series_param = ("-".join(series_codes))

    # 5. BASE_URL sonuna f-string ile parametreleri ekle:
    # Format: series=...&startDate=...&endDate=...&type=json
    url = f"{BASE_URL}series={series_param}&startDate={start_date}&endDate={end_date}&type=json"

    # 6. API anahtarını "key" adıyla headers sözlüğüne yerleştir
    headers = {"key": api_key}

    # 7. requests.get ile url, headers ve timeout vererek isteği at
    response = requests.get(url,headers=headers,timeout=TIMEOUT)

    # 8. HTTP hatası (403, 404, 500 vb.) varsa durdurmak için status kontrolü yap
    response.raise_for_status()

    # 9. Yanıtı JSON sözlüğüne çevir ve içinden "items" listesini döndür (yoksa boş liste [])
    data = response.json()
    return data.get("items", [])


if __name__ == "__main__":
    # Test: TP.KTF17 serisini liste içinde gönderip dönen listenin son 3 kaydını yazdır
    ham_veri = fetch_evds_series(["TP.KTF17"])
    print(ham_veri[-3:])

