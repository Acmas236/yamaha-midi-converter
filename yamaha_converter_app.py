import streamlit as st
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import io

st.set_page_config(page_title="Yamaha MIDI Converter", page_icon="🎹")

st.title("🎹 Convertitore MIDI → Yamaha PSR-SX920")
st.markdown("Carica un file `.mid` e scarica la versione compatibile con Yamaha PSR-SX920.")

def insert_yamaha_markers(track):
    marker_list = [
        ('Intro A', 0),
        ('Main A', 480 * 4),
        ('Fill In A', 480 * 8),
        ('Ending A', 480 * 12),
    ]
    for name, time in marker_list:
        track.append(MetaMessage('marker', text=name, time=time))

def insert_sysex(track):
    sysex_msg = Message('sysex', data=[0x43, 0x7E, 0x00, 0x00, 0x7F, 0x00], time=0)
    track.insert(0, sysex_msg)

def convert_midi(midi_bytes):
    input_midi = MidiFile(file=io.BytesIO(midi_bytes))
    new_midi = MidiFile()
    new_midi.ticks_per_beat = input_midi.ticks_per_beat

    for i, track in enumerate(input_midi.tracks):
        new_track = MidiTrack()
        for msg in track:
            if msg.type in ['note_on', 'note_off', 'control_change']:
                if msg.channel == 0:
                    msg.channel = 9
                elif msg.channel in [1, 2, 3]:
                    msg.channel = 10 + (msg.channel - 1)
                new_track.append(msg)
            else:
                new_track.append(msg)

        if i == 0:
            insert_sysex(new_track)
            insert_yamaha_markers(new_track)

        new_midi.tracks.append(new_track)

    out_buffer = io.BytesIO()
    new_midi.save(out_buffer)
    out_buffer.seek(0)
    return out_buffer

uploaded_file = st.file_uploader("📂 Carica il tuo file MIDI", type=["mid"])

if uploaded_file:
    st.success("✅ File caricato con successo!")
    if st.button("Converti per Yamaha"):
        output_midi = convert_midi(uploaded_file.read())
        st.download_button(
            label="⬇️ Scarica file compatibile",
            data=output_midi,
            file_name=uploaded_file.name.replace(".mid", "_yamaha.mid"),
            mime="audio/midi"
        )
