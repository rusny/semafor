1. Inicializácia simulácie
Frontend najprv pošle backendu definíciu križovatky: aké pruhy existujú, aké majú smery (messages typu intersection).

Backend uloží túto konfiguráciu: ktoré pruhy sú aktívne a ich smerovanie.

Následne Frontend pošle nastavenie fáz semaforov (phases) — intervaly pre zelenú pre každý pruh a smer.

Backend:

overí, či fázovanie nespôsobí zakázané kolízie (podľa tebou definovaných pravidiel).

vypočíta dĺžku celého cyklu (maximálny end čas zo všetkých fáz).

Backend potom odošle Frontendu potvrdenie a štartovací stav (signals).

2. Spustenie simulácie
Simulácia funguje v časových krokoch (napr. každú 1 sekundu).

Beží sa v nekonečnej slučke cyklu alebo po určitý počet cyklov (podľa nastavenia používateľa).

Každý časový krok:

Aktualizácia svetiel:

Backend na základe aktuálneho "sekundového času" (napr. t = 12s) určí, ktoré pruhy majú zelenú (active: true) a ktoré červenú (active: false).

Tento stav (signals) sa pošle Frontendu na vizualizáciu.

Pohyb áut:

Vozidlá na Frontende (alebo Backende, ak by ste to riešili serverovo) budú podľa aktívnych signálov:

Vozidlo v pruhu s active: true môže prejsť križovatkou (ak stojí na čele pruhu).

Vozidlá s active: false stoja.

Pri každej sekunde môžu niektoré autá "zmiznúť" (prejdu križovatkou) a nové sa môžu generovať na vstupe.

3. Generovanie vozidiel
Autá sa budú náhodne spawnovať v jednotlivých pruhov (pravdepodobnosť respawnu môže byť 5–10 % za sekundu na pruh, voliteľne nastavitelná).

Každé nové vozidlo dostane:

vetvu (north, south, east, west),

pruh,

smer jazdy (left, straight, right).

Podmienky:

Nové vozidlo sa spawnuje len v aktívnych pruhoch a len ak je tam miesto (napr. auto nie je hneď pred ním).

4. Cyklický priebeh
Cyklus simulácie sa opakuje podľa vypočítanej dĺžky (napr. cyklus má 30 sekúnd — po 30s sa simulácia resetne na t=0).

Vozidlá v simulácii sa spravajú konzistentne podľa fázy semaforov v rámci každého cyklu.

5. Zvládanie kolízií a pravidlá
Backend kontroluje pri každej zmene fázy, či nenastala nepovolená situácia (voľno v protismeroch, križovanie atď.).

Ak sa nájde chyba v nastavení fáz, simulácia sa nepovolí spustiť — chyba sa odošle Frontendu.

Praktický príklad pre lepšiu predstavu:
Čas 0s:

Severný pruh 0 (left) má zelenú → autá v tomto pruhu môžu ísť.

Východný pruh 1 (straight) má červenú → autá stoja.

Čas 5s:

Severný pruh 0 (left) končí zelenú, začne Severný pruh 1 (straight).

Čas 10s:

Severné smery končia zelenú, začne Východný pruh 1.

Čas 20s:

Cyklus končí a simulácia sa vráti na čas 0s.
