import numpy as np
import random as rm

from pyo import Server, Sine, SfPlayer
import time

SOUND = "Synth"
s = Server().boot()

duration = 60
tempo = 90

if(SOUND == "Synth"):
    c = Sine(freq=[261.626, 391.995], phase=0, mul=0.1)
    f = Sine(freq=[349.228, 523.25], phase=0, mul=0.1)
    g = Sine(freq=[391.995, 587.33], phase=0, mul=0.1)
elif(SOUND == "Piano"):
    c = SfPlayer(["sound/Piano.mf.C4.aiff", "sound/Piano.mf.G4.aiff"], speed=1, loop=False, mul=0.4)
    f = SfPlayer(["sound/Piano.mf.F4.aiff", "sound/Piano.mf.C5.aiff"], speed=1, loop=False, mul=0.4)
    g = SfPlayer(["sound/Piano.mf.G4.aiff", "sound/Piano.mf.D5.aiff"], speed=1, offset=[0.15, 0], loop=False, mul=0.4)

# Possible chords in blues sequences
states = ["C", "F", "G"]

# Example (training) data of various twelves bar pieces
example = ["C", "C", "C", "C", "F", "F", "C", "C", "G", "F", "C", "C"]

# TODO: Allow training with multidimensional array
#example = [ ["C", "C", "C", "C", "F", "F", "C", "C", "G", "F", "C", "C"],
#            ["C", "C", "F", "C", "F", "F", "C", "C", "G", "F", "C", "C"],
#            ["C", "C", "C", "C", "F", "F", "C", "C", "G", "G", "C", "C"],
#            ["C", "C", "F", "C", "F", "F", "C", "C", "G", "G", "C", "C"]]

# Returns all possible changes for possible chords
def gen_changes(chords):
    changes = []
    for chord1 in states:
        c = []
        for chord2 in states:
            c.append(chord1 + chord2)
        changes.append(c)
    return changes

# Sets transitions for Markov chain to possible changes
transition = gen_changes(states)

# Generates probability matrix for possible changes based off training data
def gen_probs(chords):
    matrix = [[0,0,0],
              [0,0,0],
              [0,0,0]]
    changes = []
    for i in range(len(chords)):
        if i < len(chords) - 1:
            changes.append(chords[i] + chords[i+1])
    for c in changes:
        for t in range(len(transition)):
            for i in range(len(transition[t])):
                if c == transition[t][i]:
                    matrix[t][i] += 1
    for m in range(len(matrix)):
        num = sum(matrix[m])
        for i in range(len(matrix[m])):
            matrix[m][i] = (matrix[m][i] / num)
    return matrix

matrix = gen_probs(example)
print("Possible changes:" + str(transition))
print("Probability of changes:" + str(matrix))

# Generates a sequence of changes using Markov Chain rules
# length is the amount of bars in the composition
# start is the starting chord for the composition
def generate_comp(length, start):
    current = start
    comp = [current]
    i = 0
    changes = []
    while i != length:
        if current == "C":
            changes = transition[0]
        elif current == "F":
            changes = transition[1]
        elif current == "G":
            changes = transition[2]
        change = np.random.choice(changes, replace=True, p=matrix[0])
        current = change[1]
        comp.append(change[1])
        i += 1
    print("Compositon of " + str(length) + " chords: " + str(comp))
    return comp

comp = generate_comp(12, "C")

s.start()
for note in comp:
    if note == "C":
        c.out()
        time.sleep(1)
        c.stop()
    elif note == "F":
        f.out()
        time.sleep(1)
        f.stop()
    elif note == "G":
        g.out()
        time.sleep(1)
        g.stop()
s.stop()