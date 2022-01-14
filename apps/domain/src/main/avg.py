from core.model_centric.syft_assets import PlanManager
from core.model_centric.models import model_manager
import torch as th
import glob
import base64
from functools import reduce
import pickle
from syft.federated.model_serialization import wrap_model_params
from syft import serialize

#Put this file in apps/domain/src/main

#Get the averaging plan input (
with open("/parcel/data/in/avg_plan","r") as f:
    data = f.read()
is_avg = True
if data == "None":
    is_avg = False
else:
    iterative_plan = int(data[-1])
    data = data[:-1]
    plan = base64.b64decode(data.encode())

# try:
#     data2 = data.decode('utf-8')
#     if data2 == "None":
#         is_avg = False
# except UnicodeDecodeError:
#     iterative_plan = int(data[-1:].decode())
#     data = data[:-1]

# print(data,iterative_plan)

#Get the current parameter inptu
with open("/parcel/data/in/orgparam","rb") as f:
    params = f.read()
model_params = model_manager.unserialize_model_params(params)

#Get the difference input
diffs = []
for diffdoc in glob.glob("/parcel/data/in/diff*.txt"):
    with open(diffdoc,"r") as f:
        data = f.read()
    # print(diffdoc)
    diffs.append(base64.b64decode(data.encode()))

# print(diffs)
diffs = [model_manager.unserialize_model_params(diff) for diff in diffs]

if is_avg:
    avg_plan = PlanManager.deserialize_plan(plan)
    if iterative_plan:
        diff_avg = diffs[0]
        for i, diff in enumerate(diffs[1:]):
            diff_avg = avg_plan(
                avg=list(diff_avg), item=diff, num=th.tensor([i + 1])
            )
    else:
        diff_avg = avg_plan(diffs)
else:
    raw_diffs = [
        [diff[model_param] for diff in diffs]
        for model_param in range(len(model_params))
    ]
    sums = [reduce(th.add, param) for param in raw_diffs]
    diff_avg = [th.div(param, len(diffs)) for param in sums]
diff_serialized = serialize(wrap_model_params(diff_avg)).SerializeToString()
x = base64.b64encode(diff_serialized).decode("ascii")
with open("/parcel/data/out/prediction.txt","w") as f:
    f.write(x)

# y = base64.b64decode(x.encode())
# print(model_manager.unserialize_model_params(y))



        