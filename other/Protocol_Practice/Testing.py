import json
from collections import defaultdict
dict1 = json.loads(json.dumps({"h": 1, "e": 3, 'temp': {"a": 1, "b": 2}, "g": [1, 2, 3]}, indent=2))
dict2 = {"h": 2, "e": 3, 'temp': {"a": 2, "b": 3}, "g": [1, 'b', 'c']}
dict3 = {"h": 1, "e": 4, 'temp': {"a": 1, "b": 1}, "g": "poo"}
# dump = json.dumps(dict1)
# print(type(dump))
# print(dump)
print((json.dumps({"h": 1, "e": 3, 'temp': {"a": 1, "b": 2}, "g": [1, 2, 3]},)))

# load = json.loads(dict)
# print(type(load))
# print(load)
print(type(dict1))
data = [dict1['temp'], dict2['temp'], dict3['temp']]
master = defaultdict(list)
for d in data:  # this is your data from the web
    for k, v in d.items():
        master[k].append(v)

# print(master)
loaded = (json.dumps(master))
print(loaded)