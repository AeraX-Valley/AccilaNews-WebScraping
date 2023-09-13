import logging
import asyncio
import re

import numpy as np
import httpx
import cv2

# logging.getLogger("httpx").setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
          (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
}


# this can't be more optimized
async def get_cookies(number: int = 1):
    cookies = []

    for i in range(number):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "http://www.bmatraffic.com/index.aspx", headers=headers
            )

            if resp.status_code == 200:
                # print(resp.headers.keys())
                cookies.append(resp.headers["set-cookie"])
            else:
                logging.error(
                    f"Check in failed. status code: {resp.status_code} loop number: {i}"
                )
                raise Exception(
                    f"Check in failed. status code: {resp.status_code} loop number: {i}"
                )

    cookies = [
        re.match(r"ASP.NET_SessionId=([a-zA-Z0-9]+);", cookie)[1] for cookie in cookies
    ]

    logging.info(f"Get cookie successfully. number: {number}")
    return cookies


async def set_camera(camera_id: list[str], cookies: list[str]):
    headers_with_cookie_list = []

    for cookie in cookies:
        headers_with_cookie = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Cookie": f"ASP.NET_SessionId={cookie}",
        }
        headers_with_cookie_list.append(headers_with_cookie)

    async with httpx.AsyncClient(
        timeout=10, limits=httpx.Limits(max_connections=50)
    ) as client:
        resps = [
            client.get(
                f"http://www.bmatraffic.com/PlayVideo.aspx?ID={id}",
                headers=headers_with_cookie,
            )
            for id, headers_with_cookie in zip(camera_id, headers_with_cookie_list)
        ]
        resps = await asyncio.gather(*resps)

        if not all(resp.status_code == 200 for resp in resps):
            codes = set([resp.status_code for resp in resps])
            logging.error(f"Set camera failed. status code: {codes}")
            raise Exception(f"Set camera failed. status code: {codes}")

    logging.info(f"Set camera successfully. number: {len(camera_id)}")


async def get_camera_image(cookies: list[str]):
    headers_with_cookie_list = []

    for cookie in cookies:
        headers_with_cookie = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
            "Cookie": f"ASP.NET_SessionId={cookie}",
        }
        headers_with_cookie_list.append(headers_with_cookie)

    image_list = []

    async with httpx.AsyncClient(
        timeout=10, limits=httpx.Limits(max_connections=50)
    ) as client:
        resps = [
            client.get(
                f"http://www.bmatraffic.com/show.aspx",
                headers=headers_with_cookie,
            )
            for headers_with_cookie in headers_with_cookie_list
        ]
        resps = await asyncio.gather(*resps)

        if not all(resp.status_code == 200 for resp in resps):
            codes = set([resp.status_code for resp in resps])
            logging.error(f"Set camera failed. status code: {codes}")
            raise Exception(f"Set camera failed. status code: {codes}")
        else:
            for resp in resps:
                if resp.content == b"":
                    logging.warning("Got empty image.")
                    image_list.append(np.zeros((266, 400, 3), dtype=np.uint8))
                else:
                    image = np.asarray(bytearray(resp.content), dtype="uint8")
                    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                    image_list.append(image)

    logging.info(f"Get camera image successfully. number: {len(cookies)}")
    return image_list


async def main():
    camera = [
        "1651", "1638", "1639"
    ]

    kies = await get_cookies(len(camera))
    print(kies)

    await set_camera(camera, kies)

    while True:
        images = await get_camera_image(kies)

        for i, image in enumerate(images):
            cv2.imshow(f"Image {i}", image)

        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            break

        await asyncio.sleep(1)


asyncio.run(main())
