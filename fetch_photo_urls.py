import asyncio
import json
import os
import time

from io import StringIO
from lxml import etree
from urllib import parse

from pyppeteer import launch, errors

async def query_images(query, first=1):
    browser = await launch()
    page = await browser.newPage()
    await page.goto('https://www.bing.com/images/search?q={}&first={}'.format(query, first))
    content = await page.content()
    await browser.close()
    return content

stars = []
if os.path.isfile('stars.json'):
    stars = json.loads(open('stars.json', 'r').read())

stars_dict = {}
stars_dict["females"] = [x for x in stars if x["gender"] == "female"][:300]
stars_dict["males"] = [x for x in stars if x["gender"] == "male"][:300]

for gender in stars_dict.keys():
    for star in stars_dict[gender]:
        if not os.path.isfile('wild/{}/{}/urls.json'.format(gender, star["imdbId"])):
            os.makedirs('wild/{}/{}'.format(gender, star["imdbId"]), exist_ok=True)
            image_sources = []
            i = 0
            retries = 0
            while len(image_sources) < 350 or retries >= 10:
                try:
                    html = asyncio.get_event_loop().run_until_complete(query_images(parse.quote_plus(star["name"]), first=i*35+1))
                    parser = etree.HTMLParser()
                    tree = etree.parse(StringIO(html), parser)
                    for row in tree.xpath('/html/body/div[@id="b_content"]/div[@id="vm_c"]/div/div/ul'):
                        for child in row.getchildren():
                            detail = child.xpath('div/div/a')[0].attrib['href']
                            img_src = parse.parse_qs(detail)['mediaurl'][0]
                            if img_src not in image_sources:
                                image_sources.append(img_src)
                    i += 1
                except errors.TimeoutError:
                    print("Page crashed, moving forward")
                    time.sleep(10)
                    if retries:
                        i += 1
                    retries += 1
            print(star["name"], len(image_sources))
            open('wild/{}/{}/urls.json'.format(gender, star["imdbId"]), 'w').write(json.dumps(image_sources))
        else:
            print(star["name"], "Already fetched urls")
