import json
import ast
import matplotlib.pyplot as plt

with open('getter_data_hexapod1.txt', 'r') as file:
    for line in file:
        name = line[:15].replace(' ', '')
        data = line[43:-2]

        data_as_dict = ast.literal_eval(data)
        # print(data_as_dict)
        print("\n \n" + f"# # # # # # # {name.upper()}" * 5)
        for a, b in data_as_dict.items():
            # Does not print lines where all values are exactly the same
            if sum(b)/len(b) != b[0]: # and sum(b) != 0:  # For just 0 excluded, uncomment this
                # print(a.ljust(50), [round(ba, 10) for ba in b])
                x_axis = range(len(b))
                y_axis = b

                plt.xlabel("instance (counts)")
                plt.ylabel(a)
                plt.title(a)
                plt.plot(x_axis, y_axis)

                plt.savefig(name + "/" + a.replace("/", '') + ".png")
                plt.clf()
