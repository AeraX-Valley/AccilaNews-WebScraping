import logging
import asyncio
import time
import re

# import matplotlib.image as mpimg
# import matplotlib.pyplot as plt
# from PIL import Image
import numpy as np
import httpx
import cv2

logging.getLogger('httpx').setLevel(logging.WARNING)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
          (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
}


async def get_cookies(number: int = 1):
    cookies = []

    for i in range(number):
        async with httpx.AsyncClient() as client:
            resp = await client.get("http://www.bmatraffic.com/index.aspx", headers=headers)

            if resp.status_code == 200:
                #print(resp.headers.keys())
                cookies.append(resp.headers["set-cookie"])
            else:
                logging.error(
                    f"Check in failed. status code: {resp.status_code} loop number: {i}"
                )
                raise Exception(
                    f"Check in failed. status code: {resp.status_code} loop number: {i}"
                )
            
    cookies = [re.match(r"ASP.NET_SessionId=([a-zA-Z0-9]+);", cookie)[1] for cookie in cookies]

    logging.info(f"Get cookie successfully. number: {number}")
    return cookies


async def set_camera(camera_id: list[str], cookies: list[str]):
    async with httpx.AsyncClient() as client:
        for i, (id, cookie) in enumerate(zip(camera_id, cookies)):
            headers_with_cookie = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
                "Cookie": f"ASP.NET_SessionId={cookie}",
            }

            resp = await client.get(
                f"http://www.bmatraffic.com/PlayVideo.aspx?ID={id}",
                headers=headers_with_cookie,
            )

            if resp.status_code != 200:
                logging.error(
                    f"Set camera failed. status code: {resp.status_code} loop number: {i}"
                )
                raise Exception(
                    f"Set camera failed. status code: {resp.status_code} loop number: {i}"
                )

    logging.info(f"Set camera successfully. number: {len(camera_id)}")


async def get_camera_image(cookies: list[str]):
    image_list = []

    async with httpx.AsyncClient() as client:
        for i, cookie in enumerate(cookies):
            headers_with_cookie = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                    (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
                "Cookie": f"ASP.NET_SessionId={cookie}",
            }

            resp = await client.get(
                f"http://www.bmatraffic.com/show.aspx", headers=headers_with_cookie
            )

            if resp.status_code == 200:
                if resp.content == b"":
                    img = np.zeros((266, 400, 3), np.uint8)
                    logging.warning(f"Get camera image failed. Skipping. loop number: {i}")
                else:
                    img = np.asarray(bytearray(resp.content), dtype="uint8")
                    img = cv2.imdecode(img, cv2.IMREAD_COLOR)

                image_list.append(np.array(img))
            else:
                logging.error(
                    f"Get camera image failed. status code: {resp.status_code} loop number: {i}"
                )
                raise Exception(
                    f"Get camera image failed. status code: {resp.status_code} loop number: {i}"
                )

    logging.info(f"Get camera image successfully. number: {len(cookies)}")
    return image_list

