import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import urllib3

import logging
import time
import io
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

http = urllib3.PoolManager()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
}

def get_cookies(number: int = 1):
    cookies = []

    for i in range(number):
        resp = http.request("GET", "http://www.bmatraffic.com/index.aspx", headers=headers)

        if resp.status == 200:
            cookies.append(re.match("ASP\.NET_SessionId=([a-zA-Z0-9]+);", resp.headers["Set-Cookie"])[1])
        else:
            logging.error(f"Check in failed. status code: {resp.status} loop number: {i}")
            raise Exception(f"Check in failed. status code: {resp.status} loop number: {i}")
        
        time.sleep(0.5)
        
    logging.info(f"Get cookie successfully. number: {number}")
    return cookies

def get_camera_image(camera_id: list[str], cookies: list[str]):
    zipped = zip(camera_id, cookies)
    for i, (id, cookie) in enumerate(zipped):
        headers_with_cookie = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Cookie": f"ASP.NET_SessionId={cookie}"
        }

        http.request("GET", f"http://www.bmatraffic.com/PlayVideo.aspx?ID={id}", headers=headers_with_cookie)
        resp = http.request("GET", f"http://www.bmatraffic.com/show.aspx", headers=headers_with_cookie)

        if resp.status == 200:
            logging.info(f"Get camera image successfully. status code: {resp.status}")
            fp = io.BytesIO(resp.data)

            with fp:
                img = mpimg.imread(fp, format="JPG")
            plt.imshow(img)
            plt.show()

kies = get_cookies(2)
print(kies)
get_camera_image(["1659", "1753"], kies)

    



