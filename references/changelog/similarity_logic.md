# Korekta logiki podobieństwa semantycznego (Similarity vs Distance)

## Opis zjawiska przed poprawką

W oryginalnej wersji silnika wystąpił błąd logiczny polegający na błędnej interpretacji wartości zwracanych przez bazę wektorową ChromaDB. Baza ta, podobnie jak większość systemów wyszukiwania wektorowego, zwraca **dystans (odległość)** między wektorami, a nie bezpośredni współczynnik podobieństwa.

### Błąd w mapowaniu danych
W pliku `Experiment.py` (metoda `step`), dystans był mapowany bezpośrednio na pole o nazwie `similarity`:

```python
collection_dict = {
    'id': self.similar_articles['ids'][0],
    'similarity': self.similar_articles['distances'][0], # Tu przypisano dystans L2/Cosine
    # ...
}

```

Distances[0] (czyli odległość w przestrzeni wektorowej) był przypisywany do klucza 'similarity'. W ChromaDB:

- Distance = 0.0: Artykuł identyczny (najwyższe podobieństwo).
- Distance = 1.5+: Artykuł bardzo odległy (niskie podobieństwo).

### Błąd w obliczaniu rankingu i sortowaniu

W silniku `VirtualAggregator`, wartość ta była używana do obliczenia wyniku (`score`), a następnie sortowana malejąco:

```python
collection_dict['score'] = [
    self.pn[0] * collection_dict['similarity'][i] +  # Używasz dystansu jako mnożnika
    self.pn[1] * collection_dict['year_normalized'][i] +
    # ... reszta wag
]

sorted_collection = sorted(
    [
        {
            # ...
            'similarity': collection_dict['similarity'][i],
            'score': collection_dict['score'][i]
        }
        for i in range(len(collection_dict['id']))
    ],
    key=lambda x: x['score'],
    reverse=True  # <--- TUTAJ PROMUJESZ WYSOKIE WYNIKI
)
```

**Skutek**: Silnik systematycznie promował artykuły **najmniej podobne** do zapytania (o największym dystansie), spychając najbardziej trafne wyniki na odległe strony paginacji.

---

## Opis wprowadzonej poprawki

Wprowadzono transformację dystansu w miarę podobieństwa (similarity score) w skali 0-1, gdzie 1.0 oznacza identyczność, a 0.0 całkowity brak powiązania.

### Nowa logika transformacji

W pliku `simulation_engine.py` dodano operację odwrócenia dystansu:

```python
# Pobranie surowych dystansów z bazy
distances = np.array(collection_dict["similarity"])

# Konwersja na podobieństwo: 1.0 - dystans (z progiem bezpieczeństwa 0.0)
similarities = np.maximum(0, 1 - distances)

# Obliczanie score na podstawie podobieństwa, a nie dystansu
scores = (
    self.pn[0] * similarities +
    self.pn[1] * scaled_values[:, 0] + # year
    self.pn[2] * scaled_values[:, 2] + # citations
    self.pn[3] * scaled_values[:, 2]   # gov_score
)

```

### Wpływ na wyniki eksperymentu

Po wprowadzeniu poprawki:

1. **Trafność**: Na pierwszych stronach wyników () znajdują się artykuły o najwyższym stopniu dopasowania semantycznego do zapytania.
2. **Spójność**: Model poprawnie odzwierciedla zachowanie realnego użytkownika, który zazwyczaj w pierwszej kolejności analizuje wyniki najbardziej zbliżone tematycznie do wyszukiwanej frazy.
3. **Wiarygodność**: Wynikowa dystrybucja cytowań opiera się na rzeczywistej "sile" podobieństwa, co pozwala na rzetelną analizę rozkładów typu Power Law.
