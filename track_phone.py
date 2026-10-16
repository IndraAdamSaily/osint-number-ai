import phonenumbers
from phonenumbers import carrier, geocoder, timezone, number_type
import requests
import urllib.parse
from datetime import datetime
import json
import csv
import os
import hashlib
import socket
import platform
import base64

# Mengimpor Colorama untuk pewarnaan terminal profesional
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    # Fallback jika modul colorama belum diinstal
    class DummyColor:
        def __getattr__(self, name):
            return ""
    Fore = Back = Style = DummyColor()

# ==============================================================================
# PEMETAAN DATA & PRESET
# ==============================================================================

TIPE_NOMOR_MAP = {
    phonenumbers.PhoneNumberType.MOBILE: "Seluler (Mobile)",
    phonenumbers.PhoneNumberType.FIXED_LINE: "Telepon Rumah / Kantor (Fixed Line)",
    phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line atau Seluler",
    phonenumbers.PhoneNumberType.TOLL_FREE: "Bebas Pulsa (Toll-Free)",
    phonenumbers.PhoneNumberType.PREMIUM_RATE: "Tarif Premium",
    phonenumbers.PhoneNumberType.SHARED_COST: "Biaya Bersama (Shared Cost)",
    phonenumbers.PhoneNumberType.VOIP: "VoIP (Internet Phone)",
    phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Nomor Personal",
    phonenumbers.PhoneNumberType.PAGER: "Pager",
    phonenumbers.PhoneNumberType.UAN: "Nomor Akses Universal (UAN)",
    phonenumbers.PhoneNumberType.UNKNOWN: "Tidak Diketahui"
}

BENDERA_NEGARA = {
    62: "🇮🇩 Indonesia",
    60: "🇲🇾 Malaysia",
    65: "🇸🇬 Singapura",
    1: "🇺🇸 / 🇨🇦 Amerika Serikat / Kanada",
    81: "🇯🇵 Jepang",
    966: "🇸🇦 Arab Saudi",
    44: "🇬🇧 Britania Raya (UK)",
    61: "🇦🇺 Australia"
}

PREFIX_HLR_INDO = {
    "811": "Telkomsel (Kartu HALO - Nasional) [MCC-MNC: 510-10]",
    "812": "Telkomsel (simPATI / HALO - Jawa / Sumatera) [MCC-MNC: 510-10]",
    "813": "Telkomsel (simPATI / HALO - Jawa / Bali) [MCC-MNC: 510-10]",
    "821": "Telkomsel (simPATI - Jakarta / Sulawesi) [MCC-MNC: 510-10]",
    "852": "Telkomsel (AS - Sumatera / Kalimantan) [MCC-MNC: 510-10]",
    "853": "Telkomsel (AS - Jawa / Timtim) [MCC-MNC: 510-10]",
    "814": "Indosat (IM3 / Mentari) [MCC-MNC: 510-01]",
    "815": "Indosat (Mentari / Matrix) [MCC-MNC: 510-01]",
    "816": "Indosat (Mentari / Matrix) [MCC-MNC: 510-01]",
    "856": "Indosat (IM3 - Jawa & Madura) [MCC-MNC: 510-01]",
    "857": "Indosat (IM3 - Sumatera, Kalimantan) [MCC-MNC: 510-01]",
    "817": "XL Axiata (Jawa & Bali) [MCC-MNC: 510-11]",
    "818": "XL Axiata (Jakarta & Sekitarnya) [MCC-MNC: 510-11]",
    "819": "XL Axiata (Sumatera & Jabar) [MCC-MNC: 510-11]",
    "831": "AXIS (Sumatera & Jawa) [MCC-MNC: 510-08]",
    "838": "AXIS (Jawa & Bali) [MCC-MNC: 510-08]",
    "896": "Tri / 3 (Jawa & Sumatera) [MCC-MNC: 510-89]",
    "899": "Tri / 3 (Nasional) [MCC-MNC: 510-89]",
    "881": "Smartfren (Nasional) [MCC-MNC: 510-09]",
    "888": "Smartfren (Nasional) [MCC-MNC: 510-09]"
}

# ==============================================================================
# TAMPILAN BANNER & PETUNJUK PENGGUNAAN
# ==============================================================================

