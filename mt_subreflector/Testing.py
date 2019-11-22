import json
import ast

with open('getter_data.txt', 'r') as file:
    for line in file:
        name = line[:15].replace(' ', '')
        data = line[43:-2]

        data_as_dict = ast.literal_eval(data)
        # print(data_as_dict)
        print("\n \n" + f"# # # # # # # {name.upper()}" * 5)
        for a, b in data_as_dict.items():
            # Does not print lines where all values are 0
            if sum(b)/len(b) != b[0] and sum(b) != 0:  # For just 0 excluded, uncomment this
                print(a.ljust(50), [round(ba, 10) for ba in b])