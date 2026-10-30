import os
from src.log_parser import parse_hdfs_logs
from src.train_detector import build_feature_matrix, train_and_detect

def run_pipeline():
    # Menentukan jalur absolut agar tersimpan tepat di folder proyek ini
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    raw_log = os.path.join(BASE_DIR, "data", "HDFS_2k.log")
    parsed_csv = os.path.join(BASE_DIR, "data", "HDFS_parsed.csv")
    templates_csv = os.path.join(BASE_DIR, "data", "HDFS_templates.csv")
    results_csv = os.path.join(BASE_DIR, "data", "anomaly_results.csv")
    model_file = os.path.join(BASE_DIR, "models", "isolation_forest_hdfs.pkl")

    print("[1/3] Menjalankan Drain3 Log Parser...")
    parsed_df = parse_hdfs_logs(raw_log, parsed_csv, templates_csv)
    print(f"      Berhasil memproses {len(parsed_df)} baris log.")

    print("[2/3] Membangun Event Count Feature Matrix...")
    feature_matrix = build_feature_matrix(parsed_df)
    print(f"      Terbentuk {feature_matrix.shape[0]} sesi BlockId dengan {feature_matrix.shape[1]} fitur.")

    print("[3/3] Melatih Isolation Forest & Mendeteksi Anomali...")
    results_df = train_and_detect(feature_matrix, model_file, results_csv, contamination=0.05)
    anomaly_count = results_df['Anomaly_Flag'].sum()
    print(f"      Selesai! Terdeteksi {anomaly_count} sesi anomali dari {len(results_df)} total sesi.")

if __name__ == "__main__":
    run_pipeline()