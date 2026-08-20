                    # --- DOĞRU COĞRAFİ YÜKSELEN (ASCENDANT) HESAPLAMA ---
                    gmst = observer.sidereal_time() # Radyan cinsinden Greenwich Yıldız Zamanı
                    lmst = float(gmst) + float(observer.lon) # Yerel Sidereal Zaman
                    
                    # Dünya'nın eksen eğikliği (yaklaşık 23.4369 derece = 0.4090928 radyan)
                    eps = ephem.obliquity() 
                    lat_rad = float(observer.lat)

                    # Yükselen derece formülü (Spherical Trigonometry - Ascendant Formula)
                    # tan(Asc) = cos(LMST) / - (sin(LMST) * cos(eps) + tan(lat) * sin(eps))
                    y_val = np.cos(lmst)
                    x_val = -(np.sin(lmst) * np.cos(eps) + np.tan(lat_rad) * np.sin(eps))
                    
                    asc_rad = np.arctan2(y_val, x_val)
                    asc_lon_deg = (asc_rad * 180.0 / np.pi) % 360
                    yukselen_burc = get_zodiac_sign_from_lon(asc_lon_deg)
