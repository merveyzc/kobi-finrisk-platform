from datetime import date, datetime
from pydantic import BaseModel, Field


class FxRate(BaseModel):
    source: str = "TCMB_TODAY_XML"
    currency_pair: str
    buying_rate: float = Field(gt=0)
    selling_rate: float = Field(gt=0)
    captured_at: date


class MarketRate(BaseModel):
    source: str = "TCMB_EVDS"
    series_code: str
    # 1. Faiz oranı 0'dan büyük float olmalı (yukarıdaki FxRate'e bak)
    value: float = Field(gt=0)
    # 2. Tarih alanı date tipinde olmalı
    observed_at: date


def normalize_fx_rates(raw_rates):
    cleaned = []

    for item in raw_rates:
        # 3. "26.11.2026" formatındaki metni Python date nesnesine çevir
        # İpucu: datetime.strptime(metin, "%d.%m.%Y").date()
        parsed_date = datetime.strptime(item["raw_date"],"%d.%m.%Y" ).date()

        # 4. "USD" -> "USD/TRY" formatına getir (f-string kullan)
        pair = f"{item['currency_code']}/TRY"

        # 5. FxRate modelini oluştur (Pydantic metin kurları otomatik float yapar)
        rate = FxRate(
            currency_pair=pair,
            buying_rate=item["buying_rate"],
            selling_rate=item["selling_rate"],
            captured_at=parsed_date,
        )
        cleaned.append(rate)

    return cleaned


def normalize_evds_rates(raw_items, series_code="TP.KTF17"):
    cleaned = []
    # EVDS çıktısında nokta alt tireye döner: "TP.KTF17" -> "TP_KTF17"
    json_key = series_code.replace(".", "_")

    for item in raw_items:
        # 6. Sözlükten json_key değerini .get() ile al
        raw_value = item.get(json_key)

        # 7. Tatil veya henüz yayımlanmamış haftada değer None gelebilir; boşsa bu satırı atla
        if raw_value is None:
            continue

        # 8. EVDS tarihi "13-11-2026" şeklinde tireli geliyor; onu date nesnesine çevir
        parsed_date = datetime.strptime(item["Tarih"], "%d-%m-%Y").date()

        # 9. MarketRate modelini oluşturup cleaned listesine ekle
        rate = MarketRate(
            series_code=series_code,
            value=raw_value,
            observed_at=parsed_date,
        )
        cleaned.append(rate)

    return cleaned


if __name__ == "__main__":
    from src.external_data.tcmb_evds_client import fetch_evds_series
    from src.external_data.tcmb_fx_client import fetch_tcmb_fx_rates

    ham_kurlar = fetch_tcmb_fx_rates()
    temiz_kurlar = normalize_fx_rates(ham_kurlar)
    print("TEMİZ KURLAR:")
    print([r.model_dump(mode="json") for r in temiz_kurlar])

    ham_faiz = fetch_evds_series(["TP.KTF17"])
    temiz_faiz = normalize_evds_rates(ham_faiz, "TP.KTF17")
    print("\nTEMİZ FAİZ (SON 2 KAYIT):")
    print([r.model_dump(mode="json") for r in temiz_faiz[-2:]])