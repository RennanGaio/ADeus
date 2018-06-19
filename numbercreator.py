import random as rd
import numpy.random

tam_pacote=numpy.random.choice(numpy.arange(1, 5), p=[0.3, 0.1, 0.3, 0.3])
print tam_pacote
if tam_pacote==4:
    true_tam=numpy.random.randint(64,1500)
elif tam_pacote==1:
    true_tam=64
elif tam_pacote==2:
    true_tam=512
else:
    true_tam=1500

print true_tam
