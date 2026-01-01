# Korekta metodologii estymacji i wizualizacji rozkładu potęgowego (Power Law)

## Opis problemu przed poprawką

W pierwotnej wersji analizy statystycznej wystąpił błąd metodologiczny dotyczący sposobu przekazywania danych do estymatora biblioteki `powerlaw` oraz doboru metody wizualizacji dystrybuanty. Dane wejściowe były podawane w formie zagregowanej, co uniemożliwiało rzetelną weryfikację właściwości "ogona" rozkładu.

### Błąd wejścia danych (Frequencies)

Do funkcji `powerlaw.Fit()` przekazywana była lista wartości ze słownika (liczebności), np. `sorted_values = [66117, 33132, 21832, ...]`.
**Skutek:** Biblioteka interpretowała te liczby jako surowe wartości cytowań dla pojedynczych artykułów, zamiast jako liczbę wystąpień danej wartości. Prowadziło to do błędnego obliczenia parametrów statystycznych.

### Niewłaściwa wizualizacja skumulowana

Pierwotne wykresy prezentowały standardową dystrybuantę (CDF), która w skali liniowej przybiera postać charakterystycznego "łuku" dążącego do wartości 1.
**Problem:** W skali logarytmicznej (niezbędnej do analizy Power Law) standardowy CDF staje się niemal płaski przy większych wartościach cytowań, maskując zachowanie "ciężkiego ogona" (heavy tail) i uniemożliwiając wizualną weryfikację zgodności z modelem potęgowym.

---

## Opis wprowadzonej poprawki

Wprowadzono mechanizm rekonstrukcji wektora obserwacji oraz zmieniono strategię wizualizacji danych skumulowanych na standard naukowy stosowany w fizyce statystycznej i naukometrii.

### 1. Rekonstrukcja wektora obserwacji

Zamiast podawać liczności, silnik wizualizacji przekształca zagregowany słownik `{liczba_cytowań: częstotliwość}` z powrotem w płaską listę obserwacji (np. zapis `{22: 3}` jest rozwijany do `[22, 22, 22]`). Dzięki temu algorytmy Maximum Likelihood Estimation (MLE) pracują na rzeczywistej populacji losowań.

### 2. Estymacja progu 

Włączono procedurę automatycznego poszukiwania optymalnej wartości . Algorytm iteracyjnie szuka punktu, poniżej którego dane przestają pasować do modelu potęgowego (tzw. "głowa rozkładu"). Pozwala to na obiektywne oddzielenie szumu statystycznego od właściwego rozkładu potęgowego.

### 3. Zastosowanie CCDF (Complementary Cumulative Distribution Function)

Wizualizacja skumulowana została zmieniona z CDF na **CCDF**.

* **Logika:** Zamiast sumować prawdopodobieństwa od zera, CCDF mierzy prawdopodobieństwo, że zmienna przyjmie wartość większą lub równą .
* **Prezentacja:** W skali log-log, CCDF dla rozkładu potęgowego przyjmuje postać **linii prostej opadającej w dół**. Jest to najsilniejszy wizualny dowód na istnienie prawa potęgowego w danych (nachylenie tej prostej wynosi ).
