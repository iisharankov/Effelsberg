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