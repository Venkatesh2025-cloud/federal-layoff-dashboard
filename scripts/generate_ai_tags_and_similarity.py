import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv("data/dashboard_ai_tagged_renamed.csv.gz", compression='gzip')
df.columns = df.columns.str.strip().str.lower()

# AI skill tagging
ai_keywords = ['machine learning', 'deep learning', 'tensorflow', 'nlp', 'ai', 'artificial intelligence', 'pytorch']
df['ai_exposed'] = df['skill'].str.lower().apply(lambda x: int(any(k in x for k in ai_keywords)))

# Clean job title
df['clean_job_title'] = df['occupation_title'].str.lower().str.strip().str.replace(' ', '_')

# Save back
df.to_csv("data/dashboard_ai_tagged.csv", index=False)

# Skill transferability matrix
job_skills_df = df.groupby('occupation_title')['skill'].apply(lambda x: ' '.join(x)).reset_index()
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(job_skills_df['skill'])
similarity_matrix = cosine_similarity(tfidf_matrix)
similarity_df = pd.DataFrame(similarity_matrix, index=job_skills_df['occupation_title'], columns=job_skills_df['occupation_title'])
similarity_df.to_csv("data/occupation_similarity_matrix.csv")
