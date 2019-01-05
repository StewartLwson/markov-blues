import numpy as np
import random as rm

from pyo import *
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
def generate_comp(chords):
    current = "C"
    print("Start: " + current)
    comp = [current]
    i = 0
    prob = 1
    while i != chords:
        if current == "C":
            change = np.random.choice(transition[0], replace=True, p=matrix[0])
            if change == "CC":
                prob *= matrix[0][0]
                comp.append("C")
                pass
            elif change == "CF":
                prob *= matrix[0][1]
                current = "F"
                comp.append("F")
            else:
                prob *= matrix[0][2]
                current = "G"
                comp.append("G")
        elif current == "F":
            change = np.random.choice(transition[1], replace=True, p=matrix[1])
            if change == "FF":
                prob *= matrix[1][1]
                comp.append("F")
                pass
            elif change == "FC":
                prob *= matrix[1][0]
                current = "C"
                comp.append("C")
            else:
                prob *= matrix[1][2]
                current = "G"
                comp.append("G")
        elif current == "G":
            change = np.random.choice(transition[2], replace=True, p=matrix[2])
            if change == "GG":
                prob *= matrix[2][2]
                comp.append("G")
                pass
            elif change == "GC":
                prob *= matrix[2][0]
                current = "C"
                comp.append("C")
            else:
                prob *= matrix[2][1]
                current = "F"
                comp.append("F")
        i += 1
    print("Compositon of " + str(chords) + " chords: " + str(comp))
    print("Probability of chord sequence " + str(prob))
    return comp

comp = generate_comp(12)

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