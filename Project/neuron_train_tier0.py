from sklearn.linear_model import PassiveAggressiveClassifier
import pickle

with open('./bank/0_number', 'rb') as f:
    number = pickle.load(f)
    
def flatten2list(object_list):
    gather = []
    for item in object_list:
        if isinstance(item, (list, tuple, set)):
            gather.extend(flatten2list(item))            
        else:
            gather.append(item)
    return gather

def elongate(object_list):
    return object_list + [0.0]*(10000 - len(object_list))

net = PassiveAggressiveClassifier(C=0.001)
classes = [','.join([str(bool(i//16)), str(bool(i//8%2)), str(bool(i//4%2)), str(bool(i//2%2)), str(bool(i%2))]) for i in range(1, 32)]


for i in range(number):
    print(f'{i} out of {number}')
    with open(f'./bank/{i}', 'rb') as f:
        data = pickle.load(f)
        X = [elongate(flatten2list([j[i][0:3] + [0.0, 0.0, 0.0] for j in data['X'][0:2]]))\
                 for i in range(len(data['X'][0]))]
        y = [','.join([str(j[i]) for j in data['y']]) for i in range(len(data['y'][0]))]
        net.partial_fit([j for ID, j in enumerate(X) if [y[i] != 'False,False,False,False,False' for i in range(len(y))][ID]],\
                        [j for ID, j in enumerate(y) if [y[i] != 'False,False,False,False,False' for i in range(len(y))][ID]], classes=classes)

with open('./net.dump', 'wb') as f:
    pickle.dump(net, f)