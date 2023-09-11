import logging
import time
import re

# import matplotlib.image as mpimg
# import matplotlib.pyplot as plt
# from PIL import Image
import numpy as np
import urllib3
import cv2


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

http = urllib3.PoolManager(num_pools=30)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
          (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
}


def get_cookies(number: int = 1):
    cookies = []

    for i in range(number):
        resp = http.request(
            "GET", "http://www.bmatraffic.com/index.aspx", headers=headers
        )

        if resp.status == 200:
            cookies.append(
                re.match(
                    r"ASP.NET_SessionId=([a-zA-Z0-9]+);", resp.headers["Set-Cookie"]
                )[1]
            )
        else:
            logging.error(
                f"Check in failed. status code: {resp.status} loop number: {i}"
            )
            raise Exception(
                f"Check in failed. status code: {resp.status} loop number: {i}"
            )

        time.sleep(0.1)

    logging.info(f"Get cookie successfully. number: {number}")
    return cookies


def set_camera(camera_id: list[str], cookies: list[str]):
    zipped = zip(camera_id, cookies)
    for i, (id, cookie) in enumerate(zipped):
        headers_with_cookie = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Cookie": f"ASP.NET_SessionId={cookie}",
        }

        resp = http.request(
            "GET",
            f"http://www.bmatraffic.com/PlayVideo.aspx?ID={id}",
            headers=headers_with_cookie,
        )

        if resp.status != 200:
            logging.error(
                f"Set camera failed. status code: {resp.status} loop number: {i}"
            )
            raise Exception(
                f"Set camera failed. status code: {resp.status} loop number: {i}"
            )

        time.sleep(0.1)

    logging.info(f"Set camera successfully. number: {len(camera_id)}")


def get_camera_image(cookies: list[str]):
    image_list = []
    for i, cookie in enumerate(cookies):
        headers_with_cookie = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Cookie": f"ASP.NET_SessionId={cookie}",
        }

        resp = http.request(
            "GET", f"http://www.bmatraffic.com/show.aspx", headers=headers_with_cookie
        )

        if resp.status == 200:
            if resp.data == b"":
                img = np.zeros((266, 400, 3), np.uint8)
                logging.warning(f"Get camera image failed. Skipping. loop number: {i}")
            else:
                img = np.asarray(bytearray(resp.data), dtype="uint8")
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)
            image_list.append(np.array(img))
        else:
            logging.error(
                f"Get camera image failed. status code: {resp.status} loop number: {i}"
            )
            raise Exception(
                f"Get camera image failed. status code: {resp.status} loop number: {i}"
            )

    logging.info(f"Get camera image successfully. number: {len(cookies)}")

    return image_list


camera = ["536", "619", "1703"]


kies = get_cookies(len(camera))
print(kies)

set_camera(camera, kies)

while True:
    images = get_camera_image(kies)

    # for i, image in enumerate(images):
    #     cv2.imshow(f"Image {i}", image)

    # if cv2.waitKey(1) == 27:
    #     cv2.destroyAllWindows()
    #     break

    time.sleep(1)
