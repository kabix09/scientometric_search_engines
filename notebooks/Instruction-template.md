# Instruction

## Files

1. scientometrics_quotes

Generate files `../data/interim/articles_with_score_df.csv`
With db and after that check ...

Pliki wejściowe:
- `..//data//external//Wykaz_dyscyplin_do_czasopism_i_materiałów_konferencyjnych.xlsx` (czasopisma i konferencje)

- `../data/external/dblp-ref-10` (publikacje)

Pliki pośrednie:
- `../data/interim/articles_with_score_df.csv`


2. scientometrisc_search_engine

Generuje listy fraz z zapytaniami które dalje są używane do odpytywania silnika.

Były próby użycia bibliotek:
a) labguagetool
b) gramformer
Ale źle działały

Finalnie użyana jest sekcja `generate queries`


Pliki predefiniowane:
2.1 `../data/raw/{name}.csv` - (nouns, verbs, adjctives, participles, gerounds)

Pliki wyjsciowe:
2.2 `../data/queries_df` - plik z surowymi dzdaniami
2.3 `../data/queries_with_embedding.pkl` - 
`..//data//interim//titles_with_embedings.pk` - plik z juz zembedingownymi zapytaniami dla szybszegło ładowania do silnika



3. scientometrics_queries_generator

3.1 przygotowuje embedingi
3.2 ładuje embedingi do abzy wektorowej 
3.3 przygotowuje frazy zapytań
3.4

pliki wejściowe:
3.1 `../data/interim//articles_with_score_df.csv`

pliki pośrednie:
3.2 ../data/pre_chroma_data.pk

IDK CO Z SEKCJĄ ## Word collection initialization (????)*+
- dodaje ona listy słów do bazy wektorowej
- 

4. scientometrics_distribution_experiment

a) cientometrics_distribution_experiment
- nieużywane!!
b) cientometrics_distribution_experiment_muliprocessing
- nieużywane !!! NIE DZIAŁAŁY procesy !!!

c) scientometrics_distribution_experiment_embedding
- to ma wykres prezentujący funkcje spadku losowań - ważny fragment!!!

d) scientometrics_distribution_experiment_embedding-copy-1
- UŻYWANE W CAŁOŚCI - zawiera podizał na bache  w razie przerwań programu!!!


używa:
- `queries_with_embedding.pkl` - do załadowania plikó z wygenerowanymi pytaniami
CZYLI NIE UŻYWA ŁADOWANIA DO BAZY DANYCH

pliki pośrednie:
- `../data/settings_primary.pkl` - plik z zapisem wygenerwoanych 306 zestawów ustawień silnika

pliki zapisu:
- `../data/results/{settings_id}.results.csv`
- `../distributions.csv` - plik z zapisem 1. ustawień, 2. dystrybucji cytowań dla tego zestawu ustawień

5. scientometrics_distribution_summary

a) scientometrics_distribution_summary - sprawdzić czy neid aje outputów użyanych przez `-Copy1`

b) scientometrics_distribution_summary-Copy1

5.1 merguje pliki 

5.2 sprawdzanie czy mozna zastosowac powerlaw
- TO CHYBA W INNYM PLIKU - przejrzec pozostałe :/

5.2 generwoanie wykresów 
CND & PDF przedstawiających rozkąłdy cytowań na 
a) danych źródłowych DPLR
b) wygenerownych danych

