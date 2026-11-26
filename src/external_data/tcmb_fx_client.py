import xml.etree.ElementTree as ET
import requests

TCMB_FX_URL = "https://www.tcmb.gov.tr/kurlar/today.xml"
TIMEOUT = 15


def fetch_tcmb_fx_rates(target_currencies=("USD", "EUR")):
    # 1. requests.get ile TCMB_FX_URL adresine timeout=TIMEOUT vererek istek at
    # (EVDS'deki gibi headers gerekmiyor, bu sayfa herkese açık)
    response = requests.get(TCMB_FX_URL, timeout=TIMEOUT)

    # 2. HTTP hatası varsa durdur (EVDS'de kullandığın aynı metot)
    response.raise_for_status()

    # 3. response.content içindeki ham XML'i ET.fromstring(...) ile ağaca çevir
    root = ET.fromstring(response.content)

    # 4. En dıştaki <Tarih_Date Tarih="..."> etiketinden "Tarih" özelliğini al
    # İpucu: root.attrib.get(...)
    raw_date = root.attrib.get("Tarih")

    raw_rates = []

    # 5. root altındaki tüm "Currency" etiketlerini bul ve döngüye sok
    # İpucu: root.findall(...)
    for currency in root.findall("Currency"):
        # 6. Sıradaki <Currency CurrencyCode="..."> etiketinden "CurrencyCode" özelliğini al
        code = currency.attrib.get("CurrencyCode")

        # 7. Eğer code değeri target_currencies içinde varsa (in operatörü) içeri gir
        if code in target_currencies:
            # 8. Etiketlerin arasındaki alış ("ForexBuying") ve satış ("ForexSelling") metnini oku
            # İpucu: currency.findtext(...)
            buying = currency.findtext("ForexBuying")
            selling = currency.findtext("ForexSelling")

            # 9. Ham verileri dönüştürmeden sözlük olarak listeye ekle
            raw_rates.append({
                "currency_code": code,
                "buying_rate": buying,
                "selling_rate": selling,
                "raw_date": raw_date,
            })

    return raw_rates


if __name__ == "__main__":
    ham_kurlar = fetch_tcmb_fx_rates()
    print(ham_kurlar)