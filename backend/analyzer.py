import ollama
import json

class KIAnalyzer:
    def __init__(self, model="llama3.1:8b"):
        self.model = model

    def analyze_data(self, data):
        prompt = f"""
Analysiere die folgenden GA4 und SEO-Daten und erstelle eine strukturierte Analyse auf Deutsch.

Daten:
{json.dumps(data, indent=2)}

Erstelle:
1. Datenvalidierung & Tracking-Status
2. Technische Analyse (Top 5 Probleme)
3. Performance-Insights (5-8 Insights)
4. Massnahmenkatalog (10-15 Massnahmen mit Priorität, Aufwand, Effekt)

Sprache: Schweizer Hochdeutsch, professionell.
"""
        
        response = ollama.chat(model=self.model, messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content']

# Example usage
if __name__ == "__main__":
    analyzer = KIAnalyzer()
    data = {"traffic": "example"}
    analysis = analyzer.analyze_data(data)
    print(analysis)