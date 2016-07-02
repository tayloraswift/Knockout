import cProfile, pstats, io
from kt import main

PR = cProfile.Profile(timeunit=0.0001)
PR.enable()
main((None, 'test.html'))
PR.disable()

s = io.StringIO()
sortby = 'cumulative'
PS = pstats.Stats(PR, stream=s).sort_stats(sortby)
PS.print_stats()
print(s.getvalue())
