import numpy as np
import random as rm

from pyo import Server, Sine, SfPlayer
import time

SOUND = "Synth"
s = Server().boot()

key = "c"
duration = 60
tempo = 90

# Lowest pitch value for every note
notes = {
    "c": 16.35,
    "c#": 17.32,
    "d": 18.35,
    "d#": 19.45,
    "e": 20.60,
    "f": 21.83,
    "f#": 23.12,
    "g": 24.50,
    "g#": 25.96,
    "a": 27.50,
    "a#": 29.14,
    "b": 30.87
}

# Multiplies pitch value by 2 to power of given octave band to transpose to
# that octave
# note is the pitch being scaled
# band is the target octave band
def to_band(note, band):
    return notes[note] * (2**band)

if(SOUND == "Synth"):
    one_chord = Sine(freq=[to_band("c", 4), to_band("g", 4)], phase=0, mul=0.1)
    four_chord = Sine(freq=[to_band("f", 4), to_band("c", 5)], phase=0, mul=0.1)
    five_chord = Sine(freq=[to_band("g", 4), to_band("d", 5)], phase=0, mul=0.1)
elif(SOUND == "Piano"):
    path = "sound/Piano.mf."
    ext = ".aiff"
    one_chord = SfPlayer([path + "C4" + ext, path + "G4" + ext], speed=1,
    loop=False, mul=0.4)
    four_chord = SfPlayer([path + "F4" + ext, path + "C5" + ext], speed=1,
    loop=False, mul=0.4)
    five_chord = SfPlayer([path + "G4" + ext, path + "D5" + ext], speed=1,
    offset=[0.15, 0], loop=False, mul=0.4)

# Possible chords in blues sequences
states = ["1", "4", "5"]

# Example (training) data of various twelves bar pieces
example = ["1", "1", "1", "1", "4", "4", "1", "1", "5", "4", "1", "1"]

# TODO: Allow training with multidimensional array
#example = [ ["1", "1", "1", "1", "4", "4", "1", "1", "5", "4", "1", "1"],
#            ["1", "1", "4", "1", "4", "4", "1", "1", "5", "4", "1", "1"],
#            ["1", "1", "1", "1", "4", "4", "1", "1", "5", "5", "1", "1"],
#            ["1", "1", "4", "1", "4", "4", "1", "1", "5", "5", "1", "1"]]

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
    # Matrix of transition probabilties (initially all set to 0)
    matrix = [[0,0,0],
              [0,0,0],
              [0,0,0]]
    # List of all exisiting transitions in input composition
    changes = []

    # Iterates through input composition and adds each transition to the list
    for i in range(len(chords)):
        if i < len(chords) - 1:
            changes.append(chords[i] + chords[i+1])

    # Iterates through transition list and adds to the matrix each time a
    # corresponding transition exists
    for c in changes:
        for t in range(len(transition)):
            for i in range(len(transition[t])):
                if c == transition[t][i]:
                    matrix[t][i] += 1

    # Iterates through the matrix and normalizes each row to contain values
    # corresponding to probability of transition taking place
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
        if current == "1":
            changes = transition[0]
        elif current == "4":
            changes = transition[1]
        elif current == "5":
            changes = transition[2]
        change = np.random.choice(changes, replace=True, p=matrix[0])
        current = change[1]
        comp.append(change[1])
        i += 1
    print("Compositon of " + str(length) + " chords: " + str(comp))
    return comp

comp = generate_comp(12, "1")

s.start()
for note in comp:
    if note == "1":
        one_chord.out()
        time.sleep(1)
        one_chord.stop()
    elif note == "4":
        four_chord.out()
        time.sleep(1)
        four_chord.stop()
    elif note == "5":
        five_chord.out()
        time.sleep(1)
        five_chord.stop()
s.stop()