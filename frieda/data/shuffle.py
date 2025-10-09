import pickle

with open('./instruction.pkl', 'rb') as handle:
    print(pickle.load(handle))