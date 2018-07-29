import json

with open('api_data.json', 'r') as f:
    datafile = json.load(f)
    
results = []
for data in datafile:
    if len(results) == 0:
        results.append(data)
    else:
        if data['created'] != results[-1]['created']:
            results.append(data)

with open("api_data_final.json", 'w') as f:
    json.dump(results, f)

    