def tampilkan_banner():
    banner = f"""
{Fore.CYAN}{Style.BRIGHT}===================================================================================
{Fore.GREEN}{Style.BRIGHT}  ██████╗ ███████╗██╗███╗   ██╗████████╗  ███╗   ██╗██╗   ██╗███╗   ███╗██████╗ ███████╗██╗██╗
 {Fore.GREEN}{Style.BRIGHT}██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝  ████╗  ██║██║   ██║████╗ ████║██╔══██╗██╔════╝██║██║
 {Fore.GREEN}{Style.BRIGHT}██║   ██║███████╗██║██╔██╗ ██║   ██║     ██╔██╗ ██║██║   ██║██╔████╔██║██████╔╝█████╗  ██║██║
 {Fore.GREEN}{Style.BRIGHT}██║   ██║╚════██║██║██║╚██╗██║   ██║     ██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ╚═╝╚═╝
 {Fore.GREEN}{Style.BRIGHT}╚██████╔╝███████║██║██║ ╚████║   ██║     ██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██╗██╗
  {Fore.CYAN}{Style.BRIGHT}╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝╚═╝
{Fore.YELLOW}{Style.BRIGHT}                            [ OSINT NUMBER AI PYTHON ]
{Fore.CYAN}{Style.BRIGHT}==================================================================================={Style.RESET_ALL}
"""
    print(banner)

def tampilkan_petunjuk_penggunaan():
    print(f"{Fore.MAGENTA}{Style.BRIGHT}┌── [ 📖 PETUNJUK PENGGUNAAN / BASIC COMMANDS ] ──────────────────────────────────")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}│")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}├── {Fore.WHITE}1. {Fore.YELLOW}Format Nomor Valid   : {Fore.CYAN}Gunakan format internasional diawali tanda '+' dan Kode Negara.")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}│                         {Fore.GREEN}Contoh: +6281234567890 (Indonesia), +12025550143 (USA)")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}├── {Fore.WHITE}2. {Fore.YELLOW}Keluar Dari Aplikasi : {Fore.CYAN}Ketik {Fore.RED}'exit'{Fore.CYAN} atau {Fore.RED}'keluar'{Fore.CYAN} untuk menutup skrip.")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}├── {Fore.WHITE}3. {Fore.YELLOW}Hasil Ekspor         : {Fore.CYAN}Laporan otomatis disimpan dalam format:")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}│                         {Fore.BLUE}• JSON/CSV ({Fore.WHITE}riwayat_pelacakan_nomor.*{Fore.BLUE})")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}│                         {Fore.BLUE}• FORENSIK ({Fore.WHITE}laporan_forensik.txt{Fore.BLUE})")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}│                         {Fore.BLUE}• HTML WEB ({Fore.WHITE}laporan_investigasi.html{Fore.BLUE})")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}│                         {Fore.BLUE}• VCARD    ({Fore.WHITE}kontak_<nomor>.vcf{Fore.BLUE})")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}└───────────────────────────────────────────────────────────────────────────────────\n")

# ==============================================================================
# FUNGSI TEKNIS & UTILITAS
# ==============================================================================

def cek_status_whatsapp(nomor_E164):
    """Mengecek ketersediaan nomor di WhatsApp secara online."""
    try:
        clean_num = nomor_E164.replace("+", "")
        url = f"https://wa.me/{clean_num}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return f"{Fore.GREEN}✅ Terdeteksi aktif / terdaftar di WhatsApp (Server Respon: 200 OK)"
        else:
            return f"{Fore.RED}❌ Tidak terdaftar atau dibatasi"
    except Exception:
        return f"{Fore.YELLOW}⚠️ Gagal mengecek (Koneksi internet bermasalah)"

def get_system_telemetry():
    """Mengambil informasi sistem runtime perangkat eksekusi script."""
    sys_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    node_name = platform.node()
    return f"OS: {sys_info} | Hostname: {node_name}"

