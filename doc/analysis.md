# Analýza projektu: Simulácia križovatky so semaformi

## 1. Základná charakteristika systému

Simulácia sa zameriava na riadenie dopravy na klasickej križovatke v tvare **+ (4 cesty)**. Zohľadňuje len **motorové vozidlá**, bez chodcov, cyklistov, priechodov atď. Uvažujeme bez otáčania vozidiel v križovatke.

Simulácia počíta so štyrmi smermi (vetvami): **Sever, Juh, Východ, Západ**. Všetky štyri smery majú **3** jazdné pruhy (nie všetky musia byť aktívne).

Simulátor funguje na princípe 2 typov správ, kedy používateľ najprv vytvorí križovatku, teda nastavenia jazdných pruhov pomocou checkoxov. 
Keď je vytvorená križovatka, následne nastavuje, kedy majú semafory zobrazovať signál Voľno.


## 2. Nastavenie pruhov
Používateľ môže pomocou checkboxov pre každý pruh zvoliť, akým smerom tento pruh pokračuje.
Je možné v jazdnom pruhu nevybrať žiaden povolený smer jazdy - v takomto prípade sa tento pruh nepoužíva. <br> 
→ Jazdný pruh, v ktorom je zvolený v checkboxe aspoň 1 smer budeme označovať ako **Aktívny pruh**.


Základným obmedzením je, že **2 susedné aktívne pruhy** sa nemôžu križovať. 

**Tabuľka zakázaných konfigurácií 2 susedných aktívnych pruhov:**
| Ľavý pruh | Pravý pruh |
|-----------|------------|
|↑|←|
|→|←|
|→|↑|


<img src="intersection_checkboxes_priklad_zakazany_cropped.png" alt="Zakázaná konfigurácia jazdných pruho" width="280">
<img src="intersection_checkboxes_priklad_zakazany2_cropped.png" alt="Zakázaná konfigurácia jazdných pruho" width="170">

<img src="intersection_checkboxes_priklad_povoleny_cropped.png" alt="Povolená konfigurácia jazdných pruhov" width="200">
<img src="intersection_checkboxes_priklad_povoleny2_cropped.png" alt="Povolená konfigurácia jazdných pruhov" width="170">

## 3.1. Semafory

Používajú sa len semafory so smerovými signálmi, čo znamená, že vozidlá nedávajú nikomu prednosť, križovanie voľných smerov je neprípustné.<br> 
→ Neuvažujeme s oranžovým signálom.<br> 
→ Semafor (a teda aj signál na ňom) sa vždy vzťahuje k jazdným jednotlivým aktívnym pruhom.


## 3.2. Nastavenie fáz semaforov
→ Používateľ nastavuje pre každý jazdný pruh práve jeden časový interval (fáza) v sekundách, kedy je na tomto semafore rozsvietená zelená → keď nesvieti zelená, svieti červená.<br> 
→ Križovatku riadi cyklus, ktorý sa opakuje.<br> 
→ Dĺžka cyklu je automaticky vypočítaná z najvačšej hodnoty konca signálu voľno v rámci celej križovatky.<br> 

<img src="fazy_priklad.png" alt="Povolená konfigurácia jazdných pruhov">


## 3.3. Zakázané fázové kombinácie
→ Fázy musia byť nastavené tak, aby počas simulácie nedošlo ku kolízií - križovaniu voľných smerov.<br> 
→ Počas celého cyklu nesmú byť nastavené nasledovné kombinácie na ktoromkoľvek z pruhov v celej križovatke:
| Voľno  <br> (v ktoromkoľvek z pruhov) | Obmedzenia       |
|---------|------------------|
|↑        | - náprotivná vetva nesmie mať voľno vľavo<br> - vetva po pravej strane nesmie mať voľno v žiadnom smere<br> - vetva po ľavej strane nesmie mať voľno vľavo alebo priamo|
|←        | - náprotivná vetva nesmie mať voľno vpravo alebo priamo<br> - vetva po pravej strane nesmie mať voľno priamo alebo vľavo<br> - vetva po ľavej strane nesmie mať voľno vľavo alebo priamo|
|→        | - náprotivná vetva nesmie mať voľno vľavo<br> - vetva po ľavej strane nesmie mať voľno priamo|


## 4.1. Komunikácia Frontend - Backend


Správa na vytvorenie križovatky (definícia pruhov)

Táto správa sa odošle po nakonfigurovaní pruhov pomocou checkboxov.

Štruktúra:
```json
{
  "phases": {
    "north": {
      "left":   { "start": 0,  "end": 5 },
      "straight": { "start": 6,  "end": 10 },
      "right":  { "start": 0,  "end": 10 }
    },
    "south": {
      "left":   { "start": 5,  "end": 10 }
    },
    "east": {
      "straight": { "start": 11, "end": 20 }
    },
    "west": {}
  }
}
```


## 4.2. Komunikácia Backend - Simulátor
Štruktúra:
```json
{
  "signals": {
    "north": [
      { "lane": 0, "direction": "left", "active": true },
      { "lane": 1, "direction": "straight", "active": false },
      { "lane": 2, "direction": "right", "active": true }
    ],
    "south": [],
    "east": [],
    "west": []
  }
}
```
```json
{
  "intersection": {
    "north": [ "left", "straight", "right" ],
    "south": [ "left", "straight" ],
    "east": [],
    "west": [ "straight", "right" ]
  }
}
```
