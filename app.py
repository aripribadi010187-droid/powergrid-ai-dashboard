import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from data_loader import load_all_data, clear_data_cache
from ai_service import (
    generate_domain_insight,
    generate_executive_summary,
    ask_ai_assistant,
    get_groq_api_key,
    MODEL_NAME
)

# Page configuration
st.set_page_config(
    page_title="PowerGrid AI Intel - Dashboard Kelistrikan",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, responsive modern UI
st.markdown("""
<style>
    /* Metric Cards styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 2px;
    }
    .badge-normal {
        background-color: #065f46;
        color: #34d399;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-warning {
        background-color: #854d0e;
        color: #fde047;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .badge-danger {
        background-color: #991b1b;
        color: #fca5a5;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.75rem;
    }
    .ai-box {
        background-color: #1e1e2e;
        border-left: 4px solid #38bdf8;
        border-radius: 8px;
        padding: 18px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Load Data
data = load_all_data()
df_gi = data.get("gardu_induk", pd.DataFrame())
df_tr = data.get("transmisi", pd.DataFrame())
df_dis = data.get("distribusi", pd.DataFrame())
df_pem = data.get("pembangkit", pd.DataFrame())

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/electricity.png", width=64)
    st.title("⚡ PowerGrid AI")
    st.caption("AI-Powered Grid Analytics & Monitoring")
    st.markdown("---")

    st.subheader("⚙️ Status Koneksi")
    api_key = get_groq_api_key()
    if api_key:
        st.success(f"🟢 **Groq AI Active**\n`{MODEL_NAME}`")
    else:
        st.error("🔴 **Groq API Key Missing**\nCek file `.env`")

    st.markdown("---")
    st.subheader("🔄 Sinkronisasi Data")
    if st.button("🔄 Refresh Data Google Sheets", use_container_width=True):
        clear_data_cache()
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()

    st.caption(f"Terakhir diperbarui: {datetime.now().strftime('%H:%M:%S WIB')}")
    st.markdown("---")
    
    st.markdown("""
    **Sumber Data Aktif:**
    - ⚡ Gardu Induk (30 Unit)
    - 🌐 Transmisi (30 Jalur)
    - 🏘️ Distribusi (30 Rayon)
    - 🏭 Pembangkit (30 Unit)
    """)

# Main Header
st.title("⚡ Dashboard Operasional Kelistrikan Berbasis AI")
st.markdown("Integrasi Real-Time 4 Sektor Kelistrikan dengan Rekomendasi Cerdas Groq LLM (`openai/gpt-oss-120b`).")

# Create 5 main tabs as specified
tab_gi, tab_tr, tab_dis, tab_pem, tab_summary = st.tabs([
    "⚡ Gardu Induk",
    "🌐 Transmisi",
    "🏘️ Distribusi",
    "🏭 Pembangkit",
    "🧠 Summary & AI Rekomendasi"
])

# ==========================================
# TAB 1: GARDU INDUK
# ==========================================
with tab_gi:
    st.header("⚡ Sektor Gardu Induk (Substation)")
    st.caption("Monitoring Kapasitas, Level Tegangan, dan Status Operasi Gardu Induk")
    
    if df_gi.empty:
        st.warning("Data Gardu Induk tidak tersedia atau gagal dimuat.")
    else:
        # Metrik KPI
        total_gi = len(df_gi)
        total_kapasitas = df_gi["Kapasitas (MVA)"].sum() if "Kapasitas (MVA)" in df_gi.columns else 0
        avg_kapasitas = df_gi["Kapasitas (MVA)"].mean() if "Kapasitas (MVA)" in df_gi.columns else 0
        
        status_col = [c for c in df_gi.columns if "status" in c.lower()][0] if any("status" in c.lower() for c in df_gi.columns) else None
        normal_gi = len(df_gi[df_gi[status_col].str.lower() == "normal"]) if status_col else total_gi
        alert_gi = total_gi - normal_gi

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Gardu Induk</div>
                <div class="metric-value">{total_gi}</div>
                <div class="metric-sub">Unit Terdata</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Kapasitas Terpasang</div>
                <div class="metric-value">{total_kapasitas:,.0f} <span style="font-size:1.1rem">MVA</span></div>
                <div class="metric-sub">Rata-rata: {avg_kapasitas:.1f} MVA / Gardu</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Status Normal</div>
                <div class="metric-value" style="color:#34d399">{normal_gi} <span style="font-size:1.1rem">({(normal_gi/total_gi*100):.0f}%)</span></div>
                <div class="metric-sub">Operasi Handal</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Perlu Perhatian / Beban Tinggi</div>
                <div class="metric-value" style="color:{'#f87171' if alert_gi>0 else '#34d399'}">{alert_gi}</div>
                <div class="metric-sub">Status Non-Normal</div>
            </div>
            """, unsafe_allow_html=True)

        # Visualisasi
        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.subheader("📊 Kapasitas Gardu Induk (MVA)")
            fig_bar = px.bar(
                df_gi.sort_values(by="Kapasitas (MVA)", ascending=True),
                x="Kapasitas (MVA)",
                y="Nama Gardu",
                orientation="h",
                color=status_col,
                color_discrete_map={"Normal": "#0284c7", "Beban Tinggi": "#f97316"},
                title="Kapasitas Tiap Gardu Induk Berdasarkan Status",
                height=550
            )
            fig_bar.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_bar, use_container_width=True)

        with c_right:
            st.subheader("🍩 Distribusi Status Operasi")
            fig_pie = px.pie(
                df_gi,
                names=status_col,
                title="Proporsi Kondisi Gardu Induk",
                color=status_col,
                color_discrete_map={"Normal": "#10b981", "Beban Tinggi": "#f59e0b"},
                hole=0.45,
                height=350
            )
            fig_pie.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_pie, use_container_width=True)

            # Warning Box jika ada beban tinggi
            if alert_gi > 0:
                st.markdown("##### ⚠️ Gardu Dalam Pantauan Khusus:")
                alerts_df = df_gi[df_gi[status_col].str.lower() != "normal"]
                for _, r in alerts_df.iterrows():
                    st.warning(f"**{r.get('Nama Gardu', 'GI')}** ({r.get('Kapasitas (MVA)')} MVA) - Status: `{r.get(status_col)}` | Catatan: *{r.get('Catatan', '-')}*")

        # Tabel Data & Filter
        st.subheader("📋 Tabel Data Gardu Induk")
        col_f1, col_f2 = st.columns([2, 2])
        with col_f1:
            search_gi = st.text_input("🔍 Cari Nama Gardu:", key="search_gi")
        with col_f2:
            status_opts = ["Semua Status"] + list(df_gi[status_col].unique()) if status_col else ["Semua Status"]
            filter_status_gi = st.selectbox("Filter Status:", status_opts, key="filter_status_gi")

        filtered_gi = df_gi.copy()
        if search_gi:
            filtered_gi = filtered_gi[filtered_gi["Nama Gardu"].str.contains(search_gi, case=False, na=False)]
        if filter_status_gi != "Semua Status":
            filtered_gi = filtered_gi[filtered_gi[status_col] == filter_status_gi]

        st.dataframe(filtered_gi, use_container_width=True, height=280)

        # AI Quick Insight Button
        st.markdown("---")
        st.subheader("🤖 Analisis AI Khusus Gardu Induk")
        if st.button("💡 Analisis Kondisi Gardu Induk dengan AI", key="btn_ai_gi"):
            with st.spinner("Menghubungi model Groq openai/gpt-oss-120b..."):
                insight_gi = generate_domain_insight("Gardu Induk", df_gi)
                st.markdown(f'<div class="ai-box">{insight_gi}</div>', unsafe_allow_html=True)

