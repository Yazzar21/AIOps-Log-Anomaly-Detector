import os
import pandas as pd
import pytest

# Menentukan jalur root utama proyek secara otomatis agar terbaca dari subfolder test/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARSED_CSV = os.path.join(BASE_DIR, "data", "HDFS_parsed.csv")
RESULTS_CSV = os.path.join(BASE_DIR, "data", "anomaly_results.csv")

@pytest.fixture
def parsed_data():
    assert os.path.exists(PARSED_CSV), f"File hasil parsing belum tersedia di {PARSED_CSV}. Jalankan main.py terlebih dahulu."
    return pd.read_csv(PARSED_CSV)

@pytest.fixture
def anomaly_results():
    assert os.path.exists(RESULTS_CSV), f"File hasil deteksi belum tersedia di {RESULTS_CSV}. Jalankan main.py terlebih dahulu."
    return pd.read_csv(RESULTS_CSV)

def test_parsed_logs_not_empty(parsed_data):
    assert len(parsed_data) > 0, "Data log hasil parsing tidak boleh kosong."
    assert "EventId" in parsed_data.columns, "Kolom EventId wajib tersedia."

def test_no_null_values_in_feature_matrix(anomaly_results):
    null_count = anomaly_results.isnull().sum().sum()
    assert null_count == 0, f"Ditemukan {null_count} nilai null pada matriks hasil."

def test_valid_anomaly_flags(anomaly_results):
    unique_flags = set(anomaly_results["Anomaly_Flag"].unique())
    assert unique_flags.issubset({0, 1}), "Nilai Anomaly_Flag hanya boleh berisi 0 atau 1."