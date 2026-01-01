# Poprawa `seed`

Podejście po zmianach jest **statystycznie poprawne** i jest standardową praktyką w symulacjach wielkoskalowych (Monte Carlo), szczególnie gdy praca jest rozproszona lub dzielona na batche.

**1. Rozwiązanie problemu "Restartu Maszyny"**

Gdybyś użył jednego globalnego seeda na początku skryptu (np. `np.random.seed(42)`):

- Przy każdym restarcie maszyny po 40k zapytań, generator liczb losowych (RNG) zaczynałby od tej samej sekwencji.

- To oznaczałoby, że zapytanie nr 1 i zapytanie nr 40,001 otrzymałyby identyczny zestaw liczb losowych (np. ten sam "traf" wybierający artykuł z 3. paginy zamiast 1.).

- To wprowadziłoby potężne, nienaturalne skorelowanie wyników wewnątrz batchy.

Użycie `seed(42 + global_query_id)` sprawia, że zapytanie nr 40,001 ma **unikalny punkt startowy**, zupełnie inny niż zapytanie nr 1, nawet jeśli maszyna została w międzyczasie zrestartowana.

**2. Statystyczna niezależność prób**

W Twoim eksperymencie każde zapytanie jest traktowane jako **niezależne zdarzenie symulacyjne**.

- W skali globalnej interesuje Cię rozkład wygenerowany z 850k zapytań.

- Resetowanie seeda per query nie zmienia faktu, że dla każdego zapytania losujesz artykuły z paginy zgodnie z zadaną funkcją gęstości prawdopodobieństwa (e^{−np.arange(1,n+1)}).

- Ponieważ każde zapytanie operuje na innym zestawie danych (różne wyniki z bazy wektorowej), "losowość" pochodząca z unikalnego seeda miesza się z naturalną zmiennością danych, dając rzetelny wynik końcowy.

**3. Powtarzalność (Reproducibility) – klucz do pracy naukowej**

Z punktu widzenia metodologii naukowej:

- Twój eksperyment jest teraz całkowicie zdeterminowany.

- Jeśli ktoś (lub Ty sam) zechce zweryfikować konkretne zapytanie nr 523,412, może to zrobić w izolacji i otrzyma bit po bicie ten sam wynik.

- Bez seedowania per query, odtworzenie wyniku pojedynczego zapytania wymagałoby uruchomienia całego eksperymentu od zera, co przy 255 mln operacji jest niewykonalne.