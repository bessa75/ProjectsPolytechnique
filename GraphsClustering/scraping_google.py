import csv
import requests
from bs4 import BeautifulSoup
import csv
import time

## fonction permettant de sauvegarder une liste dans un fichier csv
def sauvegarder_liste_csv(liste, nom_fichier):
    with open(nom_fichier, 'w', newline='') as fichier_csv:
        writer = csv.writer(fichier_csv)
        for element in liste:
            writer.writerow([element])

## fonction permettant d'extraire les titres d'une recherche google à la page n
def extraire_titres_recherche_google_news(recherche,n):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36"
    }
    cookies= {'CONSENT': 'YES+026'} # cookie
    url = "https://www.google.com/search?q="+recherche+"&tbm=nws&sxsrf=APwXEdfmtfWjnpTQZK6On1gNil5vVxU_zg:1685104476601&ei=XKdwZLirJNeskdUPhKGN4AU&start=20&sa=N&ved=2ahUKEwi4yfKt_5L_AhVXVqQEHYRQA1w4ChDy0wN6BAgFEAc&biw=1440&bih=460&dpr=1&num=100&start="+str((n)*100) ##on utilise des filtres de recherche pour avoir les résultats de Google Actualités (tbm=nws), 100 résultats par page (num=100) et commencer à la page n
    #print(url)
    response = requests.get(url,headers=headers,timeout=30,cookies=cookies) #obtention du code source de la page
    soup = BeautifulSoup(response.content, "html.parser") #parsing par Beautiful Soup
    articles = soup.find_all("div", class_="n0jPhd ynAwRc MBeuO nDgy9d") #identification de la classe correspondant aux titres d'articles
    titres = [article.text for article in articles]
    return titres


recherche = "hate crime"
titres = extraire_titres_recherche_google_news(recherche,1)
print(titres)
