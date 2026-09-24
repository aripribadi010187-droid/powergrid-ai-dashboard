import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL_NAME = "openai/gpt-oss-120b"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

def get_groq_api_key():
    return os.getenv("GROQ_API") or os.getenv("GROQ_API_KEY")

def get_groq_client():
    api_key = get_groq_api_key()
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url=GROQ_BASE_URL)

def summarize_dataframe_for_ai(df: pd.DataFrame, title: str) -> str:
    """Create a structured markdown summary of a dataframe for LLM prompt."""
    if df.empty:
        return f"### {title}\nData tidak tersedia.\n"
    
    total_records = len(df)
    summary_lines = [f"### Data {title} (Total {total_records} entitas):"]
    
    # Identify non-normal status items
    status_cols = [c for c in df.columns if "status" in c.lower()]
    if status_cols:
        status_col = status_cols[0]
        abnormal = df[df[status_col].astype(str).str.lower() != "normal"]
        if not abnormal.empty:
            summary_lines.append(f"- **Peringatan/Anomali ({len(abnormal)} item):**")
            for _, row in abnormal.iterrows():
                row_info = ", ".join([f"{col}: {val}" for col, val in row.items() if col != "No"])
                summary_lines.append(f"  * {row_info}")
        else:
            summary_lines.append("- Seluruh unit/jalur dalam kondisi status Normal.")

    # Numerical metrics
    num_cols = df.select_dtypes(include="number").columns
    for c in num_cols:
        if c.lower() != "no":
            summary_lines.append(f"- Total {c}: {df[c].sum():,.1f} | Rata-rata: {df[c].mean():,.1f} | Maksimum: {df[c].max():,.1f}")

    # Top items sample
    sample_items = df.head(8).to_dict(orient="records")
    summary_lines.append(f"- Sample Data (8 data pertama): {json.dumps(sample_items, ensure_ascii=False)}")
    
    return "\n".join(summary_lines)

def generate_domain_insight(domain_name: str, df: pd.DataFrame) -> str:
    """Generate quick AI diagnosis for a specific domain tab."""
    client = get_groq_client()
    if not client:
        return "⚠️ Kunci API Groq (`GROQ_API`) tidak ditemukan di file `.env`. Silakan periksa konfigurasi Anda."
    
    data_summary = summarize_dataframe_for_ai(df, domain_name)
    
    prompt = f"""Anda adalah Sistem Analis dan Konsultan Senior Operasi Sistem Tenaga Listrik PLN.
Analisis data operasional berikut untuk sektor: {domain_name}.

{data_summary}

Berikan analisis mendalam dan rekomendasi taktis dengan format:
1. 🔍 **Diagnosa Kondisi & Kesehatan Operasional** (Identifikasi beban, kapasitas, atau anomali)
2. ⚠️ **Analisis Risiko & Titik Kritis** (Unit/jalur/gardu yang memerlukan perhatian khusus segera)
3. 🛠️ **Rekomendasi Tindakan Operasional (SOP & Maintenance)**

Gunakan bahasa Indonesia yang profesional, ringkas, berbobot, dan berbasis data langsung dari informasi di atas."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Anda adalah AI Analis Sistem Tenaga Listrik profesional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Terjadi kesalahan saat memanggil AI Groq ({MODEL_NAME}): {str(e)}"

def generate_executive_summary(all_data: dict) -> str:
    """Generate comprehensive cross-domain AI recommendations for Tab Summary."""
    client = get_groq_client()
    if not client:
        return "⚠️ Kunci API Groq (`GROQ_API`) tidak ditemukan di file `.env`. Silakan periksa konfigurasi Anda."
    
    summaries = []
    for domain_key, title in [
        ("pembangkit", "Pembangkitan Listrik"),
        ("transmisi", "Transmisi Daya Listrik"),
        ("gardu_induk", "Gardu Induk (Substation)"),
        ("distribusi", "Jaringan Distribusi Tenaga Listrik")
    ]:
        df = all_data.get(domain_key, pd.DataFrame())
        summaries.append(summarize_dataframe_for_ai(df, title))
    
    combined_data = "\n\n".join(summaries)
    
    prompt = f"""Anda adalah Chief Power System Advisor / Kepala Operasi Sistem Tenaga Listrik Nasional.
Berikut adalah data operasional komprehensif dari 4 domain sistem kelistrikan (Pembangkitan -> Transmisi -> Gardu Induk -> Distribusi):

{combined_data}

Buatlah **Laporan Rekomendasi Eksekutif & Strategis Terpadu** dengan struktur berikut:

# 📊 1. RINGKASAN EKSEKUTIF KESEHATAN SISTEM KELISTRIKAN
- Sintesis kondisi makro kelistrikan end-to-end (dari pasokan pembangkit, transmisi, gardu, hingga distribusi rayon).

# 🚨 2. ANALISIS KEMACETAN (BOTTLENECK) & TITIK RAWAN LINTAS SEKTOR
- Sorot keterkaitan antar anomali (contoh: beban tinggi di Gardu Induk vs pasokan dari transmisi/pembangkit, rayon yang berisiko gangguan).

# ⚡ 3. RENCANA AKSI MITIGASI CEPAT (JANGKA PENDEK / 0 - 30 HARI)
- Tindakan pemeliharaan preventif/korektif spesifik per lokasi/unit bermasalah.

# 📈 4. REKOMENDASI STRATEGIS JANGKA MENENGAH & PANJANG (1 - 3 TAHUN)
- Optimalisasi bauran energi (EBT/Hidro vs Gas vs Batubara), rencana penguatan transmisi & manuver gardu induk untuk keandalan jaringan.

Gunakan format Markdown rapi, dengan poin-poin tegas, indikator emoji yang relevan, dan analisis yang tajam berbasis data nyata di atas."""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Anda adalah Senior Power Grid Strategist dan AI Advisor Sistem Kelistrikan."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Terjadi kesalahan saat memanggil AI Groq ({MODEL_NAME}): {str(e)}"

def ask_ai_assistant(query: str, all_data: dict, chat_history: list = None) -> str:
    """Interactive chat with AI about the electricity data."""
    client = get_groq_client()
    if not client:
        return "⚠️ Kunci API Groq (`GROQ_API`) tidak ditemukan di file `.env`."
    
    summaries = []
    for domain_key, title in [
        ("pembangkit", "Pembangkitan"),
        ("transmisi", "Transmisi"),
        ("gardu_induk", "Gardu Induk"),
        ("distribusi", "Distribusi")
    ]:
        df = all_data.get(domain_key, pd.DataFrame())
        summaries.append(summarize_dataframe_for_ai(df, title))
    
    data_context = "\n\n".join(summaries)
    
    system_instruction = f"""Anda adalah Asisten Virtual Cerdas Operasi Sistem Tenaga Listrik.
Berikut adalah data sistem kelistrikan yang aktif saat ini:

{data_context}

Jawab pertanyaan pengguna dengan akurat, ramah, berbasis data di atas, dan sertakan rekomendasi teknis jika relevan."""

    messages = [{"role": "system", "content": system_instruction}]
    
    if chat_history:
        for msg in chat_history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
            
    messages.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Terjadi kesalahan: {str(e)}"

