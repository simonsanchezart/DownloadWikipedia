import requests
import re
import os
import pathlib
import urllib.parse
import sys
from bs4 import BeautifulSoup

saveWikiPath = pathlib.Path(__file__).parent.absolute()
baseHtmlPath = os.path.join(saveWikiPath, 'base.html')
cssThemes = os.path.join(saveWikiPath, 'themes')

invalidChars = ('\\', '/', ':', '*', '?', '"', '<', '>', '|', '(', ')', '%')
invalidLinkSentences = ('png', 'jpeg', 'jpg', 'Wikipedia:', 'File:', '#', '.webm')
def StripInvalid(incomingString):
    for char in invalidChars:
        incomingString = incomingString.replace(char, '')

    return incomingString

def NameFromLink(link):
    name = link.split('/')[-1]
    name = name.split('_')
    name = ' '.join(name)
    name = StripInvalid(name)

    return name

theme = os.path.join(cssThemes, sys.argv[1]) 
articleLinks = sys.argv[2:]
for articleLink in articleLinks:
    articleLink = urllib.parse.unquote(articleLink)
    articleName = NameFromLink(articleLink)

    localPath = os.path.join(os.getcwd(), articleName)
    htmlFinalPath = os.path.join(localPath, f"{articleName}.html")

    try:
        response = requests.get(articleLink)
        print(f"Code: {response.status_code}")
        if response.status_code != 200:
            continue
    except Exception as e:
        print("Couldn't get {articleName}")
        continue

    print(f"Downloading {articleName}...\n")

    content = response.text
    soup = BeautifulSoup(content, 'html.parser')
    articleBody = soup.find(id='mw-content-text')

    for link in articleBody.find_all('a'):
        if 'href' in link.attrs:
            if link['href'].startswith('/wiki/'):
                link['href'] = 'https://en.wikipedia.org' + link['href']

                mustContinue = False
                for format in invalidLinkSentences:
                    if format in link['href']:
                        mustContinue = True
                if mustContinue:
                    continue

                link['href'] = urllib.parse.unquote(link['href'])
                articleLinks.append(link['href'])
                subArticleName = NameFromLink(link['href'])
                subArticleHtmlPath = os.path.join(os.getcwd(), subArticleName, f"{subArticleName}.html")
                link['href'] = subArticleHtmlPath 

    os.makedirs(localPath, exist_ok=True)
    if os.path.exists(htmlFinalPath):
        print(f"{articleName} already exists.\n")
        continue

    try:
        for image in articleBody.find_all('img'):
            if 'https:' in image['src']:
                imageSrc = image['src']
            else:
                imageSrc = f"https:{image['src']}"

            imageCompleteName = imageSrc.split('/')[-1]
            imageCompleteName = StripInvalid(imageCompleteName)

            # takes care of svg images
            if len(imageCompleteName.split('.')) == 1:
                image['class'] = 'vectorImage'
                imageCompleteName += '.svg'

            imagePath = f"{localPath}/{imageCompleteName}"
            response = requests.get(imageSrc)
            with open(f'{imagePath}', 'wb') as f:
                f.write(response.content)

            image['src'] = imagePath
    except Exception as e:
        print(f"Couldn't download {imageSrc}")

    externalLink = soup.find(id='External_links')
    if externalLink is not None:
        for sibling in externalLink.find_all_next():
            sibling.decompose()
        externalLink.decompose()

    for editSection in articleBody.find_all(class_='mw-editsection'):
        editSection.decompose()

    htmlBase = open(baseHtmlPath, 'r', encoding='utf-8').read()
    htmlBase = htmlBase.replace('#articleTitle', articleName)
    htmlBase = htmlBase.replace('#theme', theme)
    htmlBase = htmlBase.replace('#articleBody', str(articleBody.prettify))

    with open(htmlFinalPath, 'w', encoding='utf-8') as f:
        f.write(htmlBase)