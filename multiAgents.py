# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        newGhostPos = successorGameState.getGhostPositions()

        "*** YOUR CODE HERE ***"

        newGhostPos = successorGameState.getGhostPositions()
        curFood = currentGameState.getFood()

        ghostDist = min([manhattanDistance(newPos, ghostPos) for ghostPos in newGhostPos])

        if ghostDist <= 1:
            return -9999

        isFood = 0
        for foodPos in curFood.asList():
            if newPos == foodPos:
                isFood = 10

        foodDist = min([manhattanDistance(newPos, foodPos) for foodPos in curFood.asList()])

        return (isFood - foodDist + ghostDist/2)


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def max_value(self, gameState, depth):
        v = float("-inf")
        best_action = None

        # Generate successors
        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            x,a = self.value(successor, depth + 1) # Recurse
            if v < x:
                v = x
                best_action = action

        #print(v, best_action)
        return (v, best_action)

    def min_value(self, gameState, depth):
        v = float("inf")
        best_action = None
        index = depth % gameState.getNumAgents()

        # Generate successors
        for action in gameState.getLegalActions(index):
            successor = gameState.generateSuccessor(index, action)
            x,a = self.value(successor, depth + 1) # Recurse
            if v > x:
                v = x
                best_action = action

        #print(v, best_action)
        return (v, best_action)

    def value(self, gameState, depth):
        if (gameState.isWin() or gameState.isLose() or depth == self.depth * gameState.getNumAgents()):
            return (self.evaluationFunction(gameState), []) #tuple for score, action
        #print("DEPTH IS",depth, "  REMAINDER IS", depth % gameState.getNumAgents())

        remainder = depth % gameState.getNumAgents() # 0 iff on pacman
        if (remainder == 0):
            return self.max_value(gameState, depth)
        else:
            #run as ghost
            return self.min_value(gameState, depth)

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        score, action = self.value(gameState, 0)
        return action

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """
    def max_value(self, gameState, depth, alpha, beta):
        v = float("-inf")
        best_action = None

        # Generate successors
        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            x,a,X,Y = self.value(successor, depth + 1, alpha, beta) # Recurse
            if v < x:
                v = x
                best_action = action
                alpha = X
            if v > beta:
                return (v, best_action, alpha, beta)
            alpha = max(alpha, v)

        return (v, best_action, alpha, beta)

    def min_value(self, gameState, depth, alpha, beta):
        v = float("inf")
        best_action = None
        index = depth % gameState.getNumAgents()

        # Generate successors
        for action in gameState.getLegalActions(index):
            successor = gameState.generateSuccessor(index, action)
            x,a,X,Y = self.value(successor, depth + 1, alpha, beta) # Recurse
            if v > x:
                v = x
                best_action = action
                beta = Y
            if v < alpha:
                return (v, best_action, alpha, beta)
            beta = min(beta, v)

        return (v, best_action, alpha, beta)

    def value(self, gameState, depth, alpha, beta):
        if (gameState.isWin() or gameState.isLose() or depth == self.depth * gameState.getNumAgents()):
            return (self.evaluationFunction(gameState), [], alpha, beta) #tuple for score, action

        remainder = depth % gameState.getNumAgents() # 0 iff on pacman
        if (remainder == 0):
            return self.max_value(gameState, depth, alpha, beta)
        else:
            return self.min_value(gameState, depth, alpha, beta)

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        score, action, alpha, beta = self.value(gameState, 0, float("-inf"), float("inf"))
        print(alpha, beta)
        return action


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def max_value(self, gameState, depth):
        v = float("-inf")
        best_action = None

        # Generate successors
        for action in gameState.getLegalActions(0):
            successor = gameState.generateSuccessor(0, action)
            x,a = self.value(successor, depth + 1) # Recurse
            if v < x:
                v = x
                best_action = action

        #print(v, best_action)
        return (v, best_action)

    def exp_value(self, gameState, depth):
        v = 0
        best_action = None
        index = depth % gameState.getNumAgents()

        # Generate successors
        for action in gameState.getLegalActions(index):
            successor = gameState.generateSuccessor(index, action)
            p = 1/len(gameState.getLegalActions(index))
            x,a = self.value(successor, depth + 1) # Recurse
            v += p * x
        #print(v, best_action)
        return (v, best_action)

    def value(self, gameState, depth):
        if (gameState.isWin() or gameState.isLose() or depth == self.depth * gameState.getNumAgents()):
            return (self.evaluationFunction(gameState), []) #tuple for score, action
        #print("DEPTH IS",depth, "  REMAINDER IS", depth % gameState.getNumAgents())

        remainder = depth % gameState.getNumAgents() # 0 iff on pacman
        if (remainder == 0):
            return self.max_value(gameState, depth)
        else:
            #run as ghost
            return self.exp_value(gameState, depth)

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        score, action = self.value(gameState, 0)
        return action

def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    # Useful information you can extract from a GameState (pacman.py)

    pos = currentGameState.getPacmanPosition()
    food = currentGameState.getFood()
    pellets = currentGameState.getCapsules()
    ghostStates = currentGameState.getGhostStates()
    scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
    ghostPos = currentGameState.getGhostPositions()


    ghostDist = min([manhattanDistance(pos, ghostPos) for ghostPos in ghostPos])
    if ghostDist < 1:
        return -9999 #

    # isFood = 0
    # for foodPos in food.asList():
    #     if newPos == foodPos:
    #         isFood = 10
    foodDist = 1 #incentiveze low foodDist
    if len(food.asList()) != 0:
        foodDist += min([manhattanDistance(pos, foodPos) for foodPos in food.asList()])

    pelletDist = 1 #incentivize low pelletDist
    if len(pellets) != 0:
        pelletDist += min([manhattanDistance(pos, pelletPos) for pelletPos in pellets])

    return 20/pelletDist + 2/foodDist + ghostDist

# Abbreviation
better = betterEvaluationFunction
