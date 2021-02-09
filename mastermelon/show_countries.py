import json
import requests
import pymongo
from time import time
import asyncio
from bson import json_util


# with open("watermelon.config", "rb") as f:
#     js = json.load(f)
#     mongo_key: str = js["mongo_key"]
#     prefix: str = js["prefix"]
#     ipaddress_access_key: str = js["ipaddress_access_key"]
#     client = pymongo.MongoClient(mongo_key)
#     db = client.get_database("AlexMindustry")
#     expgains = db["expgains"]
#     serverplayerupdates = db["serverplayerupdates"]

# 822fbb4aa5a50c2e8db601d22f3afbd6
# http://api.ipstack.com/220.255.62.197?access_key=822fbb4aa5a50c2e8db601d22f3afbd6


async def getcountries(serverplayerupdates: pymongo.collection, ipaddress_access_key: str):
    # cursor = serverplayerupdates.find()
    # res = []
    # t0 = time()
    # count = 0
    # store = {}
    # for i, cur in enumerate(cursor):
    #     count += 1
    #     if count % 1000 == 0:
    #         print(count, end=" ")
    #     res.append(cur)
    #     store[i] = cur
    #     if count % 100000 == 0:
    #         with open(f"data/serverplayerupdates_{count//100000}.data", "w") as f:
    #             f.write(json_util.dumps(store))
    #         store = {}
    # with open(f"data/serverplayerupdates_{ (count // 100000)+1}.data", "w") as f:
    #     f.write(json_util.dumps(store))

    # for i in range(1,16):
    #     with open(f"data/serverplayerupdates_{i}.data", "r") as f:
    #         data = json_util.loads(f.read())
    #         res.append(data)
    # t1 = time()
    # muuids_dict = {}
    # count = 0
    # for data in res:
    #     for key, doc in data.items():
    #         count += 1
    #         if count % 100000 == 0:
    #             print(count, end=" ")
    #         if doc["muuid"]:
    #             muuid = doc["muuid"]
    #             if muuid in muuids_dict:
    #                 muuids_dict[muuid].append(doc["con_address"])
    #             else:
    #                 muuids_dict[muuid] = [doc["con_address"]]
    # t2 = time()
    # for muuid, ips in muuids_dict.items():
    #     print(len(set(ips)), end=" ")
    # print(f"timetaken= {t1 - t0:.2f}s {t2 - t1:.2f}s")
    # with open(f"data/uuid_ip.data", "w") as f:
    #     f.write(json_util.dumps(muuids_dict))
    with open(f"data/uuid_ip.data", "r") as f:
        muuids_dict = json_util.loads(f.read())
    continent = {}
    country = {}
    for i, (muuid, ips) in enumerate(muuids_dict.items()):
        if i % 1000 == 0:
            print(i, end="  ")
            response = requests.get(f"http://api.ipstack.com/{ips[0]}?access_key=822fbb4aa5a50c2e8db601d22f3afbd6")
            if response.ok:
                res = response.json()
                if res["continent_name"] in continent:
                    continent[res["continent_name"]] += 1
                else:
                    continent[res["continent_name"]] = 1
                if res["country_name"] in country:
                    country[res["country_name"]] += 1
                else:
                    country[res["country_name"]] = 1
    print( sorted(continent.items(),key=lambda x:x[1],reverse=True) )
    print(sorted(country.items(), key=lambda x: x[1], reverse=True))
    await asyncio.sleep(1)
