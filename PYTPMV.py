from moviepy.editor import *
from mido import MidiFile
import mido, sys
import math, statistics

try:
    file_source_midi = sys.argv[1]
    files_source_tracks = sys.argv[2:]
except IndexError:
    raise SystemExit("Usage:\n  YTPMVer.py <midi file> [video clips]\n\nCreate YTPMVs automatically from a MIDI file and one video clip for each track.")


def get_semitones_timeline():
    miditofreq = lambda notecode : (440/32) * (2** ((notecode-9) /12))
    freqdifftosemit = lambda f1, f2 : -12 * math.log(f1/f2, 2)

    try:
        midi = MidiFile(file_source_midi, clip=True)
    except OSError:
        raise SystemExit("First argument must be a valid midi file.")
    except FileNotFoundError:
        raise SystemExit(f"File {file_source_midi} does not exist.")

    for i in range(len(midi.tracks)):
        notes, times, tempo = __decode_midi_loop(midi, i)
        if len(notes) != 0:
            break

    median_note = statistics.median(notes)
    median_freq = miditofreq(median_note)
    semitones = []

    for note in notes:
        freq_curr = miditofreq(note)
        semitones.append(freqdifftosemit(median_freq, freq_curr))

    return [semitones, times]


def __decode_midi_loop(midi, tracknum):
    tempo = 0
    ppq = midi.ticks_per_beat
    notes = []
    times = []
    times_incrementor = 0

    for message in midi.tracks[tracknum]:
        #print(message)

        if message.type == "note_on":
            notes.append(message.note)
            times_incrementor += message.time
            times.append(mido.tick2second(times_incrementor, ppq, tempo))
        elif message.type == "note_off":
            times_incrementor += message.time

        if message.type == "set_tempo" and tempo == 0:
            tempo = message.tempo

    return [notes, times, tempo]


def render_video(semitones_list, times_list):
    semittospeed = lambda semitones : math.pow(2, (semitones/12))

    #print(semitones_list)
    #print(times_list)

    try:
        clip = VideoFileClip(files_source_tracks[0])
    except (OSError, IndexError):
        raise SystemExit("Second argument must be a valid video file.")

    if clip.duration > 0.5:
        try:
            cutstart = float(input("Clip is longer than maximum (0.5s). Cut at which timestamp (in seconds)? "))
            cutend = float(input("Cut for how much time (maximum 0.5s)? "))
        except ValueError:
            print("Must be number. Defaulting to cutting from 0 to 0.5")
            cutstart = 0
            cutend = 0.5
        if cutend - cutstart > 0.5:
            cutend = cutstart + 0.5
            print("Must be maximum 0.5s. Defaulting to cutting for 0.5s")

        try:
            clip = clip.subclip(cutstart, cutend)
        except ValueError:
            print(f"Must be lower than clip's duration ({clip.duration}). Defaulting to cutting from 0 to 0.5")
            clip = clip.subclip(0, 0.5)

    song = []

    for i, j in zip(semitones_list, times_list):
        song.append(clip.fx(vfx.speedx, semittospeed(i)).set_start(j))

    return(CompositeVideoClip(song))


render_video(*get_semitones_timeline()).write_videofile("output_ytpmv.webm")
