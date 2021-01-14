import json
import os
from io import StringIO

from lxml import etree

import requests

parser = etree.HTMLParser()

stars = []
if os.path.isfile('stars.json'):
    stars = json.loads(open('stars.json', 'r').read())

if not stars:
    for gender in ["female", "male"]:
        for page in range(5):
            response = requests.get('https://www.imdb.com/search/name?gender={}&count=250&start={}&ref_=rlm'.format(gender, page*250+1))
            tree = etree.parse(StringIO(response.text), parser)
            content_list = tree.xpath("/html/body/div[@id='wrapper']/div[@id='root']/div[@id='pagecontent']/div[@id='content-2-wide']/div[@id='main']/div/div[@class='lister-list']")[0]
            for child in content_list.findall('div'):
                try:
                    job = child.xpath("div[@class='lister-item-content']/p")[0].text.strip()
                    if (gender == "female" and job == "Actress") or (gender == "male" and job == "Actor"):
                        imdbId = child.xpath("div[@class='lister-item-content']/h3/a")[0].attrib['href'].split("/")[-1]
                        name = child.xpath("div[@class='lister-item-content']/h3/a")[0].text.strip()
                        response = requests.get('https://www.imdb.com/name/{}/mediaindex?ref_=nm_phs_md_sm'.format(imdbId))
                        tree = etree.parse(StringIO(response.text), parser)
                        photo_div = tree.xpath("/html/body/div[@id='wrapper']/div[@id='root']/div[@id='pagecontent']/div[@id='content-2-wide']/div[@id='main']/div")[0].xpath("div/div[@class='media_index_pagination leftright']/div[@id='left']")
                        if photo_div:
                            photo_count = int(photo_div[0].text.split()[-2].replace(",", ""))
                            stars.append({
                                "imdbId": imdbId,
                                "name": name,
                                "gender": gender,
                                "imdbPopular": photo_count,
                                # "imdbUrls": [],
                                # "contextualUrls": [],
                            })
                            print(name)
                except Exception as e:
                    print(e)
                    import pdb; pdb.set_trace()
    stars = sorted(stars, key=lambda x: x['imdbPopular'], reverse=True)
    open('stars.json', 'w').write(json.dumps(stars))
