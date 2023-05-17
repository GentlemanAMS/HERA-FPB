import json

try:
    with open("patch_maintainer.json", "r") as fp:
        updates_info = json.load(fp)
except:
    with open("patch_maintainer.json", "x") as fp:
        function1 = {
            "version_number" : 0,
            "old_version"    : "blue",
            "current_version": "blue"
        }
        function2 = {
            "version_number" : 0,
            "old_version"    : "blue",
            "current_version": "blue"
        }
        function3 = {
            "version_number" : 0,
            "old_version"    : "blue",
            "current_version": "blue"
        }
        functions = {
                "function_1" : function1, 
                "function_2" : function2, 
                "function_3" : function3}
        json.dump(functions, fp, indent=4)

version = updates_info["function_1"]["old_version"]
print(version)

