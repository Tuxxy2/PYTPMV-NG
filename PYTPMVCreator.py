from moviepy.editor import *
from mido import MidiFile
import mido, sys
import math, statistics
import uuid

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






def render_video(clipfile, semitones_list, *, output_file=None, with_audio=True):
    if semitones_list == [] or semitones_list[0] == [] or semitones_list[1] == []:
        return None
    print("Running MoviePy...")
    semittospeed = lambda semitones : math.pow(2, (semitones/12))

    # Create a flipped version of the video
    tmp_clipfile = f"{os.path.splitext(clipfile)[0]}_tmp{os.path.splitext(clipfile)[1]}"
    os.system(f"ffmpeg -i {clipfile} -vf hflip -c:a copy {tmp_clipfile}")

    try:
        clip1 = VideoFileClip(clipfile)
        clip2 = VideoFileClip(tmp_clipfile)
    except (OSError, IndexError):
        raise SystemExit("Not a valid video file.")

    if clip1.duration > 0.5:
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
            clip1 = clip1.subclip(cutstart, cutstart+cutdur)
            clip2 = clip2.subclip(cutstart, cutstart+cutdur)
        except ValueError:
            print(f"Must be lower than clip's duration ({clip1.duration}). Defaulting to cutting from 0 to 0.5")
            clip1 = clip1.subclip(0, 0.5)
            clip2 = clip2.subclip(0, 0.5)

    song = []
    clip_alternate = True

    for i, j in zip(semitones_list[0], semitones_list[1]):
        if clip_alternate:
            song.append(clip1.fx(vfx.speedx, semittospeed(i)).set_start(j))
        else:
            song.append(clip2.fx(vfx.speedx, semittospeed(i)).set_start(j))
        clip_alternate = not clip_alternate

    final_clip = CompositeVideoClip(song)
    output_file = f"{os.path.splitext(clipfile)[0]}_output_{uuid.uuid4().hex[:6]}.mp4"
    final_clip.write_videofile(output_file)

    os.remove(tmp_clipfile)

    return CompositeVideoClip(song)
    

if __name__ == '__main__':
    try:
        file_source_midi = sys.argv[1]
        source_midi_track = int(sys.argv[2])
        file_source_clip = sys.argv[3]
        with_audio = True
        if len(sys.argv) > 4 and sys.argv[4] == '--no-audio':
            with_audio = False

    except IndexError:

        raise SystemExit("Usage:\n  PYTPMVCreator.py <midi file> <track number (-1 for auto)> <video clip> [--no-audio]\n\nCreate YTPMVs automatically from a MIDI file and one video clip for the specified track.\nRun the Helper program instead for a better experience!")


    if with_audio:

        render_video(file_source_clip, *get_semitones_timeline(file_source_midi, source_midi_track), with_audio=True).write_videofile("output_ytpmv.webm", 
                                                                                                             codec="libvpx",
                                                                                                             bitrate="5000k",
                                                                                                             fps=30,
                                                                                                             audio_codec="libvorbis",
                                                                                                             audio_bitrate="128k")

    else:

        render_video(file_source_clip, *get_semitones_timeline(file_source_midi, source_midi_track), with_audio=False).write_videofile("output_ytpmv.webm", 
                                                                                                             codec="libvpx",
                                                                                                             bitrate="5000k",
                                                                                                             fps=30)

    print("\nThanks! PYTPMVCreator job is done.")
    os.remove(tmp_clipfile)
