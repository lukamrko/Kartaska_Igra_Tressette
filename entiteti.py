class Karta(object):
    def __init__(self, broj, zog):
        self.broj=broj
        self.zog=zog
        self.oznaka=zog[0]+str(broj)

    def __eq__(self, oznaka):
        return self.oznaka==oznaka

class Tim:
    def __init__(self, naziv):
        self.naziv=naziv
        self.punti=0
        self.bele=0

    def dodaj_bele(self, bele):
        self.bele+=bele
        while(self.bele>=3):
            self.punti+=1
            self.bele-=3

    def restartiraj_bele(self):
        self.bele=0

class Karta_ruke():
    def __init__(self, redoslijed, igrac, karta):
        self.redoslijed=redoslijed
        self.igrac=igrac
        self.karta=karta
