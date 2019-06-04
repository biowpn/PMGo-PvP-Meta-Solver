
from ctypes import *
import os
import platform

if platform.system() == "Windows":
    lib = CDLL(os.path.join(os.path.dirname(__file__), "GameSolver.dll"))
else:
    lib = CDLL(os.path.join(os.path.dirname(__file__), "libGameSolver.so"))
    



class Game:

    lib.Game_new.argtypes = [POINTER(POINTER(c_double)), c_int, c_int]
    lib.Game_new.restype = c_void_p
    def __init__(self, A):
        '''
        A is the payoff matrix.
        '''
        assert len(A) > 0
        assert len(A[0]) > 0
        
        self.m = len(A)
        self.n = len(A[0])
        rows = [(c_double * self.n)(*row) for row in A]
        t_A = (POINTER(c_double) * self.m)(*rows)

        self.obj = lib.Game_new(t_A, self.m, self.n)


    lib.Game_delete.argtypes = [c_void_p]
    lib.Game_delete.restype = c_void_p
    def __del__(self):
        lib.Game_delete(self.obj)


    lib.Game_solve.argtypes = [c_void_p]
    lib.Game_solve.restype = c_void_p
    def solve(self):
        return lib.Game_solve(self.obj)


    lib.Game_optstrat.argtypes = [c_void_p, c_bool, POINTER(c_double)]
    lib.Game_optstrat.restype = c_void_p
    def opstrat(self, player):
        '''
        For Player I, player is true; for Player II, player is false.
        '''

        size = self.m if player else self.n
        weights = (c_double * size)()
        lib.Game_optstrat(self.obj, bool(player), weights)
        return [weights[i] for i in range(size)]

    def get_solution(self, player):
        return self.opstrat(player)


    lib.Game_value.argtypes = [c_void_p, c_bool]
    lib.Game_value.restype = c_double
    def value(self, player):
        '''
        For Player I, player is true; for Player II, player is false.
        '''
        return lib.Game_value(self.obj, bool(player))

    def get_value(self, player):
        return self.value(player)



    