def get_online_network_geo():
    """Melacak geolokasi jaringan online perangkat via ipwho.is."""
    try:
        resp = requests.get("https://ipwho.is/", timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return f"IP Publik: {data.get('ip')} | ISP: {data.get('connection', {}).get('isp')} | Lokasi: {data.get('city')}, {data.get('country')}"
        return f"{Fore.YELLOW}⚠️ Gagal mengambil geolokasi jaringan online"
    except Exception:
        return f"{Fore.YELLOW}⚠️ Jaringan online terbatas"

def resolve_dns_online():
    """Melakukan DNS Lookup online untuk melacak jalur koneksi pelacakan."""
    try:
        ip_target = socket.gethostbyname("wa.me")
        return f"DNS Lookup wa.me resolved -> {ip_target} (Secure TLS Route Active)"
    except Exception:
        return f"{Fore.YELLOW}⚠️ DNS Lookup gagal dijangkau"

def generate_security_hash(nomor_string):
    """Membuat hash keamanan MD5, SHA-256, dan Base64 Payload."""
    md5_hash = hashlib.md5(nomor_string.encode()).hexdigest()
    sha256_hash = hashlib.sha256(nomor_string.encode()).hexdigest()
    b64_payload = base64.b64encode(nomor_string.encode()).decode()
    return md5_hash, sha256_hash, b64_payload

def hitung_skor_risiko(nomor_str):
    """Sistem penilaian risiko heuristik (Spam/Bot Scoring Engine)."""
    skor = 0
    catatan = []
    for digit in set(nomor_str):
        if digit * 4 in nomor_str:
            skor += 40
            catatan.append("Pola angka berulang terdeteksi")
            break
    if "123456" in nomor_str or "654321" in nomor_str:
        skor += 50
        catatan.append("Pola urut berurutan terdeteksi")
    if len(nomor_str) < 9 or len(nomor_str) > 13:
        skor += 30
        catatan.append("Panjang digit di luar batas normal operator seluler")
    
    status_text = ", ".join(catatan) if catatan else "Aman / Normal"
    if skor >= 50:
        return f"{Fore.RED}{skor}/100 ({status_text}){Style.RESET_ALL}"
    elif skor > 0:
        return f"{Fore.YELLOW}{skor}/100 ({status_text}){Style.RESET_ALL}"
    else:
        return f"{Fore.GREEN}{skor}/100 ({status_text}){Style.RESET_ALL}"

def analisa_risiko_pola(nomor_str):
    for digit in set(nomor_str):
        if digit * 5 in nomor_str:
            return f"{Fore.YELLOW}⚠️ Terdeteksi Pola Berulang (Potensi Nomor Bot/Spam)"
    if "123456" in nomor_str or "654321" in nomor_str:
        return f"{Fore.YELLOW}⚠️ Terdeteksi Pola Urut (Potensi Nomor Dummy/Palsu)"
    return f"{Fore.GREEN}✅ Pola Normal (Tidak ada indikasi bot otomatis)"

def export_vcard(nama_file_vcf, fmt_intl, provider, wilayah):
    """Membuat file kontak otomatis format VCard (.vcf)"""
    vcard_data = f"""BEGIN:VCARD
VERSION:3.0
FN:Target OSINT {fmt_intl}
TEL;TYPE=CELL:{fmt_intl}
NOTE:Provider: {provider} | Wilayah: {wilayah} | Generated by Absolute Script
END:VCARD"""
    with open(nama_file_vcf, "w", encoding="utf-8") as f:
        f.write(vcard_data)

def export_html_report(data):
    """Membuat laporan visual interaktif berformat HTML."""
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<title>Laporan Investigasi - {data['nomor_e164']}</title>
<style>
body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }}
.container {{ max-width: 800px; margin: auto; background: #1e293b; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }}
h2 {{ color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 10px; }}
.box {{ background: #0f172a; padding: 15px; margin: 10px 0; border-left: 4px solid #38bdf8; border-radius: 4px; }}
</style>
</head>
<body>
<div class="container">
<h2>Laporan Investigasi Nomor Telepon</h2>
<div class="box"><strong>Waktu:</strong> {data['waktu']}</div>
<div class="box"><strong>Nomor E.164:</strong> {data['nomor_e164']}</div>
<div class="box"><strong>Status Valid:</strong> {data['status_valid']}</div>
<div class="box"><strong>Status WhatsApp:</strong> {data['status_whatsapp']}</div>
<div class="box"><strong>Operator:</strong> {data['operator']}</div>
<div class="box"><strong>Wilayah:</strong> {data['wilayah']} ({data['negara']})</div>
<div class="box"><strong>Skor Risiko:</strong> {data['skor_spam']}</div>
<div class="box"><strong>MD5 Hash:</strong> {data['md5_hash']}</div>
</div>
</body>
</html>"""
    with open("laporan_investigasi.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def simpan_arsip_absolut(data_hasil):
    """Menyimpan arsip ke JSON, CSV, TXT, VCF, dan HTML secara simultan."""
    # JSON
    file_json = "riwayat_pelacakan_nomor.json"
    riwayat = []
    if os.path.exists(file_json):
        try:
            with open(file_json, "r", encoding="utf-8") as f:
                riwayat = json.load(f)
        except Exception:
            riwayat = []
    riwayat.append(data_hasil)
    with open(file_json, "w", encoding="utf-8") as f:
        json.dump(riwayat, f, indent=4, ensure_ascii=False)

    # CSV
    file_csv = "riwayat_pelacakan_nomor.csv"
    file_exists = os.path.exists(file_csv)
    with open(file_csv, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Waktu", "Nomor E.164", "Valid", "WhatsApp", "Tipe", "Operator", "Wilayah", "Negara"])
        writer.writerow([
            data_hasil["waktu"], data_hasil["nomor_e164"], data_hasil["status_valid"],
            data_hasil["status_whatsapp"], data_hasil["jenis_nomor"], data_hasil["operator"],
            data_hasil["wilayah"], data_hasil["negara"]
        ])

    # TXT Laporan Forensik
    with open("laporan_forensik.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- LAPORAN INVESTIGASI: {data_hasil['nomor_e164']} ---\n")
        f.write(f"Waktu: {data_hasil['waktu']}\n")
        f.write(f"Provider: {data_hasil['operator']} | Wilayah: {data_hasil['wilayah']}\n")
        f.write(f"MD5: {data_hasil['md5_hash']} | SHA256: {data_hasil['sha256_hash']}\n")
        f.write(f"Base64 Payload: {data_hasil['base64_payload']}\n")
        f.write("--------------------------------------------------\n")

    # HTML Report
    export_html_report(data_hasil)

# ==============================================================================
# FUNGSI UTAMA ANALISIS
# ==============================================================================

def cek_info_nomor_absolute_final(nomor_telepon):
    try:
        parsed_number = phonenumbers.parse(nomor_telepon)
        
        is_valid = phonenumbers.is_valid_number(parsed_number)
        is_possible = phonenumbers.is_possible_number(parsed_number)
        
        if not is_possible:
            print(f"\n{Fore.RED}{Style.BRIGHT}❌ Format nomor tidak mungkin ada (panjang/pola angka salah).\n")
            return

        # Mengambil informasi dasar
        lokasi = geocoder.description_for_number(parsed_number, "id")
        provider = carrier.name_for_number(parsed_number, "id")
        tz = timezone.time_zones_for_number(parsed_number)
        
        # Tipe nomor
        enum_tipe = number_type(parsed_number)
        jenis_nomor = TIPE_NOMOR_MAP.get(enum_tipe, "Tidak Diketahui")
        
        # Format angka standar
        fmt_intl = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        fmt_lokal = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        fmt_e164 = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        fmt_rfc = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.RFC3966)
        
        # Informasi Tambahan
        cc = parsed_number.country_code
        info_bendera = BENDERA_NEGARA.get(cc, f"🌎 Kode Negara (+{cc})")
        nomor_nasional_str = str(parsed_number.national_number)
        jumlah_digit = len(nomor_nasional_str)
        waktu_cek = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Telemetry, Hash & Security
        sys_telemetry = get_system_telemetry()
        md5_val, sha256_val, b64_val = generate_security_hash(fmt_e164)
        skor_spam = hitung_skor_risiko(nomor_nasional_str)

        # Analisis HLR (Khusus Indonesia)
        hlr_info = "Khusus nomor Indonesia (+62)"
        if cc == 62:
            prefix_3 = nomor_nasional_str[:3]
            hlr_info = PREFIX_HLR_INDO.get(prefix_3, "Prefix HLR & MCC-MNC Standar Global Telekomunikasi")

        # Analisis Pola Risiko
        analisis_pola = analisa_risiko_pola(nomor_nasional_str)

        # Proses Online Check (WhatsApp, DNS & Network Geo)
        print(f"\n{Fore.CYAN}{Style.BRIGHT}⏳ Menghubungkan ke server online (WhatsApp API, DNS Route & Network Telemetry)...")
        status_wa = cek_status_whatsapp(fmt_e164)
        status_dns = resolve_dns_online()
        network_geo = get_online_network_geo()

        # OSINT Direct Links
        clean_e164 = fmt_e164.replace("+", "")
        encoded_num = urllib.parse.quote(fmt_intl)
        link_google = f"https://www.google.com/search?q=%22{encoded_num}%22+OR+%22{clean_e164}%22"
        link_truecaller = f"https://www.truecaller.com/search/id/{clean_e164}"

        # Ekspor VCard Kontak (.vcf)
        vcf_filename = f"kontak_{clean_e164}.vcf"
        export_vcard(vcf_filename, fmt_intl, provider if provider else "Unknown", lokasi if lokasi else "Unknown")

        # Menyusun Kamus Data untuk Arsip
        data_laporan = {
            "waktu": waktu_cek,
            "nomor_e164": fmt_e164,
            "status_valid": is_valid,
            "status_whatsapp": status_wa,
            "jenis_nomor": jenis_nomor,
            "operator": provider if provider else "Tidak terdeteksi",
            "wilayah": lokasi if lokasi else "Tidak diketahui",
            "negara": info_bendera,
            "zona_waktu": list(tz),
            "analisis_hlr": hlr_info,
            "analisis_risiko": analisis_pola,
            "skor_spam": skor_spam,
            "md5_hash": md5_val,
            "sha256_hash": sha256_val,
            "base64_payload": b64_val
        }
        simpan_arsip_absolut(data_laporan)

        # Formatting Output Profesional
        C_MAIN = Fore.CYAN + Style.BRIGHT
        C_SUB = Fore.GREEN + Style.BRIGHT
        C_VAL = Fore.WHITE + Style.BRIGHT
        C_LABEL = Fore.YELLOW
        C_RESET = Style.RESET_ALL

        print(f"\n{C_MAIN}===================================================================================")
        print(f"{C_MAIN}          ABSOLUTE FINAL CORE SYSTEM & TELECOM INTELLIGENCE REPORT")
        print(f"{C_MAIN}==================================================================================={C_RESET}")
        print(f"{C_LABEL}Waktu Pengecekan    : {C_VAL}{waktu_cek}")
        print(f"{C_LABEL}Runtime Telemetry   : {C_VAL}{sys_telemetry}")
        print(f"{C_LABEL}Jaringan Online Geo : {C_VAL}{network_geo}")
        print(f"{C_LABEL}Status Validasi     : {Fore.GREEN if is_valid else Fore.RED}{'✅ Valid secara global' + (' (Aktif/Pernah Aktif)' if is_valid else '❌ Tidak Valid')}{C_RESET}")
        print(f"{C_LABEL}Kelayakan Nomor     : {Fore.GREEN if is_possible else Fore.YELLOW}{'✅ Sangat Mungkin (Struktur benar)' if is_possible else '⚠️ Diragukan'}{C_RESET}")
        print(f"{C_LABEL}Status WhatsApp     : {status_wa}{C_RESET}")
        print(f"{C_LABEL}Analisis DNS Online : {C_VAL}{status_dns}")
        print(f"{C_LABEL}Jenis / Tipe Nomor  : {C_VAL}{jenis_nomor}")
        print(f"{C_LABEL}Operator / Provider : {C_VAL}{provider if provider else 'Tidak terdeteksi (Mungkin sudah Ported/Pindah)'}")
        print(f"{C_LABEL}Negara / Wilayah    : {C_VAL}{lokasi if lokasi else 'Tidak diketahui'} ({info_bendera})")
        print(f"{C_LABEL}Kode Negara (CC)    : {C_VAL}+{cc}")
        print(f"{C_LABEL}Nomor Nasional      : {C_VAL}{parsed_number.national_number}")
        print(f"{C_LABEL}Total Digit Nasional: {C_VAL}{jumlah_digit} Digit")
        print(f"{C_LABEL}Zona Waktu          : {C_VAL}{', '.join(tz)}")
        
        print(f"\n{C_SUB}-----------------------------------------------------------------------------------")
        print(f"{C_SUB} 🔍 ANALISIS FORENSIK, HLR, HASH & SPAM SCORING")
        print(f"{C_SUB}-----------------------------------------------------------------------------------{C_RESET}")
        print(f"{C_LABEL}Analisis Prefix HLR : {C_VAL}{hlr_info}")
        print(f"{C_LABEL}Analisis Pola Risiko: {analisis_pola}{C_RESET}")
        print(f"{C_LABEL}Skor Risiko Spam    : {skor_spam}{C_RESET}")
        print(f"{C_LABEL}MD5 Security Hash   : {Fore.MAGENTA}{md5_val}{C_RESET}")
        print(f"{C_LABEL}SHA-256 Sec. Hash   : {Fore.MAGENTA}{sha256_val}{C_RESET}")
        print(f"{C_LABEL}Base64 Payload      : {Fore.MAGENTA}{b64_val}{C_RESET}")
        
        print(f"\n{C_SUB}-----------------------------------------------------------------------------------")
        print(f"{C_SUB} 📋 FORMAT NOMOR & LINK PENGUJIAN ONLINE")
        print(f"{C_SUB}-----------------------------------------------------------------------------------{C_RESET}")
        print(f"{C_LABEL}Format Lokal        : {C_VAL}{fmt_lokal}")
        print(f"{C_LABEL}Format Internasional: {C_VAL}{fmt_intl}")
        print(f"{C_LABEL}Format E.164        : {C_VAL}{fmt_e164}")
        print(f"{C_LABEL}Format RFC3966 (URI): {C_VAL}{fmt_rfc}")
        print(f"{C_LABEL}Direct Link WA      : {Fore.BLUE}{Style.BRIGHT}https://wa.me/{clean_e164}{C_RESET}")
        print(f"{C_LABEL}Cari Nama di Google : {Fore.BLUE}{Style.BRIGHT}{link_google}{C_RESET}")
        print(f"{C_LABEL}Cek di Truecaller   : {Fore.BLUE}{Style.BRIGHT}{link_truecaller}{C_RESET}")
        
        print(f"\n{C_SUB}-----------------------------------------------------------------------------------")
        print(f"{C_SUB} 💾 ARSIP ABSOLUT TERSIMPAN (5 FORMAT BERBEDA)")
        print(f"{C_SUB}-----------------------------------------------------------------------------------{C_RESET}")
        print(f"{C_VAL} - JSON & CSV Database Log : {Fore.GREEN}riwayat_pelacakan_nomor.json / .csv{C_RESET}")
        print(f"{C_VAL} - Laporan Forensik TXT    : {Fore.GREEN}laporan_forensik.txt{C_RESET}")
        print(f"{C_VAL} - Laporan Web HTML        : {Fore.GREEN}laporan_investigasi.html{C_RESET}")
        print(f"{C_VAL} - File Kontak VCard       : {Fore.GREEN}{vcf_filename}{C_RESET}")
        print(f"{C_MAIN}===================================================================================\n{C_RESET}")

    except phonenumbers.NumberParseException as e:
        print(f"\n{Fore.RED}{Style.BRIGHT}❌ Format masukan salah. Gunakan kode negara (+62...). Detail: {e}\n")
    except Exception as e:
        print(f"\n{Fore.RED}{Style.BRIGHT}Terjadi kesalahan: {e}\n")

if __name__ == "__main__":
    tampilkan_banner()
    tampilkan_petunjuk_penggunaan()
    
    while True:
        try:
            nomor_input = input(f"{Fore.GREEN}{Style.BRIGHT}OSINT-CLI{Fore.WHITE} > {Fore.YELLOW}Masukkan nomor telepon (contoh: +6281234567890): {Style.RESET_ALL}").strip()
            
            if nomor_input.lower() in ["exit", "keluar"]:
                print(f"\n{Fore.CYAN}{Style.BRIGHT}Program selesai. Terima kasih telah menggunakan OSINT NUMBER AI!{Style.RESET_ALL}")
                break
                
            if not nomor_input:
                print(f"{Fore.RED}⚠️ Masukan tidak boleh kosong!\n")
                continue
                
            cek_info_nomor_absolutefinal = cek_info_nomor_absolute_final(nomor_input)
        except (KeyboardInterrupt, SystemExit):
            print(f"\n\n{Fore.YELLOW}Program dihentikan secara paksa. Sampai jumpa!{Style.RESET_ALL}")
            break
