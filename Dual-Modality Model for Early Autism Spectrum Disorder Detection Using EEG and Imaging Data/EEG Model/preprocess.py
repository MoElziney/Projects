import os
import pandas as pd
import numpy as np
import mne
from scipy import signal
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# --- Configuration ---
DATA_DIR = Path("D:/ds006780-download")
PROCESSED_DIR = DATA_DIR / "processed_data_v2"
PROCESSED_DIR.mkdir(exist_ok=True)

EPOCH_DURATION = 2.0  
SFREQ = 512           

def get_subjects():
    participants_file = DATA_DIR / "participants.tsv"
    df = pd.read_csv(participants_file, sep='\t')
    df = df[df['group'].isin(['ASD', 'TD'])]
    return dict(zip(df['participant_id'], df['group']))

def preprocess_spectrogram(file_path, subject_id, group_label):
    """
    Alternative preprocessing: Extracts Time-Frequency Spectrograms (STFT) from EEG.
    """
    out_filename = PROCESSED_DIR / f"{subject_id}_{file_path.stem}_spec.npy"
    if out_filename.exists():
        print(f"Skipping {file_path.name} - Already processed.")
        return out_filename

    print(f"Processing Spectrogram: {file_path.name} -> {group_label}")
    try:
        if file_path.suffix == '.bdf':
            raw = mne.io.read_raw_bdf(file_path, preload=True, verbose='ERROR')
        elif file_path.suffix == '.eeg':
            vhdr_file = file_path.with_suffix('.vhdr')
            raw = mne.io.read_raw_brainvision(vhdr_file, preload=True, verbose='ERROR')
        else:
            return None

        if raw.info['sfreq'] != SFREQ:
            raw.resample(SFREQ)

        picks = mne.pick_types(raw.info, eeg=True, meg=False, stim=False, eog=False)
        if len(picks) == 0:
            raw.pick(raw.ch_names[:64])
        else:
            raw.pick(picks[:64])

        # Basic signal cleaning
        raw.filter(l_freq=1.0, h_freq=100.0, fir_design='firwin', verbose='ERROR')
        raw.notch_filter(freqs=60.0, fir_design='firwin', verbose='ERROR')
        raw.set_eeg_reference('average', projection=False, verbose='ERROR')

        epochs = mne.make_fixed_length_epochs(raw, duration=EPOCH_DURATION, preload=True, verbose='ERROR')
        data = epochs.get_data()
        
        # Artifact rejection (Peak-to-Peak)
        ptp_max = np.ptp(data, axis=2) 
        good_epochs_idx = np.all(ptp_max < 500e-6, axis=1)
        data = data[good_epochs_idx]
        
        if len(data) == 0:
            return None

        # --- Transformation: Short-Time Fourier Transform (STFT) ---
        # data shape: (Epochs, 64, Time_Points)
        # Using nperseg=128 (0.25s windows) with 50% overlap
        f, t, Zxx = signal.stft(data, fs=SFREQ, nperseg=128, noverlap=64, axis=-1)
        
        # We only care about frequencies up to 100Hz (the limit of our bandpass)
        freq_mask = f <= 100.0
        f_filtered = f[freq_mask]
        Zxx_filtered = Zxx[:, :, freq_mask, :]
        
        # Calculate Magnitude
        magnitude = np.abs(Zxx_filtered)
        
        # Log-Scaling (10 * log10(Power))
        # Adding 1e-8 to prevent log(0)
        log_mag = 10 * np.log10(magnitude**2 + 1e-8)
        
        # Z-score Normalization (per channel, per epoch)
        means = np.mean(log_mag, axis=(2, 3), keepdims=True)
        stds = np.std(log_mag, axis=(2, 3), keepdims=True)
        norm_spec = (log_mag - means) / (stds + 1e-8)
        
        # Final shape: (Epochs, Channels, Freqs, Time_Bins)
        # Note: We do NOT need task_id anymore.
        label = 1 if group_label == 'ASD' else 0

        out_dict = {
            'data': norm_spec, 
            'subject': subject_id,
            'label': label,
        }

        np.save(out_filename, out_dict)
        return out_filename

    except Exception as e:
        print(f"Error processing {file_path.name}: {e}")
        return None

if __name__ == "__main__":
    print("Starting Spectrogram Preprocessing Pipeline...")
    subject_map = get_subjects()
    print(f"Found {len(subject_map)} ASD/TD subjects.")

    processed_count = 0
    
    # Just process a single subject to test
    for subject, group in subject_map.items():
        subject_dir = DATA_DIR / subject / "eeg"
        if not subject_dir.exists():
            continue
            
        raw_files = list(subject_dir.glob("*_eeg.bdf")) + list(subject_dir.glob("*_eeg.eeg"))
        
        for file_path in raw_files:
            res = preprocess_spectrogram(file_path, subject, group)
            if res:
                processed_count += 1
                
    print(f"Finished full dataset processing. Total files processed: {processed_count}")