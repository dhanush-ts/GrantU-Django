import numpy as np
from scipy.optimize import linprog


c = [-3,-2]
a = [[2,1],[4,-5]]

b = [20,10]

x_bound = (0,None)
y_bound = (0,None)
bounds = [x_bound,y_bound] 

result = linprog(c,A_ub=a,b_ub=b,method="highs",bounds=bounds)

print(f"optimal result : " {-result.fun})
print(f"value os x : " {result.x})
