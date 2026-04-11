import streamlit as st
import pandas as pd
from datetime import date
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
st_autorefresh(interval=5000)

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
# CUSTOM CSS — "Deep Ocean" Theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=DM+Mono:wght@400;500&display=swap');

:root {
    --ocean-900: #020c1b;
    --ocean-800: #050f20;
    --ocean-700: #071628;
    --ocean-600: #0a1f3a;
    --ocean-500: #0d2d52;
    --ocean-400: #114075;
    --surface-a: rgba(255,255,255,0.04);
    --surface-b: rgba(255,255,255,0.07);
    --surface-c: rgba(255,255,255,0.10);
    --border:    rgba(100,180,255,0.12);
    --border-h:  rgba(100,180,255,0.28);
    --accent-1:  #38bdf8;   /* sky-400  */
    --accent-2:  #0ea5e9;   /* sky-500  */
    --accent-3:  #7dd3fc;   /* sky-300  */
    --accent-glow: rgba(56,189,248,0.22);
    --text-1: #e0f2fe;
    --text-2: #7ec8e3;
    --text-3: #4a90a4;
    --danger: #f87171;
    --success: #34d399;
    --warning: #fbbf24;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
}

/* ── BACKGROUND: deep ocean mesh gradient ── */
.stApp {
    background:
        radial-gradient(ellipse 90% 60% at 10% 0%, #0a2a5e 0%, transparent 55%),
        radial-gradient(ellipse 70% 50% at 90% 100%, #062044 0%, transparent 55%),
        radial-gradient(ellipse 60% 40% at 50% 50%, #071e3d 0%, transparent 70%),
        linear-gradient(160deg, #020c1b 0%, #041428 40%, #030e1f 100%);
    min-height: 100vh;
}

/* subtle animated noise overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.6;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── TYPOGRAPHY ── */
.main-title {
    font-family: 'DM Mono', monospace;
    font-size: clamp(1.6rem, 3vw, 2.4rem);
    font-weight: 500;
    color: var(--accent-3);
    letter-spacing: -0.5px;
    text-align: center;
    margin-bottom: 0.3rem;
    text-shadow: 0 0 40px rgba(125,211,252,0.4);
}
.sub-title {
    font-size: 0.85rem;
    color: var(--text-3);
    text-align: center;
    margin-bottom: 2.5rem;
    font-weight: 400;
    letter-spacing: 0.02em;
}

/* ── CARD ── */
.card {
    background: var(--surface-a);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2rem 2.2rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    margin-bottom: 1.4rem;
    transition: border-color 0.3s;
}
.card:hover { border-color: var(--border-h); }

/* ── BADGES ── */
.badge {
    display: inline-block; padding: 3px 12px;
    border-radius: 999px; font-size: 0.7rem;
    font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px;
}
.badge-guru  { background: rgba(56,189,248,0.15); color: var(--accent-1); border: 1px solid rgba(56,189,248,0.3); }
.badge-siswa { background: rgba(52,211,153,0.12); color: #34d399; border: 1px solid rgba(52,211,153,0.3); }
.badge-ortu  { background: rgba(251,191,36,0.12); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }

/* ── SECTION HEADER ── */
.section-header {
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--accent-1);
    text-transform: uppercase;
    letter-spacing: 2px;
    border-left: 3px solid var(--accent-2);
    padding-left: 12px;
    margin: 1.8rem 0 1.2rem 0;
}

/* ── STAT BOXES ── */
.stat-box {
    background: linear-gradient(135deg, rgba(14,165,233,0.08), rgba(56,189,248,0.04));
    border: 1px solid rgba(56,189,248,0.18);
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.stat-box::before {
    content: '';
    position: absolute;
    top: 0; left: 50%; transform: translateX(-50%);
    width: 60%; height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-1), transparent);
}
.stat-box:hover {
    border-color: rgba(56,189,248,0.38);
    background: linear-gradient(135deg, rgba(14,165,233,0.13), rgba(56,189,248,0.07));
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(14,165,233,0.12);
}
.stat-num {
    font-family: 'DM Mono', monospace;
    font-size: 2.2rem; font-weight: 500;
    color: var(--accent-3);
    line-height: 1;
    margin-bottom: 0.4rem;
}
.stat-lbl {
    font-size: 0.68rem; color: var(--text-3);
    font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px;
}

/* ── LOGIN WRAP ── */
.login-wrap { max-width: 460px; margin: 3rem auto 0; }

/* ── LOGOUT BUTTON ── */
.logout-btn > button {
    background: rgba(248,113,113,0.07) !important;
    color: var(--danger) !important;
    border: 1px solid rgba(248,113,113,0.25) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    transition: all 0.2s !important;
}
.logout-btn > button:hover {
    background: rgba(248,113,113,0.14) !important;
    border-color: rgba(248,113,113,0.45) !important;
}

/* ── FORM INPUTS ── */
.stTextInput > div > div > input,
input[type="text"], input[type="password"] {
    background: rgba(10,30,60,0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-1) !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent-2) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}
.stTextArea > div > div > textarea {
    background: rgba(10,30,60,0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-1) !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-2) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}
.stSelectbox > div > div {
    background: rgba(10,30,60,0.6) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-1) !important;
}

