Instrukcja projektu Scientometrics
===================================

Spis plików i zależności
-------------------------

.. list-table::
   :header-rows: 1

   * - Skrypt / Moduł
     - Opis
   * - ``scientometrics_quotes``
     - Przetwarza dane wejściowe, łączy dane o publikacjach i czasopismach
   * - ``scientometrisc_search_engine``
     - Generuje zapytania (frazy) do silnika semantycznego
   * - ``scientometrics_queries_generator``
     - Generuje embeddingi oraz przygotowuje dane dla bazy wektorowej
   * - ``scientometrics_distribution_experiment-*``
     - Przeprowadza eksperymenty z dystrybucją cytowań
   * - ``scientometrics_distribution_summary``
     - Agreguje wyniki i generuje wykresy końcowe

Workflow (schemat przepływu danych)
-----------------------------------

.. mermaid::

   graph TD

   A[Input Files] --> B[scientometrics_quotes]
   B --> B1[articles_with_score_df.csv]

   B1 --> C[scientometrisc_search_engine]
   C --> C1[queries_df, queries_with_embedding.pkl, titles_with_embeddings.pk]

   C1 --> D[scientometrics_queries_generator]
   D --> D1[pre_chroma_data.pk]

   D1 --> E[scientometrics_distribution_experiment_embedding-copy-1]
   E --> E1[settings_primary.pkl]
   E --> E2[results/<settings_id>/results.csv, distributions.csv]

   E2 --> F[scientometrics_distribution_summary-Copy1]
   F --> G[Wykresy i analizy końcowe]

Szczegółowy opis modułów
-------------------------

scientometrics_quotes
^^^^^^^^^^^^^^^^^^^^^^

**Opis:**  
Łączy dane z publikacji (``dblp-ref-10``) i listy dyscyplin (``Wykaz_dyscyplin_do_czasopism_i_materiałów_konferencyjnych.xlsx``).  
Tworzy dataframe z artykułami oraz ich punktacją.

**Pliki wejściowe:**

- ``../data/external/Wykaz_dyscyplin_do_czasopism_i_materiałów_konferencyjnych.xlsx``
- ``../data/external/dblp-ref-10``

**Pliki wyjściowe (pośrednie):**

- ``../data/interim/articles_with_score_df.csv``

scientometrisc_search_engine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Opis:**  
Generuje frazy zapytań do wyszukiwania naukowego.  
Próbowano użyć bibliotek: ``languagetool``, ``gramformer`` (nieskuteczne).  
Ostatecznie użyto własnej sekcji ``generate queries``.

**Pliki wejściowe:**

- ``../data/raw/{name}.csv`` — listy części mowy (rzeczowniki, czasowniki, itd.)

**Pliki wyjściowe:**

- ``../data/queries_df``
- ``../data/queries_with_embedding.pkl``
- ``../data/interim/titles_with_embeddings.pk``

scientometrics_queries_generator
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Opis:**  
Moduł ten:

- przygotowuje embeddingi  
- ładuje dane do bazy wektorowej  
- przetwarza zapytania  

**Pliki wejściowe:**

- ``../data/interim/articles_with_score_df.csv``

**Pliki pośrednie:**

- ``../data/pre_chroma_data.pk``

.. note::

   Sekcja "Word collection initialization" dodaje listy słów do bazy wektorowej — wymaga doprecyzowania.

scientometrics_distribution_experiment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Uwaga:**  
Większość wersji tego pliku jest nieużywana lub nieskuteczna.

**Używana wersja:** ``scientometrics_distribution_experiment_embedding-copy-1``

**Opis:**  

- Przeprowadza eksperymenty z zapytaniami  
- Obsługuje przetwarzanie wsadowe (batch) na wypadek przerwań  
- Nie korzysta z bazy wektorowej (embeddingi są ładowane z pliku)  

**Pliki wejściowe:**

- ``../data/queries_with_embedding.pkl``

**Pliki pośrednie:**

- ``../data/settings_primary.pkl``

**Pliki wynikowe:**

- ``../data/results/{settings_id}.results.csv``
- ``../distributions.csv``

scientometrics_distribution_experiment_merge
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Opis:**

- Scala pliki wynikowe z eksperymentu przeprowadzonego sekwencjami na kilku maszynach

**Pliki wejściowe:**

- ``../data/results_{abc}/{config_id}/results.csv``
- ``../data/results_{xyz}/{config_id}/results.csv``

**Pliki wynikowe:**

- ``../data/merged_results/{config_id}/results.csv``

scientometrics_distribution_summary
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Opis funkcjonalny:**

1. Scalanie wyników eksperymentów  
2. Analiza rozkładów cytowań (powerlaw — sprawdzić, gdzie dokładnie)  
3. Generowanie wykresów:

   - CND  
   - PDF (rozkłady cytowań)

**Źródła danych:**

- Dane źródłowe (DPLR)  
- Wygenerowane eksperymentalnie
