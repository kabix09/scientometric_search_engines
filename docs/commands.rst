Komendy (Makefile)
==================

Główny plik ``Makefile`` w korzeniu projektu służy jako centralny punkt dostępu do najczęstszych zadań rozwojowych i operacyjnych.

Zarządzanie środowiskiem
------------------------

* **Tworzenie środowiska**: Tworzy nowe środowisko wirtualne (Conda lub Virtualenv) o nazwie zdefiniowanej w projekcie.
  .. code-block:: bash

     make create_environment

* **Instalacja zależności**: Instaluje wymagane biblioteki z pliku ``requirements.txt`` oraz aktualizuje podstawowe narzędzia (pip, setuptools).
  .. code-block:: bash

     make requirements

* **Test środowiska**: Sprawdza, czy interpreter Python i kluczowe zależności są poprawnie skonfigurowane.
  .. code-block:: bash

     make test_environment

Przetwarzanie danych
--------------------

* **Budowa zbioru danych**: Uruchamia proces ETL (skrypt ``make_dataset.py``), który łączy dane DBLP z punktacją MEiN.
  .. code-block:: bash

     make data

* **Synchronizacja z S3 (Upload)**: Wysyła lokalną zawartość katalogu ``data/`` do zdefiniowanego w Makefile bucketu AWS S3.
  .. code-block:: bash

     make sync_data_to_s3

* **Synchronizacja z S3 (Download)**: Pobiera dane z bucketu S3 do lokalnego katalogu ``data/``. Przydatne przy konfiguracji projektu na nowej maszynie.
  .. code-block:: bash

     make sync_data_from_s3

Jakość kodu i czyszczenie
-------------------------

* **Linting**: Sprawdza zgodność kodu w katalogu ``src/`` ze standardem PEP8 przy użyciu narzędzia ``flake8``.
  .. code-block:: bash

     make lint

* **Czyszczenie**: Usuwa wszystkie skompilowane pliki Pythona (``.pyc``, ``.pyo``) oraz katalogi ``__pycache__``.
  .. code-block:: bash

     make clean

Ręczne uruchamianie modułów
---------------------------

Niektóre zadania specyficzne dla eksperymentu Scientometrics wymagają bezpośredniego wywołania skryptów:

* **Generowanie konfiguracji**:
  ``python src/config/settings_generator.py``
* **Inżynieria cech i Scaler**:
  ``python src/features/build_features.py``
* **Budowa bazy wektorowej**:
  ``python src/features/feature_builder.py``
* **Uruchomienie pełnego eksperymentu**:
  ``python src/run_experiment.py``