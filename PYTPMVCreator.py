from moviepy.editor import *
from mido import MidiFile
import mido, sys
import math, statistics


def get_semitones_timeline(midifile, tracknum):
    miditofreq = lambda notecode : (440/32) * (2** ((notecode-9) /12))
    freqdifftosemit = lambda f1, f2 : -12 * math.log(f1/f2, 2)

    try:
        midi = MidiFile(midifile, clip=True)
    except OSError:
        print("First argument must be a valid midi file.")

    if tracknum == -1:
        print("Searching for first valid MIDI track...")
        for i in range(len(midi.tracks)):
            notes, times, tempo = __decode_midi_loop(midi, i)
            if len(notes) != 0:
                print(f"Chose track #{i}")
                break
    else:
        print("Fetching notes and timestamps...")
        notes, times, tempo = __decode_midi_loop(midi, tracknum)

    if len(notes) == 0:
        print("Specified MIDI track or file is empty (no notes to be rendered).")
        return [[], []]
    median_note = statistics.median(notes)
    median_freq = miditofreq(median_note)
    semitones = []

    for note in notes:
        freq_curr = miditofreq(note)
        semitones.append(freqdifftosemit(median_freq, freq_curr))

    return [semitones, times]


def __decode_midi_loop(midi, tracknum):
    tempo = __get_tempo(midi)
    ppq = midi.ticks_per_beat
    notes = []
    times = []
    times_incrementor = 0

    for message in midi.tracks[tracknum]:
        #print(message)
        if message.type == "note_on" and message.velocity != 0:
            notes.append(message.note)
            times_incrementor += message.time
            times.append(mido.tick2second(times_incrementor, ppq, tempo))
        elif message.type == "note_off" or (message.type == "note_on" and message.velocity == 0):
            times_incrementor += message.time
        elif message.type not in ["note_on", "note_off"]:
            try:
                times_incrementor += message.time
            except:
                pass

    return [notes, times, tempo]


def __get_tempo(midi):
    print("Finding tempo value...")
    for track in midi.tracks:
        for message in track:
            if message.type == "set_tempo":
                return message.tempo


def get_track_names(midifile):
    try:
        midi = MidiFile(midifile, clip=True)
    except OSError:
        raise SystemExit("Not a valid MIDI file.")

    tracks_list = []
    for track in midi.tracks:
        tracks_list.append(track.name)

    return tracks_list


def render_video(clipfile, semitones_list, times_list):
    if semitones_list == [] or times_list == []:
        return None
    print("Running MoviePy...")
    semittospeed = lambda semitones : math.pow(2, (semitones/12))

    #print(semitones_list)
    #print(times_list)

    try:
        clip = VideoFileClip(clipfile)
    except (OSError, IndexError):
        raise SystemExit("Not a valid video file.")

    if clip.duration > 0.5:
        try:
            cutstart = float(input("Clip is longer than maximum (0.5s). Cut at which timestamp (in seconds)? "))
            cutdur = float(input("Cut for how much time (maximum 0.5s)? "))
        except ValueError:
            print("Must be number. Defaulting to cutting from 0 to 0.5")
            cutstart = 0
            cutdur = 0.5
        if cutdur > 0.5:
            cutdur = 0.5
            print("Must be maximum 0.5s. Defaulting to cutting for 0.5s")

        try:
            clip = clip.subclip(cutstart, cutstart+cutdur)
        except ValueError:
            print(f"Must be lower than clip's duration ({clip.duration}). Defaulting to cutting from 0 to 0.5")
            clip = clip.subclip(0, 0.5)

    song = []

    for i, j in zip(semitones_list, times_list):
        song.append(clip.fx(vfx.speedx, semittospeed(i)).set_start(j))

    return(CompositeVideoClip(song))


def save_standalone(clip, filename):
    if clip is None:
        return
    clip.write_videofile(filename)


def save_collage(clips, filename):
    if len(clips) == 0:
        return
    save_standalone(clips_array(clips), filename)


def blank_clip():
    return ColorClip((100, 100), (0, 0, 0), duration=2)

if __name__ == '__main__':
    try:
        file_source_midi = sys.argv[1]
        source_midi_track = int(sys.argv[2])
        file_source_clip = sys.argv[3]
    except IndexError:
        raise SystemExit("Usage:\n  PYTPMVCreator.py <midi file> <track number (-1 for auto)> <video clip>\n\nCreate YTPMVs automatically from a MIDI file and one video clip for the specified track.\nRun the Helper program instead for a better experience!")

    render_video(file_source_clip, *get_semitones_timeline(file_source_midi, source_midi_track)).write_videofile("output_ytpmv.webm")
    print("\nThanks! PYTPMVCreator job is done.")
