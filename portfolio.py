import pandas as pd
import chromadb
import uuid

class Portfolio:
    def __init__(self, file_path="/Users/juhianand/Documents/UIC/Spring/DeepLearning/Cold_Email_Project/app/resource/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=row["Techstack"],
                    metadatas={"links": row["Links"]},
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        """Return top 2 matching portfolio links for the extracted skills."""
        if not skills:
            return []
        try:
            results = self.collection.query(query_texts=skills, n_results=2)
            return results.get('metadatas', [])
        except Exception as e:
            print(f"Portfolio query error: {e}")
            return []
