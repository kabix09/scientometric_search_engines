# Dokumentacja merytoryczna i metodologiczna

Niniejszy folder zawiera opisy założeń teoretycznych, słowniki danych oraz rejestr kluczowych decyzji projektowych wpływających na przebieg symulacji.

## Rejestr poprawek logicznych (Changelog)

W trakcie rozwoju silnika `Scientometrics` zidentyfikowano i wyeliminowano błędy krytyczne, które mogły wpływać na statystyczną poprawność generowanych rozkładów cytowań. Szczegółowe opisy zmian znajdują się w poniższych dokumentach:

* **[Poprawka mechanizmu losowania (Index Mismatch) - Page shifting](changelog/page_draw.md)**
    * Opis błędu polegającego na przesunięciu indeksów stron podczas losowania bez powtórzeń.
    * Wyjaśnienie nowej logiki mapowania `active_indices`, gwarantującej unikalność artykułów w ramach jednego zapytania.

* **[Gwarancja odtwarzalności (Seed per Query)](changelog/seed.md)**
    * Dokumentacja zmiany strategii ustawiania ziarna losowości (seed).
    * Zastosowanie techniki *Seed Offset* ($42 + \text{global\_query\_id}$), zapewniającej unikalną, ale w pełni powtarzalną sekwencję losowań dla każdego zapytania, niezależnie od podziału na batche.

* **[Similarity vs Distance](changelog/similarity_logic.md)**
    * ChromaDB domyślnie zwraca distances. W kodzie sortowanie `reverse=True` (malejąco) promowało artykuły z największym dystansem, czyli najmniej podobne. Poprawiono to, przekształcając dystans w miarę podobieństwa: `similarity=1−distance`.

* **[Normalizacja Globalna i Logarytmiczna](changelog/global_scaling.md)**:
    * Wyeliminowano problem "relatywizmu lokalnego", w którym lokalny lider popularności (np. 5 cytowań) był oceniany identycznie jak lider globalny (10 000 cytowań). 
    * Wprowadzono transformację logarytmiczną $\log(1+x)$ oraz **Global Scaler** wyuczony na pełnym zbiorze danych (300k+ rekordów). 
    * Zmiana ta zapewnia spójność wyników między batchami oraz poprawną reprezentację rozkładów potęgowych (Power Law), co jest fundamentem rzetelnych badań naukometrycznych.

* **[Korekta metodologii Power Law (Observations vs Frequencies))](changelog/statistical_validity.md)**:
    * Wyeliminowano błąd polegający na dopasowywaniu modelu do zagregowanych liczności (częstotliwości) zamiast do surowych wartości cytowań.
    * Skorygowano obliczenia współczynnika α oraz włączono procedurę estymacji progu $x_{min}$​, co umożliwiło poprawne wyznaczenie "ciężkiego ogona" rozkładu (heavy tail) zgodnie ze standardami statystyki matematycznej.
---

## Pozostałe materiały

* **Słownik Danych**: (Wkrótce) Opis kolumn zintegrowanego zbioru DBLP i punktacji ministerialnej.
* **Model Matematyczny**: (Wkrótce) Szczegółowe wyprowadzenie funkcji gęstości prawdopodobieństwa $e^{-x}$ zastosowanej w paginacji.