# ==========================================
# TAB 2: TRANSMISI
# ==========================================
with tab_tr:
    st.header("🌐 Sektor Transmisi Daya")
    st.caption("Monitoring Jaringan Transmisi Tegangan Tinggi (500 kV & 150 kV)")
    
    if df_tr.empty:
        st.warning("Data Transmisi tidak tersedia atau gagal dimuat.")
    else:
        total_tr = len(df_tr)
        total_panjang_tr = df_tr["Panjang (km)"].sum() if "Panjang (km)" in df_tr.columns else 0
        
        status_tr_col = [c for c in df_tr.columns if "status" in c.lower()][0] if any("status" in c.lower() for c in df_tr.columns) else None
        normal_tr = len(df_tr[df_tr[status_tr_col].str.lower() == "normal"]) if status_tr_col else total_tr
        alert_tr = total_tr - normal_tr

        tegangan_500 = len(df_tr[df_tr["Tegangan (kV)"] == 500]) if "Tegangan (kV)" in df_tr.columns else 0
        tegangan_150 = len(df_tr[df_tr["Tegangan (kV)"] == 150]) if "Tegangan (kV)" in df_tr.columns else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Jalur Transmisi</div>
                <div class="metric-value">{total_tr}</div>
                <div class="metric-sub">SUTET / SUTT</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Panjang Jalur</div>
                <div class="metric-value">{total_panjang_tr:,.0f} <span style="font-size:1.1rem">km</span></div>
                <div class="metric-sub">Rata-rata: {(total_panjang_tr/total_tr if total_tr else 0):.1f} km / jalur</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Klasifikasi Tegangan</div>
                <div class="metric-value">{tegangan_500} <span style="font-size:1.1rem">SUTET (500kV)</span></div>
                <div class="metric-sub">{tegangan_150} Jalur SUTT (150kV)</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Jalur Normal / Gangguan</div>
                <div class="metric-value" style="color:{'#34d399' if alert_tr==0 else '#f87171'}">{normal_tr} <span style="font-size:1.1rem">/ {alert_tr}</span></div>
                <div class="metric-sub">{'Semua Jalur Sehat' if alert_tr==0 else f'{alert_tr} Perlu Inspeksi/Perbaikan'}</div>
            </div>
            """, unsafe_allow_html=True)

        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.subheader("📊 Panjang Jalur Transmisi (km)")
            fig_bar_tr = px.bar(
                df_tr.sort_values(by="Panjang (km)", ascending=True),
                x="Panjang (km)",
                y="Nama Jalur",
                orientation="h",
                color=status_tr_col,
                color_discrete_map={"Normal": "#0ea5e9", "Gangguan Minor": "#ef4444"},
                title="Panjang Tiap Jalur Transmisi Antar Wilayah",
                height=550
            )
            fig_bar_tr.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_bar_tr, use_container_width=True)

        with c_right:
            st.subheader("🍩 Breakdown Tegangan Transmisi")
            fig_pie_teg = px.pie(
                df_tr,
                names="Tegangan (kV)",
                title="Proporsi Jalur Berdasarkan Tegangan (kV)",
                color_discrete_sequence=["#38bdf8", "#818cf8"],
                hole=0.45,
                height=350
            )
            fig_pie_teg.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_pie_teg, use_container_width=True)

            if alert_tr > 0:
                st.markdown("##### 🚨 Jalur Perlu Penanganan:")
                alerts_tr_df = df_tr[df_tr[status_tr_col].str.lower() != "normal"]
                for _, r in alerts_tr_df.iterrows():
                    st.error(f"**{r.get('Nama Jalur')}** ({r.get('Panjang (km)')} km, {r.get('Tegangan (kV)')} kV) - Status: `{r.get(status_tr_col)}` | Catatan: *{r.get('Catatan', '-')}*")

        st.subheader("📋 Tabel Data Transmisi")
        col_f1, col_f2 = st.columns([2, 2])
        with col_f1:
            search_tr = st.text_input("🔍 Cari Nama Jalur:", key="search_tr")
        with col_f2:
            teg_opts = ["Semua Tegangan"] + [str(int(t)) for t in df_tr["Tegangan (kV)"].unique()] if "Tegangan (kV)" in df_tr.columns else ["Semua"]
            filter_teg_tr = st.selectbox("Filter Tegangan (kV):", teg_opts, key="filter_teg_tr")

        filtered_tr = df_tr.copy()
        if search_tr:
            filtered_tr = filtered_tr[filtered_tr["Nama Jalur"].str.contains(search_tr, case=False, na=False)]
        if filter_teg_tr != "Semua Tegangan":
            filtered_tr = filtered_tr[filtered_tr["Tegangan (kV)"] == float(filter_teg_tr)]

        st.dataframe(filtered_tr, use_container_width=True, height=280)

        # AI Quick Insight Button
        st.markdown("---")
        st.subheader("🤖 Analisis AI Khusus Transmisi")
        if st.button("💡 Analisis Jaringan Transmisi dengan AI", key="btn_ai_tr"):
            with st.spinner("Menghubungi model Groq openai/gpt-oss-120b..."):
                insight_tr = generate_domain_insight("Transmisi Tenaga Listrik", df_tr)
                st.markdown(f'<div class="ai-box">{insight_tr}</div>', unsafe_allow_html=True)

# ==========================================
# TAB 3: DISTRIBUSI
# ==========================================
with tab_dis:
    st.header("🏘️ Sektor Distribusi Listrik (Rayon)")
    st.caption("Monitoring Panjang Jaringan Distribusi 20 kV di Seluruh Rayon")
    
    if df_dis.empty:
        st.warning("Data Distribusi tidak tersedia atau gagal dimuat.")
    else:
        total_rayon = len(df_dis)
        total_panjang_dis = df_dis["Panjang Jaringan (km)"].sum() if "Panjang Jaringan (km)" in df_dis.columns else 0
        avg_panjang_dis = total_panjang_dis / total_rayon if total_rayon else 0
        
        status_dis_col = [c for c in df_dis.columns if "status" in c.lower()][0] if any("status" in c.lower() for c in df_dis.columns) else None
        normal_dis = len(df_dis[df_dis[status_dis_col].str.lower() == "normal"]) if status_dis_col else total_rayon
        alert_dis = total_rayon - normal_dis

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Rayon Pelayanan</div>
                <div class="metric-value">{total_rayon}</div>
                <div class="metric-sub">Wilayah Kerja</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Panjang Jaringan</div>
                <div class="metric-value">{total_panjang_dis:,.0f} <span style="font-size:1.1rem">km</span></div>
                <div class="metric-sub">Tegangan Menengah 20 kV</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Rata-rata Panjang / Rayon</div>
                <div class="metric-value">{avg_panjang_dis:.1f} <span style="font-size:1.1rem">km</span></div>
                <div class="metric-sub">Distribusi Jaringan</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Rayon Bermasalah / Gangguan</div>
                <div class="metric-value" style="color:{'#34d399' if alert_dis==0 else '#f87171'}">{alert_dis}</div>
                <div class="metric-sub">{'Semua Rayon Normal' if alert_dis==0 else f'{alert_dis} Perlu Perbaikan'}</div>
            </div>
            """, unsafe_allow_html=True)

        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.subheader("📊 Top Rayon Berdasarkan Panjang Jaringan (km)")
            top_dis = df_dis.sort_values(by="Panjang Jaringan (km)", ascending=True)
            fig_bar_dis = px.bar(
                top_dis,
                x="Panjang Jaringan (km)",
                y="Rayon",
                orientation="h",
                color=status_dis_col,
                color_discrete_map={"Normal": "#6366f1", "Gangguan Minor": "#ef4444"},
                title="Panjang Jaringan Distribusi per Rayon",
                height=550
            )
            fig_bar_dis.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_bar_dis, use_container_width=True)

        with c_right:
            st.subheader("🍩 Status Kesehatan Jaringan")
            fig_pie_dis = px.pie(
                df_dis,
                names=status_dis_col,
                title="Status Distribusi Rayon",
                color=status_dis_col,
                color_discrete_map={"Normal": "#10b981", "Gangguan Minor": "#ef4444"},
                hole=0.45,
                height=350
            )
            fig_pie_dis.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_pie_dis, use_container_width=True)

            if alert_dis > 0:
                st.markdown("##### 🚨 Rayon Dalam Penanganan:")
                alerts_dis_df = df_dis[df_dis[status_dis_col].str.lower() != "normal"]
                for _, r in alerts_dis_df.iterrows():
                    st.error(f"**Rayon {r.get('Rayon')}** ({r.get('Panjang Jaringan (km)')} km) - Status: `{r.get(status_dis_col)}` | Catatan: *{r.get('Catatan', '-')}*")

        st.subheader("📋 Tabel Data Jaringan Distribusi")
        col_f1, col_f2 = st.columns([2, 2])
        with col_f1:
            search_dis = st.text_input("🔍 Cari Nama Rayon:", key="search_dis")
        with col_f2:
            status_opts_dis = ["Semua Status"] + list(df_dis[status_dis_col].unique()) if status_dis_col else ["Semua"]
            filter_status_dis = st.selectbox("Filter Status Rayon:", status_opts_dis, key="filter_status_dis")

        filtered_dis = df_dis.copy()
        if search_dis:
            filtered_dis = filtered_dis[filtered_dis["Rayon"].str.contains(search_dis, case=False, na=False)]
        if filter_status_dis != "Semua Status":
            filtered_dis = filtered_dis[filtered_dis[status_dis_col] == filter_status_dis]

        st.dataframe(filtered_dis, use_container_width=True, height=280)

        # AI Quick Insight Button
        st.markdown("---")
        st.subheader("🤖 Analisis AI Khusus Distribusi")
        if st.button("💡 Analisis Jaringan Distribusi dengan AI", key="btn_ai_dis"):
            with st.spinner("Menghubungi model Groq openai/gpt-oss-120b..."):
                insight_dis = generate_domain_insight("Distribusi Tenaga Listrik", df_dis)
                st.markdown(f'<div class="ai-box">{insight_dis}</div>', unsafe_allow_html=True)

