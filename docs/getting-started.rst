Pierwsze kroki
==============

Niniejsza instrukcja przeprowadzi Cię przez proces konfiguracji środowiska oraz uruchomienia pierwszej pełnej symulacji w systemie Scientometrics Simulation System (S3).

Wymagania wstępne
------------------

Przed rozpoczęciem upewnij się, że masz zainstalowane:
* Python 3.10 lub nowszy.
* Narzędzie ``make`` (opcjonalnie, do obsługi skrótów komend).
* Dostęp do internetu (w celu pobrania wag modeli Sentence Transformers).

Konfiguracja środowiska
-----------------------

1. **Klonowanie repozytorium**:
   Pobierz kod źródłowy na lokalną maszynę.

2. **Tworzenie środowiska wirtualnego**:
   Możesz użyć komendy z pliku Makefile, aby automatycznie stworzyć środowisko:

   .. code-block:: bash

      make create_environment
      source activate master_thesis

3. **Instalacja zależności**:
   Zainstaluj wymagane biblioteki:

   .. code-block:: bash

      make requirements

Przygotowanie danych
--------------------

System wymaga przejścia przez pełną ścieżkę ETL oraz inżynierii cech przed uruchomieniem eksperymentu:

1. **Budowa zbioru danych (ETL)**:
   Połącz surowe dane DBLP z punktacją ministerialną MEiN i wygeneruj rozkład empiryczny:

   .. code-block:: bash

      python src/data/make_dataset.py

2. **Generowanie Global Scalera (Statystyka)**:
   Przygotuj model normalizacji logarytmicznej cytowań (KRYTYCZNY ARTEFAKT):

   .. code-block:: bash

      python src/features/build_features.py

3. **Budowa bazy wektorowej (Semantyka)**:
   Wygeneruj embeddingi tytułów oraz zapytań i zaindeksuj je w ChromaDB:

   .. code-block:: bash

      python src/features/feature_builder.py

Uruchomienie symulacji
-----------------------

Po poprawnym przygotowaniu danych możesz uruchomić eksperyment masowy:

* **Przez skrypt Python**:
  Uruchamia domyślną partię 40 000 zapytań z automatycznym zapisem punktów kontrolnych (checkpointing):

  .. code-block:: bash

     python src/run_experiment.py

* **Przez notatnik Jupyter**:
  Otwórz ``notebooks/03_scientometrics_distribution_experiment_embedding.ipynb``, aby mieć większą kontrolę nad parametrami pojedynczych przebiegów.

Analiza wyników
---------------

Po zakończeniu symulacji, zagregowane dane znajdą się w pliku ``data/processed/global_distributions.csv``. Aby wygenerować wykresy porównawcze i raporty PDF, skorzystaj z notatnika:

.. code-block:: text

   notebooks/06_visualization_dashboard.ipynb