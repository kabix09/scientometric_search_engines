Scientometrics Simulation System (S3) – Dokumentacja
=====================================================

System symulacji zachowań naukometrycznych oparty na wyszukiwaniu semantycznym, uwzględniający polskie parametry punktacji ministerialnej oraz analizę rozkładów potęgowych (Power Law).

.. toctree::
   :maxdepth: 2
   :caption: Spis treści:

   getting-started
   commands
   changelog

Workflow (Schemat przepływu danych)
-----------------------------------

System realizuje dwie równoległe ścieżki: empiryczną (Ground Truth) oraz symulacyjną, które spotykają się w module wizualizacji.

.. mermaid::

   graph TD
      A[Raw Data: DBLP + MEiN] -->|make_dataset.py| B[Interim Data]

      %% Ścieżka Empiryczna
      B --> P1[data/processed/dblp_distribution_citations.csv]

      %% Ścieżka Symulacyjna
      B -->|build_features.py| C[Global Scaler]
      B -->|feature_builder.py| D[ChromaDB & Embeddings]

      C --> E[simulation_engine.py]
      D --> E

      E -->|experiment.py| F[Experiment Orchestrator]
      F --> G[data/results/*/results.csv]
      G --> P2[data/processed/global_distributions.csv]

      P1 --> H[visualize.py]
      P2 --> H
      H --> I[Raporty PDF/CDF & Analiza Power Law]

Szczegółowy opis modułów (src/)
-------------------------------

1. src.data.make_dataset
^^^^^^^^^^^^^^^^^^^^^^^^
Moduł ETL odpowiedzialny za czyszczenie danych wejściowych.
* **Funkcja**: Łączy dane publikacyjne DBLP z oficjalnym wykazem punktacji MEiN/MNiSW.
* **Wyjście**: ``data/interim/articles_with_score_df.csv`` oraz empiryczny punkt odniesienia ``data/processed/dblp_distribution_citations.csv``.

2. src.features.build_features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Odpowiada za przygotowanie statystyczne danych.
* **Funkcja**: Logarytmizacja liczby cytowań oraz trenowanie globalnej normalizacji (Global Scaler).
* **Wyjście**: ``models/global_scaler.pkl``.

3. src.features.feature_builder
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Moduł semantyczny systemu.
* **Funkcja**: Generuje embeddingi zapytań i artykułów (Sentence Transformers) oraz zasila bazę wektorową ChromaDB.

4. src.models.simulation_engine
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Rdzeń symulacyjny (Virtual Aggregator).
* **Funkcja**: Implementuje zachowanie wyszukiwarki: ważony ranking (podobieństwo, cytowania, punktacja) oraz paginację wyników.

5. src.models.experiment
^^^^^^^^^^^^^^^^^^^^^^^^
Orkiestrator eksperymentów masowych.
* **Funkcja**: Obsługuje przetwarzanie wsadowe (batch) i generuje zagregowane rozkłady cytowań dla różnych konfiguracji wag.

6. src.visualization.visualize
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Moduł analityczno-porównawczy.
* **Funkcja**: Generuje wykresy PDF/CDF, estymuje parametry Power Law (alfa, xmin) i analizuje zjawisko heavy tail.

Notatniki Badawcze (Test-Driven Analysis)
-----------------------------------------

Analiza została podzielona na kroki weryfikacyjne w formie notebooków:

1. ``01_scientometrics_quotes.ipynb``: Walidacja merge'owania danych MEiN.
2. ``02_scientometrics_search_engine.ipynb``: Testy bazy wektorowej i embeddingów.
3. ``03_scientometrics_distribution_experiment.ipynb``: Smoke testy silnika symulacyjnego.
4. ``04_scientometrics_data_distribution.ipynb``: Analiza wstępna rozkładów.
5. ``05_scientometrics_statistical_aggregation.ipynb``: Agregacja wyników masowych.
6. ``06_visualization_dashboard.ipynb``: Finalna analiza porównawcza i dobór parametrów.