# ==========================================
# TAB 4: PEMBANGKIT
# ==========================================
with tab_pem:
    st.header("🏭 Sektor Pembangkitan Listrik")
    st.caption("Monitoring Kapasitas Terpasang, Bauran Energi (PLTU, PLTA, PLTG), dan Kesiapan Unit")
    
    if df_pem.empty:
        st.warning("Data Pembangkit tidak tersedia atau gagal dimuat.")
    else:
        total_pem = len(df_pem)
        total_kapasitas_pem = df_pem["Kapasitas (MW)"].sum() if "Kapasitas (MW)" in df_pem.columns else 0
        
        status_pem_col = [c for c in df_pem.columns if "status" in c.lower()][0] if any("status" in c.lower() for c in df_pem.columns) else None
        normal_pem = len(df_pem[df_pem[status_pem_col].str.lower() == "normal"]) if status_pem_col else total_pem
        alert_pem = total_pem - normal_pem

        # Breakdown by Energy Source
        batubara_mw = df_pem[df_pem["Jenis"].str.lower() == "batubara"]["Kapasitas (MW)"].sum() if "Jenis" in df_pem.columns else 0
        hidro_mw = df_pem[df_pem["Jenis"].str.lower() == "hidro"]["Kapasitas (MW)"].sum() if "Jenis" in df_pem.columns else 0
        gas_mw = df_pem[df_pem["Jenis"].str.lower() == "gas"]["Kapasitas (MW)"].sum() if "Jenis" in df_pem.columns else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Unit Pembangkit</div>
                <div class="metric-value">{total_pem}</div>
                <div class="metric-sub">PLTU, PLTA & PLTG</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Total Kapasitas Terpasang</div>
                <div class="metric-value">{total_kapasitas_pem:,.0f} <span style="font-size:1.1rem">MW</span></div>
                <div class="metric-sub">Daya Mampu Pasok</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            ebt_pct = (hidro_mw / total_kapasitas_pem * 100) if total_kapasitas_pem else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Bauran Energi Bersih (Hidro)</div>
                <div class="metric-value" style="color:#34d399">{hidro_mw:,.0f} <span style="font-size:1.1rem">MW ({ebt_pct:.1f}%)</span></div>
                <div class="metric-sub">PLTA Hijau</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Unit Gangguan / Check</div>
                <div class="metric-value" style="color:{'#34d399' if alert_pem==0 else '#f87171'}">{alert_pem}</div>
                <div class="metric-sub">{'Seluruh Pembangkit Normal' if alert_pem==0 else f'{alert_pem} Perlu Tindakan'}</div>
            </div>
            """, unsafe_allow_html=True)

        c_left, c_right = st.columns([3, 2])
        with c_left:
            st.subheader("📊 Top 10 Pembangkit Terbesar (MW)")
            top10_pem = df_pem.sort_values(by="Kapasitas (MW)", ascending=False).head(10).sort_values(by="Kapasitas (MW)", ascending=True)
            fig_bar_pem = px.bar(
                top10_pem,
                x="Kapasitas (MW)",
                y="Nama PLTU/PLTA/PLTG",
                orientation="h",
                color="Jenis",
                color_discrete_map={"Batubara": "#64748b", "Hidro": "#10b981", "Gas": "#f59e0b"},
                title="Top 10 Kapasitas Pembangkit Terbesar",
                height=550
            )
            fig_bar_pem.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_bar_pem, use_container_width=True)

        with c_right:
            st.subheader("🍩 Bauran Energi Pembangkitan (MW)")
            fig_pie_mix = px.pie(
                df_pem,
                names="Jenis",
                values="Kapasitas (MW)",
                title="Komposisi Energi Primer (MW)",
                color="Jenis",
                color_discrete_map={"Batubara": "#475569", "Hidro": "#10b981", "Gas": "#f59e0b"},
                hole=0.45,
                height=350
            )
            fig_pie_mix.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_pie_mix, use_container_width=True)

            if alert_pem > 0:
                st.markdown("##### 🚨 Unit Pembangkit Dalam Pemeliharaan:")
                alerts_pem_df = df_pem[df_pem[status_pem_col].str.lower() != "normal"]
                for _, r in alerts_pem_df.iterrows():
                    st.error(f"**{r.get('Nama PLTU/PLTA/PLTG')}** ({r.get('Kapasitas (MW)')} MW, {r.get('Jenis')}) - Status: `{r.get(status_pem_col)}` | Catatan: *{r.get('Catatan', '-')}*")

        st.subheader("📋 Tabel Data Unit Pembangkit")
        col_f1, col_f2 = st.columns([2, 2])
        with col_f1:
            search_pem = st.text_input("🔍 Cari Nama Pembangkit:", key="search_pem")
        with col_f2:
            jenis_opts = ["Semua Jenis"] + list(df_pem["Jenis"].unique()) if "Jenis" in df_pem.columns else ["Semua"]
            filter_jenis_pem = st.selectbox("Filter Jenis Pembangkit:", jenis_opts, key="filter_jenis_pem")

        filtered_pem = df_pem.copy()
        if search_pem:
            filtered_pem = filtered_pem[filtered_pem["Nama PLTU/PLTA/PLTG"].str.contains(search_pem, case=False, na=False)]
        if filter_jenis_pem != "Semua Jenis":
            filtered_pem = filtered_pem[filtered_pem["Jenis"] == filter_jenis_pem]

        st.dataframe(filtered_pem, use_container_width=True, height=280)

        # AI Quick Insight Button
        st.markdown("---")
        st.subheader("🤖 Analisis AI Khusus Pembangkitan")
        if st.button("💡 Analisis Kondisi Pembangkit dengan AI", key="btn_ai_pem"):
            with st.spinner("Menghubungi model Groq openai/gpt-oss-120b..."):
                insight_pem = generate_domain_insight("Pembangkit Tenaga Listrik", df_pem)
                st.markdown(f'<div class="ai-box">{insight_pem}</div>', unsafe_allow_html=True)

# ==========================================
# TAB 5: SUMMARY & AI RECOMMENDATIONS
# ==========================================
with tab_summary:
    st.header("🧠 Tab Summary: Rekomendasi Terpadu Berbasis AI")
    st.caption("Sintesis Komprehensif Lintas 4 Sektor Kelistrikan Menggunakan Model Groq `openai/gpt-oss-120b`")

    # Macro Overview Grid
    st.subheader("🌐 Kondisi Makro Sistem Kelistrikan Terpadu")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">1. Total Pasokan Pembangkit</div>
            <div class="metric-value">{df_pem['Kapasitas (MW)'].sum() if not df_pem.empty else 0:,.0f} <span style="font-size:1.1rem">MW</span></div>
            <div class="metric-sub">{len(df_pem)} Unit Pembangkit</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">2. Jaringan Transmisi</div>
            <div class="metric-value">{df_tr['Panjang (km)'].sum() if not df_tr.empty else 0:,.0f} <span style="font-size:1.1rem">km</span></div>
            <div class="metric-sub">{len(df_tr)} Jalur Interkoneksi</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">3. Kapasitas Gardu Induk</div>
            <div class="metric-value">{df_gi['Kapasitas (MVA)'].sum() if not df_gi.empty else 0:,.0f} <span style="font-size:1.1rem">MVA</span></div>
            <div class="metric-sub">{len(df_gi)} Substation Trafo</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">4. Jaringan Distribusi Rayon</div>
            <div class="metric-value">{df_dis['Panjang Jaringan (km)'].sum() if not df_dis.empty else 0:,.0f} <span style="font-size:1.1rem">km</span></div>
            <div class="metric-sub">{len(df_dis)} Rayon Pelanggan</div>
        </div>
        """, unsafe_allow_html=True)

    # Cross-Sector Anomaly Tracker
    st.markdown("---")
    st.subheader("🚨 Pusat Pantauan Anomali & Risiko Lintas Sektor")
    
    anomalies_found = []
    
    # Check Gardu Induk
    if not df_gi.empty and "Status Operasi" in df_gi.columns:
        ab = df_gi[df_gi["Status Operasi"].str.lower() != "normal"]
        for _, r in ab.iterrows():
            anomalies_found.append({"Sektor": "⚡ Gardu Induk", "Entitas": r.get("Nama Gardu"), "Status": r.get("Status Operasi"), "Catatan": r.get("Catatan")})
            
    # Check Transmisi
    if not df_tr.empty and "Status" in df_tr.columns:
        ab = df_tr[df_tr["Status"].str.lower() != "normal"]
        for _, r in ab.iterrows():
            anomalies_found.append({"Sektor": "🌐 Transmisi", "Entitas": r.get("Nama Jalur"), "Status": r.get("Status"), "Catatan": r.get("Catatan")})

    # Check Distribusi
    if not df_dis.empty and "Status" in df_dis.columns:
        ab = df_dis[df_dis["Status"].str.lower() != "normal"]
        for _, r in ab.iterrows():
            anomalies_found.append({"Sektor": "🏘️ Distribusi", "Entitas": f"Rayon {r.get('Rayon')}", "Status": r.get("Status"), "Catatan": r.get("Catatan")})

    # Check Pembangkit
    if not df_pem.empty and "Status" in df_pem.columns:
        ab = df_pem[df_pem["Status"].str.lower() != "normal"]
        for _, r in ab.iterrows():
            anomalies_found.append({"Sektor": "🏭 Pembangkit", "Entitas": r.get("Nama PLTU/PLTA/PLTG"), "Status": r.get("Status"), "Catatan": r.get("Catatan")})

    if anomalies_found:
        df_anomalies = pd.DataFrame(anomalies_found)
        st.dataframe(df_anomalies, use_container_width=True)
    else:
        st.success("✅ Tidak terdeteksi anomali! Seluruh sektor berada dalam status operasi normal.")

    # Executive AI Recommendation Section
    st.markdown("---")
    st.subheader("📑 Rekomendasi Eksekutif & Rencana Strategis AI")
    st.info("💡 Tekan tombol di bawah untuk menghasilkan analisis sintesis menyeluruh dari model AI Groq `openai/gpt-oss-120b`.")

    if "executive_summary_content" not in st.session_state:
        st.session_state.executive_summary_content = None

    col_btn, col_empty = st.columns([2, 3])
    with col_btn:
        if st.button("🚀 Generate Rekomendasi AI Menyeluruh", type="primary", use_container_width=True):
            with st.spinner("Model Groq sedang menganalisis seluruh data kelistrikan..."):
                st.session_state.executive_summary_content = generate_executive_summary(data)

    if st.session_state.executive_summary_content:
        st.markdown(f'<div class="ai-box">{st.session_state.executive_summary_content}</div>', unsafe_allow_html=True)
        st.download_button(
            label="📥 Download Laporan Rekomendasi AI (.md)",
            data=st.session_state.executive_summary_content,
            file_name=f"Rekomendasi_Sistem_Kelistrikan_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown"
        )

    # Interactive Q&A Assistant Section
    st.markdown("---")
    st.subheader("💬 Tanya Jawab Interaktif dengan Asisten AI (Ask AI)")
    st.caption("Ajukan pertanyaan spesifik terkait beban gardu, jalur transmisi, bauran pembangkit, atau mitigasi kendala.")

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Halo! Saya Asisten AI Sistem Kelistrikan. Ada yang ingin Anda tanyakan seputar data Gardu Induk, Transmisi, Distribusi, atau Pembangkit?"}
        ]

    # Render Chat History
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            role = msg["role"]
            content = msg["content"]
            if hasattr(st, "chat_message"):
                with st.chat_message(role):
                    st.markdown(content)
            else:
                if role == "user":
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: white; padding: 12px 18px; border-radius: 14px 14px 2px 14px; margin: 8px 0; max-width: 85%; margin-left: auto; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <strong style="font-size:0.85rem; color: #bae6fd;">👤 Anda:</strong><br>
                        <div style="margin-top: 4px;">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background-color: #1e293b; border: 1px solid #334155; color: #f8fafc; padding: 14px 18px; border-radius: 14px 14px 14px 2px; margin: 8px 0; max-width: 90%; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        <strong style="font-size:0.85rem; color: #38bdf8;">🤖 Asisten AI Grid:</strong><br>
                        <div style="margin-top: 6px;">{content}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # Chat Input Handler
    def process_chat_query(query_text):
        if not query_text or not query_text.strip():
            return
        st.session_state.chat_messages.append({"role": "user", "content": query_text})
        with st.spinner("Asisten AI sedang menganalisis dan menyusun jawaban..."):
            ai_reply = ask_ai_assistant(query_text, data, st.session_state.chat_messages)
            st.session_state.chat_messages.append({"role": "assistant", "content": ai_reply})
        if hasattr(st, "rerun"):
            st.rerun()
        else:
            st.experimental_rerun()

    if hasattr(st, "chat_input"):
        user_query = st.chat_input("Tulis pertanyaan Anda seputar sistem kelistrikan di sini...")
        if user_query:
            process_chat_query(user_query)
    else:
        with st.form(key="chat_input_form", clear_on_submit=True):
            user_query = st.text_input("Ajukan pertanyaan Anda seputar sistem kelistrikan:", key="custom_chat_input", placeholder="Contoh: Gardu mana saja yang mengalami beban tinggi dan apa dampaknya?")
            submit_btn = st.form_submit_button("🚀 Kirim Pertanyaan", use_container_width=True)
            if submit_btn and user_query:
                process_chat_query(user_query)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>"
    "⚡ PowerGrid AI Intel Dashboard | Dikembangkan dengan Streamlit & Groq AI (openai/gpt-oss-120b) | Sumber Data: Google Sheets Terpadu"
    "</div>",
    unsafe_allow_html=True
)

