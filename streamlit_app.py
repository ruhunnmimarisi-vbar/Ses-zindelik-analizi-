import swisseph as swe

def yukselen_hesapla(yil, ay, gun, saat, dakika, enlem, boylam, ev_sistemi=b'P'):
    """
    Swiss Ephemeris kullanarak kusursuz Yükselen (Ascendant) hesaplar.
    enlem/boylam: Ondalık derece cinsinden (Örn: İstanbul -> Lat: 41.0082, Lon: 28.9784)
    saat: Yerel saat (Local Time)
    """
    # Türkiye yerel saatinden UTC'ye geçiş (Yaz saati uygulaması dikkate alınmalıdır)
    # Örnek olması açısından UTC hesaplamasını doğrudan saat üzerinden yapıyoruz:
    utc_saat = saat - 3  # Türkiye UTC+3 bölgesindedir (Standart saat varsayımıyla)
    
    # Julian Günü (UT) hesaplama
    jd_ut = swe.julday(yil, ay, gun, utc_saat + (dakika / 60.0))
    
    # Evler ve Asc/MC hesaplama (swe.houses fonksiyonu ev cusps ve Asc/MC dizilerini döner)
    cusps, ascmc = swe.houses(jd_ut, enlem, boylam, ev_sistemi)
    
    # ascmc[0] Yükselen (Ascendant) derecesini verir
    asc_derece = ascmc[0]
    
    # Dereceyi burca çevirme fonksiyonu
    burclar = [
        "Koç", "Boğa", "İkizler", "Yengeç", "Aslan", "Başak",
        "Terazi", "Akrep", "Yay", "Oğlak", "Kova", "Balık"
    ]
    
    burc_index = int(asc_derece // 30)
    derece_içinde = asc_derece % 30
    
    asc_burc = burclar[burc_index]
    
    return {
        "asc_derece": asc_derece,
        "burc": asc_burc,
        "detay": f"{int(derece_içinde)}° {int((derece_içinde % 1) * 60)}' {asc_burc}"
    }

# Test Örneği (Koordinatları ve bilgileri kendi doğum haritana göre girebilirsin)
# Örn: Saray, Tekirdağ için yaklaşık koordinatlar (Enlem: 41.44, Boylam: 27.99)
sonuc = yukselen_hesapla(1984, 12, 29, 12, 0, 41.44, 27.99)
print("Hesaplanan Yükselen:", sonuc["detay"])
