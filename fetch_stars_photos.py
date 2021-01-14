import json
import os
from urllib import request
from urllib import parse
from urllib.error import HTTPError, URLError
from http.client import IncompleteRead
import sys


VALID_IMG_FORMATS = ['jpg', 'jpeg', 'bmp', 'png', 'gif', 'tiff']

stars = []
if os.path.isfile('stars.json'):
    stars = json.loads(open('stars.json', 'r').read())

stars_dict = {}
stars_dict["females"] = [x for x in stars if x["gender"] == "female"][:300]
stars_dict["males"] = [x for x in stars if x["gender"] == "male"][:300]

for gender in stars_dict.keys():
    for star in stars_dict[gender]:
        wild_path = "wild/{}/{}".format(gender, star["imdbId"])
        urls_file = os.path.join(wild_path, 'urls.json')
        if os.path.isfile(urls_file):
            print("Downloading pics of {}".format(star["name"]))
            urls = json.loads(open(urls_file, 'r').read())
            for url_idx in range(len(urls)):
                sys.stdout.write("\r{:.2f}%".format(url_idx*100/len(urls)))
                url = urls[url_idx]
                fmt = parse.urlparse(url).path.split('.')[-1].split('/')[0]
                if not fmt.lower() in VALID_IMG_FORMATS:
                    fmt = "jpg"
                pic_file = os.path.join(wild_path, "{}.{}".format(url_idx, fmt))
                if not os.path.isfile(pic_file):
                    try:
                        request.urlretrieve(url.split("?")[0], pic_file)
                    except URLError as e:
                        pass
                    except HTTPError as e:
                        if int(e.code/100) != 4:
                            print(e)
                            import pdb; pdb.set_trace()
                            raise(e)
                    except IncompleteRead as e:
                        print(e)
                        import pdb; pdb.set_trace()
                        raise(e)
            sys.stdout.write("\r100.00%\n")
        else:
            print("{} has no urls".format(star["name"]))
