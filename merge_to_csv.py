from os import listdir
from os.path import isfile, join
import json
import pandas as pd

mypath = 'data/'
onlyfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) and '.json' in f)]
print (len(onlyfiles))
res_list = []

for filename in onlyfiles:
    with open ('{}{}'.format(mypath, filename), 'r') as fp:
        cur_dict = json.load(fp)
    fp.close()
    res_list.append(cur_dict)

print (len(res_list))

res_df = pd.DataFrame(res_list)
res_df.to_csv('res.csv', index=False)