import os
import urllib.parse
from bs4 import BeautifulSoup

cwd = os.getcwd()

allHtmlPaths = []
for path, dirname, filenames in os.walk(cwd):
    for filename in filenames:
        if filename.endswith('.html'):
            htmlPath = os.path.join(path, filename)
            allHtmlPaths.append(htmlPath)

for htmlPath in allHtmlPaths:
    with open(htmlPath, 'r', encoding='utf-8') as f:
        htmlContent = f.read()
        soup = BeautifulSoup(htmlContent, 'html.parser')

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
                    articleName = linkHref.split('/')[-1]
                    possiblePath = os.path.join(cwd, articleName, f"{articleName}.html")
                    if os.path.exists(possiblePath):
                        del link['class']
                        link['href'] = possiblePath
                        print(f"Added local link for: {articleName}")
                    else:
                        link['class'] = 'invalidLink'

    with open(htmlPath, 'w', encoding='utf=8') as f:
        f.write(str(soup.prettify))