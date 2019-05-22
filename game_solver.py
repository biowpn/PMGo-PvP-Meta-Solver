
'''
Solve arbitrary two player zero sum game using Pivot Method.

System requirement: 64-bit Windows, 64-bit Python
'''


from ctypes import *

lib = CDLL("game_solver.dll")



class Game:

    lib.Game_new.argtypes = [POINTER(POINTER(c_double)), c_int, c_int]
    lib.Game_new.restype = c_void_p
    def __init__(self, A):
        '''
        A is the payoff matrix.
        '''

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


    lib.Game_get_solution.argtypes = [c_void_p, c_bool]
    lib.Game_get_solution.restype = POINTER(c_double)
    lib.delete_double_array.argtypes = [c_void_p]
    lib.delete_double_array.restype = c_void_p
    def get_solution(self, player):
        '''
        For Player I, player is true; for player II, player is false.
        '''

        solution = lib.Game_get_solution(self.obj, bool(player))
        size = self.m if player else self.n
        weights = [solution[i] for i in range(size)]
        lib.delete_double_array(solution)
        return weights


    lib.Game_get_value.argtypes = [c_void_p, c_bool]
    lib.Game_get_value.restype = c_double
    def get_value(self, player):
        '''
        For Player I, player is true; for player II, player is false.
        '''
        
        return lib.Game_get_value(self.obj, bool(player))



def test():
    game = Game([
        [0, -2, 1],
        [2, 0, -1],
        [-1, 1, 0]
        ])
    game.solve()
    print(game.get_value(True))
    print(game.get_solution(True))
                



    
