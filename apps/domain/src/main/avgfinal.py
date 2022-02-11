from core.model_centric.syft_assets import PlanManager
from core.model_centric.models import model_manager
import torch as th
import glob
import base64
from functools import reduce
import pickle
from syft.federated.model_serialization import wrap_model_params
from syft import serialize
import sys
sys.path.append("/parcel/data/in")
from inference_model import Inference
import crypten
from crypten import mpc
import crypten.communicator as comm 
crypten.init()

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

#Get the current parameter inptu
with open("/parcel/data/in/orgparam","rb") as f:
    params = f.read()
    params = base64.b64decode(params)
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


updated_model_params = [
    model_param - diff_param
    for model_param, diff_param in zip(model_params, diff_avg)
]


crypten.common.serial.register_safe_class(Inference)
model = Inference()

modelweights = model.state_dict()
i = 0
for key in modelweights:
    assert modelweights[key].shape == updated_model_params[i].shape
    modelweights[key] = updated_model_params[i]
    i += 1     
model.load_state_dict(modelweights)

@mpc.run_multiprocess(world_size=2)
def model_split():
    dummy_input = th.empty((1,10,)) ,th.empty((1,10,))
    private_model = crypten.nn.from_pytorch(model,dummy_input)
    private_model.encrypt(src=0)
    rank = comm.get().get_rank()
    crypten.save(private_model.state_dict(), f"/parcel/data/out/modelweights{rank}.pth")    
    
model_split()