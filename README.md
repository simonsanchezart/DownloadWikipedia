# Download Wikipedia
A command line app to download a Wikipedia article, including nested articles and images.


---

## Requirements

- [Python](https://www.python.org/downloads/)
- [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)

---
## Usage

Python and both `.py` files should be added to `PATH`.

1. Open `cmd` and navigate to the folder you want to download the article in.
2. Run: `downloadWiki.py [theme] [article]` where **[theme]** is the name of any .css file located in the themes folder. And **[article]** is the url of the article you want to download.

![Example of downloaded article](images/exampleOfDownload.gif)

This will start downloading **[article]** in the current folder, it will keep downloading nested articles until you stop the execution of the program either by closing `cmd` or with a keyboard interruption.

---
After your download the articles, you can run `fixLinks.py`.

This will assign a css styling to all links inside your downloaded articles that point to articles that you haven't downloaded. It will also modify the `src` of those articles to point to the online Wikipedia article.

If you run `downloadWiki.py` with the same article in the same folder, it will only download the articles that you haven't downloaded already. 

You can then run `fixLinks.py` again to re-assign links in your previously downloaded articles to the new downloaded articles.

**TL;DR:** Always run `fixLinks.py` after downloading.

---
## Themes

You can create your own .css themes, by default, 3 themes are included:

- Dark
- Light
- Empty

The empty theme is a completely empty .css theme that you can use to create your own theme for the downloaded articles.

You can also use either the Dark or Light theme as a template for another theme.

You can modify the colors in `:root` to quickly create themes:

```css
:root{
    --text-color: #FFFFFF;
    --main: #292828;
    --light-main: #3b3939;
    --lighter-main: #464343;
    --accent-main: #ea6962;
    --darker-accent: #b34242;
    --secondary-accent: #7daea3;
    --tertiary-accent: #4a6446;
    --invalid: #928374;

    --contents-size: 400px; /* Width of content table */
}
```
