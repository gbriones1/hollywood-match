

import json
import os
import sys
import urllib

import cv2

import requests

face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')


stars = []
if os.path.isfile('stars.json'):
    stars = json.loads(open('stars.json', 'r').read())

for star in stars:
    print("Finding pictures of {}".format(star["name"]))
    os.makedirs("wild/{}/{}".format(star["gender"], star["imdbId"]), exist_ok=True)



import pdb; pdb.set_trace()
    
os.makedirs("wild", exist_ok=True)
os.makedirs("error", exist_ok=True)
os.makedirs("faces", exist_ok=True)

for star in stars[7:8]:
    dirname = star["name"].replace(" ", "_")
    os.makedirs("wild/{}".format(dirname), exist_ok=True)
    os.makedirs("error/{}".format(dirname), exist_ok=True)
    print("Finding pictures of {}".format(star["name"]))
    query = urllib.parse.urlencode({'q': '"{}"'.format(star["name"])})
    round = 1
    star["popular"] = 1
    while round <= 2 and star["popular"]:
        round_photo_count = 0
        url_count = 0
        response = requests.get('https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPIWithPagination?autoCorrect=false&pageNumber={}&pageSize=50&{}&safeSearch=true'.format(round, query), headers={"X-RapidAPI-Key": "b2028ce3b8msh03ae80a1602a764p1392f2jsn50ff5d9b5202"})
        for finding in json.loads(response.text)['value']:
            url_count += 1
            if not finding["url"] in star["urls"]:
                # print("Fetching picture: {}".format(finding["url"]))
                star["urls"].append(finding["url"])
                file_name = os.path.basename(urllib.parse.urlparse(finding["url"]).path)
                file_format = file_name.split('.')[-1].lower()
                if file_format in VALID_IMG_FORMATS:
                    img = None
                    try:
                        r = requests.get(finding["url"])
                        open('wild/{}/{}'.format(dirname, file_name), 'wb').write(r.content)
                        img = cv2.imread('wild/{}/{}'.format(dirname, file_name))
                    except:
                        pass
                    if img is not None:
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                        if len(faces) != 1:
                            os.remove('wild/{}/{}'.format(dirname, file_name))
                        else:
                            round_photo_count += 1
                        #     print("Picture found: {}".format(finding["url"]))
                        #     for (x, y, w, h) in faces:
                        #         cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        #     cv2.imshow("Faces found", img)
                        #     cv2.waitKey(0)
                        #     import pdb; pdb.set_trace()
                    elif os.path.isfile('wild/{}/{}'.format(dirname, file_name)):
                        os.rename('wild/{}/{}'.format(dirname, file_name), 'error/{}/{}'.format(dirname, file_name))
                        # print("Couldn't read file: {}".format(finding["url"]))
            # else:
            #     print("Picture already fetched: {}".format(finding["url"]))
            sys.stdout.write("\rRound {}: {}%".format(round, url_count*2))
            sys.stdout.flush()
        sys.stdout.write("\rRound {}: 100%\n".format(round))
        print("Round {} got {} photos".format(round, round_photo_count))
        if round_photo_count < 25:
            if round == 1:
                star["popular"] = 0
            else:
                round = 20
        round += 1
        open('stars.json', 'w').write(json.dumps(stars))
    print("{} has {} photos".format(star["name"], len(os.listdir('wild/{}'.format(dirname)))))