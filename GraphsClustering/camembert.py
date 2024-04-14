import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import spacy
import pandas as pd
nlp = spacy.load("en_core_web_sm")
f=open('hate_crime.csv',encoding='latin-1')
df=pd.read_csv(f,low_memory=False)
ai=pd.DataFrame.to_numpy(df)

# date : du 13 février au 28 octobre 2017
# indices dans le CSV 12:date 18:race de l'offender 24:race de la victime
a=[]
mois_interdits={'JAN','NOV','DEC'}
RACES=[]
dic_race={}

## remplissage du dictionnaire des ethnicités
for data in ai:
    if data[1]==2017:
        races= re.split(";", data[24])
        for race2 in races:
            if race2[5:] in {'Gender Non-Conforming','Transgender','Gay (Male)','Lesbian, Gay, Bisexual, or Transgender (Mixed Group)','Lesbian (Female)','Bisexual'}:
                race='LGBT'
            elif race2[len(race2)-10:]=='Disability':
                race='Disability'
            elif race2[5:]=='Arab':
                race='Islamic (Muslim)'
            else:
                race=race2[5:]
            if race in dic_race:
                dic_race[race]+=1
            else:
                dic_race[race]=1
sorted_Races = sorted(dic_race.items(), key=lambda item:item[1])

dic_race2={}
dic_race2["other"]=0
for key in dic_race:
    if dic_race[key]>80 and key!='Other Race/Ethnicity/Ancestry':
        dic_race2[key]=dic_race[key]
    else:
        dic_race2['other']+=dic_race[key]
RACE=[]
OCC=[]
setOther={'other','White','Other Religion','Multiple Races, Group'}
for race in dic_race2:
    if race not in setOther:
        RACE.append(race)
        OCC.append(dic_race2[race])

## réarrangement d'indices pour correspondre au camembert sur le dataset des articles
RACE2=[ 'Black or African American','Disability', 'Asian', 'Hispanic or Latino', 'American Indian', 'Jewish', 'LGBT', 'Islamic(Muslim)']
I=[0,3,7,1,6,5,4,2]
OCC2=[OCC[i] for i in I]
colors=['purple','cornflowerblue','grey','blue','orange','red','gold','seagreen']
plt.pie(OCC2,labels=RACE2,colors=colors,startangle=270,textprops={'fontsize':10},autopct='%.2f')
plt.show()