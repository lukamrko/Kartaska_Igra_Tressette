import spade
import time
import random
import asyncio
from entiteti import Karta
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade import quit_spade
from spade.message import Message


class Igrac(Agent):
    class PonasanjeKA(FSMBehaviour):
        async def on_start(self):
            print(f"Započinjem ponašanje igrača: {self.agent.jid}")

        async def on_end(self):
            print(f"Završavam ponašanje igrača.  {self.agent.jid}")

    class Cekaj(State):
        async def run(self):
            if self.agent.zastava_igraj:
                self.set_next_state("Odigraj")
            else:
                time.sleep(1)
                self.set_next_state("Cekaj")

    class Odigraj(State):
        async def run(self):
            print(f"{self.agent.jid} Igram potez.")
            self.agent.zastava_igraj=False
            self.odigraj()
            self.agent.zastava_obrađeno=True
            self.set_next_state("Cekaj")
        
        def odigraj(self):
            moguce_karte=[]
            if self.agent.redoslijed==1:
                moguce_karte=self.agent.karte
            else:
                moguce_karte=self.odredi_moguce_karte(self.agent.prva_karta, self.agent.karte)
            karta=self.odaberi_nasumicnu_mogucu_kartu(moguce_karte)
            if self.agent.redoslijed==1:
                karta=self.dohvati_kartu_za_prvog_igraca(moguce_karte)
            elif self.agent.redoslijed==2:
                karta=self.dohvati_kartu_za_drugog_igraca(moguce_karte, self.agent.prva_karta)
            elif self.agent.redoslijed==3:
                karta=self.dohvati_kartu_za_treceg_igraca(moguce_karte, self.agent.prva_karta, self.agent.druga_karta)
            else:
                karta=self.dohvati_kartu_za_cetvrtog_igraca(moguce_karte, self.agent.prva_karta, self.agent.druga_karta, self.agent.treca_karta)
            print(f"Bacam {karta.oznaka}")
            self.agent.baci_kartu(karta)
            self.agent.bacena_karta=karta
        
        def dohvati_kartu_za_prvog_igraca(self, moguce_karte):
            if(len(moguce_karte)==1):
                return moguce_karte[0]
            karta_odluke=self.postoji_zog_koji_imam_a_protivnici_ne(moguce_karte)
            if isinstance(karta_odluke, Karta):
                return karta_odluke
            karta_odluke=self.postoji_sigurni_as_za_prvog_igraca(moguce_karte)
            if isinstance(karta_odluke, Karta):
                return karta_odluke
            nasumicno=random.randint(1, 2)
            if nasumicno==1:
                karta_odluke=self.pokusaj_izvuci_liso_pa_jaku(moguce_karte)
            else:
                karta_odluke=self.pokusaj_izvuci_jaku_pa_liso(moguce_karte)
            if isinstance(karta_odluke, Karta):
                return karta_odluke
            karta_odluke=self.pokusaj_izvuci_plemstvo(moguce_karte)
            if isinstance(karta_odluke, Karta):
                return karta_odluke
            return self.odaberi_nasumicnu_mogucu_kartu(moguce_karte)
        
        def dohvati_kartu_za_drugog_igraca(self, moguce_karte, prva_karta):
            if(len(moguce_karte)==1):
                return moguce_karte[0]
            pratim_zog=self.pratim_li_zog(moguce_karte, prva_karta)
            if pratim_zog==False:
                return self.baci_nasumicno_kartu_najnize_vrijednosti(moguce_karte)
            mogu_dobiti=self.mogu_li_dobiti_kartu(moguce_karte, prva_karta)
            if mogu_dobiti==False:
                return self.baci_najnizu_mogucu_kartu(moguce_karte)
            karta_odluke=self.postoji_sigurni_as_za_drugog_igraca(moguce_karte, prva_karta)
            if isinstance(karta_odluke, Karta):
                return karta_odluke
            return self.baci_najnizu_dobitnu_kartu(moguce_karte, prva_karta)
        
        def dohvati_kartu_za_treceg_igraca(self, moguce_karte, prva_karta, druga_karta):
            if(len(moguce_karte)==1):
                return moguce_karte[0]
            pratim_zog=self.pratim_li_zog(moguce_karte, prva_karta)
            moj_tim_gubi=self.nova_karta_jaca(druga_karta, prva_karta)
            if pratim_zog==False and moj_tim_gubi==True:
                return self.baci_nasumicno_kartu_najnize_vrijednosti(moguce_karte)
            protivnik1_prati=self.agent.protivnik1_ima[prva_karta.oznaka[0]]
            if pratim_zog==False and moj_tim_gubi==False:
                if protivnik1_prati==False:
                    return self.baci_najvredniju_mogucu_kartu(moguce_karte)
                return self.baci_sigurniju_mogucu_karte(moguce_karte)
            #Odavde treci igrac prati zog
            karta_odluke=self.postoji_sigurni_as_za_treceg_igraca(moguce_karte, prva_karta, druga_karta)
            if isinstance(karta_odluke, Karta):
                return karta_odluke
            if moj_tim_gubi==True:
                mogu_dobiti=self.mogu_li_dobiti_kartu(moguce_karte, druga_karta)
                if mogu_dobiti==True:
                    return self.baci_najnizu_dobitnu_kartu(moguce_karte, druga_karta)
                return self.baci_najnizu_mogucu_kartu(moguce_karte)
            #Odavde moj tim zasad ne gubi
            if protivnik1_prati==False:
                return self.baci_najvredniju_mogucu_kartu(moguce_karte)
            if prva_karta.broj in (1, 2, 3, 11, 12, 13):
                return self.baci_najjacu_mogucu_kartu(moguce_karte)
            return self.baci_najnizu_mogucu_kartu(moguce_karte)
        
        def dohvati_kartu_za_cetvrtog_igraca(self, moguce_karte, prva_karta, druga_karta, treca_karta):
            if(len(moguce_karte)==1):
                return moguce_karte[0]
            pratim_zog=self.pratim_li_zog(moguce_karte, prva_karta)
            moj_tim_gubi=self.gubi_li_moj_tim(prva_karta, druga_karta, treca_karta)
            if pratim_zog==False and moj_tim_gubi==True:
                return self.baci_nasumicno_kartu_najnize_vrijednosti(moguce_karte)
            if pratim_zog==False and moj_tim_gubi==False:
                    return self.baci_najvredniju_mogucu_kartu(moguce_karte)
            #Odavde cetvrti igrac prati zog
            if moj_tim_gubi==True:
                karta_za_dobiti=prva_karta
                treca_karta_jaca=self.nova_karta_jaca(treca_karta, prva_karta)
                if treca_karta_jaca==True:
                    karta_za_dobiti=treca_karta
                mogu_dobiti=self.mogu_li_dobiti_kartu(moguce_karte, karta_za_dobiti)
                if mogu_dobiti==True:
                    return self.baci_najvredniju_dobitnu_kartu(moguce_karte, karta_za_dobiti)
                return self.baci_najnizu_mogucu_kartu(moguce_karte)
            return self.baci_najjacu_mogucu_kartu(moguce_karte)

        def postoji_sigurni_as_za_treceg_igraca(self, moguce_karte, prva_karta, druga_karta):
            if druga_karta.broj==1 or druga_karta.broj==2:
                return ""
            mojAs=""
            for moj_as in moguce_karte:
                if moj_as.broj==1:
                    mojAs=moj_as
                    break
            if isinstance(mojAs, str):
                return ""
            dvica_izasla_ili_ju_imam=self.odredi_stanje_broj(moj_as, 2, moguce_karte)
            trica_izasla_ili_ju_imam=self.odredi_stanje_broj(moj_as, 3, moguce_karte)
            if dvica_izasla_ili_ju_imam==True and trica_izasla_ili_ju_imam==True:
                return moj_as
            protivnik1_prati=self.agent.protivnik1_ima[prva_karta.oznaka[0]]
            if protivnik1_prati==False:
                return moj_as
            return ""

        def postoji_sigurni_as_za_drugog_igraca(self, moguce_karte, prva_karta):
            if prva_karta.broj==1 or prva_karta.broj==2:
                return ""
            mojAs=""
            for moj_as in moguce_karte:
                if moj_as.broj==1:
                    mojAs=moj_as
                    break
            if isinstance(mojAs, str):
                return ""
            dvica_izasla_ili_ju_imam=self.odredi_stanje_broj(moj_as, 2, moguce_karte)
            trica_izasla_ili_ju_imam=self.odredi_stanje_broj(moj_as, 3, moguce_karte)
            if dvica_izasla_ili_ju_imam==True and trica_izasla_ili_ju_imam==True:
                return moj_as
            protivnik1_prati=self.agent.protivnik1_ima[prva_karta.oznaka[0]]
            if protivnik1_prati==False:
                return moj_as
            return ""

        def postoji_sigurni_as_za_prvog_igraca(self, moguce_karte):
            mojiAsevi=[]
            for moj_as in moguce_karte:
                if moj_as.broj==1:
                    mojiAsevi.append(moj_as)
            if len(mojiAsevi)==0:
                return ""
            for moj_as in mojiAsevi:
                dvica_izasla_ili_ju_imam=self.odredi_stanje_broj(moj_as, 2, moguce_karte)
                trica_izasla_ili_ju_imam=self.odredi_stanje_broj(moj_as, 3, moguce_karte)
                if dvica_izasla_ili_ju_imam==True and trica_izasla_ili_ju_imam==True:
                    return moj_as
            return ""

        def odredi_stanje_broj(self, moj_as, broj, moguce_karte):
            for karta in moguce_karte:
                if moj_as.zog==karta.zog and karta.broj==broj:
                    return True
            for karta in self.agent.bacena_karte:
                if moj_as.zog==karta.zog and karta.broj==broj:
                    return True
            return False

        def pokusaj_izvuci_liso_pa_jaku(self, moguce_karte):
            liso=(4, 5, 6, 7)
            random.shuffle(moguce_karte)
            for karta in moguce_karte:
                if karta.broj in liso:
                    return karta
            jaka=(2, 3)
            for karta in moguce_karte:
                if karta.broj in jaka:
                    return karta
            return ""

        def pokusaj_izvuci_jaku_pa_liso(self, moguce_karte):
            jaka=(2, 3)
            for karta in moguce_karte:
                if karta.broj in jaka:
                    return karta
            liso=(4, 5, 6, 7)
            random.shuffle(moguce_karte)
            for karta in moguce_karte:
                if karta.broj in liso:
                    return karta
            return ""

        def pokusaj_izvuci_plemstvo(self, moguce_karte):
            plemstvo=(2, 3)
            for karta in moguce_karte:
                if karta.broj in plemstvo:
                    return karta
            return ""

        def postoji_zog_koji_imam_a_protivnici_ne(self, moguce_karte):
            moji_zogovi=[]
            for karta in moguce_karte:
                moji_zogovi.append(karta.oznaka[0].lower())
            moji_zogovi=list(dict.fromkeys(moji_zogovi))
            zogovi=['b', 'd', 'k', 's']
            for zog in zogovi:
                imam=False
                for karta in moguce_karte:
                    if karta.oznaka[0].lower()==zog:
                        imam=True
                        break
                if self.agent.protivnik1_ima[zog]==False and self.agent.protivnik2_ima[zog]==False and imam==True:
                    return self.dohvati_kartu_s_zogom(moguce_karte, zog)
            return ""

        def dohvati_kartu_s_zogom(self, moguce_karte, zog):
            for karta in moguce_karte:
                if karta.oznaka[0].lower()==zog:
                    return karta
            return ""
        
        def pratim_li_zog(self, moguce_karte, prva_karta):
            for karta in moguce_karte:
                if karta.oznaka[0]==prva_karta.oznaka[0]:
                    return True
            return False

        def baci_nasumicno_kartu_najnize_vrijednosti(self, moguce_karte):
            random.shuffle(moguce_karte)
            hijerarhija_vrijednosti=(4, 5, 6, 7, 11, 12, 13, 2, 3, 1)
            for vrijednost in hijerarhija_vrijednosti:
                for karta in moguce_karte:
                    if karta.broj==vrijednost:
                        return karta

        def mogu_li_dobiti_kartu(self, moguce_karte, prva_karta):
            for karta in moguce_karte:
                if self.nova_karta_jaca(karta, prva_karta):
                    return True
            return False

        def baci_najnizu_mogucu_kartu(self, moguce_karte):
            hijerarhija_vrijednosti=(4, 5, 6, 7, 11, 12, 13, 2, 3, 1)
            for vrijednost in hijerarhija_vrijednosti:
                for karta in moguce_karte:
                    if karta.broj==vrijednost:
                        return karta
        
        def baci_najnizu_dobitnu_kartu(self, moguce_karte, prva_karta):
            hijerarhija_snage=(4, 5, 6, 7, 11, 12, 13, 1, 2, 3)
            for vrijednost in hijerarhija_snage:
                for karta in moguce_karte:
                    if karta.broj==vrijednost:
                        if self.nova_karta_jaca(karta, prva_karta)==True:
                            return karta

        def baci_najjacu_mogucu_kartu(self, moguce_karte):
            hijerarhija_vrijednosti=(3, 2, 1, 13, 12, 11, 7, 6, 5, 4)
            for vrijednost in hijerarhija_vrijednosti:
                for karta in moguce_karte:
                    if karta.broj==vrijednost:
                        return karta
            
        def baci_najvredniju_mogucu_kartu(self, moguce_karte):
            hijerarhija_vrijednosti=(1, 11, 12, 13, 2, 3, 4, 5, 6, 7)
            for vrijednost in hijerarhija_vrijednosti:
                for karta in moguce_karte:
                    if karta.broj==vrijednost:
                        return karta

        def baci_sigurniju_mogucu_karte(self, moguce_karte):
            hijerarhija_vrijednosti=(11, 12, 13, 4, 5, 6, 7, 2, 3, 1)
            for vrijednost in hijerarhija_vrijednosti:
                for karta in moguce_karte:
                    if karta.broj==vrijednost:
                        return karta

        def gubi_li_moj_tim(self, prva_karta, druga_karta, treca_karta):
            druga_jaca_od_prve=self.nova_karta_jaca(druga_karta, prva_karta)
            if druga_jaca_od_prve==False:
                return True
            treca_jaca_od_druge=self.nova_karta_jaca(treca_karta, druga_karta)
            if treca_jaca_od_druge:
                return True
            return False
        
        def baci_najvredniju_dobitnu_kartu(self, moguce_karte, karta_za_dobiti):
            hijerarhija_snage=(1, 11, 12, 13, 2, 3, 4, 5, 6, 7)
            for vrijednost in hijerarhija_snage:
                for karta in moguce_karte:
                    if karta.broj==vrijednost:
                        if self.nova_karta_jaca(karta, karta_za_dobiti)==True:
                            return karta

        def nova_karta_jaca(self, nova_karta, stara_karta):
            hijerarhija_snage=(4, 5, 6, 7, 11, 12, 13, 1, 2, 3)
            if(nova_karta.oznaka[0]!=stara_karta.oznaka[0]):
                return False
            prvi_broj=hijerarhija_snage.index(nova_karta.broj)
            drugi_broj=hijerarhija_snage.index(stara_karta.broj)
            if(drugi_broj>prvi_broj):
                return False
            return True

        def odaberi_nasumicnu_mogucu_kartu(self, moguce_karte):
            nasumican_broj=random.randrange(0, len(moguce_karte))
            karta=moguce_karte[nasumican_broj]
            return karta
        
        def odredi_moguce_karte(self, prva_karta, karte):
            moguce_karte=[]
            for karta in karte:
                if(karta.zog==prva_karta.zog):
                    moguce_karte.append(karta)
            if(len(moguce_karte)==0):
                moguce_karte=karte
            return moguce_karte

    async def setup(self):
        print("Konačni automat kreće u akciju!")
        random.seed()
        self.zastava_igraj=False
        self.zastava_obrađeno=False

        fsm = self.PonasanjeKA()

        fsm.add_state(name="Cekaj", state=self.Cekaj(), initial=True)
        fsm.add_state(name="Odigraj", state=self.Odigraj())

        fsm.add_transition(source="Cekaj", dest="Odigraj")
        fsm.add_transition(source="Odigraj", dest="Cekaj")
        fsm.add_transition(source="Cekaj", dest="Cekaj")

        self.add_behaviour(fsm)

    def ucitaj_pocetne_postavke(self, tim, igrac):
        self.tim=tim
        self.karte=[]
        self.iduci_igrac=igrac

    def dodaj_karte(self, karte):
        self.karte=karte

    def baci_kartu(self, karta):
        self.karte.remove(karta)
    
    def ucitaj_postavke_partije(self):
        self.bacena_karte=[]
        self.protivnik1_ima={"b":True, "d":True, "k":True, "s":True}
        self.saveznik_ima={"b":True, "d":True, "k":True, "s":True}
        self.protivnik2_ima={"b":True, "d":True, "k":True, "s":True}
    
    def igraj_i_obradi(self, redoslijed, prva_karta="", druga_karta="", treca_karta=""):
        self.redoslijed=redoslijed
        self.bacena_karta=""
        self.prva_karta=prva_karta
        self.druga_karta=druga_karta
        self.treca_karta=treca_karta
        self.zastava_igraj=True
        while(self.zastava_obrađeno is False):
            time.sleep(1)
        self.zastava_obrađeno=False
        return self.bacena_karta
    
    def obradi_informacije_nakon_ruke(self, bacene_karte, protivnik1, saveznik, protivnik2):
        self.bacena_karte.extend(bacene_karte)
        prva_karta_oznaka=bacene_karte[0].oznaka[0] #dobije se samo oznaka
        if protivnik1 == False:
            self.protivnik1_ima[prva_karta_oznaka]=False
        if saveznik == False:
            self.saveznik_ima[prva_karta_oznaka]=False
        if protivnik2 == False:
            self.protivnik2_ima[prva_karta_oznaka]=False
