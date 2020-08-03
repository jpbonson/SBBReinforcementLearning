[![Build Status](https://travis-ci.org/jpbonson/SBBFramework.svg?branch=master)](https://travis-ci.org/jpbonson/SBBFramework) [![Coverage Status](https://coveralls.io/repos/github/jpbonson/SBBFramework/badge.svg?branch=master)](https://coveralls.io/github/jpbonson/SBBFramework?branch=master)[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fjpbonson%2FSBBFramework.svg?type=shield)](https://app.fossa.com/projects/git%2Bgithub.com%2Fjpbonson%2FSBBFramework?ref=badge_shield)


# SBBFramework
Python implementation of **Symbiotic Bid-Based (SBB)** framework for problem decomposition using Genetic Programming (GP). This algorithm was developed by the NIMS laboratory, Dalhousie University, Canada.

This framework can be used in the following ways:

**Reinforcement Learning tasks (via sockets)**

1. implement a socket client that follows SBB socket interface (available below)

2. define a configuration

3. run SBB

4. run the socket client

- a simple socket client for tictactoe is available [here](https://github.com/jpbonson/SBBFramework/blob/master/SBB/tests/system_tests/tictactoe_game.py).

- sample configurations for this task are available [here](https://github.com/jpbonson/SBBFramework/tree/master/SBB/configs/sockets).

**Reinforcement Learning tasks (via code extension)**

1. implement a class that inherits SBB/environments/default_environment

2. add the new environment to _initialize_environment in SBB/sbb.py

3. define a configuration

4. run SBB

- a simple class implementation for tictactoe is available [here](https://github.com/jpbonson/SBBFramework/blob/master/SBB/environments/reinforcement/tictactoe/tictactoe_environment.py).

- sample configurations for this task are available [here](https://github.com/jpbonson/SBBFramework/tree/master/SBB/configs/tictactoe) for tictactoe and [here](https://github.com/jpbonson/SBBFramework/tree/master/SBB/configs/poker) for poker.

**Classification tasks**

1. add a .train and a .test file to SBB/datasets

2. define a configuration

3. run SBB

- sample configurations for this task are available [here](https://github.com/jpbonson/SBBFramework/tree/master/SBB/configs/classification).

- *warning: This framework was developed focusing on reinforcement learning, so it is not able to deal with big datasets.*


# Index
1. Introduction to SBB
2. References
3. How to Install
4. How to Run
5. How to Test
6. Socket Interface

## 1. Introduction to SBB

**General Idea:**
- teams of programs evolve and compete over time
- each team represents a player in the game
- at each generation they play many matches against various opponents
- the best ones reproduce and keep evolving, the others are discarded

**Main Algorithms**:
- It follows the structure of a typical genetic algorithm:

![](https://s13.postimg.org/uej2lc0fr/image.png "Overview of a Genetic Algorithm")

- Modified with the SBB algorithm:

![](https://s13.postimg.org/6c28qgjsn/sbb.png "Overview of SBB")

- each team (host) is composed of 2 or more programs (symbionts)
- programs are composed of a set of instructions, registers and an action
- before a team executes an action:
   - all of its programs run over the inputs for the current match state
   - the action from the program with the highest output is selected as the team’s action
- a point is a game match, that represents the environment

## 2. References

Below there are a few of the publications about SBB.

**Papers**

P. Lichodzijewski and M. I. Heywood. Symbiosis, complexification and simplicity under GP. In Proceedings of the ACM Genetic and Evolutionary Computation Conference, pages 853–860, 2010.

J. A. Doucette, P. Lichodzijewski, and M. I. Heywood. Hierarchical task decomposition through symbiosis in reinforcement learning. In ACM Genetic and Evolutionary Computation Conference, pages 97–104, 2012.

S. Kelly, P. Lichodzijewski, and M. I. Heywood. On run time libraries and hierarchical symbiosis. In Evolutionary Computation (CEC), 2012 IEEE Congress on, pages 1–8. IEEE, 2012.

J. P. C. Bonson, A. Mcintyre, and M. I. Heywood. On Novelty Driven Evolution in Poker. In Computational Intelligence, 2016 IEEE Symposium Series on. IEEE, 2016.

**Master Thesis**

J. P. C. Bonson. Diversity and Novelty as Objectives in Poker, 2016. ([link](http://web.cs.dal.ca/~mheywood/Thesis/JPCBonson.pdf))

**PhD Thesis**

P. Lichodzijewski. A Symbiotic Bid-Based (SBB) framework for problem decomposition using Genetic Programming, 2011. ([link](http://web.cs.dal.ca/~mheywood/Thesis/PLichodzijewski.pdf))

## 3. How to Install

**Windows:**

Install [Anaconda for Python 2.7](http://continuum.io/downloads)

In the Windows console, type 'anaconda' before running the python commands.

**Ubuntu:**

Install the dependencies:
```
apt-get install build-essential python-dev pkg-config python-setuptools python-numpy python-scipy libatlas-dev libatlas3gf-base libfreetype6-dev python-pip
```

Then execute:
```
pip install -r requirements.txt
```
Obs.: You also have the option to use Anaconda for Ubuntu.

Obs.: You should also install the library 'python-pypoker-eval' if you want to generate poker hands.

## 4. How to Run

```
python main.py -f CONFIG_FILE
```

Various predefined configuration files are available [here](https://github.com/jpbonson/SBBFramework/tree/master/SBB/configs).

## 5. How to Test

```
nosetests
```

## 6. Socket Interface

All the messages have the format:
{'message_type': message_type, 'params': {}}

The server sends the following message types: ['new_match', 'perform_action']

The client sends the following message types: ['match_running', 'match_ended']

A match starts with a 'new_match' message from the server, then sequences of 'match_running' from the client and 'perform_action' from the server, until the client sends a 'match_ended'.

### Message Types:

**'new_match'**
- Informs the client that it should set up a new match.
- **Sent by:** server
- **Parameters:** 
    - 'mode': 'training', 'validation', or 'champion', can be used to debug (string)
    - 'match_id': can be used to debug (string)
    - 'opponent_label': used by the client, to know what opponent should be used to initialize the match (optional) (string)
    - 'point_label': used by the client, to know what label should be used to initialize the match (optional) (int)
        - for example, in the case of poker there are 9 labels, for 9 hands based on the player's strength and the opponent's strength, where the strength is [weak, intermediate, strong]
    - 'point_seed': used by the client, to know what seed should be used to initialize the match (optional) (int)
    - 'point_id': used by the client, to know what point should be used to initialize the match (optional) (int)

**'match_running'**
- Gives information about the match state to the server.
- **Sent by:** client
- **Parameters:** 
    - 'inputs': the current match state, all values must be between 0.0 and 10.0 (list of floats)
    - 'valid_actions': the valid actions for the current match state (list of ints)
    - 'current_player': 'sbb' or 'hall_of_fame', only is used if the hall of fame is enabled (string)
                            
**'perform_action'**
- Based on the match state, defines an action to execute in the client.
- **Sent by:** server
- **Parameters:** 
    - 'mode': 'training', 'validation', or 'champion', can be used to debug (string)
    - 'match_id': can be used to debug (string)
    - 'action': the chosen action (int)

**'match_ended'**
- Informs the server that the match ended.
- **Sent by:** client
- **Parameters:** 
    - 'result': a value from 0.0 to 1.0 indicating how the player performed in this match (float)


## License
[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2Fjpbonson%2FSBBFramework.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2Fjpbonson%2FSBBFramework?ref=badge_large)