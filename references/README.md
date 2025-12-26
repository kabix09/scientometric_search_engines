# Dokumentacja merytoryczna i metodologiczna

Niniejszy folder zawiera opisy założeń teoretycznych, słowniki danych oraz rejestr kluczowych decyzji projektowych wpływających na przebieg symulacji.

## Rejestr poprawek logicznych (Changelog)

W trakcie rozwoju silnika `Scientometrics` zidentyfikowano i wyeliminowano błędy krytyczne, które mogły wpływać na statystyczną poprawność generowanych rozkładów cytowań. Szczegółowe opisy zmian znajdują się w poniższych dokumentach:

* **[Poprawka mechanizmu losowania (Index Mismatch)](changelog/page_draw.md)**
    * Opis błędu polegającego na przesunięciu indeksów stron podczas losowania bez powtórzeń.
    * Wyjaśnienie nowej logiki mapowania `active_indices`, gwarantującej unikalność artykułów w ramach jednego zapytania.

* **[Gwarancja odtwarzalności (Seed per Query)](changelog/seed.md)**
    * Dokumentacja zmiany strategii ustawiania ziarna losowości (seed).
    * Zastosowanie techniki *Seed Offset* ($42 + \text{global\_query\_id}$), zapewniającej unikalną, ale w pełni powtarzalną sekwencję losowań dla każdego zapytania, niezależnie od podziału na batche.

---

## Pozostałe materiały

* **Słownik Danych**: (Wkrótce) Opis kolumn zintegrowanego zbioru DBLP i punktacji ministerialnej.
* **Model Matematyczny**: (Wkrótce) Szczegółowe wyprowadzenie funkcji gęstości prawdopodobieństwa $e^{-x}$ zastosowanej w paginacji.