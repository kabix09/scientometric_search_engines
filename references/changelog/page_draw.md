# Poprawa loswania artykułów z paginy

**1. Jak było wcześniej (Ukryte losowanie z powtórzeniami)**

W oryginalnym podejściu proces losowania *k* artykułów przebiegał w następujący sposób:

- **Paginacja:** Artykuły były sortowane według `score` i dzielone na strony o rozmiarze `N`.

- **Losowanie strony:** Program obliczał rozkład prawdopodobieństwa `e^{−x}` dla dostępnych stron.

- **Obsługa pustych stron:** Gdy z danej strony "wyciągnięto" już wszystkie artykuły (losowanie bez powtórzeń), program tworzył nową listę o nazwie `non_empty_pages`, która zawierała tylko te strony, na których coś jeszcze zostało.

- **Krytyczny błąd (Index Mismatch):** Program losował indeks z tej **nowej, skróconej listy**, a następnie próbował użyć tego indeksu, aby zmodyfikować **oryginalną listę** `pages`.

**Przykład błędu:** 
Jeśli było 10 stron i strona nr 1 stała się pusta, nowa lista miała 9 elementów. Jeśli wylosowałeś "ostatni" element z nowej listy (indeks 8), kod wykonywał operację na `pages[8]` (dziewiąta strona w oryginale), zamiast na faktycznie ostatniej dziesiątej stronie. Powodowało to "pudłowanie" w puste miejsca lub wielokrotne losowanie tych samych artykułów mimo założenia braku powtórzeń.

W starej wersji kodu mechanizm usuwania wylosowanego artykułu był wadliwy ze względu na błąd mapowania indeksów:

- **Intencja:** Po wylosowaniu artykułu kod próbował go usunąć linią `pages[selected_page_index] = [x for x in selected_page if x != selected_paper_index]`.

- **Błąd:** `selected_page_index` pochodził z przefiltrowanej listy `non_empty_pages`, a próba usunięcia następowała w oryginalnej liście `pages`.

- **Skutek:**

    - Artykuł był usuwany z niewłaściwej strony (o innym numerze) lub w ogóle nie był usuwany z listy, z której go pobrano.

    - W kolejnych iteracjach (aż do k) ten sam artykuł mógł zostać wylosowany ponownie, ponieważ system "myślał", że go usunął, ale fizycznie nadal znajdował się on na swojej pierwotnej stronie.

    - Z punktu widzenia statystyki, zamiast unikalnego zbioru k artykułów, otrzymywałeś zbiór, w którym te same publikacje mogły się dublować, co całkowicie wypaczało końcowe rozkłady cytowań.

**2. Jak jest teraz (Gwarantowana unikalność)**

W nowej architekturze silnika `VirtualAggregator` wyeliminowany został ten problem, wprowadzając mechanizm bezpiecznego usuwania:

- **Mapowanie Indeksów:** Dzięki `active_indices` system dokładnie wie, z której fizycznej strony (`abs_page_idx`) pobrał artykuł.

    - Jeśli puste są strony 2 i 5, lista aktywnych indeksów to `[0, 1, 3, 4, 6, 7, 8, 9]`.

- **Fizyczne usunięcie:** Użycie metody `pop()` lub `remove()` na konkretnej liście wewnątrz `working_pages` gwarantuje, że artykuł znika ze zbioru dostępnego dla kolejnych losowań w ramach tego samego zapytania.

- **Relatywne losowanie:** Funkcja distribution_function generuje rozkład dla aktualnej liczby dostępnych stron `e^{−x}`.

- **Mapowanie Relatywne → Absolutne:**

    1. Losujemy rel_idx (np. pozycja nr 2 w liście aktywnych indeksów).

    2. Sprawdzamy, jaki numer strony kryje się pod tą pozycją (`abs_page_idx = active_indices[rel_idx]`).

    3. Pobieramy artykuł z `working_pages[abs_page_idx]`.

- **Rezultat:** Z każdego zapytania otrzymywane jest teraz *k* **unikalnych artykułów**. Symuluje to realne zachowanie użytkownika, który nie cytuje tej samej pracy wielokrotnie w jednym tekście.

**3. Co to zmienia w eksperymencie?**

Poprzedni błąd sprawiał, że:

- **Rozkłady były "sztucznie zawężone":** Kilka bardzo wysoko ocenionych artykułów mogło zdominować wyniki, będąc losowanymi po kilka razy dla jednego zapytania.

- **Zafałszowanie Power Law:** Analiza rozkładu potęgowego na danych z powtórzeniami dawała błędne wyniki, bo "siła" topowych artykułów była nienaturalnie potęgowana przez błąd w kodzie, a nie przez realne parametry modelu.