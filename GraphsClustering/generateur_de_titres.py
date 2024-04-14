import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import spacy
import networkx as nx
from random import choices
nlp = spacy.load("en_core_web_sm")
f=open('dataset_article.csv',encoding='latin-1')
df=pd.read_csv(f)
articles=pd.DataFrame.to_numpy(df)
compteur=0

## liste de mots catégorisés autrement pour éviter des incohérences dans les phrases
setOther={'in','of','to','man','a','for','on','the','s','with','after','anti','at',"and",'was',"not","is",'who'}

## 3 graphes correspondant à 3 profondeurs différentes
G=nx.DiGraph() #G lie les mots qui se suivent directement
G2=nx.DiGraph() #G2 lie les mots qui ont un seul mot entre eux
G3=nx.DiGraph() #G3 lie les mots qui ont deux mots entre eux
G.add_nodes_from(["START","END"])
G2.add_nodes_from(["START","END"])
G3.add_nodes_from(["START","END"])
LTitle=None
dicTitre={'oui'}
n=0
init=False
nbdoublons=0

## construction des graphes G1, G2 et G3
for article in articles:
    datap=[]
    if article[1] not in dicTitre:
        dicTitre.add(article[1])
        Title=article[1]
        KeyWords=article[6]
        ##parsing et passage en caractères minuscules
        if init:
            if isinstance(Title,str):
                LTitle = re.sub("[^\w]", " ",  Title).split()
                LTitle=[str.lower() for str in LTitle]
            else :
                LTitle=None
        init=True
        if LTitle!=None:
            word="START"
            n+=1
            Lword=["START"]
            word=''
            ## parsing du titre
            for l in Title:
                if l!=' ':
                    word+=l
                else:
                    if word in setOther: #on lie les mots de l'ensemble setOther au mot d'avant
                        Lword[-1]+=" "+word
                    else:
                        Lword.append(word)
                    word=''
            Lword.append(word)
            Lword.append('END')
            ## ajout des noeuds aux graphes G1,G2,G3
            G.add_nodes_from(Lword[1:len(Lword)-1])
            G2.add_nodes_from(Lword[1:len(Lword)-1])
            G3.add_nodes_from(Lword[1:len(Lword)-1])
            ## ajout des arêtes aux graphes G1,G2,G3
            for i in range (0,len(Lword)-1):
                if word != "START" and word!="END":
                    if Lword[i+1] in G.neighbors(Lword[i]):
                        G[Lword[i]][Lword[i+1]]["weight"]+=1
                    else:
                        G.add_weighted_edges_from([(Lword[i],Lword[i+1],1)])
                if i>=1:
                    if Lword[i+1] in G2.neighbors(Lword[i-1]):
                        G2[Lword[i-1]][Lword[i+1]]["weight"]+=1
                    else:
                        G2.add_weighted_edges_from([(Lword[i-1],Lword[i+1],1)])
                if i>=2:

                    if Lword[i+1] in G3.neighbors(Lword[i-2]):

                        G3[Lword[i-2]][Lword[i+1]]["weight"]+=1

                    else:
                        G3.add_weighted_edges_from([(Lword[i-2],Lword[i+1],1)])

    else:
        nbdoublons+=1

## On génère 100 titres automatiquement, et on réalisera ensuite une sélection
for i in range(0,100):
    wii=""
    wi=""
    w="START"
    max=30
    sentence=""
    count=0
    PROBS=[]
    while count<max and w!="END":
        ## cas général
        if wi!="" and wii!="":

            ## à partir des graphes G1, G2 et G3, on sélectionne les potentiels prochains mots et on leur associe une probabilité liée à leur probabilité dans chacun des graphes G1, G2 et G3
            edgesii={e[1]:e[2]['weight'] for e in G3.edges(wii,data=True) if e[2]['weight']>=1}
            edgesi={e[1]:e[2]['weight'] for e in G2.edges(wi,data=True) if e[2]['weight']>=1}
            edges=[[e[1],e[2]['weight']**2+edgesi[e[1]]**2+edgesii[e[1]]**2] for e in G.edges(w,data=True) if e[2]['weight']>=2 and e[1] in edgesi and e[1] in edgesii]+[[e[1],e[2]['weight']**2+edgesi[e[1]]**2] for e in G.edges(w,data=True) if e[2]['weight']>=2 and e[1] in edgesi and e[1] not in edgesii]+[[e[1],e[2]['weight']**2+edgesii[e[1]]**2] for e in G.edges(w,data=True) if e[2]['weight']>=2 and e[1] not in edgesi and e[1] in edgesii]+[[e[1],e[2]['weight']**2] for e in G.edges(w,data=True) if e[2]['weight']>=2 and e[1] not in edgesi and e[1] not in edgesii]
            if edges==[]:
                edges=[[e[1],e[2]['weight']] for e in G.edges(w,data=True) if e[1] in edgesi]
        ##cas du 2ème mot
        elif wi!="":
            edgesi={e[1]:e[2]['weight'] for e in G2.edges(wi,data=True) if e[2]['weight']>=1}
            edges=[[e[1],e[2]['weight']**2] for e in G.edges(w,data=True) if e[2]['weight']>=2 and e[1] in edgesi]
            if edges==[]:
                edges=[[e[1],e[2]['weight']] for e in G.edges(w,data=True) if e[1] in edgesi]
        ##cas du 1er mot
        else:
            edges=[[e[1],e[2]['weight']] for e in G.edges(w,data=True) if e[2]['weight']>=2]
        total=0
        wii=wi
        wi=w
        for e in edges:
            total+=e[1]
        probs=[e[1]/total for e in edges]
        c=choices([i for i in range(0,len(edges))],probs)[0]
        w=edges[c][0]
        PROBS.append(probs[c])

        ##suite au constat que les titres étaient souvent trop courts, on refait un tirage au sort si on tombe sur END prématurément
        while w=="END" and len(sentence)<=50 and len(edges)>1:
            c=choices([i for i in range(0,len(edges))],probs)[0]
            w=edges[c][0]
        if w!="END":
            sentence+=w+" "
        count+=1

    ## on sélectionne les titres d'une longueur cohérente et qui n'existent pas déjà
    if len(sentence)>=50 and len(sentence)<=20000 and sentence[0:len(sentence)-1] not in dicTitre:
        print(sentence)
        compteur+=1
        #print(PROBS)