async def main():
    camera = ["1651", "1638", "1639", "1758", "601", "602", "603", "604", "597", "598", "599", "1567", "609", "610", "612", "479", "481", "1569", "1456", "1531", "556", "1537", "1539", "639", "305", "1466", "310", "309", "1553", "1471", "1527", "1528", "318", "1529", "320", "1508", "1545", "1546", "1547", "1489", "630", "1552", "332", "1534", "1535", "364", "363", "335", "1469", "1536", "1541", "1472", "1474", "1542", "546", "1533", "1467", "1475", "1554", "1523", "1759", "1458", "354", "1555", "1549", "1548", "1226", "1228", "1230", "1232", "1231", "1470", "1382", "1461", "1515", "1362", "991", "590", "595", "596", "1556", "576", "1757", "1486", "1477", "648", "1422", "584", "395", "1453", "569", "1478", "1418", "1566", "1480", "1481", "1482", "1483", "1479", "1584", "1596", "1593", "1594", "1595", "506", "1564", "1581", "1582", "432", "642", "1707", "1708", "1755", "1578", "1580", "1756", "622", "623", "1204", "1264", "1200", "1207", "439", "500", "1463", "1464", "1621", "1388", "1598", "1089", "613", "615", "616", "1568", "1353", "1286", "1258", "1674", "1326", "1325", "1333", "1249", "1282", "1283", "1284", "1750", "1305", "1243", "1244", "1246", "1329", "1287", "1318", "1319", "1320", "1322", "1323", "1324", "1242", "1248", "1247", "1330", "1297", "1293", "1295", "1301", "1304", "1314", "1315", "1291", "1288", "1327", "1298", "1299", "248", "1451", "1452", "1442", "1443", "1357", "1053", "1152", "1645", "971", "1646", "924", "1641", "1655", "908", "1662", "1162", "1166", "1167", "1616", "289", "1172", "1625", "1763", "1764", "1642", "968", "1669", "938", "939", "1670", "1234", "1649", "1650", "1338", "1339", "1658", "1643", "1654", "1648", "942", "1647", "1336", "1652", "1672", "1716", "1717", "1718", "1719", "1436", "198", "199", "200", "201", "208", "209", "202", "203", "11", "12", "999", "184", "216", "217", "186", "291", "1661", "1189", "1191", "1188", "1183", "1185", "1347", "1192", "1715", "1710", "1711", "105", "1511", "1731", "1732", "1735", "1733", "1431", "1433", "1358", "1063", "233", "1618", "1677", "1678", "1679", "1620", "1692", "1752", "1673", "1617", "1619", "1695", "1693", "1296", "1694", "1751", "1696", "1098", "1689", "1086", "1259", "526", "1161", "1428", "1349", "1182", "572", "394", "1156", "1158", "1163", "1164", "1165", "1698", "527", "1379", "1154", "1174", "1178", "1344", "1345", "1563", "413", "477", "411", "1502", "1503", "1659", "1660", "1157", "1597", "1255", "1440", "1441", "1072", "1073", "108", "1088", "1635", "109", "1728", "1747", "229", "230", "1745", "1746", "1600", "1570", "962", "1395", "1260", "1261", "1263", "1332", "1585", "1588", "1107", "1108", "63", "1071", "1720", "1721", "1680", "1505", "1506", "1497", "1613", "1133", "1134", "1135", "87", "90", "88", "89", "1136", "1572", "1574", "1575", "1559", "1557", "98", "99", "96", "97", "947", "93", "94", "95", "92", "1087", "100", "102", "101", "103", "1724", "1725", "1399", "113", "1530", "1558", "317", "1499", "374", "1744", "1085", "32", "1101", "1094", "26", "1195", "1723", "1510", "1690", "79", "78", "77", "80", "81", "1629", "1630", "1631", "1632", "1403", "1405", "1601", "1589", "1590", "1691", "37", "1103", "1102", "36", "123", "124", "125", "119", "121", "118", "120", "1681", "1682", "1683", "1043", "1058", "1622", "1447", "1626", "1602", "1603", "1604", "562", "1591", "1592", "1543", "1684", "387", "388", "386", "1027", "1081", "1123", "1360", "1082", "1083", "1359", "1668", "385", "1028", "926", "20", "18", "19", "1762", "1121", "1131", "1748", "1749", "1685", "1686", "1525", "1709", "1092", "1122", "1112", "1397", "1398", "390", "116", "117", "114", "304", "1587", "1736", "1737", "1705", "47", "46", "1194", "1526", "301", "1688", "1730", "1607", "1687", "1037", "1038", "146", "147", "239", "240", "148", "149", "1627", "1628", "150", "151", "1065", "1066", "1068", "1067", "1064", "156", "1076", "1125", "191", "206", "207", "180", "181", "182", "1061", "190", "188", "189", "172", "173", "1070", "1069", "256", "257", "250", "218", "219", "222", "223", "162", "163", "1760", "1761", "1434", "1435", "82", "83", "39", "258", "259", "158", "159", "1143", "996", "132", "133", "136", "137", "195", "194", "1633", "1634", "170", "171", "251", "252", "128", "129", "130", "131", "51", "1124", "997", "241", "185", "1444", "253", "1127", "1445", "1446", "1128", "178", "179", "1430", "140", "141", "254", "255", "197", "196", "138", "139", "226", "1132", "1078", "168", "169", "1074", "1075", "176", "177", "220", "221", "1432", "1429", "228", "1426", "1427", "152", "1168", "1169", "1712", "1713", "227", "68", "70", "1361", "1439", "1060", "44", "45", "242", "1170", "542", "1273", "1274", "1206", "276", "277", "1605", "1606", "536", "619", "1703"]

    kies = await get_cookies(len(camera))
    print(kies)

    await set_camera(camera, kies)

    while True:
        images = await get_camera_image(kies)

        # for i, image in enumerate(images):
        #     cv2.imshow(f"Image {i}", image)

        # if cv2.waitKey(1) == 27:
        #     cv2.destroyAllWindows()
        #     break

        await asyncio.sleep(1)

asyncio.run(main())
