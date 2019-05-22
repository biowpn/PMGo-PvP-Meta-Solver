
'''
Make Pokemon Go PvP Tier list.

'''


import argparse
import copy
import sys
import os

from game_solver import Game



def to_initials(phrase):
    '''
    Razor Leaf -> RL
    '''

    return ''.join([word[0].upper() for word in phrase.split(' ')])


def load_pokemon_matrix(pkm_list_file, matrix_file):
    '''
    Load Pokemon battle list and matrix from csv files.
    Return (pkm_name_list, matrix)
    '''

    pkm_name_list = []
    matrix = []
    with open(pkm_list_file, encoding='utf-8') as fd:
        header_line = fd.readline()
        attrs = header_line.strip().split(',')
        for i, line in enumerate(fd):
            vals = line.strip().split(',')
            pkm_dict = dict(zip(attrs, vals))
            pkm_label = "{}: {}.{}.{} {}".format(i + 1,
                                             to_initials(pkm_dict.get("fmove", "")),
                                             to_initials(pkm_dict.get("cmove", "")),
                                             to_initials(pkm_dict.get("cmove2", "")),
                                             pkm_dict.get("name", "").capitalize())
            pkm_name_list.append(pkm_label)
    with open(matrix_file, encoding='utf-8') as fd:
        for line in fd:
            cells = line.strip().split(',')
            matrix.append([float(c) for c in cells])

    return pkm_name_list, matrix


def remove_by_indices(L, indices):
    '''
    Remove multiple elements from a list by given indices.
    The change will be in place.
    '''
    
    removed_count = 0
    for index in sorted(indices):
        L.pop(index - removed_count)
        removed_count += 1



def make_smogon_tier_list(pkm_list_file, matrix_file, num_tiers, outfile):
    '''
    Make smogon style tier list.
    
    The tier 1 consists of the optimal meta derived from the orginal matrix.
    
    Remove the optimal meta from the pool, and solve for the reduced matrix to get tier 2.
    Repeat and get tier 3 and so on.
    '''
    
    print("Loading Pokemon list and matrix...", file=outfile)
    pokemon_names, matrix = load_pokemon_matrix(pkm_list_file, matrix_file)
    num_pokemon = len(pokemon_names)

    print("Symmetrizing matrix...", file=outfile)
    for i in range(num_pokemon):
        for j in range(i + 1, num_pokemon):
            matrix[i][j] = (matrix[i][j] - matrix[j][i]) / 2
            matrix[j][i] = -matrix[i][j]

    print("Solving smogon tiers...", file=outfile)
    tier = 1
    while tier <= num_tiers and len(pokemon_names) > 0:
        game = Game(matrix)
        game.solve()
        meta = [(pokemon_names[i], w) for i, w in enumerate(game.get_solution(True)) if w > 0]
        meta.sort(key=lambda x: -x[1])
        print("\nTier {}".format(tier), file=outfile)

        indices = []
        for name, weight in meta:
            print(name, round(weight, 5), sep='\t', file=outfile)
            for i, name2 in enumerate(pokemon_names):
                if name2 == name:
                    indices.append(i)
        remove_by_indices(pokemon_names, indices)
        remove_by_indices(matrix, indices)
        for row in matrix:
            remove_by_indices(row, indices)
        tier += 1



def get_all_dominators(index, dominators):
    '''
    For a given Pokemon index, find all its direct and indirect dominators.
    Return a set of indices, including the Pokemon's index.
    '''

    s = set([index])
    for dominator_index in dominators[index]:
        s = s.union(get_all_dominators(dominator_index, dominators))
    return s
    

