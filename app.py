import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client


# ─────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Daily Check-In Siswa",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0ea5e9, #2563eb);
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }

.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2.2rem; font-weight: 700; color: #ffffff;
    letter-spacing: -1px; text-align: center; margin-bottom: 0.2rem;
}
.sub-title {
    font-size: 0.95rem; color: #a78bfa; text-align: center;
    margin-bottom: 2rem; font-weight: 400;
}
.card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 18px; padding: 2rem;
    backdrop-filter: blur(12px); margin-bottom: 1.5rem;
}
.badge {
    display: inline-block; padding: 4px 14px; border-radius: 999px;
    font-size: 0.75rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
}
.badge-dosen { background: #7c3aed; color: #fff; }
.badge-siswa { background: #0ea5e9; color: #fff; }
.badge-ortu  { background: #16a34a; color: #fff; }

.section-header {
    font-size: 1.1rem; font-weight: 700; color: #e2e8f0;
    border-left: 4px solid #7c3aed; padding-left: 12px;
    margin: 1.5rem 0 1rem 0;
}
.stat-box {
    background: rgba(124,58,237,0.18);
    border: 1px solid rgba(124,58,237,0.35);
    border-radius: 14px; padding: 1rem 1.4rem; text-align: center;
}
.stat-num { font-size: 2rem; font-weight: 800; color: #a78bfa; }
.stat-lbl { font-size: 0.78rem; color: #94a3b8; font-weight: 500; text-transform: uppercase; letter-spacing: 0.8px; }

.login-wrap { max-width: 440px; margin: 4rem auto 0; }

.logout-btn > button {
    background: rgba(239,68,68,0.15) !important; color: #f87171 !important;
    border: 1px solid rgba(239,68,68,0.35) !important;
    border-radius: 10px !important; font-weight: 600 !important; font-size: 0.85rem !important;
}
.stTextInput > div > div > input,
input[type="text"], input[type="password"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important; color: #111827 !important;
}
.stTextArea > div > div > textarea {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important; color: #f1f5f9 !important;
}
.stSelectbox > div > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.18) !important;
    border-radius: 10px !important; color: #f1f5f9 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important; border-radius: 12px !important;
    font-weight: 700 !important; color: #fff !important;
    padding: 0.6rem 1.8rem !important; font-size: 0.95rem !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(124,58,237,0.45) !important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: rgba(255,255,255,0.05) !important;
    border-radius: 12px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important; color: #94a3b8 !important;
    font-weight: 600 !important; font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(124,58,237,0.55) !important; color: #fff !important;
}
.stAlert { border-radius: 12px !important; }
label, .stSlider label, [data-testid="stWidgetLabel"] {
    color: #cbd5e1 !important; font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# KONEKSI SUPABASE
# ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = get_supabase()
except Exception:
    st.error("⚠️ Koneksi Supabase gagal!")
    st.stop()

# ─────────────────────────────────────────────
# FUNGSI DATABASE — USERS
# ─────────────────────────────────────────────
def authenticate(username: str, password: str) -> dict | None:
    """
    Login untuk dosen & siswa: cocokkan username + tanggal_lahir.
    Password diformat DDMMYYYY, contoh: 15081995
    """
    resp = (
        supabase.table("users")
        .select("*")
        .ilike("username", username.strip())
        .eq("tanggal_lahir", password.strip())
        .in_("role", ["dosen", "siswa"])
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None

def authenticate_ortu(username_anak: str, tanggal_lahir_anak: str) -> dict | None:
    """
    Login orang tua: masukkan username anak + tanggal lahir anak.
    Jika cocok, kembalikan data siswa tersebut dengan flag is_ortu=True.
    """
    resp = (
        supabase.table("users")
        .select("*")
        .ilike("username", username_anak.strip())
        .eq("tanggal_lahir", tanggal_lahir_anak.strip())
        .eq("role", "siswa")
        .limit(1)
        .execute()
    )
    if resp.data:
        siswa = resp.data[0]
        siswa["_mode"] = "ortu"   # tandai sebagai sesi pantau orang tua
        return siswa
    return None

def get_all_siswa() -> list[dict]:
    resp = supabase.table("users").select("*").eq("role", "siswa").execute()
    return resp.data or []

def get_user_by_nim(nim: str) -> dict | None:
    resp = supabase.table("users").select("*").eq("nim", nim).limit(1).execute()
    return resp.data[0] if resp.data else None

# ─────────────────────────────────────────────
# FUNGSI DATABASE — CHECK-IN
# ─────────────────────────────────────────────
def get_all_checkin() -> pd.DataFrame:
    resp = supabase.table("checkin").select("*").order("tanggal", desc=False).execute()
    return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()

def get_checkin_by_nim(nim: str) -> pd.DataFrame:
    resp = (
        supabase.table("checkin")
        .select("*")
        .eq("nim", nim)
        .order("tanggal", desc=False)
        .execute()
    )
    return pd.DataFrame(resp.data) if resp.data else pd.DataFrame()

def already_checkin_today(nim: str) -> bool:
    resp = (
        supabase.table("checkin")
        .select("id")
        .eq("nim", nim)
        .eq("tanggal", str(date.today()))
        .limit(1)
        .execute()
    )
    return bool(resp.data)

def insert_checkin(row: dict) -> bool:
    try:
        supabase.table("checkin").insert(row).execute()
        return True
    except Exception as e:
        st.error(f"❌ Gagal menyimpan data: {e}")
        return False

# ─────────────────────────────────────────────
# HELPER CHART & STATS
# ─────────────────────────────────────────────
def render_charts(df: pd.DataFrame):
    if df.empty:
        st.info("📭 Belum ada data untuk ditampilkan.")
        return
    df = df.copy()
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    df = df.sort_values("tanggal").set_index("tanggal")

    st.markdown("**😊 Mood per Hari**")
    st.line_chart(df[["mood"]], color=["#623bd7"])

    st.markdown("**⚡ Energi per Hari**")
    st.line_chart(df[["energi"]], color=["#34d399"])

    st.markdown("**💓 Perasaan per Hari**")
    st.line_chart(df[["perasaan"]], color=["#f472b6"])

def stat_boxes(nums: list, lbls: list):
    cols = st.columns(len(nums))
    for col, num, lbl in zip(cols, nums, lbls):
        with col:
            st.markdown(
                f'<div class="stat-box">'
                f'<div class="stat-num">{num}</div>'
                f'<div class="stat-lbl">{lbl}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

# ─────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<div class="main-title">📋 Sistem Daily Check-In Siswa</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Pantau kondisi harian siswa dengan mudah & terstruktur · Powered by Supabase</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# HALAMAN LOGIN
# ═══════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 🔐 Masuk ke Sistem")
    st.markdown("---")

    login_mode = st.radio(
        "Masuk sebagai:",
        ["👨‍🏫 Dosen / Siswa", "👨‍👩‍👦 Orang Tua"],
        horizontal=True,
        label_visibility="visible"
    )

    if login_mode == "👨‍🏫 Dosen / Siswa":
        with st.form("login_form"):
            username = st.text_input("👤 Username (Nama)", placeholder="Contoh: Andi")
            password = st.text_input(
                "🎂 Tanggal Lahir (DDMMYYYY)",
                type="password",
                placeholder="Contoh: 15081995"
            )
            submitted = st.form_submit_button("Masuk →", type="primary", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("⚠️ Username dan tanggal lahir tidak boleh kosong.")
            else:
                with st.spinner("Memverifikasi..."):
                    user = authenticate(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"✅ Selamat datang, **{user['nama']}**!")
                    st.rerun()
                else:
                    st.error("❌ Username atau tanggal lahir salah.")

    else:  # Orang Tua
        with st.form("login_ortu_form"):
            st.caption("Masukkan username dan tanggal lahir **anak** Anda.")
            username_anak = st.text_input("👤 Username Anak", placeholder="Contoh: Andi")
            tgl_lahir_anak = st.text_input(
                "🎂 Tanggal Lahir Anak (DDMMYYYY)",
                type="password",
                placeholder="Contoh: 15082010"
            )
            submitted_ortu = st.form_submit_button("Masuk →", type="primary", use_container_width=True)

        if submitted_ortu:
            if not username_anak or not tgl_lahir_anak:
                st.error("⚠️ Semua kolom harus diisi.")
            else:
                with st.spinner("Memverifikasi..."):
                    user = authenticate_ortu(username_anak, tgl_lahir_anak)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success(f"✅ Selamat datang! Menampilkan data **{user['nama']}**.")
                    st.rerun()
                else:
                    st.error("❌ Data anak tidak ditemukan. Periksa username dan tanggal lahir.")

    st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("💡 Panduan Akun Demo"):
        demo = {
            "Role":             ["Dosen", "Siswa", "Siswa", "Orang Tua (login pakai data anak)"],
            "Username":         ["Bu Rina", "Andi", "Budi", "→ pakai username: Andi"],
            "Tanggal Lahir":    ["123", "111", "222", "→ pakai tgl lahir: 111"],
        }
        st.dataframe(pd.DataFrame(demo), use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# SETELAH LOGIN
# ═══════════════════════════════════════════════
else:
    user = st.session_state.user
    role = user["role"]
    is_ortu_mode = user.get("_mode") == "ortu"

    # ── Top bar ──
    col_info, col_logout = st.columns([5, 1])
    with col_info:
        if is_ortu_mode:
            label = f'👨‍👩‍👦 Mode Orang Tua — memantau <strong>{user["nama"]}</strong> &nbsp;<span class="badge badge-ortu">Orang Tua</span>'
        else:
            badge_cls = "badge-dosen" if role == "dosen" else "badge-siswa"
            badge_lbl = "Dosen" if role == "dosen" else "Siswa"
            label = f'👋 Halo, <strong>{user["nama"]}</strong> &nbsp;<span class="badge {badge_cls}">{badge_lbl}</span>'

        st.markdown(
            f'<div style="color:#e2e8f0;font-weight:600;font-size:1rem;padding:8px 0">{label}</div>',
            unsafe_allow_html=True
        )
    with col_logout:
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ══════════════════════════════════════
    # MODE ORANG TUA (lihat data anak saja)
    # ══════════════════════════════════════
    if is_ortu_mode:
        st.markdown(
            f'<div class="section-header">👨‍👩‍👦 Pantau Kondisi Anak: {user["nama"]} ({user.get("kelas", "-")})</div>',
            unsafe_allow_html=True
        )
        st.info("ℹ️ Anda masuk sebagai orang tua. Hanya bisa memantau data anak, tidak bisa mengisi check-in.")

        with st.spinner("Memuat data anak..."):
            df_anak = get_checkin_by_nim(user["nim"])

        avg_mood   = round(df_anak["mood"].mean(), 1)   if not df_anak.empty else "-"
        avg_energi = round(df_anak["energi"].mean(), 1) if not df_anak.empty else "-"
        stat_boxes(
            [len(df_anak), avg_mood, avg_energi],
            ["Total Check-In", "Rata-rata Mood", "Rata-rata Energi"]
        )

        tab1, tab2 = st.tabs(["📋 Tabel Riwayat", "📈 Grafik Perkembangan"])
        with tab1:
            if df_anak.empty:
                st.info(f"📭 {user['nama']} belum pernah melakukan check-in.")
            else:
                cols_show = ["tanggal", "mood", "perasaan", "energi", "cerita"]
                cols_show = [c for c in cols_show if c in df_anak.columns]
                st.dataframe(df_anak[cols_show], use_container_width=True, hide_index=True)
        with tab2:
            render_charts(df_anak)

    # ══════════════════════════
    # ROLE: DOSEN
    # ══════════════════════════
    elif role == "dosen":
        st.markdown('<div class="section-header">📊 Dashboard Dosen — Semua Data Siswa</div>', unsafe_allow_html=True)

        with st.spinner("Memuat data..."):
            df_all     = get_all_checkin()
            siswa_list = get_all_siswa()

        total_siswa   = len(siswa_list)
        total_checkin = len(df_all)
        avg_mood   = round(df_all["mood"].mean(), 1)   if not df_all.empty else "-"
        avg_energi = round(df_all["energi"].mean(), 1) if not df_all.empty else "-"

        stat_boxes(
            [total_siswa, total_checkin, avg_mood, avg_energi],
            ["Total Siswa", "Total Check-In", "Rata-rata Mood", "Rata-rata Energi"]
        )

        st.markdown('<div class="section-header">🔍 Filter & Eksplorasi Data</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["📋 Tabel Data", "📈 Grafik"])

        with tab1:
            nama_opts   = ["Semua Siswa"] + sorted(s["nama"] for s in siswa_list)
            filter_nama = st.selectbox("Filter berdasarkan siswa:", nama_opts)

            if df_all.empty:
                st.info("📭 Belum ada data check-in.")
            else:
                df_show = df_all.copy()
                if filter_nama != "Semua Siswa":
                    df_show = df_show[df_show["nama"] == filter_nama]
                cols_show = ["tanggal", "nama", "kelas", "mood", "perasaan", "energi", "cerita"]
                cols_show = [c for c in cols_show if c in df_show.columns]
                st.dataframe(df_show[cols_show], use_container_width=True, hide_index=True)
                st.caption(f"Menampilkan {len(df_show)} entri")

        with tab2:
            if df_all.empty:
                st.info("📭 Belum ada data untuk grafik.")
            else:
                nama_opts2 = ["Semua Siswa"] + sorted(s["nama"] for s in siswa_list)
                filter_g   = st.selectbox("Filter grafik:", nama_opts2, key="grafik_filter")

                df_g = df_all.copy()
                if filter_g != "Semua Siswa":
                    df_g = df_g[df_g["nama"] == filter_g]

                df_g["tanggal"] = pd.to_datetime(df_g["tanggal"])
                df_g_agg = (
                    df_g.groupby("tanggal")[["mood", "perasaan", "energi"]]
                    .mean().reset_index().sort_values("tanggal").set_index("tanggal")
                )
                render_charts(df_g_agg.reset_index())

    # ══════════════════════════
    # ROLE: SISWA
    # ══════════════════════════
    elif role == "siswa":
        st.markdown('<div class="section-header">🎒 Dashboard Siswa — Data Pribadi</div>', unsafe_allow_html=True)

        with st.spinner("Memuat data..."):
            df_mine = get_checkin_by_nim(user["nim"])

        avg_mood   = round(df_mine["mood"].mean(), 1)   if not df_mine.empty else "-"
        avg_energi = round(df_mine["energi"].mean(), 1) if not df_mine.empty else "-"
        stat_boxes(
            [len(df_mine), avg_mood, avg_energi],
            ["Total Check-In", "Rata-rata Mood", "Rata-rata Energi"]
        )

        tab1, tab2 = st.tabs(["📝 Isi Check-In", "📊 Riwayat & Grafik"])

        with tab1:
            st.markdown('<div class="section-header">📝 Form Daily Check-In</div>', unsafe_allow_html=True)
            today = date.today()

            if already_checkin_today(user["nim"]):
                st.success("✅ Kamu sudah melakukan check-in hari ini! Sampai jumpa besok 😊")
            else:
                with st.form("checkin_form"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.text_input("📅 Tanggal", value=str(today), disabled=True)
                        st.text_input("👤 Nama",    value=user["nama"], disabled=True)
                    with col_b:
                        st.text_input("🏫 Kelas",   value=user["kelas"], disabled=True)
                        st.text_input("🪪 NIM",     value=user["nim"], disabled=True)

                    st.markdown("---")
                    mood     = st.slider("😊 Mood hari ini",     1, 5, 3, help="1=Sangat buruk · 5=Sangat baik")
                    perasaan = st.slider("💓 Perasaan hari ini", 1, 5, 3, help="1=Sangat sedih · 5=Sangat bahagia")
                    energi   = st.slider("⚡ Energi hari ini",   1, 5, 3, help="1=Sangat lelah · 5=Sangat berenergi")
                    cerita   = st.text_area("📖 Cerita hari ini", placeholder="Ceritakan bagaimana harimu...", height=120)
                    submit   = st.form_submit_button("✅ Kirim Check-In", type="primary", use_container_width=True)

                if submit:
                    if not cerita.strip():
                        st.error("⚠️ Kolom cerita tidak boleh kosong.")
                    else:
                        ok = insert_checkin({
                            "tanggal":  str(today),
                            "nim":      user["nim"],
                            "nama":     user["nama"],
                            "kelas":    user["kelas"],
                            "mood":     mood,
                            "perasaan": perasaan,
                            "energi":   energi,
                            "cerita":   cerita.strip(),
                        })
                        if ok:
                            st.success("🎉 Check-in berhasil disimpan! Semangat terus ya!")
                            st.rerun()

        with tab2:
            st.markdown('<div class="section-header">📊 Riwayat Check-In Saya</div>', unsafe_allow_html=True)
            if df_mine.empty:
                st.info("📭 Belum ada riwayat. Isi form check-in pertamamu!")
            else:
                cols_show = ["tanggal", "mood", "perasaan", "energi", "cerita"]
                cols_show = [c for c in cols_show if c in df_mine.columns]
                st.dataframe(df_mine[cols_show], use_container_width=True, hide_index=True)
                render_charts(df_mine)
