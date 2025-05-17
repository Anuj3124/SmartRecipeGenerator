# Smart Recipe Generator 🍽️

Smart Recipe Finder is a simple yet powerful web application that allows users to discover recipes using selected ingredients or natural language queries. It leverages [TheMealDB API](https://www.themealdb.com/api.php) to fetch recipe data and provides an intuitive interface for both checkbox-based and NLP-based search.

---

## Features

- ✅ Select multiple ingredients and find recipes using checkboxes
- 🧠 Search recipes using natural language input (e.g., "Show me dinner recipes with eggs and no milk")
- 🔍 Displays included ingredients in NLP mode
- 📸 Recipe images, ingredients, and cooking instructions
- ⚡ Responsive and clean UI
- 🛠️ Powered by Flask and JavaScript

---

## Installation & Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/smart-recipe-finder.git
   cd smart-recipe-finder
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install required dependencies:

   ```bash
   pip install -r req.txt
   ```

4. Run the Flask application:

   ```bash
   flask run
   ```

5. Open your browser and navigate to:

   ```
   http://127.0.0.1:5000/
   ```

---

## Project Structure

```
smart-recipe-finder/
├── app.py
├── index.html
├── nlp.html
├── requirements.txt
```

---

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **NLP**: spaCy for parsing natural language ingredient queries
- **API**: [TheMealDB](https://www.themealdb.com)

---

## License
Feel free to use and modify as needed.
