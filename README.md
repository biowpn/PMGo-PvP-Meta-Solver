# PMGo-PvP-Meta-Solver

Tools to analyze Pokemon GO PvP Meta.

## Getting Started

### Prerequisites

64-bit Windows

64-bit Python 3.5+

## Quick Start

Download the repository. Navigate to it. Then open the command line and run:

```
python make-tier-list.py smogon
```

The output should be:

```
Loading Pokemon list and matrix...
Symmetrizing matrix...
Solving smogon tiers...

Tier 1
11: WG.HC.IB Blastoise  0.38468
40: WA.BB.DC Charizard  0.32021
50: RL.FP.SB Venusaur   0.15003
56: VW.FP.SB Venusaur   0.13028
19: AS.F.DC Charizard   0.0148

```

To make dominator-style tier list with 3 tiers, the command would be

```
python make-tier-list.py dominator -n 3
```

The output should be (some parts are ommitted, marked by "..."):

```
Loading Pokemon list and matrix...
Symmetrizing matrix...
Solving dominator tiers...

Tier 1
40: WA.BB.DC Charizard
11: WG.HC.IB Blastoise
50: RL.FP.SB Venusaur
19: AS.F.DC Charizard
56: VW.FP.SB Venusaur

Tier 2
4: B.HC.HP Blastoise
10: WG.HC.HP Blastoise
13: AS.BB.DC Charizard
46: WA.F.DC Charizard
17: AS.DC.O Charizard

Tier 3
9: WG.HC.FC Blastoise
3: B.HC.FC Blastoise
44: WA.DC.O Charizard
16: AS.DC.FB Charizard

Dominator Sets:
...

```

The script will first look for two files, `matrix.csv` and `pokemon_list.csv`. By default, it will search the current directory.
Use "-d" flag to specify the directory to search for.

Refer to the [matrix.csv](./matrix.csv) and [pokemon_list.csv](./pokemon_list.csv) provided in this repository for the format required.

Then it will start calculating the tiers, and when it's done it will print the output. Use "-o" flag to specify an output file other than the standard output.

To acquire more matchup data, you may use the [Battle Matrix](https://pokemongo.gamepress.gg/pvp-battle-matrix).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
