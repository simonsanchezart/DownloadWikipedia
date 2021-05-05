import os
import urllib.parse
from bs4 import BeautifulSoup

cwd = os.getcwd()

allHtmlPaths = []
for filePath, _, filenames in os.walk(cwd):
    for filename in filenames:
        if filename.endswith('.html'):
            htmlPath = os.path.join(filePath, filename)
            allHtmlPaths.append(htmlPath)

for htmlPath in allHtmlPaths:
    with open(htmlPath, 'r', encoding='utf-8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')

        for link in soup.find_all('a'):
            if 'href' in link.attrs:
                linkHref = link['href']
                linkHref = urllib.parse.unquote(linkHref)

                if '#' not in linkHref:
                    link['target'] = '_blank'

                if not linkHref.startswith('http') and linkHref.endswith('.html'):
                    if not os.path.exists(linkHref):
                        linkArticleName = linkHref.split('.')[-2]
                        linkArticleName = linkArticleName.split('\\')[-1]
                        wikiLink = f"https://en.wikipedia.org/wiki/{linkArticleName}"

                        link['class'] = 'invalidLink'
                        link['href'] = wikiLink
                elif linkHref.startswith('https://en.wikipedia.org/wiki/'):
                    pathExists = False
                    possiblePath = ''

                    articleName = linkHref.split('/')[-1]
                    for innerHtmlPath in allHtmlPaths:
                        possiblePath = innerHtmlPath
                        htmlFileName = os.path.basename(possiblePath)
                        if f"{articleName}.html" == htmlFileName:
                            pathExists = True
                            break

                    if pathExists:
                            del link['class']
                            link['href'] = possiblePath
                            print(f"Added local link for: {articleName}")
                    else:
                        link['class'] = 'invalidLink'

    with open(htmlPath, 'w', encoding='utf=8') as f:
        f.write(str(soup.prettify))