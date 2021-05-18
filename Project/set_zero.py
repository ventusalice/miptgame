import pickle
import os
for f in os.listdir('./bank/'):
    os.remove(os.path.join('./bank/', f))
with open('./bank/0_number', 'wb') as f:
    pickle.dump(0, f)