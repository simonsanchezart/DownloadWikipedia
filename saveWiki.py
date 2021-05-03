import requests
import os
import pathlib
import urllib.parse
import sys
from bs4 import BeautifulSoup

scriptPath = pathlib.Path(__file__).parent.absolute()
baseHtmlPath = os.path.join(scriptPath, 'base.html')
cssThemes = os.path.join(scriptPath, 'themes')

invalidChars = ('\\', '/', ':', '*', '?', '"', '<', '>', '|', '(', ')', '%')
invalidWords = ('png', 'jpeg', 'jpg', 'Wikipedia:', 'File:', '#', '.webm')
def StripInvalid(s):
    for char in invalidChars:
        s = s.replace(char, '')
    return s

def NameFromLink(link):
    name = link.split('/')[-1]
    name = name.split('_')
    name = ' '.join(name)
    name = StripInvalid(name)

    return name

cssTheme = os.path.join(cssThemes, sys.argv[1]) 
articleLinks = sys.argv[2:]

i = 0
mainLocalPath = os.getcwd()
INNER_LINK_SUBDIRECTORY = 'internal'
for articleLink in articleLinks:
    articleLink = urllib.parse.unquote(articleLink)
    articleName = NameFromLink(articleLink)

    if i == 0:
        localPath = os.path.join(mainLocalPath, articleName)
        mainLocalPath = localPath
        i+=1
    else:
        localPath = os.path.join(mainLocalPath, INNER_LINK_SUBDIRECTORY, articleName)
    htmlPath = os.path.join(localPath, f"{articleName}.html")

    try:
        response = requests.get(articleLink)
        if response.status_code != 200:
            raise Exception()
    except Exception as e:
        print(f"Couldn't get {articleName}")
        continue

    print(f"Downloading {articleName}...\n")

    content = response.text
    soup = BeautifulSoup(content, 'html.parser')

    articleBody = soup.find(id='mw-content-text')
    for link in articleBody.find_all('a'):
        if 'href' in link.attrs:
            if link['href'].startswith('/wiki/'):
                link['href'] = 'https://en.wikipedia.org' + link['href']
                link['href'] = urllib.parse.unquote(link['href'])

                mustContinue = False
                for word in invalidWords:
                    if word in link['href']:
                        mustContinue = True
                if mustContinue:
                    continue

                articleLinks.append(link['href'])
                subArticleName = NameFromLink(link['href'])
                subArticleHtmlPath = os.path.join(mainLocalPath,
                                                  INNER_LINK_SUBDIRECTORY,
                                                  subArticleName,
                                                  f"{subArticleName}.html")
                link['href'] = subArticleHtmlPath 

    os.makedirs(localPath, exist_ok=True)
    if os.path.exists(htmlPath):
        print(f"{articleName} already exists.\n")
        continue

    imageBasePath = os.path.join(localPath, 'images')
    os.makedirs(imageBasePath, exist_ok=True)
    try:
        for image in articleBody.find_all('img'):
            if 'https:' in image['src']:
                imageSrc = image['src']
            else:
                imageSrc = f"https:{image['src']}"

            imageName = imageSrc.split('/')[-1]
            imageName = StripInvalid(imageName)

            # takes care of svg images
            if len(imageName.split('.')) == 1:
                image['class'] = 'vectorImage'
                imageName += '.svg'

            imageCompletePath = os.path.join(imageBasePath, imageName)

            response = requests.get(imageSrc)
            with open(f'{imageCompletePath}', 'wb') as f:
                f.write(response.content)

            image['src'] = imageCompletePath
    except Exception as e:
        print(e)
        print(f"Couldn't download {imageSrc}")

    externalLinkDiv = soup.find(id='External_links')
    if externalLinkDiv is not None:
        for sibling in externalLinkDiv.find_all_next():
            sibling.decompose()
        externalLinkDiv.decompose()

    for editSection in articleBody.find_all(class_='mw-editsection'):
        editSection.decompose()

    htmlBase = open(baseHtmlPath, 'r', encoding='utf-8').read()
    htmlBase = htmlBase.replace('#articleTitle', articleName)
    htmlBase = htmlBase.replace('#theme', cssTheme)
    htmlBase = htmlBase.replace('#articleBody', str(articleBody.prettify))

    with open(htmlPath, 'w', encoding='utf-8') as f:
        f.write(htmlBase)