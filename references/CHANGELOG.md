# Dokumentacja merytoryczna i metodologiczna

Niniejszy folder zawiera opisy założeń teoretycznych, słowniki danych oraz rejestr kluczowych decyzji projektowych wpływających na przebieg symulacji w ramach silnika **Scientometrics Simulation System (S3)**.

---

## ⚖️ Rejestr poprawek logicznych (Changelog)

W trakcie rozwoju systemu zidentyfikowano i wyeliminowano szereg błędów krytycznych, które miały bezpośredni wpływ na statystyczną poprawność generowanych rozkładów, odtwarzalność eksperymentów oraz zgodność wyników z teorią rozkładów potęgowych.

### 1. Mechanizm losowania (Index Mismatch / Page Shifting)

**Plik szczegółowy:** [`changelog/page_draw.md`](changelog/page_draw.md)

* **Problem:** Pierwotna implementacja paginacji powodowała przesunięcia indeksów stron podczas losowania bez powtórzeń. Skutkowało to duplikacją artykułów w obrębie jednego zapytania, pomijaniem części rekordów i deformacją rozkładów cytowań.
* **Rozwiązanie:** Wprowadzono jawną logikę mapowania `active_indices`. Oddzielono mechanizm paginacji od rankingu, gwarantując unikalność dokumentów w ramach pojedynczego zapytania.
* **Efekt:** Statystyczna niezależność próbek i poprawna reprezentacja populacji dokumentów.

### 2. Gwarancja odtwarzalności (Seed per Query)

**Plik szczegółowy:** [`changelog/seed.md`](changelog/seed.md)

* **Problem:** Eksperymenty uruchamiane w batchach nie były replikowalne. Zmiana kolejności zapytań lub rozmiaru paczki wpływała na sekwencję losowań (globalny stan generatora RNG).
* **Rozwiązanie:** Zastosowano strategię **Seed Offset**. Każde zapytanie otrzymuje deterministyczny, unikalny seed obliczany według wzoru:


* **Efekt:** Pełna odtwarzalność eksperymentów niezależnie od sposobu ich procesowania (batching/streaming) oraz możliwość walidacji wyników metodą regresji statystycznej.

### 3. Logika podobieństwa (Similarity vs Distance)

**Plik szczegółowy:** [`changelog/similarity_logic.md`](changelog/similarity_logic.md)

* **Problem:** ChromaDB domyślnie zwraca dystans wektorowy (gdzie mniejsza wartość oznacza większe podobieństwo). Kod błędnie sortował wyniki malejąco (`reverse=True`), przez co system promował artykuły najmniej trafne semantycznie.
* **Rozwiązanie:** Wprowadzono jawną transformację dystansu w miarę podobieństwa:


* **Efekt:** Przywrócenie poprawnej hierarchii trafności w wyszukiwaniu semantycznym i spójność logiki rankingowej.

### 4. Normalizacja Globalna i Logarytmiczna

**Plik szczegółowy:** [`changelog/global_scaling.md`](changelog/global_scaling.md)

* **Problem:** "Relatywizm lokalny" – cytowania skalowane w obrębie małych paczek danych sprawiały, że lokalny lider (np. 5 cytowań) otrzymywał taką samą wagę jak lider globalny (10 000 cytowań). Uniemożliwiało to odtworzenie "ciężkiego ogona" rozkładu.
* **Rozwiązanie:** * Wprowadzono transformację logarytmiczną  dla liczby cytowań.
* Wytrenowano **Global Scaler** na pełnym zbiorze danych (300k+ rekordów DBLP), który stał się stałym artefaktem systemu (`models/global_scaler.pkl`).


* **Efekt:** Zachowanie globalnych proporcji popularności i poprawne odwzorowanie rozkładów potęgowych (Power Law).

### 5. Metodologia Power Law (Observations vs Frequencies)

**Plik szczegółowy:** [`changelog/statistical_validity.md`](changelog/statistical_validity.md)

* **Problem:** Model rozkładu potęgowego był błędnie dopasowywany do zagregowanych liczności (histogramów) zamiast do surowych wartości cytowań (raw observations).
* **Rozwiązanie:** * Skorygowano obliczenia współczynnika  z wykorzystaniem metody największej wiarygodności (MLE).
* Włączono procedurę estymacji progu  oraz testy dobroci dopasowania (Kolmogorov-Smirnov, log-likelihood ratio).


* **Efekt:** Statystycznie poprawna estymacja "ciężkiego ogona" zgodnie ze standardami literatury (Clauset, Shalizi, Newman).
