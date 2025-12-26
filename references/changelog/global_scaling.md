# Wdrożenie Globalnego Skalowania Cech (Global Scaling)

## Opis problemu (Skalowanie Lokalne)
Wcześniejsza wersja silnika używała `MinMaxScaler.fit_transform()` na poziomie pojedynczego zapytania. Powodowało to błąd relatywizmu:
* Artykuł z 5 cytowaniami w "słabym" zapytaniu otrzymywał wagę popularności 1.0.
* Artykuł z 10 000 cytowaniami w "silnym" zapytaniu otrzymywał taką samą wagę 1.0.
Uniemożliwiało to porównywanie wyników między różnymi batchami eksperymentu.

## Rozwiązanie: Globalny Scaler i Transformacja Logarytmiczna
Zaimplementowano podejście hybrydowe, które gwarantuje spójność wyników niezależnie od momentu uruchomienia programu:

1. **Pre-fitting**: Scaler jest "uczony" raz na całym zbiorze danych (300k+ rekordów). Obiekt jest utrwalony w pliku `models/global_scaler.pkl`.
2. **Transformacja Logarytmiczna**: Przed skalowaniem cytowania poddawane są funkcji $\ln(1+x)$. Pozwala to zachować czułość modelu zarówno dla prac niszowych (mało cytowań), jak i wybitnych (bardzo dużo cytowań).
3. **Consistency (Spójność)**: Wewnątrz `VirtualAggregator` używana jest wyłącznie metoda `.transform()`. Każdy artykuł o danej liczbie cytowań i roku wydania otrzyma identyczną wartość znormalizowaną, bez względu na to, w którym batchu zostanie przetworzony.

## Korzyści
* Pełna porównywalność wyników między uruchomieniami programu.
* Odporność na "pływanie" wyników przy przetwarzaniu wsadowym (batching).
* Zgodność z rozkładem Power Law typowym dla naukometrii.