def make_dominator_tier_list(pkm_list_file, matrix_file, num_tiers, outfile):
    '''
    Make dominator style tier list.

    The tier 1 consists of the optimal meta derived from the orginal matrix.
    
    For each Pokemon X in the optimal meta, remove X from the pool, then solve for the reduced matrix.
    Add each new Pokemon Y (if any) to tier 2. Add X to Y's dominator set. Add back X to the pool. Repeat.

    For each Pokemon Y in tier 2, remove Y and all of its dominators, then solve for the reduced matrix.
    Add each new Pokemon Z (if any) to tier 3. Add Y to Z's dominator set. Add back Y and all its dominawtors to the pool. Repeat.
    '''

    print("Loading Pokemon list and matrix...", file=outfile)
    pokemon_names, matrix = load_pokemon_matrix(pkm_list_file, matrix_file)
    num_pokemon = len(pokemon_names)

    print("Symmetrizing matrix...", file=outfile)
    for i in range(num_pokemon):
        for j in range(i + 1, num_pokemon):
            matrix[i][j] = (matrix[i][j] - matrix[j][i]) / 2
            matrix[j][i] = -matrix[i][j]
    
    print("Solving dominator tiers...", file=outfile)
    dominators = [set() for _ in range(num_pokemon)]
    tier_compositions = {}
    for tier in range(1, num_tiers + 1):
        tier_compositions[tier] = set()
        if tier > 1:
            for pokemon_index in tier_compositions[tier - 1]:
                
                # For each Pokemon in the previous tier, remove it and all its dominators
                pokemon_indices_to_remove = get_all_dominators(pokemon_index, dominators)
                pokemon_indices_remained = [i for i in range(num_pokemon) if i not in pokemon_indices_to_remove]
                matrix_reduced = copy.deepcopy(matrix)
                remove_by_indices(matrix_reduced, pokemon_indices_to_remove)
                for row in matrix_reduced:
                    remove_by_indices(row, pokemon_indices_to_remove)

                # Solve for the reduced game
                game = Game(matrix_reduced)
                game.solve()

                # Add the new Pokemon (if any) to the current tier, and mark its dominators
                for i, weight in enumerate(game.get_solution(True)):
                    new_pokemon_index = pokemon_indices_remained[i]
                    if weight > 0:
                        new_pokemon = True
                        for higher_tier in range(1, tier):
                            if new_pokemon_index in tier_compositions[higher_tier]:
                                new_pokemon = False
                                break
                        if new_pokemon:
                            dominators[new_pokemon_index].add(pokemon_index)
                            tier_compositions[tier].add(new_pokemon_index)
        else:
            # For tier 1, directly solve for the optimal meta
            game = Game(matrix)
            game.solve()
            for pokemon_index, weight in enumerate(game.get_solution(True)):
                if weight > 0:
                    tier_compositions[tier].add(pokemon_index)
        print("\nTier {}".format(tier), file=outfile)
        for pokemon_index in tier_compositions[tier]:
            print(pokemon_names[pokemon_index]) 
        tier += 1

    print("\nDominator Sets:", file=outfile)
    for dominatee_index, dominator_indices in enumerate(dominators):
        dominatee_name = pokemon_names[dominatee_index]
        dominator_names = [pokemon_names[i] for i in dominator_indices]
        if len(dominator_names):
            print(f"{dominatee_name} is dominated by:", ', '.join(dominator_names), file=outfile)
        
    

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("type",
                        type=str,
                        choices=["smogon", "dominator"],
                        default="smogon",
                        help="The type of PvP Tier List to make")
    parser.add_argument("-d", "--directory",
                        type=str,
                        default=os.curdir,
                        help="The directory to look for the two required input .csv files")
    parser.add_argument("-n", "--num-tiers",
                        type=int,
                        default=1,
                        help="The number of tiers to make")
    parser.add_argument("-o", "--outfile",
                        type=argparse.FileType('w'),
                        nargs='?',
                        default=sys.stdout)

    ns = parser.parse_args()
    
    list_making_method = globals()["make_{}_tier_list".format(ns.type)]

    if not os.path.isdir(ns.directory):
        print("Directory {} does not exist".format(ns.directory))
        return
    
    pkm_list_fname = os.path.join(ns.directory, "pokemon_list.csv")
    matrix_fname = os.path.join(ns.directory, "matrix.csv")
    if not os.path.isfile(pkm_list_fname):
        print("File {} does not exist".format(pkm_list_fname))
        return
    if not os.path.isfile(matrix_fname):
        print("File {} does not exist".format(matrix_fname))
        return

    list_making_method(pkm_list_fname, matrix_fname, ns.num_tiers, ns.outfile)



if __name__ == "__main__":
    main()




    
