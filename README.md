# Advanced Product Recommendation Engine

A Python-based AI-driven system designed to provide personalized product suggestions on an e-commerce platform. This project uses collaborative filtering via cosine similarity to recommend items based on user behavior and rating patterns.

## 🔍 Overview

This project focuses on the **Recommendation Generation Module**, the core engine responsible for analyzing user data and predicting relevant products.

## 📌 Features

- Collaborative Filtering using Cosine Similarity
- Formal Verification of similarity logic using Microsoft SLAM
- Modular and well-documented Python code
- Black-box and white-box testing with `pytest`
- Updated UML diagrams (Use Case, DFD, Sequence)

---

## 📁 Project Structure

```
recommendation.py     # Core logic for recommendation generation
data_processor_verify.c          # SLAM-verified cosine similarity logic in C
test_data_processor.py       # Pytest-based automated testing
README.md                    # This documentation
/diagrams/                   # Use Case, DFD, and Sequence Diagrams (PDF/PNG)
```

---

## ⚙️ Technologies Used

- **Language**: Python 3.11
- **Libraries**: pandas, scikit-learn
- **Testing**: pytest
- **Verification Tool**: SLAM (Microsoft Research)
- **Diagram Tools**: draw.io, Mermaid.js

---

## 🧠 Recommendation Logic

The recommendation engine works by:

1. Accepting a user-item rating matrix.
2. Normalizing the data.
3. Computing user-user similarity using cosine similarity.
4. Aggregating scores from top similar users.
5. Returning the top-N recommended items.

```python
result = engine.recommend(user_index=0, top_n=3)
```

---

## ✅ How to Run

### Step 1: Install Dependencies

```bash
pip install pandas scikit-learn pytest
```

### Step 2: Use the Recommendation Module

```python
import pandas as pd
from recommendation_module import RecommendationEngine

df = pd.DataFrame({
    'item1': [5, 3, 0],
    'item2': [4, 0, 0],
    'item3': [1, 1, 0],
    'item4': [0, 0, 5],
    'item5': [0, 0, 4]
})

engine = RecommendationEngine(df)
recommendations = engine.recommend(0, top_n=2)
print(recommendations)
```

### Step 3: Run Automated Tests

```bash
pytest test_recommendation.py
```

---

## 🔒 Formal Verification

The cosine similarity function was re-implemented in C and verified using **SLAM** to ensure:

- Result is always in the range [-1, 1]
- Division-by-zero is avoided

**Command Used**:
```bash
slam verify_similarity.c
```

**Result**: All assertions hold. No unsafe conditions found.

---

## 📊 Design Diagrams

Diagrams created using draw.io and Mermaid.js:

- Use Case Diagram
- DFD Level 1
- Sequence Diagram

See `/diagrams/` folder or render the Mermaid snippets in VS Code or the Mermaid Live Editor.

---

## 🧪 Sample Manual Test Case

| Test ID | Input (user_index, top_n) | Expected Output | Status |
|--------|-----------------------------|------------------|--------|
| TC01   | (0, 3)                       | 3 items returned | Pass   |
| TC02   | (2, 1)                       | 1 item returned  | Pass   |
| TC03   | Invalid user index          | Handled gracefully | Pass |

---

## 📈 Quality Attributes Evaluated

- **Performance**: Fast similarity computation using `scikit-learn`
- **Maintainability**: Modular class-based design
- **Reliability**: Verified using SLAM and passed multiple test cases

---

## 📚 References

- [Python 3.11](https://www.python.org)
- [Scikit-learn](https://scikit-learn.org)
- [Pandas](https://pandas.pydata.org)
- [pytest](https://docs.pytest.org)
- [SLAM (Microsoft)](https://www.microsoft.com/en-us/research/project/slam/)
- [draw.io](https://draw.io)
- [Mermaid.js](https://mermaid.js.org)

---

## 📄 License

This project is released under the MIT License.
