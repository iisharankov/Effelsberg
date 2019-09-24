# Python code to demonstrate
# converting string to json
# using json.loads
import json

# inititialising json object
ini_string = {'nikhil': (1, 3), 'akash': [5, [4, 5], ["str"]],
              'manjeet': "string", 'akshat': 15}
print(type(ini_string))
# printing initial json
ini_string = json.dumps(ini_string)
print("initial 1st dictionary", ini_string)
print("type of ini_object", type(ini_string))

# converting string to json
final_dictionary = json.loads(ini_string)

# printing final result
print("final dictionary", str(final_dictionary))
print("type of final_dictionary", type(final_dictionary))
print(final_dictionary['nikhil'])



# import json
# # with open('user.json','w') as file:
# #     json.dump({
# #         "name": "Foo Bar",
# #         "age": 78,
# #         "friends": ["Jane","John"],
# #         "balance": 345.80,
# #         "other_names":("Doe","Joe"),
# #         "active":True,
# #         "spouse":None
# #     }, file, sort_keys=True, indent=4)
#
#
# humanData = json.loads(json.dumps({
#     'people': [
#         {
#             'Name': 'Ivan Sharankov',
#             'Age': 21,
#             'Height': 190,
#             'Weight': 78.5,
#             'Active': True,
#             'Balance': 100_000,
#         },
#         {
#             'Name': 'Alex Mechev',
#             'Age': 30,
#             'Height': 181,
#             'Weight': 70.5,
#             'Active': False,
#             'Balance': 1000
#         }
#     ]
# }, indent=2))
#