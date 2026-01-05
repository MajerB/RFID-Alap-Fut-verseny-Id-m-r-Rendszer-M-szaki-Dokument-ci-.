import serial
import time
from datetime import datetime

# --- BEÁLLÍTÁSOK ---
# Írd át arra a portra, amit az Eszközkezelőben látsz (pl. COM3, COM4)
PORT_NEV = 'COM3' 
BAUD_RATE = 115200
FAJL_NEV = "futas_eredmeny.txt"

def adat_tisztitas(nyers_sor):
    """
    Kiveszi a nyers hexából a lényeget (EPC).
    Bemenet pl: BB 02 22 ... 30 00 E2 80 ...
    Kimenet: E2 80 ... (csak a kártya azonosító)
    """
    # Kivesszük a szóközöket és a felesleges szöveget
    tiszta_hex = nyers_sor.replace(" ", "").replace("ADAT:", "").strip()
    
    # SZŰRÉS: A valódi kártyaadat hosszú. A rövid rendszerüzeneteket eldobjuk.
    if len(tiszta_hex) < 30:
        return None

    # KERESÉS: A "3000" (Protocol Control) jelzi az adat kezdetét a Gen2 kártyáknál
    # Ez a legbiztosabb pont a megtaláláshoz
    try:
        pc_index = tiszta_hex.find("3000")
        if pc_index != -1:
            # A "3000" utáni részt vesszük ki (általában 24 karakter = 12 bájt)
            epc_kezdet = pc_index + 4
            epc_veg = epc_kezdet + 24
            epc_adat = tiszta_hex[epc_kezdet:epc_veg]
            
            # Formázzuk olvashatóbbra (pl. E2 80 69...)
            olvashato_epc = " ".join(epc_adat[i:i+2] for i in range(0, len(epc_adat), 2))
            return olvashato_epc
    except Exception:
        pass
        
    return None

# --- FŐPROGRAM ---
try:
    print(f"Csatlakozás a porthoz: {PORT_NEV}...")
    ser = serial.Serial(PORT_NEV, BAUD_RATE, timeout=1)
    print("Sikeres csatlakozás! Várakozás a futókra...")
    print(f"Az eredmények ide lesznek mentve: {FAJL_NEV}")
    print("-" * 40)

    # Fájl megnyitása (hozzáfűzés módban)
    with open(FAJL_NEV, "a", encoding="utf-8") as f:
        while True:
            if ser.in_waiting > 0:
                try:
                    # Sor beolvasása
                    bejovo_sor = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    # Ha üres sor jön, lépjünk tovább
                    if not bejovo_sor:
                        continue

                    # Adat feldolgozása a tisztító függvénnyel
                    futokartya = adat_tisztitas(bejovo_sor)

                    # Ha találtunk érvényes kártyát
                    if futokartya:
                        ido = datetime.now().strftime("%H:%M:%S")
                        
                        # Kiírás a képernyőre
                        print(f" >> FUTO ERZEKELVE! Idő: {ido} | Chip: {futokartya}")
                        
                        # Mentés a fájlba
                        f.write(f"{ido};{futokartya}\n")
                        f.flush() # Azonnali mentés
                        
                except Exception as e:
                    print(f"Hiba az olvasás közben: {e}")

except serial.SerialException:
    print(f"HIBA: Nem tudtam megnyitni a {PORT_NEV} portot.")
    print("Ellenőrizd, hogy be van-e dugva az USB, és nem fut-e az Arduino IDE Serial Monitora!")
except KeyboardInterrupt:
    print("\nProgram leállítva.")