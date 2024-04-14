# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 10:53:11 2023

@author: augus
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import fcluster



f=open('dataset_article.csv',encoding='latin-1')
df=pd.read_csv(f)
articles=pd.DataFrame.to_numpy(df)


"""
Création de trois listes :
    Une liste (liste_title) de tous les titres d'articles qui ont des KeyWords en enlevant les mots "hate" et "crime(s)"
    Une liste (liste_keywords) de tous les KeyWords des articles en enlevant les mots "hate" et "crime(s)"
    Une liste (liste_total) contenant la concaténation des tites et Keywords en enlevant les mots "hate" et "crime(s)"
"""

liste_title = []
liste_keywords = []
liste_total = []

for article in articles:
    Title = article[1] 
    Keywords = article[6]
    LKeywords = [] #liste des keywords de l'article
    LTitle = [] #liste des mots du titre de l'article
    if isinstance(Keywords,str) and isinstance(Title,str): #on ne garde que les articles contenant un titre et des KeyWords
        LKeywords = re.sub("[^\w]", " ",  Keywords).split() #on ne garde que les mots et on les passent en minuscule
        LKeywords = [str.lower() for str in LKeywords]
        LTitle = re.sub("[^\w]", " ",  Title).split()
        LTitle = [str.lower() for str in LTitle]
        Title = ''
        for word in LTitle: #on enlève les mots hate et crime(s) et on reconsitue les titres et KeyWords
            if word!='hate' and word[0:5]!='crime': 
                Title += word + ' '
        Keywords = ''
        for word in LKeywords:
            if word!='hate' and word[0:5]!='crime':
                Keywords += word + ' '
        liste_title.append(Title)
        liste_keywords.append(Keywords)
        liste_total.append(Title + Keywords)



"""
On effectue un TF-IDF + cosine similarity sur les titres, keywords ou sur le total
Le but est de créer:
    Un dendogramme dont la hauteur est la cosine similarity
    Un dictionnaire contenant les noeuds (les articles) avec le titre et les keywords)
    Un dictionnaire contenant les arêtes si la similarité entre deux articles est "suffisamment" grandes

Les dictionnaires seront utiles pour réaliser des méthodes de clustering plus tard (en les transformant en csv)
"""

dico_nodes = {'Id' : [], 'label' : [], 'description' : []}
dico_edges = {'Source' : [], 'Target' : [], 'Weight' : []} #les noms seront utiles pour l'utilisation d'autres outils


vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = vectorizer.fit_transform(liste_total) #on entraîne sur tous les articles

N = 2000
similarity_matrix = np.zeros((N, N)) #matrice de similarité entre les phrases

count = 0
for i in range(0, N):
    for j in range (i,N):
        count+=1
        if count%1000==0:
            print(str(100*count/N**2)+'%')
        vec1 = tfidf_matrix[i]
        vec2 = tfidf_matrix[j]
        similarity_matrix[i][j] = cosine_similarity(vec1,vec2)[0][0]
        similarity_matrix[j][i] = cosine_similarity(vec1,vec2)[0][0]


#création du dendogramme
linkage_matrix = linkage(similarity_matrix, method='average')
dendrogram(linkage_matrix, labels=liste_title, orientation='left')


#création des deux dictionnaires 
for i in range(0, N):
    dico_nodes['Id'].append(i)
    dico_nodes['label'].append(liste_title[i])
    dico_nodes['description'].append(liste_keywords[i])

for i in range(0,N):
    for j in range (i+1,N):
        similarity = similarity_matrix[i][j]
        if similarity > 0.1: #choix du seuil qui est expliqué dans le rapport
            dico_edges['Source'].append(i)
            dico_edges['Target'].append(j)
            dico_edges['Weight'].append(similarity)


#On conserve les résultats dans un csv
np.savetxt("similarity_matrix.csv", similarity_matrix, delimiter=',')

df1 = pd.DataFrame(dico_nodes)
df2 = pd.DataFrame(dico_edges)

df1.to_csv('data_nodes.csv', index=False)
df2.to_csv('data_edges.csv', index=False)

#affichage des cluster obtenus par average_linkage

plt.xlabel('Similarity') 
plt.show() #affichage du dendogramme

k = 10 #on choisit k proche du nombre d'ethnicité choisie
clusters = fcluster(linkage_matrix, k, criterion='maxclust')

cluster_dict = {}
for i, cluster in enumerate(clusters):
    if cluster not in cluster_dict:
        cluster_dict[cluster] = []
    cluster_dict[cluster].append(i)


for cluster, phrases_indices in cluster_dict.items():
    print("Cluster", cluster, ":")
    for i in phrases_indices:
        print(liste_title[i])