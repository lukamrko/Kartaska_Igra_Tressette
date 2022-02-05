from entiteti import Karta

karte_zogovi=('bastoni', 'dinari', 'kupe', 'spade')
karte_brojevi=(1, 2, 3, 4, 5, 6, 7, 11, 12, 13)

def dohvati_dek():
    dek=[]
    for zog in karte_zogovi:
        for broj in karte_brojevi:
            dek.append(Karta(broj, zog))
    return dek