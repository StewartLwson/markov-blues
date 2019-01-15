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
notes_dict = {
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

# All available notes (whole tone scale)
all_notes = sorted(notes_dict.keys())

start = all_notes.index(key)

# Shift the the notes list to begin with the key
for _ in range(start):
    all_notes.append(all_notes.pop(0))

degrees = [0, 2, 3, 5, 7, 8, 10]

def to_chords(notes, degrees, band):
    chords = []
    octave = band
    for degree in degrees:
        if degree > notes.index("c") and key is not "c":
            octave = band + 1
        note = notes_dict[notes[degree]]
        chords.append(Sine(freq=[note * (2**octave), note * (2**octave) * (3/2)], phase=0, mul=0.1))
    return chords

chords = to_chords(all_notes, degrees, 4)

if(SOUND == "Synth"):
    one_chord = chords[0]
    four_chord = chords[3]
    five_chord = chords[4]
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