from math import ceil
import random

data = """51,33.6,0.4630912926
41,24.9,0.5369087074
49,32.1,0.7255197349
44,25.1,0.1256402531
33,18.7,0.0873757156
35,23.5,0.0433865622
28,19.7,0.0647785478
49,31,0.1319674601
54,36,0.2627297379
47,30,0.2756854474
39,23,0.1340765291
36,19,0.1307622778
32,19.9,0.061765592
42,25.1,0.2814100633
47,31.7,0.2332027719
58,37.2,0.2473636638
61,37.3,0.1319674601
43,26.6,0.632720699
50,33.6,0.367279301
43,23.2,0.1877071407
43,26.9,0.2440494125
48,32.4,0.3901777644
48,30.9,0.1780656824"""

DB = [tuple(float(s) for s in p.split(',')) for p in data.split('\n')]

nk = 89
ratio = 0.6536195419
        
def F(sd, j):
    samplemeans = DB
    population = []
    for mux, muy, weight in samplemeans:
        population.extend((random.gauss(mux, sd), random.gauss(muy, sd*ratio) ) for i in range(int(round(weight * nk))))
    
    
    N = len(population)
#    print('n total = ' + str(N))
    
    xvalues, yvalues = zip( * population )
    xvalues = sorted(xvalues)
    yvalues = sorted(yvalues)
    
    i33 = int(round(N/3))
    i67 = int(round(2*N/3))
    
    xbins = [xvalues[i33], xvalues[i67]] + [1989000]
    ybins = [yvalues[i33], yvalues[i67]] + [1989000]
    
    SS = ' '.join(','.join(str(c) for c in p) for p in population)
#    print(xbins, ybins)
    counts = []
    for x1, x2 in zip([0] + xbins, xbins):
        for y1, y2 in zip([0] + ybins, ybins):
            counts.append((x1, y1, sum(x1 <= x < x2 and y1 <= y < y2 for x, y in population) / N))
    
#    proportion = [c[2] for c in counts]
#    print('\n'.join(str(c) for c in counts))
    # verify
#    print(sum(c[2] for c in counts))
    return counts[j][2]