/* ── PRIMARY BUTTON ── */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
    border: none !important;
    border-radius: 11px !important;
    font-weight: 600 !important;
    color: #fff !important;
    padding: 0.65rem 1.8rem !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(14,165,233,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(14,165,233,0.4) !important;
    background: linear-gradient(135deg, #38bdf8 0%, #0ea5e9 100%) !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(10,30,60,0.5) !important;
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    color: var(--text-3) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.02em !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, rgba(14,165,233,0.3), rgba(56,189,248,0.2)) !important;
    color: var(--accent-3) !important;
    box-shadow: inset 0 0 0 1px rgba(56,189,248,0.3) !important;
}

/* ── ALERTS ── */
.stAlert { border-radius: 12px !important; }
.stSuccess { background: rgba(52,211,153,0.08) !important; border-color: rgba(52,211,153,0.25) !important; }
.stInfo    { background: rgba(56,189,248,0.08) !important; border-color: rgba(56,189,248,0.25) !important; }
.stError   { background: rgba(248,113,113,0.08) !important; border-color: rgba(248,113,113,0.25) !important; }

/* ── LABELS ── */
label, .stSlider label, [data-testid="stWidgetLabel"] {
    color: var(--text-2) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
}

/* ── SLIDER ── */
.stSlider [data-baseweb="slider"] [data-testid="stSliderThumb"] {
    background: var(--accent-1) !important;
    box-shadow: 0 0 12px var(--accent-glow) !important;
}

/* ── DATAFRAME ── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* ── RADIO ── */
[data-testid="stRadio"] label {
    background: rgba(10,30,60,0.4) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 4px 14px !important;
    transition: all 0.2s !important;
}
[data-testid="stRadio"] label:hover {
    border-color: var(--accent-2) !important;
    background: rgba(14,165,233,0.1) !important;
}

/* ── DIVIDER ── */
hr {
    border-color: var(--border) !important;
    margin: 1.2rem 0 !important;
}

