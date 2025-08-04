# Master Thesis: Citation Distribution in Scientometric Search Engines

## Cel projektu

Celem pracy magisterskiej było przeprowadzenie eksperymentu symulującego działanie wyszukiwarki naukowej – podobnej do Google Scholar – umożliwiającej rankingowanie wyników wyszukiwania na podstawie różnych wag i metryk, takich jak:
- liczba cytowań,
- data publikacji,
- punktacja naukowa (np. MNiSW).

W ramach eksperymentu skonstruowano **sztuczny agregator prac naukowych** z mechanizmem paginacji oraz różnymi strategiami sortowania wyników.

---

## Opis projektu

System składa się z pięciu głównych komponentów:

1. **Przygotowanie danych źródłowych**: integracja informacji o czasopismach, konferencjach i publikacjach.
2. **Generacja zapytań**: tworzenie zapytań tekstowych z wykorzystaniem słowników części mowy.
3. **Embeddingi i baza wektorowa**: generacja reprezentacji semantycznych zapytań oraz artykułów.
4. **Silnik wyszukujący**: rankingowanie wyników według wybranych parametrów.
5. **Eksperymenty i analiza**: ocena wpływu wybranych strategii na rozkład cytowań wyników.

Eksperyment miał na celu sprawdzić, jak różne algorytmy rankingowe wpływają na widoczność artykułów o różnej liczbie cytowań.

---

## Przebieg eksperymentu

1. **Wczytanie danych**
   - `dblp-ref-10` (zbiory publikacji)
   - Lista czasopism i punktów naukowych

2. **Generacja zapytań**
   - Na podstawie list słów (rzeczowniki, czasowniki itd.)
   - Embeddingi zapytań przygotowane za pomocą Sentence Transformers

3. **Symulacja wyszukiwań**
   - Dla każdego zapytania: wyszukiwanie podobnych artykułów
   - Paginacja wyników (np. top 10, top 20)
   - Różne strategie sortowania

4. **Eksperyment dystrybucji**
   - Zapisywanie wyników (liczby cytowań, pozycji, wag sortowania)
   - Analiza rozkładów cytowań (czy wyniki promują prace cytowane?)

5. **Podsumowanie i wizualizacja**
   - Porównanie rozkładów wyników (PDF, CND)
   - Próba dopasowania do rozkładu potęgowego (power law)

---

## Struktura projektu

```
master_thesis
    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io

```

---

## Dokumentacja

Omówienie notatników python znajduje się [tutaj](./docs/Instruction.md)

---

## Wymagania

Aby zainstalować środowisko, uruchom:

```bash
pip install -r requirements.txt
```

---

## Źródło szablonu

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

---

© 2025 Autor pracy magisterskiej. Wszelkie prawa zastrzeżone.