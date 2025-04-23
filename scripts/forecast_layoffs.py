# federal_layoffs_dashboard.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# === Load and Tag AI Skills + Clean Occupation ===
df = pd.read_csv("data/dashboard_ai_tagged_renamed.csv.gz", compression='gzip')
df.columns = df.columns.str.strip().str.lower()

# Tag AI exposure
ai_keywords = ['machine learning', 'deep learning', 'tensorflow', 'nlp', 'ai', 'artificial intelligence', 'pytorch']
df['ai_impact_flag'] = df['skill'].str.lower().apply(lambda x: any(k in x for k in ai_keywords))

# Clean job title for similarity use
df['clean_job_title'] = df['occupation'].str.lower().str.strip().str.replace(' ', '_')

# Save cleaned version
output_path = "data/dashboard_ai_tagged_minified.csv.gz"
df.to_csv(output_path, index=False, compression='gzip')
print(f"✅ Saved AI-tagged file to: {output_path}")

# === Generate Skill Transferability Matrix ===
job_skills_df = df.groupby('occupation')['skill'].apply(lambda x: ' '.join(x)).reset_index()
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(job_skills_df['skill'])
similarity_matrix = cosine_similarity(tfidf_matrix)

similarity_df = pd.DataFrame(similarity_matrix, index=job_skills_df['occupation'], columns=job_skills_df['occupation'])
similarity_df.index.name = 'occupation'
similarity_df.to_csv("data/occupation_similarity_matrix.csv")
print("✅ Saved occupation similarity matrix.")
