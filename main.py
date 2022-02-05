import random
import spade
import time
from argparse import ArgumentParser
from ucitavanjeDeka import *
from entiteti import *
from igrac import Igrac
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade import quit_spade


def main():
    #Pocetne postavke
    random.seed()

    parser = ArgumentParser()
    parser.add_argument(
        "-jid1", type=str, help="JID 1. agenta", default="agent@rec.foi.hr")
    parser.add_argument(
        "-pwd1", type=str, help="Lozinka 1. agenta", default="tajna")
    parser.add_argument(
        "-jid2", type=str, help="JID 2. agenta", default="receiver@rec.foi.hr")
    parser.add_argument(
        "-pwd2", type=str, help="Lozinka 2. agenta", default="secret")
    parser.add_argument(
        "-jid3", type=str, help="JID 3. agenta", default="lukamrko@rec.foi.hr")
    parser.add_argument(
        "-pwd3", type=str, help="Lozinka 3. agenta", default="zmijavci")
    parser.add_argument(
        "-jid4", type=str, help="JID 4. agenta", default="sender@rec.foi.hr")
    parser.add_argument(
        "-pwd4", type=str, help="Lozinka 4. agenta", default="secret")
    args = parser.parse_args()

    tim1=Tim("timA")
    tim2=Tim("timB")
    timovi=(tim1, tim2)

    igrac1 = Igrac(args.jid1, args.pwd1)
    pokretanje1=igrac1.start()

    igrac2 = Igrac(args.jid2, args.pwd2)
    pokretanje2=igrac2.start()

    igrac3 = Igrac(args.jid3, args.pwd3)
    pokretanje3=igrac3.start()

    igrac4 = Igrac(args.jid4, args.pwd4)
    pokretanje4=igrac4.start()

    igrac1.ucitaj_pocetne_postavke(igrac1.jid.bare(), tim1, igrac2)
    igrac2.ucitaj_pocetne_postavke(igrac2.jid.bare(), tim2, igrac3)
    igrac3.ucitaj_pocetne_postavke(igrac3.jid.bare(), tim1, igrac4)
    igrac4.ucitaj_pocetne_postavke(igrac4.jid.bare(), tim2, igrac1)

    time.sleep(35)

    igraci=(igrac1, igrac2, igrac3, igrac4)
    hijerarhija_snage=(4, 5, 6, 7, 11, 12, 13, 1, 2, 3)
    trenutni_igrac=igrac1
    igra_gotova=False
    partija=1

    while(igra_gotova==False):
        def prikazi_karte_igraca(igrac):
            print(f"{igrac.ime}: ", end="")
            igrac.karte.sort(key=lambda x: x.zog).sort(key=lambda x: x.broj)
            for karta in igrac.karte:
                print(f"{karta.oznaka},",end=" ")
            print()

        def prikazi_karte_svih_igraca():
            for igrac in igraci:
                print(f"{igrac.ime}: ", end="")
                igrac.karte.sort(key=lambda x: (x.zog, x.broj))
                for karta in igrac.karte:
                    print(f"{karta.oznaka},",end=" ")
                print()

        def dohvati_10_nasumicnih_karti_iz_deka():
            karte=[]
            for i in range(10):
                nasumican_broj=random.randrange(0, len(dek))
                karte.append(dek[nasumican_broj])
                del(dek[nasumican_broj])
            return karte

        def zavrsi_krug(karte_ruke, zadnja):
            najjaca_karta=karte_ruke[0].karta
            bele=0
            for karta_ruke in karte_ruke:
                print(karta_ruke.karta, end="")
                if(karta_ruke.redoslijed!=4):
                    print("->", end="")
                if prva_karta_jaca(karta_ruke.karta, najjaca_karta):
                    najjaca_karta=karta_ruke.karta
                broj_karte=int(karta_ruke.karta[1:])
                if(broj_karte in (3, 2, 13, 12, 11)):
                    bele+=1
                elif(broj_karte==1):
                    bele+=3
            print()
            if zadnja==True:
                bele+=3
            for karta_ruke in karte_ruke:
                if najjaca_karta==karta_ruke.karta:
                    karta_ruke.igrac.tim.dodaj_bele(bele)
                    return karta_ruke.igrac

        def prva_karta_jaca(prva_karta, druga_karta):
            if(prva_karta[0]!=druga_karta[0]):
                return False
            prvi_broj=hijerarhija_snage.index(int(prva_karta[1:]))
            drugi_broj=hijerarhija_snage.index(int(druga_karta[1:]))
            if(drugi_broj>prvi_broj):
                return False
            return True

        def ispisi_moguce_karte(karte):
            for karta in karte:
                print(f"{karta.oznaka}",end=" ")
            print()

        def odredi_moguce_karte(prva_karta, karte):
            moguce_karte=[]
            for karta in karte:
                if(karta.oznaka[0]==prva_karta[0]):
                    moguce_karte.append(karta)
            if(len(moguce_karte)==0):
                moguce_karte=karte
            return moguce_karte

        def odaberi_nasumicnu_mogucu_kartu(moguce_karte):
            nasumican_broj=random.randrange(0, len(moguce_karte))
            karta=moguce_karte[nasumican_broj].oznaka
            print(f"Bacam {karta}")
            return karta
        
        def je_li_igrac_pratio_prvu_kartu(prva_karta, bacena_karta):
            if prva_karta[0]==bacena_karta[0]:
                return True
            return False

        def odredi_status_igraca_i_karti(karte_ruke):
            bacene_karte=[]
            for karta in karte_ruke:
                bacene_karte.append(karta.karta)
            prva_karta=bacene_karte[0]
            drugi_igrac_pratio=je_li_igrac_pratio_prvu_kartu(prva_karta, bacene_karte[1])
            treci_igrac_pratio=je_li_igrac_pratio_prvu_kartu(prva_karta, bacene_karte[2])
            cetvrti_igrac_pratio=je_li_igrac_pratio_prvu_kartu(prva_karta, bacene_karte[3])
            karte_ruke[0].igrac.obradi_informacije_nakon_ruke(bacene_karte, drugi_igrac_pratio, treci_igrac_pratio, cetvrti_igrac_pratio)
            karte_ruke[1].igrac.obradi_informacije_nakon_ruke(bacene_karte, treci_igrac_pratio, cetvrti_igrac_pratio, True)
            karte_ruke[2].igrac.obradi_informacije_nakon_ruke(bacene_karte,  cetvrti_igrac_pratio, True, drugi_igrac_pratio)
            karte_ruke[3].igrac.obradi_informacije_nakon_ruke(bacene_karte, True, drugi_igrac_pratio, treci_igrac_pratio)

        dek=dohvati_dek()
        for igrac in igraci:
            igrac.dodaj_karte(dohvati_10_nasumicnih_karti_iz_deka())
            igrac.ucitaj_postavke_partije()

        print(f"Zapocinjemo {partija}. partiju")

        for i in range(1,11):
            print(f"{partija}. partija! {i}. ruka!")
            zadnja=False
            prikazi_karte_svih_igraca()

            karte_ruke=[] # Oblik: Karta_ruke
            moguce_karte=[]
            redoslijed=1

            karta=trenutni_igrac.igraj_i_obradi(redoslijed)
            prva_karta=karta
            karte_ruke.append(Karta_ruke(redoslijed, trenutni_igrac, karta.oznaka))
            trenutni_igrac=trenutni_igrac.iduci_igrac
            redoslijed+=1
            time.sleep(0.1)

            karta=trenutni_igrac.igraj_i_obradi(redoslijed, prva_karta)
            druga_karta=karta
            karte_ruke.append(Karta_ruke(redoslijed, trenutni_igrac, karta.oznaka))
            trenutni_igrac=trenutni_igrac.iduci_igrac
            redoslijed+=1
            time.sleep(0.1)

            karta=trenutni_igrac.igraj_i_obradi(redoslijed, prva_karta, druga_karta)
            treca_karta=karta
            karte_ruke.append(Karta_ruke(redoslijed, trenutni_igrac, karta.oznaka))
            trenutni_igrac=trenutni_igrac.iduci_igrac
            redoslijed+=1
            time.sleep(0.1)

            karta=trenutni_igrac.igraj_i_obradi(redoslijed, prva_karta, druga_karta, treca_karta)
            karte_ruke.append(Karta_ruke(redoslijed, trenutni_igrac, karta.oznaka))
            trenutni_igrac=trenutni_igrac.iduci_igrac
            time.sleep(0.1)

            if(i==10):
                zadnja=True
            odredi_status_igraca_i_karti(karte_ruke)
            trenutni_igrac=zavrsi_krug(karte_ruke, zadnja)

            print(f"Najacu kartu u trenutnj ruci je imao {trenutni_igrac.ime}\n")
            time.sleep(1)
            karte_ruke.clear()

        tim1.restartiraj_bele()
        tim2.restartiraj_bele()

        print(f"Tim 1 ima {tim1.punti} punata")
        print(f"Tim 2 ima {tim2.punti} punata\n")

        if(tim1.punti>31 and tim2.punti>31):
            print("Imamo pobjednika. Oba tima su pobjednici!")
            igra_gotova=True
        elif(tim1.punti>31):
            print("Imamo pobjednika. Tim 1 su pobjednici!")
            igra_gotova=True
        elif(tim2.punti>31):
            print("Imamo pobjednika. Tim 2 su pobjednici!")
            igra_gotova=True
        else:
            print("Nemamo pobjednika. Ulazimo u iduću partiju!")
        time.sleep(3)
        partija+=1

    print("Hvala na igranju :)")
    igrac1.stop()
    igrac2.stop()
    igrac3.stop()
    igrac4.stop()
    quit_spade()

if __name__=='__main__':
    main()