/* ── CAPTION ── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-3) !important;
    font-size: 0.75rem !important;
}

/* ── TOP BAR INFO ── */
.topbar-info {
    color: var(--text-1);
    font-weight: 500;
    font-size: 0.92rem;
    padding: 6px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── DEMO TABLE ── */
.stDataFrame [data-testid="StyledDataFrameDataCell"] {
    color: var(--text-1) !important;
    font-size: 0.82rem !important;
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
    # Guru: pakai kolom 'password'
    resp = (
        supabase.table("users")
        .select("*")
        .ilike("username", username.strip())
        .eq("password", password.strip())
        .eq("role", "guru")
        .limit(1)
        .execute()
    )
    if resp.data:
        return resp.data[0]
    # Siswa: pakai kolom 'tanggal_lahir'
    resp = (
        supabase.table("users")
        .select("*")
        .ilike("username", username.strip())
        .eq("tanggal_lahir", password.strip())
        .eq("role", "siswa")
        .limit(1)
        .execute()
    )
    return resp.data[0] if resp.data else None

def authenticate_ortu(username_anak: str, tanggal_lahir_anak: str) -> dict | None:
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
        siswa["_mode"] = "ortu"
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

def delete_checkin_by_month(year: int, month: int) -> tuple[bool, int]:
    """Hapus semua data check-in pada bulan & tahun tertentu. Return (sukses, jumlah_dihapus)."""
    try:
        # Hitung dulu berapa baris yang akan dihapus
        start = f"{year:04d}-{month:02d}-01"
        if month == 12:
            end = f"{year+1:04d}-01-01"
        else:
            end = f"{year:04d}-{month+1:02d}-01"

        count_resp = (
            supabase.table("checkin")
            .select("id", count="exact")
            .gte("tanggal", start)
            .lt("tanggal", end)
            .execute()
        )
        jumlah = count_resp.count or 0

        if jumlah == 0:
            return True, 0

        supabase.table("checkin").delete().gte("tanggal", start).lt("tanggal", end).execute()
        return True, jumlah
    except Exception as e:
        st.error(f"❌ Gagal menghapus data: {e}")
        return False, 0

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
    st.line_chart(df[["mood"]], color=["#38bdf8"])

    st.markdown("**⚡ Energi per Hari**")
    st.line_chart(df[["energi"]], color=["#34d399"])

    st.markdown("**💓 Perasaan per Hari**")
    st.line_chart(df[["perasaan"]], color=["#fb7185"])

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
st.markdown('<div class="main-title">◈ Daily Check-In Siswa</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Pantau kondisi harian siswa dengan mudah & terstruktur &nbsp;·&nbsp; Powered by Supabase</div>',
    unsafe_allow_html=True
)

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
        ["👨‍🏫 Guru / Siswa", "👨‍👩‍👦 Orang Tua"],
        horizontal=True,
        label_visibility="visible"
    )

    if login_mode == "👨‍🏫 Guru / Siswa":
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

    else:
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
            "Role":          ["Guru", "Siswa", "Siswa", "Orang Tua (login pakai data anak)"],
            "Username":      ["Bu Rina", "Andi", "Budi", "→ pakai username: Andi"],
            "Tanggal Lahir": ["123", "111", "222", "→ pakai tgl lahir: 111"],
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
            badge_cls = "badge-guru" if role == "guru" else "badge-siswa"
            badge_lbl = "Guru" if role == "guru" else "Siswa"
            label = f'👋 Halo, <strong>{user["nama"]}</strong> &nbsp;<span class="badge {badge_cls}">{badge_lbl}</span>'

        st.markdown(
            f'<div class="topbar-info">{label}</div>',
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
    # MODE ORANG TUA
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
    # ROLE: GURU (dosen)
    # ══════════════════════════
    elif role == "guru":
        st.markdown('<div class="section-header">📊 Dashboard Guru — Semua Data Siswa</div>', unsafe_allow_html=True)

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
        tab1, tab2, tab3 = st.tabs(["📋 Tabel Data", "📈 Grafik", "🗑️ Kelola Data"])

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

        with tab3:
            st.markdown('<div class="section-header">🗑️ Hapus Data Check-In per Bulan</div>', unsafe_allow_html=True)
            st.warning("⚠️ **Perhatian:** Data yang dihapus **tidak dapat dikembalikan**. Pastikan sudah mengunduh atau mencatat data sebelum menghapus.")

            # Tampilkan ringkasan data per bulan jika ada
            if not df_all.empty:
                df_summary = df_all.copy()
                df_summary["tanggal"] = pd.to_datetime(df_summary["tanggal"])
                df_summary["bulan"] = df_summary["tanggal"].dt.to_period("M").astype(str)
                summary = df_summary.groupby("bulan").size().reset_index(name="jumlah_checkin")
                summary.columns = ["Bulan", "Jumlah Check-In"]
                st.markdown("**📅 Ringkasan Data per Bulan:**")
                st.dataframe(summary, use_container_width=True, hide_index=True)
                st.markdown("---")

            import calendar
            col_y, col_m = st.columns(2)
            with col_y:
                tahun_hapus = st.selectbox(
                    "📆 Pilih Tahun",
                    options=list(range(date.today().year, date.today().year - 5, -1)),
                    key="del_year"
                )
            with col_m:
                bulan_list = {
                    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
                    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
                    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
                }
                bulan_hapus = st.selectbox(
                    "📅 Pilih Bulan",
                    options=list(bulan_list.keys()),
                    format_func=lambda x: bulan_list[x],
                    index=date.today().month - 1,
                    key="del_month"
                )

            target_label = f"{bulan_list[bulan_hapus]} {tahun_hapus}"

            # Cek preview berapa data yang akan dihapus
            if not df_all.empty:
                df_prev = df_all.copy()
                df_prev["tanggal"] = pd.to_datetime(df_prev["tanggal"])
                start_prev = pd.Timestamp(tahun_hapus, bulan_hapus, 1)
                end_prev   = start_prev + pd.offsets.MonthEnd(0)
                count_prev = len(df_prev[(df_prev["tanggal"] >= start_prev) & (df_prev["tanggal"] <= end_prev)])
                st.info(f"ℹ️ Data untuk **{target_label}**: **{count_prev} entri** check-in.")
            else:
                count_prev = 0
                st.info("ℹ️ Tidak ada data check-in sama sekali.")

            st.markdown("")

            # Double-confirm: checkbox + tombol
            konfirmasi = st.checkbox(
                f"✅ Saya memahami bahwa data bulan **{target_label}** akan dihapus permanen",
                key="konfirmasi_hapus"
            )

            if konfirmasi:
                if st.button(
                    f"🗑️ Hapus Semua Data — {target_label}",
                    type="primary",
                    use_container_width=True,
                    key="btn_hapus"
                ):
                    if count_prev == 0:
                        st.warning(f"⚠️ Tidak ada data untuk bulan {target_label}.")
                    else:
                        with st.spinner(f"Menghapus {count_prev} entri..."):
                            ok, n = delete_checkin_by_month(tahun_hapus, bulan_hapus)
                        if ok:
                            if n == 0:
                                st.warning(f"⚠️ Tidak ada data ditemukan untuk {target_label}.")
                            else:
                                st.success(f"✅ Berhasil menghapus **{n} entri** check-in bulan {target_label}.")
                                st.rerun()
            else:
                st.button(
                    f"🗑️ Hapus Semua Data — {target_label}",
                    type="primary",
                    use_container_width=True,
                    disabled=True,
                    key="btn_hapus_disabled"
                )

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
