"""
╔══════════════════════════════════════════════════════╗
║            🌍 WW3 CLUB – Telegram Bot 🌍             ║
║         بازی جنگ جهانی سوم | ناتو vs بریکس          ║
╚══════════════════════════════════════════════════════╝
نصب:  pip install python-telegram-bot==20.7
اجرا: python ww3_bot.py
"""

import json, os, logging, random
from datetime import datetime, time as dtime
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ──────────────────────────────────────────────
TOKEN     = "8970644951:AAHIdcyXrRgEPqzUOcDur3Z9K3vPoHbYn84"
DATA_FILE = "ww3_data.json"
RESET_CODE      = "194646"
UN_CODE         = "25555"
LEAVE_CODE      = "00000"   # رمز خروج از کشور (برای انتخاب اشتباه)
BROADCAST_CODE  = "656646"  # رمز ارسال پیام همگانی (فقط ادمین سازمان ملل)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
#  اطلاعات کشورها
# ──────────────────────────────────────────────
COUNTRIES = {
    "🇺🇸 آمریکا": {
        "group": "NATO", "leader": "دونالد ترامپ", "level": "superpower", "flag": "🇺🇸",
        # آمریکا: نفت (اول جهان)، گاز (اول جهان)، زغال‌سنگ، طلا، اورانیوم
        "resources": ["oil", "gas", "coal", "gold", "uranium"],
        "weapons": {"rifle":"M4 Carbine","tank":"M1A2 Abrams","fighter":"F-35 Lightning II","bomber":"B-2 Spirit","missile_cruise":"BGM-109 Tomahawk","missile_ballistic":"MGM-140 ATACMS","drone_attack":"MQ-9 Reaper","drone_recon":"RQ-4 Global Hawk","air_defense":"Patriot / THAAD", "missile_special": "LGM-30G Minuteman III ICBM", "drone_special": "RQ-170 Sentinel"},
        "can_build": ["air_factory","bomber_factory","missile_factory","drone_factory","defense_factory","nuclear_plant","hack_room","satellite"],
    },
    "🇬🇧 انگلیس": {
        "group": "NATO", "leader": "کیر استارمر", "level": "powerful", "flag": "🇬🇧",
        # انگلیس: نفت و گاز دریای شمال، طلا
        "resources": ["oil", "gas", "gold"],
        "weapons": {"rifle":"SA80 L85A3","tank":"Challenger 3","fighter":"Eurofighter Typhoon","bomber":"Tornado GR4","missile_cruise":"Storm Shadow","missile_ballistic":"Brimstone","drone_attack":"Protector RG Mk1","drone_recon":"Watchkeeper WK450","air_defense":"Sky Sabre / CAMM", "missile_special": "Trident II D5 SLBM", "drone_special": "Protector RG Mk1"},
        "can_build": ["air_factory","missile_factory","drone_factory","defense_factory","nuclear_plant","hack_room"],
    },
    "🇫🇷 فرانسه": {
        "group": "NATO", "leader": "امانوئل ماکرون", "level": "powerful", "flag": "🇫🇷",
        # فرانسه: اورانیوم (بزرگ‌ترین هسته‌ای اروپا)، زغال‌سنگ
        "resources": ["uranium", "coal"],
        "weapons": {"rifle":"FAMAS / HK416","tank":"Leclerc","fighter":"Dassault Rafale F4","bomber":"Mirage 2000N","missile_cruise":"SCALP-EG","missile_ballistic":"ASMP-A","drone_attack":"Patroller","drone_recon":"MALE RPAS","air_defense":"Aster 30 SAMP/T", "missile_special": "M51.3 SLBM", "drone_special": "Dassault nEUROn UCAV"},
        "can_build": ["air_factory","missile_factory","drone_factory","defense_factory","nuclear_plant","hack_room"],
    },
    "🇩🇪 آلمان": {
        "group": "NATO", "leader": "فریدریش مرتس", "level": "powerful", "flag": "🇩🇪",
        # آلمان: زغال‌سنگ لیگنیت (اول اروپا)، گاز
        "resources": ["coal", "gas"],
        "weapons": {"rifle":"HK G36 / HK416","tank":"Leopard 2A7","fighter":"Eurofighter Typhoon","bomber":"Tornado ECR","missile_cruise":"Taurus KEPD 350","missile_ballistic":"IRIS-T SLM","drone_attack":"Heron TP","drone_recon":"EuroHawk","air_defense":"Patriot PAC-3 / IRIS-T", "missile_special": "Taurus KEPD 350", "drone_special": "Heron TP"},
        "can_build": ["air_factory","missile_factory","drone_factory","defense_factory","hack_room"],
    },
    "🇹🇷 ترکیه": {
        "group": "NATO", "leader": "رجب طیب اردوغان", "level": "powerful", "flag": "🇹🇷",
        # ترکیه: گاز (کشف دریای سیاه)، زغال‌سنگ لیگنیت، طلا
        "resources": ["gas", "coal", "gold"],
        "weapons": {"rifle":"MPT-76","tank":"Altay","fighter":"F-16 Fighting Falcon","bomber":"F-16C Block 70","missile_cruise":"SOM-J","missile_ballistic":"Bora","drone_attack":"Bayraktar TB2 / Akinci","drone_recon":"Bayraktar Akinci","air_defense":"HISAR-A+ / S-400", "missile_special": "Tayfun ICBM", "drone_special": "Bayraktar Akıncı UCAV"},
        "can_build": ["drone_factory","missile_factory","defense_factory","hack_room"],
    },
    "🇮🇹 ایتالیا": {
        "group": "NATO", "leader": "جورجیا ملونی", "level": "normal", "flag": "🇮🇹",
        # ایتالیا: گاز (دریای آدریاتیک)، زغال‌سنگ
        "resources": ["gas", "coal"],
        "weapons": {"rifle":"Beretta ARX-160","tank":"C1 Ariete","fighter":"Eurofighter Typhoon","bomber":"Tornado IDS","missile_cruise":"Aster 15","missile_ballistic":"CAMM-ER","drone_attack":"P.1HH HammerHead","drone_recon":"Heron","air_defense":"SAMP/T Aster 30", "missile_special": "Aster 30 SAMP/T", "drone_special": "P.1HH HammerHead"},
        "can_build": ["air_factory","missile_factory","defense_factory","hack_room"],
    },
    "🇵🇱 لهستان": {
        "group": "NATO", "leader": "دونالد توسک", "level": "normal", "flag": "🇵🇱",
        # لهستان: زغال‌سنگ (صادرکننده بزرگ اروپا)، گاز
        # لهستان: زغال‌سنگ (صادرکننده بزرگ اروپا)، گاز
        "resources": ["coal", "gas"],
        "weapons": {"rifle":"MSBS Grot","tank":"K2 Black Panther","fighter":"F-35 / FA-50","bomber":"Su-22","missile_cruise":"AGM-158 JASSM","missile_ballistic":"HIMARS","drone_attack":"Warmate","drone_recon":"FlyEye","air_defense":"Patriot / Narew SHORAD", "missile_special": "AGM-158B JASSM-ER", "drone_special": "FlyEye MALE"},
        "can_build": ["drone_factory","missile_factory","defense_factory","hack_room"],
    },
    "🇨🇦 کانادا": {
        "group": "NATO", "leader": "مارک کارنی", "level": "powerful", "flag": "🇨🇦",
        # کانادا: نفت، گاز، اورانیوم (بزرگ‌ترین صادرکننده)، طلا، زغال‌سنگ
        "resources": ["oil","gas","uranium","gold","coal"],
        "weapons": {"rifle":"Colt Canada C8","tank":"Leopard 2A6M CAN","fighter":"CF-18 Hornet","bomber":"CC-130 Hercules","missile_cruise":"CRV7","missile_ballistic":"NLOS","drone_attack":"Heron","drone_recon":"Sperwer","air_defense":"NASAMS", "missile_special": "CF-18 JDAM-ER", "drone_special": "MQ-9A Reaper"},
        "can_build": ["air_factory","missile_factory","defense_factory","hack_room"],
    },
    "🇳🇴 نروژ": {
        "group": "NATO", "leader": "یوناس گار استوره", "level": "normal", "flag": "🇳🇴",
        "resources": ["oil","gas"],
        "weapons": {"rifle":"HK416","tank":"Leopard 2A7NO","fighter":"F-35A","bomber":"F-35A","missile_cruise":"Naval Strike Missile","missile_ballistic":"NASAMS","drone_attack":"Penguin ASM","drone_recon":"Camcopter S-100","air_defense":"NASAMS", "missile_special": "Naval Strike Missile (NSM)", "drone_special": "MQ-4C Triton"},
        "can_build": ["missile_factory","defense_factory","hack_room"],
    },
    "🇬🇷 یونان": {
        "group": "NATO", "leader": "کیریاکوس میتسوتاکیس", "level": "normal", "flag": "🇬🇷",
        # یونان: نفت (دریای اژه)، گاز (مدیترانه شرقی)، طلا
        # یونان: نفت (دریای اژه)، گاز (مدیترانه شرقی)، طلا
        "resources": ["oil", "gas", "gold"],
        "weapons": {"rifle":"G3 / HK33","tank":"Leopard 2HEL","fighter":"F-16 Viper / Rafale","bomber":"F-16 Block 52+","missile_cruise":"Scalp / Taurus","missile_ballistic":"ATACMS","drone_attack":"Bayraktar TB2","drone_recon":"RQ-7 Shadow","air_defense":"Patriot / SHORAD", "missile_special": "ATACMS MGM-140", "drone_special": "Bayraktar TB2"},
        "can_build": ["missile_factory","defense_factory","hack_room"],
    },
    "🇪🇸 اسپانیا": {
        "group": "NATO", "leader": "پدرو سانچز", "level": "normal", "flag": "🇪🇸",
        # اسپانیا: زغال‌سنگ، طلا، اورانیوم (معادن فعال)
        "resources": ["coal", "gold", "uranium"],
        "weapons": {"rifle":"HK G36E","tank":"Leopard 2E","fighter":"Eurofighter Typhoon","bomber":"F/A-18 Hornet","missile_cruise":"Taurus KEPD 350E","missile_ballistic":"SILAM","drone_attack":"SIVA","drone_recon":"Searcher Mk2","air_defense":"Patriot / SHORAD", "missile_special": "Taurus KEPD 350E", "drone_special": "Atlante MALE UAV"},
        "can_build": ["air_factory","missile_factory","defense_factory","hack_room"],
    },
    "🇮🇱 اسرائیل": {
        "group": "NATO", "leader": "بنیامین نتانیاهو", "level": "powerful", "flag": "🇮🇱",
        "resources": ["gas"],
        "weapons": {"rifle":"IWI Tavor X95","tank":"Merkava Mk4M","fighter":"F-35I Adir","bomber":"F-15I Ra'am","missile_cruise":"Delilah / Popeye","missile_ballistic":"Jericho III","drone_attack":"IAI Harop / Hermes 900","drone_recon":"IAI Heron TP","air_defense":"Iron Dome / Arrow-3 / David's Sling", "missile_special": "Jericho III ICBM", "drone_special": "IAI Harop Loitering Munition"},
        "can_build": ["air_factory","missile_factory","drone_factory","defense_factory","hack_room","satellite"],
    },
    "🇷🇺 روسیه": {
        "group": "BRICS", "leader": "ولادیمیر پوتین", "level": "superpower", "flag": "🇷🇺",
        # روسیه: نفت، گاز، طلا (بزرگ‌ترین تولیدکننده)، اورانیوم، زغال‌سنگ
        "resources": ["oil","gas","gold","uranium","coal"],
        "weapons": {"rifle":"AK-12","tank":"T-14 Armata / T-90M","fighter":"Su-57 Felon","bomber":"Tu-160 Blackjack","missile_cruise":"Kalibr 3M14 / Kh-101","missile_ballistic":"Iskander-M / RS-28 Sarmat","drone_attack":"Shahed-136 / Lancet-3","drone_recon":"Orion","air_defense":"S-400 / S-500", "missile_special": "RS-28 Sarmat (Satan 2)", "drone_special": "S-70 Okhotnik UCAV"},
        "can_build": ["air_factory","bomber_factory","missile_factory","drone_factory","defense_factory","nuclear_plant","hack_room","satellite"],
    },
    "🇨🇳 چین": {
        "group": "BRICS", "leader": "شی جین‌پینگ", "level": "superpower", "flag": "🇨🇳",
        # چین: زغال‌سنگ (اول جهان)، نفت، گاز، طلا، اورانیوم
        "resources": ["coal","oil","gas","gold","uranium"],
        "weapons": {"rifle":"QBZ-191","tank":"Type 99A","fighter":"J-20 Mighty Dragon","bomber":"H-6K / H-20","missile_cruise":"DF-10A / CJ-10","missile_ballistic":"DF-41 / DF-21D","drone_attack":"Wing Loong II","drone_recon":"WZ-7 Soaring Dragon","air_defense":"HQ-9B / HQ-22", "missile_special": "DF-41 ICBM", "drone_special": "GJ-11 Sharp Sword UCAV"},
        "can_build": ["air_factory","bomber_factory","missile_factory","drone_factory","defense_factory","nuclear_plant","hack_room","satellite"],
    },
    "🇮🇳 هند": {
        "group": "BRICS", "leader": "ناریندرا مودی", "level": "powerful", "flag": "🇮🇳",
        # هند: زغال‌سنگ (سوم جهان)، نفت، طلا، اورانیوم
        "resources": ["coal","oil","gold","uranium"],
        "weapons": {"rifle":"INSAS / AK-203","tank":"Arjun Mk2","fighter":"Tejas Mk2 / Rafale","bomber":"Jaguar IS","missile_cruise":"BrahMos","missile_ballistic":"Agni-V","drone_attack":"Rustom-2","drone_recon":"TAPAS","air_defense":"Akash-NG / S-400", "missile_special": "Agni-V ICBM", "drone_special": "CATS Warrior UCAV"},
        "can_build": ["air_factory","missile_factory","drone_factory","defense_factory","nuclear_plant","hack_room"],
    },
    "🇧🇷 برزیل": {
        "group": "BRICS", "leader": "لوئیس لولا داسیلوا", "level": "normal", "flag": "🇧🇷",
        # برزیل: نفت، گاز، طلا، اورانیوم (ذخایر بزرگ)
        "resources": ["oil","gas","gold","uranium"],
        "weapons": {"rifle":"IA2","tank":"Leopard 1A5BR","fighter":"Gripen E/F","bomber":"A-29 Super Tucano","missile_cruise":"MAR-1","missile_ballistic":"SS-300","drone_attack":"Heron TP","drone_recon":"VANT","air_defense":"IGLA-S / RBS-70", "missile_special": "VLS-1 / ASTROS II MKVI", "drone_special": "OGMA/Embraer MALE UAV"},
        "can_build": ["air_factory","missile_factory","drone_factory","defense_factory","hack_room"],
    },
    "🇮🇷 ایران": {
        "group": "BRICS", "leader": "سید علی خامنه‌ای", "level": "powerful", "flag": "🇮🇷",
        # ایران: نفت (سوم جهان)، گاز (دوم جهان)، طلا، اورانیوم
        "resources": ["oil","gas","gold","uranium"],
        "weapons": {"rifle":"KH-2002 Khaybar","tank":"Karrar / T-72S","fighter":"HESA Kowsar","bomber":"F-4D Phantom","missile_cruise":"Quds-1 / Soumar","missile_ballistic":"Shahab-3 / Fattah","drone_attack":"Shahed-129 / Mohajer-6","drone_recon":"Mohajer-10","air_defense":"Bavar-373 / Raad", "missile_special": "Fattah-2 Hypersonic Missile", "drone_special": "Shahed-149 Gaza UCAV"},
        "can_build": ["missile_factory","drone_factory","defense_factory","nuclear_plant","hack_room","satellite"],
    },
    "🇸🇦 عربستان": {
        "group": "BRICS", "leader": "محمد بن سلمان", "level": "normal", "flag": "🇸🇦",
        # عربستان: نفت (دوم جهان)، گاز، طلا (معادن بزرگ)
        "resources": ["oil","gas","gold"],
        "weapons": {"rifle":"Steyr AUG / M16A2","tank":"M1A2 Abrams / Leopard 2A7","fighter":"Typhoon / F-15SA","bomber":"F-15SA","missile_cruise":"Storm Shadow / AGM-84","missile_ballistic":"DF-3A","drone_attack":"CH-4 / Wing Loong","drone_recon":"Heron","air_defense":"Patriot PAC-3 / THAAD", "missile_special": "DF-3A MRBM", "drone_special": "Wing Loong II"},
        "can_build": ["defense_factory","hack_room"],
    },
    "🇦🇪 امارات": {
        "group": "BRICS", "leader": "محمد بن زاید", "level": "normal", "flag": "🇦🇪",
        "resources": ["oil","gas"],
        "weapons": {"rifle":"Caracal","tank":"Leclerc UAE","fighter":"F-16E/F Desert Falcon","bomber":"Mirage 2000-9","missile_cruise":"Storm Shadow / Black Shaheen","missile_ballistic":"PATRIOT PAC-3","drone_attack":"YABHON / Wing Loong","drone_recon":"Yabhon-R","air_defense":"THAAD / Patriot", "missile_special": "Taurus KEPD 350", "drone_special": "YABHON United 40"},
        "can_build": ["defense_factory","hack_room"],
    },
    "🇵🇰 پاکستان": {
        "group": "BRICS", "leader": "شهباز شریف", "level": "normal", "flag": "🇵🇰",
        # پاکستان: نفت، گاز (کشف عظیم دریایی)، زغال‌سنگ (تار)، طلا
        "resources": ["oil","gas","coal","gold"],
        "weapons": {"rifle":"G3 / HK33","tank":"Al-Khalid-1 / VT-4","fighter":"JF-17 Thunder Block III","bomber":"Mirage IIIEP","missile_cruise":"Babur-3","missile_ballistic":"Shaheen-III","drone_attack":"Burraq","drone_recon":"Shahpar-2","air_defense":"HQ-9P / LY-80", "missile_special": "Shaheen-III MRBM", "drone_special": "NESCOM Burraq UCAV"},
        "can_build": ["missile_factory","drone_factory","nuclear_plant","hack_room","air_factory"],
    },
    "🇰🇵 کره شمالی": {
        "group": "BRICS", "leader": "کیم جونگ اون", "level": "normal", "flag": "🇰🇵",
        # کره شمالی: اورانیوم، زغال‌سنگ، طلا (معادن بزرگ)
        "resources": ["uranium","coal","gold"],
        "weapons": {"rifle":"Type 88","tank":"Chonma-ho / M2020","fighter":"MiG-29 / MiG-21","bomber":"H-5 Il-28","missile_cruise":"KN-23 / KN-25","missile_ballistic":"Hwasong-17 ICBM","drone_attack":"MUAV","drone_recon":"MUAV","air_defense":"KN-06 / S-200", "missile_special": "Hwasong-17 ICBM", "drone_special": "Haeil-2 Underwater Drone"},
        "can_build": ["missile_factory","drone_factory","nuclear_plant","hack_room"],
    },
    "🇮🇩 اندونزی": {
        "group": "BRICS", "leader": "پرابوو سوبیانتو", "level": "normal", "flag": "🇮🇩",
        # اندونزی: نفت، گاز، طلا، زغال‌سنگ (صادرکننده بزرگ)
        "resources": ["oil","gas","gold","coal"],
        "weapons": {"rifle":"SS2","tank":"Leopard 2A4 / Harimau","fighter":"F-16C/D / Rafale","bomber":"F-16","missile_cruise":"C-705","missile_ballistic":"RX-450","drone_attack":"Elang Hitam","drone_recon":"Wulung","air_defense":"Mistral / QW-3", "missile_special": "C-705 Anti-Ship Missile", "drone_special": "Elang Hitam MALE UCAV"},
        "can_build": ["drone_factory","missile_factory","defense_factory","hack_room"],
    },
    "🇿🇦 آفریقای جنوبی": {
        "group": "BRICS", "leader": "سیریل رامافوسا", "level": "normal", "flag": "🇿🇦",
        # آفریقای جنوبی: طلا (بزرگ‌ترین ذخیره)، اورانیوم، زغال‌سنگ
        "resources": ["gold","uranium","coal"],
        "weapons": {"rifle":"R4 / Vektor","tank":"Olifant Mk2","fighter":"Gripen C/D","bomber":"Hawk Mk120","missile_cruise":"Mokopa","missile_ballistic":"UMKHONTO","drone_attack":"Bateleur","drone_recon":"Seeker 400","air_defense":"Umkhonto-IR", "missile_special": "Mokopa ZT-6 ATGM", "drone_special": "Bateleur MALE UAV"},
        "can_build": ["drone_factory","missile_factory","defense_factory","hack_room"],
    },
    "🇪🇹 اتیوپی": {
        "group": "BRICS", "leader": "آبی احمد", "level": "colony", "flag": "🇪🇹",
        # اتیوپی: طلا، نفت (اوگادن)
        "resources": ["gold","oil"],
        "weapons": {"rifle":"AK-47","tank":"T-55 / T-62","fighter":"Su-27 / MiG-23","bomber":"MiG-23","missile_cruise":"9M14 Malyutka","missile_ballistic":"BM-21 Grad","drone_attack":"TB2","drone_recon":"Bayraktar Mini","air_defense":"S-75 / Tor-M1", "missile_special": "BM-30 Smerch MLRS", "drone_special": "Wing Loong II"},
        "can_build": ["hack_room"],
    },
    "🇦🇺 استرالیا": {
        "group": "BRICS", "leader": "آنتونی آلبانیز", "level": "powerful", "flag": "🇦🇺",
        # استرالیا: طلا (دوم جهان)، زغال‌سنگ (صادرکننده بزرگ)، اورانیوم (سوم جهان)، گاز (LNG)، نفت
        "resources": ["gold","coal","uranium","gas","oil"],
        "weapons": {
            "rifle": "EF88 Austeyr (F90)",
            "tank": "M1A2 SEPv3 Abrams",
            "fighter": "F-35A Lightning II / F/A-18F Super Hornet",
            "bomber": "EA-18G Growler",
            "missile_cruise": "BGM-109 Tomahawk / Naval Strike Missile (NSM)",
            "missile_ballistic": "HIMARS / AGM-158 JASSM-ER",
            "drone_attack": "MQ-9B SkyGuardian / Boeing MQ-28 Ghost Bat",
            "drone_recon": "MQ-4C Triton",
            "air_defense": "NASAMS / SM-6 / SM-2 Block IIIC",
            "missile_special": "AGM-158C LRASM",
            "drone_special":   "MQ-9B SkyGuardian",
        },
        "can_build": ["air_factory","missile_factory","drone_factory","defense_factory","hack_room","satellite"],
    },
}

LEVELS = {"colony":"مستعمره 🟫","normal":"عادی 🟡","powerful":"قدرتمند 🟠","superpower":"ابرقدرت 🔴"}

BUILDINGS = {
    "central_bank":     {"name":"🏦 بانک مرکزی",          "cost":100_000_000,"income":100_000_000,"max":1},
    "bitcoin_miner":    {"name":"₿ ماینر بیت‌کوین",       "cost":200_000_000,"income":300_000_000,"max":3},
    "money_printer":    {"name":"🖨️ پول‌چاپ‌کن",           "cost":100_000_000,"income":150_000_000,"max":3},
    "gas_field":        {"name":"⛽ میدان گازی",           "cost":20_000_000, "income":10_000_000, "max":3,"req_resource":"gas"},
    "oil_field":        {"name":"🛢️ میدان نفتی",           "cost":20_000_000, "income":10_000_000, "max":3,"req_resource":"oil"},
    "power_plant":      {"name":"⚡ نیروگاه برق",          "cost":20_000_000, "income":10_000_000, "max":3},
    "entertainment":    {"name":"🎡 امکانات تفریحی",       "cost":100_000_000,"income":50_000_000, "max":1},
    "gold_mine":        {"name":"🥇 معدن طلا",             "cost":150_000_000,"income":200_000_000,"max":3,"req_resource":"gold"},
    "copper_mine":      {"name":"🔶 معدن مس",              "cost":40_000_000, "income":40_000_000, "max":3},
    "silver_mine":      {"name":"🥈 معدن نقره",            "cost":80_000_000, "income":100_000_000,"max":3},
    "uranium_mine":     {"name":"☢️ معدن اورانیوم",        "cost":100_000_000,"income":150_000_000,"max":3,"req_resource":"uranium"},
    "oil_gas_refinery": {"name":"🏭 پالایشگاه",            "cost":100_000_000,"income":200_000_000,"max":3,"req_resource_any":["oil","gas"]},
    "medical":          {"name":"🏥 امکانات درمانی",       "cost":10_000_000, "income":0,          "max":1, "satisfaction":2},
    "police":           {"name":"👮 امکانات پلیس",         "cost":10_000_000, "income":0,          "max":1, "satisfaction":2},
    "fire":             {"name":"🚒 آتش‌نشانی",            "cost":10_000_000, "income":0,          "max":1, "satisfaction":2},
    "university":       {"name":"🎓 دانشگاه",              "cost":500_000_000,"income":0,          "max":1, "satisfaction":20},
}

MILITARY_BUILDINGS = {
    "bullet_factory":     {"name":"🏭 کارخانه فشنگ‌سازی",     "cost":50_000_000},
    "military_base":      {"name":"🪖 پایگاه نظامی",          "cost":100_000_000},
    "tank_factory":       {"name":"⚙️ کارخانه تانک‌سازی",    "cost":150_000_000},
    "missile_factory":    {"name":"🚀 کارخانه موشک/پهپاد",    "cost":250_000_000},
    "air_factory":        {"name":"✈️ کارخانه جنگنده",        "cost":300_000_000},
    "helicopter_factory": {"name":"🚁 کارخانه هلیکوپتر",      "cost":200_000_000},
    "naval_factory":      {"name":"⚓ کارخانه نیروی دریایی",  "cost":300_000_000},
    "propaganda":         {"name":"📢 شرکت پروپاگاندا",          "cost":400_000_000},
    "transport_aircraft": {"name":"🛫 هواپیمای ترابری",       "cost":50_000_000},
    "hack_room":          {"name":"💻 اتاق هک",               "cost":200_000_000},
    "defense_factory":    {"name":"🛡️ کارخانه پدافند",       "cost":150_000_000},
    "nuclear_plant":      {"name":"☢️ نیروگاه هسته‌ای",       "cost":300_000_000},
    "research_lab":       {"name":"🔬 پژوهشگاه نظامی",       "cost":450_000_000},
    "war_room":           {"name":"🗺️ اتاق جنگ",             "cost":200_000_000},
    "satellite":          {"name":"🛰️ ماهواره نظامی",         "cost":1_000_000_000},
}

# کارخانه مواد غذایی (سطوح مختلف)
FOOD_FACTORY_LEVELS = {
    "workshop":      {"name":"🥗 کارگاه غذایی",      "cost":100_000_000, "satisfaction":5,  "income":50_000_000},
    "factory":       {"name":"🏭 کارخانه غذایی",     "cost":200_000_000, "satisfaction":10, "income":100_000_000},
    "mega_factory":  {"name":"🏗️ ابر کارخونه غذایی","cost":300_000_000, "satisfaction":15, "income":150_000_000},
}

READY_MISSILES = {
    "missiles_cruise":    {"name":"🚀 موشک کروز",    "unit":10,"cost":10_000_000},
    "missiles_ballistic": {"name":"🚀 موشک بالستیک", "unit":10,"cost":20_000_000},
    "missiles_bunker":    {"name":"💥 موشک سنگرشکن", "unit":10,"cost":30_000_000},
}

READY_DRONES = {
    "drones_attack": {"name":"🤖 پهپاد تخریبی",        "unit":10,"cost":10_000_000},
    "drones_recon":  {"name":"📡 پهپاد شناسایی",       "unit":10,"cost":20_000_000},
    "drones_ewarf":  {"name":"📻 پهپاد الکترونیک",    "unit":10,"cost":30_000_000},
    "drones_mother": {"name":"💀 پهپاد مادر",           "unit":10,"cost":40_000_000},
}

WEAPON_LABELS = {
    "soldiers":           "👥 سرباز",
    "rifles":             "🔫 اسلحه",
    "tanks":              "⚙️ تانک",
    "fighters":           "✈️ جنگنده",
    "bombers":            "💣 بمب‌افکن",
    "helicopters":        "🚁 هلیکوپتر",
    "warships":           "🚢 کشتی جنگی",
    "aircraft_carriers":  "🛳️ ناو هواپیمابر",
    "submarines":         "🤿 زیردریایی",
    "missiles_cruise":    "🚀 موشک کروز",
    "missiles_ballistic": "☠️ موشک بالستیک",
    "missiles_bunker":    "💥 موشک ویژه",
    "drones_attack":      "🤖 پهپاد تخریبی",
    "drones_recon":       "📡 پهپاد شناسایی",
    "drones_ewarf":       "📻 پهپاد الکترونیک",
    "drones_mother":      "💀 پهپاد ویژه",
    "air_defense":        "🛡️ پدافند",
}

CYBER_ATTACKS = {
    "eco":  {"name":"💸 فلج اقتصادی",          "desc":"کاهش درآمد دشمن برای ۲ روز","normal_success":0.60,"luxury_success":0.80,"normal_effect":0.40,"luxury_effect":0.60,"defense_reduce":0.30},
    "steal":{"name":"💰 هک دارایی‌ها",          "desc":"دزدیدن پول از خزانه دشمن",   "normal_success":0.50,"luxury_success":0.70,"normal_effect":0.05,"luxury_effect":0.10,"defense_reduce":0.30},
    "dis":  {"name":"🔇 از کار انداختن تسلیحات","desc":"غیرفعال کردن تسلیحات برای ۱ روز","normal_success":0.45,"luxury_success":0.65,"normal_effect":0.20,"luxury_effect":0.35,"defense_reduce":0.35},
    "spy":  {"name":"🕵️ جاسوسی اطلاعات",       "desc":"مشاهده کامل دارایی‌های دشمن","normal_success":0.65,"luxury_success":0.85,"normal_effect":1.0, "luxury_effect":1.0, "defense_reduce":0.25},
}

# ──────────────────────────────────────────────
#  دیتابیس
# ──────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    return {"players":{},"taken_countries":[],"un_admins":[],"pending_trades":{}}

def save_data(data):
    with open(DATA_FILE,"w",encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_player(data, uid):
    return data["players"].get(str(uid))

def save_player(data, uid, player):
    data["players"][str(uid)] = player
    save_data(data)

def init_player(uid, country_name):
    c = COUNTRIES[country_name]
    return {
        "country": country_name, "group": c["group"],
        "money": 500_000_000, "level": c["level"],
        "banned": False, "nuclear_bomb": False, "nuclear_approved": False,
        "treasury_sent": 0,
        "satisfaction": 50,  # رضایت مردم 0-100
        "food_factories": [],  # لیست کارخانه‌های غذایی با سطح
        "buildings": {
            "central_bank":0,"bitcoin_miner":0,"money_printer":0,"treasury_deposits":[],
            "gas_field":0,"oil_field":0,"power_plant":0,"entertainment":0,
            "gold_mine":0,"copper_mine":0,"silver_mine":0,"uranium_mine":0,"oil_gas_refinery":0,
            "medical":0,"police":0,"fire":0,"university":0,
            "bullet_factory":0,"military_base":0,"tank_factory":0,
            "missile_factory":None,"air_factory":None,"hack_room":0,"hack_rooms":[],
            "defense_factory":0,"nuclear_plant":0,"nuclear_active":False,
            "research_lab":0,"war_room":0,"satellite":0,"nuclear_approved":False,
            "helicopter_factory":0,"transport_aircraft":0,
            "naval_factory":None,"propaganda":0,
        },
        "military": {
            "soldiers":0,"tanks":0,"fighters":0,"bombers":0,"helicopters":0,
            "warships":0,"aircraft_carriers":0,"submarines":0,
            "rifles":0,
            "missiles_cruise":0,"missiles_ballistic":0,"missiles_bunker":0,
            "drones_attack":0,"drones_recon":0,"drones_ewarf":0,"drones_mother":0,"air_defense":0,
        },
        "cyber_debuffs": {},
        "university_unlocked": [],
        "propaganda_used_today": False,
    }

# ──────────────────────────────────────────────
#  کمکی‌ها
# ──────────────────────────────────────────────
def fmt(n):
    return f"{int(n):,}".replace(",","،") + " $"

def kb(*rows):
    return InlineKeyboardMarkup(list(rows))

def btn(text, data):
    return InlineKeyboardButton(text, callback_data=str(data))

BACK = btn("🔙 بازگشت", "back_main")

# ──────────────────────────────────────────────
#  منوی اصلی
# ──────────────────────────────────────────────
async def main_menu(update, context, player, edit=False):
    cname = player["country"]
    c = COUNTRIES[cname]
    satisfaction = player.get("satisfaction", 50)
    if satisfaction >= 70:
        sat_emoji = "😊"
    elif satisfaction >= 40:
        sat_emoji = "😐"
    else:
        sat_emoji = "😢"
    text = (
        f"{c['flag']} *{cname}* | {player['group']}\n"
        f"👤 {c['leader']}\n"
        f"⭐ {LEVELS[player['level']]}\n"
        f"💰 موجودی: *{fmt(player['money'])}*\n"
        f"{sat_emoji} رضایت مردم: *{satisfaction}%*"
    )
    if player.get("banned"):
        text += "\n⛔ *تحریم شده‌اید!*"
    if player.get("nuclear_bomb"):
        text += "\n☢️ بمب اتم دارید"
    rows = [
        [btn("💰 اقتصاد","eco_menu"), btn("🪖 نظامی","mil_menu")],
        [btn("💸 انتقال","transfer_menu"), btn("🤝 معامله","trade_menu")],
        [btn("💼 دارایی‌ها","assets"), btn("⚔️ حمله","attack_menu")],
        [btn("💻 حمله سایبری","cyber_menu"), btn("🌐 اطلاعات کشور","country_info")],
        [btn("📨 ارتباط با سازمان ملل","msg_un"), btn("🏦 وام","loan_menu")],
        [btn("🤲 مذاکره","negotiation_menu"), btn("🔄 انتقال به اتحاد دیگر","switch_alliance")],
        [btn("📈 بورس بین‌المللی","stock_market"), btn("🕊️ پیمان صلح","peace_menu")],
        [btn("📜 تاریخچه جنگ‌ها","war_history")],
    ]
    if player["buildings"].get("nuclear_plant") and not player["buildings"].get("nuclear_active"):
        rows.append([btn("⚡ راه‌اندازی نیروگاه هسته‌ای","launch_nuclear")])
    if not player.get("nuclear_bomb") and player["buildings"].get("nuclear_active"):
        rows.append([btn("☢️ تولید بمب اتم","build_nuke")])
    if player["buildings"].get("propaganda"):
        used = player.get("propaganda_used_today", False)
        prop_label = "📢 پروپاگاندا (استفاده شد ✅)" if used else "📢 پروپاگاندا"
        rows.append([btn(prop_label, "propaganda_menu")])
    if player["buildings"].get("satellite"):
        sat_used = player.get("satellite_used_today", 0)
        sat_label = f"🛰️ ماهواره (استفاده شد {sat_used}/2 ✅)" if sat_used >= 2 else f"🛰️ ماهواره – اطلاعات نظامی ({sat_used}/2)"
        rows.append([btn(sat_label, "satellite_spy")])
    if cname in ["🇨🇳 چین", "🇬🇧 انگلیس"]:
        rows.append([btn("🌐 ساخت اتحاد جدید", "create_alliance_menu")])
    markup = kb(*rows)
    if edit:
        await update.callback_query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, reply_markup=markup, parse_mode="Markdown")

# ──────────────────────────────────────────────
#  /start
# ──────────────────────────────────────────────
async def start(update, context):
    uid = str(update.effective_user.id)
    data = load_data()
    if uid in data.get("un_admins", []):
        await un_menu(update, context)
        return
    player = get_player(data, uid)
    text = (
        "🌍 *WW3 CLUB*\n\n"
        "به بازی جنگ جهانی سوم خوش آمدید!\n"
        "۲۴ کشور از NATO و BRICS رویاروی هم."
    )
    if player:
        rows = [[btn("▶️ ادامه بازی","resume"), btn("📖 راهنما","help")]]
    else:
        rows = [[btn("🎮 شروع بازی","choose_group"), btn("📖 راهنما","help")]]
    await update.message.reply_text(text, reply_markup=kb(*rows), parse_mode="Markdown")

async def help_text(update, context):
    q = update.callback_query
    await q.answer()
    text = (
        "📖 *راهنمای WW3 CLUB*\n\n"
        "🔹 هر بازیکن یک کشور انتخاب می‌کند\n"
        "🔹 موجودی اولیه: ۵۰۰ میلیون دلار\n"
        "🔹 هر روز ساعت ۱۲ شب درآمدها شارژ می‌شن\n\n"
        "*بخش‌های اصلی:*\n"
        "💰 اقتصاد – ساخت تأسیسات درآمدزا\n"
        "🪖 نظامی – خرید تسلیحات و کارخانه\n"
        "💸 انتقال – ارسال پول یا تسلیحات\n"
        "🤝 معامله – فروش تسلیحات\n"
        "⚔️ حمله – درخواست جنگ به سازمان ملل\n"
        "💻 حمله سایبری – هک، جاسوسی، فلج اقتصادی\n"
        "💼 دارایی‌ها – مشاهده تمام داشته‌ها\n"
    )
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb([btn("🔙 بازگشت","back_start")]))

# ──────────────────────────────────────────────
#  انتخاب کشور - FIX: استفاده از hash برای نام کشور
# ──────────────────────────────────────────────
async def choose_group(update, context):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "🌐 *گروه خود را انتخاب کنید:*",
        parse_mode="Markdown",
        reply_markup=kb(
            [btn("🔵 NATO","group_NATO"), btn("🔴 BRICS","group_BRICS")],
            [btn("🔙 بازگشت","back_start")]
        )
    )

async def choose_country(update, context):
    q = update.callback_query
    await q.answer()
    group = q.data.split("_")[1]
    data = load_data()
    taken = data.get("taken_countries", [])
    available = [n for n,c in COUNTRIES.items() if c["group"]==group and n not in taken]
    if not available:
        await q.edit_message_text("⚠️ همه کشورهای این گروه انتخاب شده‌اند!")
        return
    import hashlib
    rows = []
    for cname in available:
        # FIX: country_map در bot_data ذخیره میشه - persistent
        ckey = hashlib.md5(cname.encode()).hexdigest()[:8]
        context.bot_data.setdefault("country_map", {})[ckey] = cname
        rows.append([btn(cname, f"select_{ckey}")])
    rows.append([btn("🔙 بازگشت","choose_group")])
    await q.edit_message_text(f"🏳️ *کشور {group} خود را انتخاب کنید:*", parse_mode="Markdown", reply_markup=kb(*rows))

async def select_country(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    ckey = q.data.replace("select_","",1)

    # FIX: اول از bot_data بخون
    cname = context.bot_data.get("country_map", {}).get(ckey)

    # FIX: اگه در bot_data نبود، همه کشورها رو بررسی کن با hash
    if not cname:
        import hashlib
        for name in COUNTRIES.keys():
            if hashlib.md5(name.encode()).hexdigest()[:8] == ckey:
                cname = name
                context.bot_data.setdefault("country_map", {})[ckey] = cname
                break

    if not cname:
        await q.answer("خطا! دوباره از منو انتخاب کنید.", show_alert=True)
        return

    data = load_data()

    # FIX: اگه بازیکن قبلاً کشور داشت، اول از taken_countries پاک کن
    existing_player = get_player(data, uid)
    if existing_player:
        old_country = existing_player.get("country")
        if old_country and old_country in data.get("taken_countries", []):
            data["taken_countries"].remove(old_country)

    if cname in data.get("taken_countries", []):
        await q.edit_message_text("⚠️ این کشور قبلاً انتخاب شده! کشور دیگری انتخاب کنید.",
                                   reply_markup=kb([btn("🔙 بازگشت","choose_group")])); return

    player = init_player(uid, cname)
    data["players"][uid] = player
    data.setdefault("taken_countries",[]).append(cname)
    save_data(data)
    c = COUNTRIES[cname]
    w = c["weapons"]
    info = (
        f"{c['flag']} *{cname}*\n"
        f"👤 رهبر: {c['leader']}\n"
        f"⭐ سطح: {LEVELS[c['level']]}\n"
        f"🌏 منابع: {', '.join(c['resources']) if c['resources'] else 'ندارد'}\n\n"
        f"🔫 تفنگ: {w['rifle']}\n"
        f"⚙️ تانک: {w['tank']}\n"
        f"✈️ جنگنده: {w['fighter']}\n"
        f"🚀 موشک کروز: {w['missile_cruise']}\n"
        f"🛡️ پدافند: {w['air_defense']}"
    )
    await q.edit_message_text(
        f"✅ *کشور شما انتخاب شد!*\n\n{info}\n\n💰 موجودی اولیه: {fmt(500_000_000)}",
        parse_mode="Markdown",
        reply_markup=kb([btn("▶️ وارد بازی","resume")])
    )

async def resume(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.edit_message_text("⚠️ ابتدا بازی را شروع کنید!", reply_markup=kb([btn("🎮 شروع","choose_group")]))
        return
    await main_menu(update, context, player, edit=True)

# ──────────────────────────────────────────────
#  اقتصاد
# ──────────────────────────────────────────────
async def eco_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("ابتدا بازی کنید!", show_alert=True); return
    rows = [
        [btn("🏦 بانک مرکزی","buy_central_bank"), btn("₿ ماینر","buy_bitcoin_miner")],
        [btn("🖨️ پول‌چاپ‌کن","buy_money_printer"), btn("🏛️ خزانه‌داری","treasury")],
        [btn("⛽ میدان گاز","buy_gas_field"), btn("🛢️ میدان نفت","buy_oil_field")],
        [btn("⚡ نیروگاه برق","buy_power_plant"), btn("🎡 تفریح","buy_entertainment")],
        [btn("🥇 معدن طلا","buy_gold_mine"), btn("🔶 معدن مس","buy_copper_mine")],
        [btn("🥈 معدن نقره","buy_silver_mine"), btn("☢️ معدن اورانیوم","buy_uranium_mine")],
        [btn("🏭 پالایشگاه","buy_oil_gas_refinery")],
        [btn("🏥 درمانی (+2% رضایت)","buy_medical"), btn("👮 پلیس (+2% رضایت)","buy_police")],
        [btn("🚒 آتش‌نشانی (+2% رضایت)","buy_fire")],
        [btn("🎓 دانشگاه (+20% رضایت)","buy_university")],
        [btn("🥗 کارخانه مواد غذایی","food_factory_menu")],
        [BACK]
    ]
    await q.edit_message_text(
        f"💰 *منوی اقتصاد*\n💵 موجودی: {fmt(player['money'])}",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def buy_building(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    key = q.data.replace("buy_","",1)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("ابتدا بازی کنید!", show_alert=True); return
    binfo = BUILDINGS.get(key)
    if not binfo:
        await q.answer("نامعتبر!", show_alert=True); return
    cname = player["country"]
    country = COUNTRIES[cname]
    current = player["buildings"].get(key, 0)
    if "req_resource" in binfo and binfo["req_resource"] not in country["resources"]:
        await q.edit_message_text(f"❌ کشور شما منبع لازم ندارد!", reply_markup=kb([btn("🔙 اقتصاد","eco_menu")])); return
    if "req_resource_any" in binfo and not any(r in country["resources"] for r in binfo["req_resource_any"]):
        await q.edit_message_text("❌ کشور شما نفت یا گاز ندارد!", reply_markup=kb([btn("🔙 اقتصاد","eco_menu")])); return
    if current >= binfo["max"]:
        await q.edit_message_text(f"❌ ظرفیت پر شده! (حداکثر {binfo['max']})", reply_markup=kb([btn("🔙 اقتصاد","eco_menu")])); return
    income_text = f"📈 درآمد روزانه: {fmt(binfo['income'])}" if binfo["income"] else "📊 بدون درآمد"
    context.user_data["pending_buy"] = {"key": key}
    await q.edit_message_text(
        f"🏗️ *{binfo['name']}*\n\n💵 هزینه: {fmt(binfo['cost'])}\n{income_text}\n📦 ساخته شده: {current}/{binfo['max']}\n💰 موجودی: {fmt(player['money'])}",
        parse_mode="Markdown",
        reply_markup=kb([btn("✅ تأیید خرید","confirm_buy"), btn("❌ لغو","eco_menu")])
    )

async def confirm_buy(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    pending = context.user_data.get("pending_buy")
    if not pending or not player:
        await q.edit_message_text("❌ خطا! دوباره تلاش کنید.", reply_markup=kb([btn("🔙 اقتصاد","eco_menu")])); return
    key = pending["key"]
    binfo = BUILDINGS.get(key)
    if not binfo:
        await q.answer("خطا!", show_alert=True); return
    current = player["buildings"].get(key, 0)
    if current >= binfo["max"]:
        await q.edit_message_text("❌ ظرفیت پر شده!", reply_markup=kb([btn("🔙 اقتصاد","eco_menu")])); return
    if player["money"] < binfo["cost"]:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙 اقتصاد","eco_menu")])); return
    player["money"] -= binfo["cost"]
    player["buildings"][key] = current + 1
    # اگه دانشگاه خریده شد همه کارخانه‌های محدود رو یکجا باز کن
    if key == "university":
        cname = player.get("country", "")
        country_data = COUNTRIES.get(cname, {})
        can_build = country_data.get("can_build", [])
        RESTRICTED_BUILDINGS = ["air_factory", "defense_factory", "nuclear_plant", "missile_factory"]
        locked = [k for k in RESTRICTED_BUILDINGS if k not in can_build]
        unlocked = player.get("university_unlocked", [])
        newly_unlocked = []
        for rb in locked:
            if rb not in unlocked:
                player.setdefault("university_unlocked", []).append(rb)
                newly_unlocked.append(MILITARY_BUILDINGS.get(rb, {}).get("name", rb))
    else:
        newly_unlocked = []
    # رضایت مردم
    sat_gain = binfo.get("satisfaction", 0)
    old_satisfaction = player.get("satisfaction", 50)
    if sat_gain:
        player["satisfaction"] = min(100, old_satisfaction + sat_gain)
    save_player(data, uid, player)
    context.user_data.pop("pending_buy", None)
    sat_txt = f"\n😊 رضایت مردم: {old_satisfaction}% ← {player.get('satisfaction', old_satisfaction)}% (+{sat_gain}%)" if sat_gain else ""
    unlock_txt = ("\n\n🎓 *قابلیت‌های باز شده:*\n" + "\n".join(f"  ✅ {n}" for n in newly_unlocked)) if newly_unlocked else ""
    await q.edit_message_text(
        f"✅ *{binfo['name']}* ساخته شد!{sat_txt}{unlock_txt}\n💰 موجودی: {fmt(player['money'])}",
        parse_mode="Markdown",
        reply_markup=kb([btn("🔙 اقتصاد","eco_menu"), btn("🏠 منو اصلی","resume")])
    )

async def food_factory_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    food_list = player.get("food_factories", [])
    count_str = ""
    if food_list:
        from collections import Counter
        counts = Counter(food_list)
        count_str = "\n".join([
            f"  {'🥗 کارگاه' if t=='workshop' else ('🏭 کارخانه' if t=='factory' else '🏗️ ابر کارخونه')}: {c} عدد"
            for t, c in counts.items()
        ])
        count_str = f"\n\n🏭 *موجود:*\n{count_str}"
    rows = []
    for lvl, info in FOOD_FACTORY_LEVELS.items():
        rows.append([btn(f"{info['name']} | {fmt(info['cost'])} | +{info['satisfaction']}% رضایت | درآمد: {fmt(info['income'])}/روز", f"buy_food_{lvl}")])
    rows.append([btn("🔙 اقتصاد","eco_menu")])
    await q.edit_message_text(
        f"🥗 *کارخانه مواد غذایی*\n(بدون محدودیت تعداد){count_str}\n\nسطح مورد نظر را انتخاب کنید:",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def buy_food_factory(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    lvl = q.data.replace("buy_food_","",1)
    data = load_data()
    player = get_player(data, uid)
    if not player or lvl not in FOOD_FACTORY_LEVELS:
        await q.answer("خطا!"); return
    info = FOOD_FACTORY_LEVELS[lvl]
    if player["money"] < info["cost"]:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙","food_factory_menu")])); return
    player["money"] -= info["cost"]
    player.setdefault("food_factories", []).append(lvl)
    satisfaction_gain = info["satisfaction"]
    player["satisfaction"] = min(100, player.get("satisfaction", 50) + satisfaction_gain)
    save_player(data, uid, player)
    await q.edit_message_text(
        f"✅ *{info['name']}* ساخته شد!\n+{satisfaction_gain}% رضایت مردم 😊\n💰 موجودی: {fmt(player['money'])}",
        parse_mode="Markdown",
        reply_markup=kb([btn("🔙 اقتصاد","eco_menu"), btn("🏠 منو","resume")])
    )

async def treasury_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    sent = player.get("treasury_sent", 0)
    context.user_data["awaiting"] = "treasury_amount"
    await q.edit_message_text(
        f"🏛️ *خزانه‌داری*\n\nپول می‌دهید، ۳ روز بعد ۲ برابر برمی‌گردد!\n💰 موجودی: {fmt(player['money'])}\n📤 در خزانه: {fmt(sent)}\n\nمقدار (میلیون) را تایپ کنید:",
        parse_mode="Markdown",
        reply_markup=kb([btn("🔙 بازگشت","eco_menu")])
    )

# ──────────────────────────────────────────────
#  نظامی
# ──────────────────────────────────────────────
async def mil_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("ابتدا بازی کنید!", show_alert=True); return
    rows = [
        [btn("🏭 فشنگ‌سازی","mil_buy_bullet_factory"), btn("🪖 پایگاه نظامی","mil_buy_military_base")],
        [btn("⚙️ تانک‌سازی","mil_buy_tank_factory"), btn("🚀 موشک/پهپادسازی","mil_buy_missile_factory")],
        [btn("✈️ جنگنده‌سازی","mil_buy_air_factory"), btn("🚁 هلیکوپترسازی","mil_buy_helicopter_factory")],
        [btn("⚓ نیروی دریایی","mil_buy_naval_factory"), btn("📢 شرکت پروپاگاندا (400M)","mil_buy_propaganda")],
        [btn("💻 اتاق هک","mil_buy_hack_room"), btn("🛡️ پدافندسازی","mil_buy_defense_factory")],
        [btn("🗺️ اتاق جنگ","mil_buy_war_room"), btn("🛫 هواپیمای ترابری (50M)","mil_buy_transport_aircraft")],
        [btn("☢️ نیروگاه هسته‌ای","mil_buy_nuclear_plant"), btn("🔬 پژوهشگاه","mil_buy_research_lab")],
        [btn("🛰️ ماهواره","mil_buy_satellite")],
        [btn("🚀 خرید موشک آماده","ready_missiles"), btn("🤖 خرید پهپاد آماده","ready_drones")],
        [BACK]
    ]
    await q.edit_message_text(
        f"🪖 *منوی نظامی*\n💵 موجودی: {fmt(player['money'])}",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def mil_buy(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    key = q.data.replace("mil_buy_","",1)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("ابتدا بازی کنید!", show_alert=True); return
    binfo = MILITARY_BUILDINGS.get(key)
    if not binfo:
        await q.answer("نامعتبر!", show_alert=True); return
    cname = player["country"]
    country = COUNTRIES[cname]
    b = player["buildings"]
    current = player["buildings"].get(key) or 0
    cost = binfo["cost"]

    # ماهواره: فقط ابرقدرت یا کشوری که satellite در can_build داره
    if key == "satellite":
        can_build = country.get("can_build", [])
        if player["level"] != "superpower" and "satellite" not in can_build:
            await q.edit_message_text("❌ ماهواره فقط برای ابرقدرت‌هاست!", reply_markup=kb([btn("🔙","mil_menu")])); return
        if player["buildings"].get("satellite"):
            await q.edit_message_text("❌ شما قبلاً ماهواره ساخته‌اید!\n🛰️ فقط یک ماهواره مجاز است.", reply_markup=kb([btn("🔙","mil_menu")])); return
        context.user_data["pending_mil"] = {"key": key, "cost": cost}
        await q.edit_message_text(
            f"🛰️ *ماهواره نظامی*\nهزینه: {fmt(cost)}\n\n"
            f"✅ قابلیت: یک‌بار در روز تجهیزات نظامی هر کشور را بدون اطلاع آن‌ها ببینید!\n"
            f"⚠️ فقط ۱ ماهواره قابل ساخت است.\n\nموجودی: {fmt(player['money'])}",
            parse_mode="Markdown",
            reply_markup=kb([btn("✅ تأیید","confirm_mil_buy"), btn("❌ لغو","mil_menu")])
        ); return

    # هواپیمای ترابری - فقط یکی کافیه
    if key == "transport_aircraft":
        if player["buildings"].get("transport_aircraft", 0) >= 1:
            await q.edit_message_text("✅ شما هواپیمای ترابری دارید!\n(یک عدد کافی است)", reply_markup=kb([btn("🔙","mil_menu")])); return
        context.user_data["pending_mil"] = {"key": key, "cost": 50_000_000}
        await q.edit_message_text(
            f"🛫 *هواپیمای ترابری*\nهزینه: {fmt(50_000_000)}\n\n⚠️ برای انتقال تسلیحات به کشورهای دیگر الزامی است!\nموجودی: {fmt(player['money'])}",
            parse_mode="Markdown",
            reply_markup=kb([btn("✅ تأیید","confirm_mil_buy"), btn("❌ لغو","mil_menu")])
        ); return

    # کارخانه هلیکوپتر - حداکثر 2
    if key == "helicopter_factory":
        current_heli = player["buildings"].get("helicopter_factory", 0)
        if current_heli >= 2:
            await q.edit_message_text("❌ حداکثر ۲ کارخانه هلیکوپتر می‌توانید داشته باشید!", reply_markup=kb([btn("🔙","mil_menu")])); return
        context.user_data["pending_mil"] = {"key": key, "cost": 200_000_000}
        await q.edit_message_text(
            f"🚁 *کارخانه هلیکوپتر*\nهزینه: {fmt(200_000_000)}\nروزی ۱۰ هلیکوپتر تولید می‌کند\nداری: {current_heli}/2\nموجودی: {fmt(player['money'])}",
            parse_mode="Markdown",
            reply_markup=kb([btn("✅ تأیید","confirm_mil_buy"), btn("❌ لغو","mil_menu")])
        ); return

    # کارخانه نیروی دریایی
    if key == "naval_factory":
        nf = player["buildings"].get("naval_factory")
        nf_dict = nf if isinstance(nf, dict) else ({nf: 1} if isinstance(nf, str) else {})
        total = sum(nf_dict.values())
        if total >= 15:
            await q.edit_message_text("❌ حداکثر ۱۵ کارخانه دریایی می‌توانید داشته باشید!", reply_markup=kb([btn("🔙","mil_menu")])); return
        w = nf_dict.get("warship", 0)
        c = nf_dict.get("carrier", 0)
        s = nf_dict.get("submarine", 0)
        context.user_data["pending_mil"] = {"key": key, "cost": 300_000_000}
        await q.edit_message_text(
            f"⚓ *کارخانه نیروی دریایی*\nهزینه: {fmt(300_000_000)}\nموجودی: {fmt(player['money'])}\n\n"
            f"فعلی: 🚢{w}/5 | 🛳️{c}/5 | 🤿{s}/5\n\nچه تولید کند؟",
            parse_mode="Markdown",
            reply_markup=kb(
                [btn(f"🚢 کشتی جنگی (10/روز) {w}/5","nf_warship")],
                [btn(f"🛳️ ناو هواپیمابر (1/روز) {c}/5","nf_carrier")],
                [btn(f"🤿 زیردریایی (20/روز) {s}/5","nf_submarine")],
                [btn("🔙","mil_menu")]
            )
        ); return

    # پروپاگاندا
    if key == "propaganda":
        if player["buildings"].get("propaganda"):
            await q.edit_message_text("❌ قبلاً شرکت پروپاگاندا ساخته‌اید!", reply_markup=kb([btn("🔙","mil_menu")])); return
        context.user_data["pending_mil"] = {"key": key, "cost": 400_000_000}
        await q.edit_message_text(
            f"📢 *شرکت پروپاگاندا*\nهزینه: {fmt(400_000_000)}\nموجودی: {fmt(player['money'])}\n\n"
            f"✅ یک بار در روز می‌توانید رضایت مردم کشور دیگری را ۵ تا ۲۰ درصد کاهش دهید.\n"
            f"🛡️ اگر هدف هم شرکت پروپاگاندا داشته باشد، ۱۰ درصد از اثر کم می‌شود.",
            parse_mode="Markdown",
            reply_markup=kb([btn("✅ تأیید","confirm_mil_buy"), btn("❌ لغو","mil_menu")])
        ); return

    # FIX: hack_room برای همه آزاد - فقط air_factory, defense_factory, nuclear_plant, missile_factory چک میشن
    # (hack_room از چک can_build حذف شد چون برای همه باز است)
    RESTRICTED_BUILDINGS = ["air_factory", "defense_factory", "nuclear_plant", "missile_factory"]
    university_unlocked = player.get("university_unlocked", [])
    if key in RESTRICTED_BUILDINGS and key not in country.get("can_build", []) and key not in university_unlocked:
        await q.edit_message_text(
            f"❌ کشور شما تکنولوژی این کارخانه را ندارد!\nاز کشورهای پیشرفته خریداری کنید یا با دانشگاه (🎓) آن را باز کنید.",
            reply_markup=kb([btn("🔙","mil_menu")])
        ); return

    # نوع کارخانه موشک
    if key == "missile_factory":
        current_count = b.get("missile_factory", 0) if isinstance(b.get("missile_factory"), int) else (1 if b.get("missile_factory") else 0)
        if current_count >= 5:
            await q.edit_message_text("❌ حداکثر ۵ کارخانه موشک/پهپاد می‌توانید داشته باشید!", reply_markup=kb([btn("🔙","mil_menu")])); return
        context.user_data["pending_mil"] = {"key": key, "cost": cost}
        await q.edit_message_text(
            f"🚀 *کارخانه موشک/پهپاد*\nهزینه: {fmt(cost)}\nتعداد فعلی: {current_count}/5\n\nچه تولید کند؟\n\n💥 موشک ویژه ← روزی ۵ تا (قوی‌ترین موشک کشورت)\n💀 پهپاد ویژه ← روزی ۵ تا (پیشرفته‌ترین پهپاد کشورت)",
            parse_mode="Markdown",
            reply_markup=kb([btn("💥 موشک ویژه","mf_missile"), btn("💀 پهپاد ویژه","mf_drone"), btn("🔙","mil_menu")])
        ); return

    # نوع کارخانه هوایی
    if key == "air_factory":
        current_count = b.get("air_factory", 0) if isinstance(b.get("air_factory"), int) else (1 if b.get("air_factory") else 0)
        if current_count >= 5:
            await q.edit_message_text("❌ حداکثر ۵ کارخانه هوایی می‌توانید داشته باشید!", reply_markup=kb([btn("🔙","mil_menu")])); return
        context.user_data["pending_mil"] = {"key": key, "cost": cost}
        await q.edit_message_text(
            f"✈️ *کارخانه هوایی*\\nهزینه: {fmt(cost)}\\nتعداد فعلی: {current_count}/5\\n\\nچه تولید کند؟\\n\\n✈️ جنگنده ← روزی ۱۰ تا\\n💣 بمب‌افکن ← روزی ۲ تا",
            parse_mode="Markdown",
            reply_markup=kb([btn("✈️ جنگنده","af_fighter"), btn("💣 بمب‌افکن","af_bomber"), btn("🔙","mil_menu")])
        ); return

    # اتاق هک - حداکثر 5 تا، دو نوع معمولی و لوکس
    if key == "hack_room":
        hack_list = player["buildings"].get("hack_rooms", [])
        current_hack = len(hack_list)
        if current_hack >= 5:
            await q.edit_message_text("❌ حداکثر ۵ اتاق هک می‌توانید داشته باشید!", reply_markup=kb([btn("🔙","mil_menu")])); return
        normal_count = hack_list.count("normal")
        luxury_count = hack_list.count("luxury")
        await q.edit_message_text(
            f"💻 *اتاق هک*\n"
            f"تعداد فعلی: {current_hack}/5 (معمولی: {normal_count} | لوکس: {luxury_count})\n\n"
            f"💻 معمولی: {fmt(200_000_000)}\n"
            f"💎 لوکس: {fmt(400_000_000)}\n\n"
            f"موجودی: {fmt(player['money'])}",
            parse_mode="Markdown",
            reply_markup=kb(
                [btn("💻 معمولی (200M)","hack_normal"), btn("💎 لوکس (400M)","hack_luxury")],
                [btn("🔙","mil_menu")]
            )
        ); return

    # کارخانه‌هایی که تا 3 تا میشه ساخت (air_factory و missile_factory جداگانه هندل میشن)
    MAX_3_FACTORIES = ["bullet_factory","military_base","tank_factory","defense_factory"]
    if key in MAX_3_FACTORIES:
        current_count = player["buildings"].get(key, 0) if isinstance(player["buildings"].get(key), int) else (1 if player["buildings"].get(key) else 0)
        if current_count >= 5:
            await q.edit_message_text(f"❌ حداکثر ۵ عدد از این کارخانه می‌توانید داشته باشید!", reply_markup=kb([btn("🔙","mil_menu")])); return
        context.user_data["pending_mil"] = {"key": key, "cost": cost}
        await q.edit_message_text(
            f"🏗️ *{binfo['name']}*\nهزینه: {fmt(cost)}\nتعداد فعلی: {current_count}/5\nموجودی: {fmt(player['money'])}",
            parse_mode="Markdown",
            reply_markup=kb([btn("✅ تأیید","confirm_mil_buy"), btn("❌ لغو","mil_menu")])
        ); return

    # چک تکراری
    if current and key not in ["bullet_factory","military_base"]:
        await q.edit_message_text("❌ قبلاً ساخته‌اید!", reply_markup=kb([btn("🔙","mil_menu")])); return

    context.user_data["pending_mil"] = {"key": key, "cost": cost}
    await q.edit_message_text(
        f"🏗️ *{binfo['name']}*\nهزینه: {fmt(cost)}\nموجودی: {fmt(player['money'])}",
        parse_mode="Markdown",
        reply_markup=kb([btn("✅ تأیید","confirm_mil_buy"), btn("❌ لغو","mil_menu")])
    )

async def missile_factory_type(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    prod_type = "missile" if q.data == "mf_missile" else "drone"
    data = load_data()
    player = get_player(data, uid)
    pending = context.user_data.get("pending_mil")
    if not pending or not player:
        await q.answer("خطا!"); return
    if player["money"] < pending["cost"]:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙","mil_menu")])); return
    player["money"] -= pending["cost"]
    # ذخیره به صورت dict تعداد هر نوع
    mf = player["buildings"].get("missile_factory")
    if not mf or mf == 0:
        player["buildings"]["missile_factory"] = {prod_type: 1}
    elif isinstance(mf, str):
        if mf == prod_type:
            player["buildings"]["missile_factory"] = {prod_type: 2}
        else:
            player["buildings"]["missile_factory"] = {mf: 1, prod_type: 1}
    elif isinstance(mf, dict):
        mf[prod_type] = mf.get(prod_type, 0) + 1
        player["buildings"]["missile_factory"] = mf
    else:
        player["buildings"]["missile_factory"] = {prod_type: 1}
    save_player(data, uid, player)
    context.user_data.pop("pending_mil", None)
    mf_now = player["buildings"]["missile_factory"]
    total = sum(mf_now.values()) if isinstance(mf_now, dict) else 1
    await q.edit_message_text(
        f"✅ کارخانه {'موشک 🚀' if prod_type=='missile' else 'پهپاد 🤖'} ساخته شد! (مجموع: {total}/5)\n💰 موجودی: {fmt(player['money'])}",
        reply_markup=kb([btn("🔙 نظامی","mil_menu")])
    )

async def air_factory_type(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    prod_type = "fighter" if q.data == "af_fighter" else "bomber"
    data = load_data()
    player = get_player(data, uid)
    pending = context.user_data.get("pending_mil")
    if not pending or not player:
        await q.answer("خطا!"); return
    if player["money"] < pending["cost"]:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙","mil_menu")])); return
    player["money"] -= pending["cost"]
    af = player["buildings"].get("air_factory")
    if not af or af == 0:
        player["buildings"]["air_factory"] = {prod_type: 1}
    elif isinstance(af, str):
        if af == prod_type:
            player["buildings"]["air_factory"] = {prod_type: 2}
        else:
            player["buildings"]["air_factory"] = {af: 1, prod_type: 1}
    elif isinstance(af, dict):
        af[prod_type] = af.get(prod_type, 0) + 1
        player["buildings"]["air_factory"] = af
    else:
        player["buildings"]["air_factory"] = {prod_type: 1}
    save_player(data, uid, player)
    context.user_data.pop("pending_mil", None)
    af_now = player["buildings"]["air_factory"]
    total = sum(af_now.values()) if isinstance(af_now, dict) else 1
    await q.edit_message_text(
        f"✅ کارخانه {'جنگنده ✈️' if prod_type=='fighter' else 'بمب‌افکن 💣'} ساخته شد! (مجموع: {total}/5)\n💰 موجودی: {fmt(player['money'])}",
        reply_markup=kb([btn("🔙 نظامی","mil_menu")])
    )

async def hack_type(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    hack_kind = "luxury" if q.data == "hack_luxury" else "normal"
    cost = 400_000_000 if hack_kind == "luxury" else 200_000_000
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    hack_list = player["buildings"].get("hack_rooms", [])
    if len(hack_list) >= 5:
        await q.edit_message_text("❌ حداکثر ۵ اتاق هک می‌توانید داشته باشید!", reply_markup=kb([btn("🔙","mil_menu")])); return
    if player["money"] < cost:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙","mil_menu")])); return
    player["money"] -= cost
    hack_list.append(hack_kind)
    player["buildings"]["hack_rooms"] = hack_list
    # سازگاری: hack_room قدیمی رو هم آپدیت کن
    player["buildings"]["hack_room"] = len(hack_list)
    save_player(data, uid, player)
    label = "لوکس 💎" if hack_kind == "luxury" else "معمولی 💻"
    normal_c = hack_list.count("normal")
    luxury_c = hack_list.count("luxury")
    await q.edit_message_text(
        f"✅ اتاق هک {label} ساخته شد!\n"
        f"مجموع: {len(hack_list)}/5 (معمولی: {normal_c} | لوکس: {luxury_c})\n"
        f"💰 موجودی: {fmt(player['money'])}",
        reply_markup=kb([btn("🔙 نظامی","mil_menu")])
    )

async def naval_factory_type(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    type_map = {"nf_warship": "warship", "nf_carrier": "carrier", "nf_submarine": "submarine"}
    prod_type = type_map.get(q.data)
    if not prod_type:
        await q.answer("خطا!"); return
    data = load_data()
    player = get_player(data, uid)
    pending = context.user_data.get("pending_mil")
    if not pending or not player:
        await q.answer("خطا!"); return
    nf = player["buildings"].get("naval_factory")
    nf_dict = nf if isinstance(nf, dict) else ({nf: 1} if isinstance(nf, str) else {})
    if nf_dict.get(prod_type, 0) >= 5:
        names = {"warship":"کشتی جنگی","carrier":"ناو هواپیمابر","submarine":"زیردریایی"}
        await q.edit_message_text(f"❌ حداکثر ۵ کارخانه {names[prod_type]} می‌توانید داشته باشید!", reply_markup=kb([btn("🔙","mil_menu")])); return
    if player["money"] < pending["cost"]:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙","mil_menu")])); return
    player["money"] -= pending["cost"]
    nf_dict[prod_type] = nf_dict.get(prod_type, 0) + 1
    player["buildings"]["naval_factory"] = nf_dict
    save_player(data, uid, player)
    context.user_data.pop("pending_mil", None)
    names = {"warship":"🚢 کشتی جنگی (۱۰/روز)", "carrier":"🛳️ ناو هواپیمابر (۱/روز)", "submarine":"🤿 زیردریایی (۲۰/روز)"}
    total = sum(nf_dict.values())
    await q.edit_message_text(
        f"✅ کارخانه {names[prod_type]} ساخته شد! (مجموع: {total}/15)\n💰 موجودی: {fmt(player['money'])}",
        reply_markup=kb([btn("🔙 نظامی","mil_menu")])
    )

async def confirm_mil_buy(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    pending = context.user_data.get("pending_mil")
    if not pending or not player:
        await q.edit_message_text("❌ خطا!", reply_markup=kb([btn("🔙","mil_menu")])); return
    key = pending["key"]
    cost = pending["cost"]
    if player["money"] < cost:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙","mil_menu")])); return
    player["money"] -= cost
    MAX_3_FACTORIES = ["bullet_factory","military_base","tank_factory","air_factory","missile_factory","defense_factory"]
    if key in ["bullet_factory","military_base","helicopter_factory","transport_aircraft","hack_room"] or key in MAX_3_FACTORIES:
        player["buildings"][key] = player["buildings"].get(key, 0) + 1
    elif key == "propaganda":
        player["buildings"]["propaganda"] = 1
    else:
        player["buildings"][key] = 1
    save_player(data, uid, player)
    context.user_data.pop("pending_mil", None)
    bname = MILITARY_BUILDINGS[key]["name"]
    await q.edit_message_text(
        f"✅ *{bname}* ساخته شد!\n💰 موجودی: {fmt(player['money'])}",
        parse_mode="Markdown",
        reply_markup=kb([btn("🔙 نظامی","mil_menu"), btn("🏠 منو اصلی","resume")])
    )

async def ready_missiles_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    rows = []
    for k, v in READY_MISSILES.items():
        rows.append([btn(f"{v['name']} | {v['unit']} عدد | {fmt(v['cost'])}", f"buyrm_{k}")])
    rows.append([btn("🔙 نظامی","mil_menu")])
    await q.edit_message_text(
        f"🚀 *خرید موشک آماده*\n💰 موجودی: {fmt(player['money'])}",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def ready_drones_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    rows = []
    for k, v in READY_DRONES.items():
        rows.append([btn(f"{v['name']} | {v['unit']} عدد | {fmt(v['cost'])}", f"buyrd_{k}")])
    rows.append([btn("🔙 نظامی","mil_menu")])
    await q.edit_message_text(
        f"🤖 *خرید پهپاد آماده*\n💰 موجودی: {fmt(player['money'])}",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def buy_ready_missile(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    key = q.data.replace("buyrm_","",1)
    data = load_data()
    player = get_player(data, uid)
    v = READY_MISSILES.get(key)
    if not player or not v:
        await q.answer("خطا!"); return
    if player["money"] < v["cost"]:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙","ready_missiles")])); return
    player["money"] -= v["cost"]
    player["military"][key] = player["military"].get(key, 0) + v["unit"]
    save_player(data, uid, player)
    await q.edit_message_text(
        f"✅ {v['unit']} عدد {v['name']} خریداری شد!\n💰 موجودی: {fmt(player['money'])}",
        reply_markup=kb([btn("🔙 نظامی","mil_menu"), btn("🏠 منو اصلی","resume")])
    )

async def buy_ready_drone(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    key = q.data.replace("buyrd_","",1)
    data = load_data()
    player = get_player(data, uid)
    v = READY_DRONES.get(key)
    if not player or not v:
        await q.answer("خطا!"); return
    if player["money"] < v["cost"]:
        await q.edit_message_text("❌ موجودی کافی نیست!", reply_markup=kb([btn("🔙","ready_drones")])); return
    player["money"] -= v["cost"]
    player["military"][key] = player["military"].get(key, 0) + v["unit"]
    save_player(data, uid, player)
    await q.edit_message_text(
        f"✅ {v['unit']} عدد {v['name']} خریداری شد!\n💰 موجودی: {fmt(player['money'])}",
        reply_markup=kb([btn("🔙 نظامی","mil_menu"), btn("🏠 منو اصلی","resume")])
    )

# ──────────────────────────────────────────────
#  دارایی‌ها
# ──────────────────────────────────────────────
def calc_satisfaction_multiplier(satisfaction):
    """محاسبه ضریب و برچسب درآمد بر اساس رضایت مردم"""
    if satisfaction >= 100:   return 2.0, "🌟 ۱۰۰%+: درآمد ۲ برابر"
    elif satisfaction >= 90:  return 1.6, "😍 ۹۰-۹۹%: +۶۰%"
    elif satisfaction >= 80:  return 1.4, "😊 ۸۰-۸۹%: +۴۰%"
    elif satisfaction >= 70:  return 1.2, "🙂 ۷۰-۷۹%: +۲۰%"
    elif satisfaction >= 60:  return 1.1, "😐 ۶۰-۶۹%: +۱۰%"
    elif satisfaction >= 40:  return 1.0, "😑 ۴۰-۵۹%: بدون تغییر"
    elif satisfaction >= 30:  return 0.9, "😟 ۳۰-۳۹%: -۱۰%"
    elif satisfaction >= 20:  return 0.8, "😢 ۲۰-۲۹%: -۲۰%"
    elif satisfaction >= 10:  return 0.6, "😡 ۱۰-۱۹%: -۴۰%"
    elif satisfaction >= 0:   return 0.5, "💀 ۰-۹%: -۵۰%"
    elif satisfaction >= -9:  return 0.4, "☠️ -۱ تا -۹%: -۶۰%"
    elif satisfaction >= -19: return 0.2, "💥 -۱۰ تا -۱۹%: -۸۰%"
    else:                     return 0.0, "🔴 زیر -۲۰%: انقلاب!"

async def assets_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    b = player["buildings"]
    m = player["military"]
    cname = player["country"]
    w = COUNTRIES[cname]["weapons"]

    eco_lines = []
    eco_total_income = 0
    for k, binfo in BUILDINGS.items():
        v = b.get(k, 0)
        if v and k != "treasury_deposits":
            income_daily = binfo.get("income", 0) * v
            eco_total_income += income_daily
            income_str = f" | درآمد: {fmt(income_daily)}/روز" if income_daily else ""
            eco_lines.append(f"  {binfo['name']}: {v}{income_str}")

    # کارخانه‌های غذایی
    food_factories = player.get("food_factories", [])
    food_lines = []
    if food_factories:
        from collections import Counter
        food_counts = Counter(food_factories)
        for ft, fc in food_counts.items():
            finfo = FOOD_FACTORY_LEVELS.get(ft, {})
            total_income = finfo.get("income", 0) * fc
            eco_total_income += total_income
            food_lines.append(f"  {finfo.get('name','?')}: {fc} عدد | درآمد: {fmt(total_income)}/روز")

    mil_build_lines = []
    for k, binfo in MILITARY_BUILDINGS.items():
        v = b.get(k)
        if v:
            detail = ""
            if k == "missile_factory":
                if isinstance(v, dict):
                    parts = []
                    if v.get("missile"): parts.append(f"🚀 موشک x{v['missile']}")
                    if v.get("drone"):   parts.append(f"🤖 پهپاد x{v['drone']}")
                    total = sum(v.values())
                    detail = f" ({' | '.join(parts)} | مجموع: {total})"
                elif isinstance(v, str):
                    detail = f" ({'🚀 موشک' if v=='missile' else '🤖 پهپاد'} x1)"
                elif isinstance(v, int):
                    detail = f" ({v} عدد)"
            elif k == "air_factory":
                if isinstance(v, dict):
                    parts = []
                    if v.get("fighter"): parts.append(f"✈️ جنگنده x{v['fighter']}")
                    if v.get("bomber"):  parts.append(f"💣 بمب‌افکن x{v['bomber']}")
                    total = sum(v.values())
                    detail = f" ({' | '.join(parts)} | مجموع: {total})"
                elif isinstance(v, str):
                    detail = f" ({'✈️ جنگنده' if v=='fighter' else '💣 بمب‌افکن'} x1)"
                elif isinstance(v, int):
                    detail = f" ({v} عدد)"
            elif k in ["tank_factory","defense_factory","bullet_factory","military_base"] and isinstance(v, int) and v > 1:
                detail = f" ({v} عدد)"
            elif k == "hack_room":
                hack_list = b.get("hack_rooms", [])
                if hack_list:
                    n = hack_list.count("normal")
                    lx = hack_list.count("luxury")
                    detail = f" ({n} معمولی 💻 + {lx} لوکس 💎)" if n and lx else (f" ({lx} لوکس 💎)" if lx else f" ({n} معمولی 💻)")
                else:
                    detail = f" ({v} اتاق)"
            elif k == "helicopter_factory":
                detail = f" ({v} عدد)"
            elif k == "naval_factory" and isinstance(v, str):
                naval_names = {"warship":"🚢 کشتی جنگی", "carrier":"🛳️ ناو هواپیمابر", "submarine":"🤿 زیردریایی"}
                detail = f" ({naval_names.get(v, v)})"
            elif k == "propaganda":
                detail = " (📢 فعال)"
            elif k == "transport_aircraft":
                detail = f" ({v} عدد)"
            mil_build_lines.append(f"  {binfo['name']}{detail}")

    country_info = COUNTRIES[cname]
    resources = country_info.get("resources", [])
    res_map = {"oil":"🛢️ نفت","gas":"⛽ گاز","gold":"🥇 طلا","uranium":"☢️ اورانیوم","coal":"⚫ زغال"}
    res_str = " | ".join([res_map.get(r, r) for r in resources]) if resources else "ندارد"

    # محاسبه درآمد واقعی با ضریب رضایت
    satisfaction = player.get("satisfaction", 50)
    sat_multiplier, sat_label = calc_satisfaction_multiplier(satisfaction)
    real_income = int(eco_total_income * sat_multiplier)
    sat_diff = real_income - eco_total_income
    sat_emoji = "😊" if satisfaction >= 70 else ("😐" if satisfaction >= 40 else "😢")
    if sat_diff > 0:
        sat_income_str = f"\n📈 درآمد واقعی (با رضایت): *{fmt(real_income)}* _(+{fmt(sat_diff)})_"
    elif sat_diff < 0:
        sat_income_str = f"\n📉 درآمد واقعی (با رضایت): *{fmt(real_income)}* _({fmt(sat_diff)})_"
    else:
        sat_income_str = ""

    text = (
        f"💼 *دارایی‌های {cname}*\n"
        f"💰 موجودی: *{fmt(player['money'])}*\n"
        f"🌏 منابع: {res_str}\n"
        f"⭐ سطح: {LEVELS[player['level']]}\n"
        f"{sat_emoji} رضایت مردم: *{satisfaction}%* | {sat_label}\n\n"
        f"🏗️ *تأسیسات اقتصادی:*\n" + ("\n".join(eco_lines) if eco_lines else "  ندارد") + "\n"
        f"📈 درآمد پایه روزانه: {fmt(eco_total_income)}{sat_income_str}\n\n"
        + (f"🥗 *کارخانه‌های غذایی:*\n" + ("\n".join(food_lines) if food_lines else "  ندارد") + "\n\n" if True else "")
        + f"🏭 *تأسیسات نظامی:*\n" + ("\n".join(mil_build_lines) if mil_build_lines else "  ندارد") + "\n\n"
        f"⚔️ *نیروی نظامی:*\n"
        f"  👥 سرباز: {m.get('soldiers',0):,}\n"
        f"  🔫 اسلحه ({w['rifle']}): {m.get('rifles',0):,}\n"
        f"  ⚙️ تانک ({w['tank']}): {m.get('tanks',0):,}\n"
        f"  ✈️ جنگنده ({w['fighter']}): {m.get('fighters',0):,}\n"
        f"  💣 بمب‌افکن ({w['bomber']}): {m.get('bombers',0):,}\n"
        f"  🚁 هلیکوپتر: {m.get('helicopters',0):,}\n"
        f"  🚢 کشتی جنگی: {m.get('warships',0):,}\n"
        f"  🛳️ ناو هواپیمابر: {m.get('aircraft_carriers',0):,}\n"
        f"  🤿 زیردریایی: {m.get('submarines',0):,}\n"
        f"  🚀 موشک کروز ({w['missile_cruise']}): {m.get('missiles_cruise',0):,}\n"
        f"  ☠️ موشک بالستیک ({w['missile_ballistic']}): {m.get('missiles_ballistic',0):,}\n"
        f"  💥 موشک ویژه ({w.get('missile_special','موشک ویژه')}): {m.get('missiles_bunker',0):,}\n"
        f"  🤖 پهپاد تخریبی ({w['drone_attack']}): {m.get('drones_attack',0):,}\n"
        f"  📡 پهپاد شناسایی ({w['drone_recon']}): {m.get('drones_recon',0):,}\n"
        f"  📻 پهپاد الکترونیک: {m.get('drones_ewarf',0):,}\n"
        f"  💀 پهپاد ویژه ({w.get('drone_special','پهپاد ویژه')}): {m.get('drones_mother',0):,}\n"
        f"  🛡️ پدافند ({w['air_defense']}): {m.get('air_defense',0):,}\n"
    )
    if b.get("nuclear_plant"):
        text += f"\n☢️ نیروگاه: {'فعال ✅' if b.get('nuclear_active') else 'غیرفعال ⏳'}"
    if player.get("nuclear_bomb"):
        text += "\n💣 بمب اتم: دارد ☢️"
    if player.get("treasury_sent"):
        text += f"\n📤 در خزانه‌داری: {fmt(player.get('treasury_sent',0))}"
    if player.get("banned"):
        text += "\n⛔ وضعیت: تحریم"

    rows = [
        [btn("➖ کم کردن دارایی نظامی","self_mil_subtract")],
        [BACK]
    ]
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb(*rows))

# ──────────────────────────────────────────────
#  کم کردن تسلیحات
# ──────────────────────────────────────────────
async def self_mil_subtract(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    m = player["military"]
    rows = []
    for wkey, label in WEAPON_LABELS.items():
        if m.get(wkey, 0) > 0:
            rows.append([btn(f"{label}: {m[wkey]:,}", f"selfmiltype_{wkey}")])
    if not rows:
        await q.edit_message_text("⚠️ تسلیحاتی ندارید!", reply_markup=kb([btn("🔙","assets")])); return
    rows.append([btn("🔙 بازگشت","assets")])
    await q.edit_message_text("➖ *کم کردن تسلیحات*\nکدام سلاح؟", parse_mode="Markdown", reply_markup=kb(*rows))

async def self_mil_subtract_type(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    wkey = q.data.replace("selfmiltype_","",1)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    label = WEAPON_LABELS.get(wkey, wkey)
    current = player["military"].get(wkey, 0)
    context.user_data["self_mil_wkey"] = wkey
    context.user_data["awaiting"] = "self_milsub_amount"
    await q.edit_message_text(
        f"➖ *کم کردن {label}*\nموجودی فعلی: {current:,}\nتعداد کم کردن را تایپ کنید:",
        parse_mode="Markdown",
        reply_markup=kb([btn("🔙","self_mil_subtract")])
    )

# ──────────────────────────────────────────────
#  انتقال
# ──────────────────────────────────────────────
async def transfer_menu(update, context):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "💸 *انتقال – چه چیزی؟*", parse_mode="Markdown",
        reply_markup=kb(
            [btn("💰 انتقال پول","transfer_money"), btn("⚔️ انتقال تسلیحات","transfer_weapons")],
            [BACK]
        )
    )

async def transfer_money_countries(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    active = [(cid, p["country"]) for cid, p in data["players"].items() if cid != uid]
    if not active:
        await q.edit_message_text("⚠️ کشوری فعال نیست!", reply_markup=kb([BACK])); return
    rows = [[btn(cname, f"tm_{cid}")] for cid, cname in active]
    rows.append([BACK])
    await q.edit_message_text("💰 *انتقال پول – مقصد را انتخاب کنید:*", parse_mode="Markdown", reply_markup=kb(*rows))

async def transfer_money_select(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("tm_","",1)
    data = load_data()
    target = data["players"].get(target_uid)
    if not target:
        await q.answer("خطا!", show_alert=True); return
    context.user_data["transfer_target_uid"] = target_uid
    context.user_data["transfer_target"] = target["country"]
    context.user_data["awaiting"] = "transfer_money_amount"
    await q.edit_message_text(
        f"💰 انتقال به *{target['country']}*\nمقدار (میلیون دلار) را تایپ کنید:",
        parse_mode="Markdown", reply_markup=kb([btn("🔙","transfer_menu")])
    )

async def transfer_weapons_countries(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    m = player["military"]
    has_weapons = any(m.get(k,0) > 0 for k in WEAPON_LABELS)
    if not has_weapons:
        await q.edit_message_text("⚠️ تسلیحاتی برای انتقال ندارید!", reply_markup=kb([BACK])); return
    rows = []
    for wkey, label in WEAPON_LABELS.items():
        if m.get(wkey, 0) > 0:
            rows.append([btn(f"{label}: {m[wkey]:,}", f"twtype_{wkey}")])
    rows.append([BACK])
    context.user_data["transfer_weapons_basket"] = {}
    await q.edit_message_text("⚔️ *کدام تسلیح؟*\nانتخاب کنید (هر بار ۱۰ واحد):", parse_mode="Markdown", reply_markup=kb(*rows))

async def transfer_weapon_add(update, context):
    """FIX: هندلر انتخاب نوع تسلیح برای انتقال"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    wkey = q.data.replace("twtype_","",1)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    m = player["military"]
    basket = context.user_data.get("transfer_weapons_basket", {})
    avail = m.get(wkey, 0)
    current = basket.get(wkey, 0)
    step = get_weapon_step(wkey)
    add = min(step, avail - current)
    if add <= 0:
        await q.answer("موجودی کافی نیست!", show_alert=True); return
    basket[wkey] = current + add
    context.user_data["transfer_weapons_basket"] = basket

    basket_text = "\n".join([f"{WEAPON_LABELS.get(k,k)}: {v}" for k,v in basket.items()])
    rows = []
    for wk, label in WEAPON_LABELS.items():
        if m.get(wk, 0) > 0:
            s = basket.get(wk, 0)
            step_wk = get_weapon_step(wk)
            step_txt = f"+{step_wk}" if step_wk > 1 else "+۱"
            mark = f" ✅{s}" if s else ""
            rows.append([btn(f"{label} ({m[wk]:,}){mark} [{step_txt}]", f"twtype_{wk}")])
    rows.append([btn("✅ انتخاب مقصد","tw_select_target"), btn("🔙","transfer_menu")])
    await q.edit_message_text(
        f"📦 *تسلیحات انتخابی:*\n{basket_text}\n\n💡 موشک/پهپاد = +۱۰ | بقیه = +۱\nبیشتر اضافه کنید یا مقصد را انتخاب کنید:",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def transfer_weapon_target(update, context):
    """انتخاب مقصد برای انتقال تسلیحات"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    basket = context.user_data.get("transfer_weapons_basket", {})
    if not basket:
        await q.edit_message_text("⚠️ تسلیحاتی انتخاب نکردید!", reply_markup=kb([btn("🔙","transfer_weapons")])); return
    active = [(cid, p["country"]) for cid, p in data["players"].items() if cid != uid]
    if not active:
        await q.edit_message_text("⚠️ کشوری فعال نیست!", reply_markup=kb([BACK])); return
    rows = [[btn(cname, f"twdest_{cid}")] for cid, cname in active]
    rows.append([btn("🔙","transfer_weapons")])
    await q.edit_message_text("🎯 *مقصد انتقال تسلیحات:*", parse_mode="Markdown", reply_markup=kb(*rows))

async def transfer_weapon_confirm(update, context):
    """تأیید و اجرای انتقال تسلیحات"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    target_uid = q.data.replace("twdest_","",1)
    data = load_data()
    player = get_player(data, uid)
    target = data["players"].get(target_uid)
    basket = context.user_data.get("transfer_weapons_basket", {})
    if not player or not target or not basket:
        await q.answer("خطا!", show_alert=True); return
    if player.get("banned"):
        await q.edit_message_text("⛔ شما تحریم هستید!", reply_markup=kb([BACK])); return
    # چک هواپیمای ترابری
    if not player["buildings"].get("transport_aircraft", 0):
        await q.edit_message_text(
            "❌ *هواپیمای ترابری ندارید!*\n\nبرای انتقال تسلیحات باید هواپیمای ترابری (🛫) داشته باشید.\nاز منوی نظامی خریداری کنید (۵۰ میلیون دلار).",
            parse_mode="Markdown",
            reply_markup=kb([btn("🪖 منوی نظامی","mil_menu"), btn("🔙","transfer_menu")])
        ); return
    # انتقال
    for wkey, amount in basket.items():
        current = player["military"].get(wkey, 0)
        if amount > current:
            await q.edit_message_text(f"❌ موجودی {WEAPON_LABELS.get(wkey,wkey)} کافی نیست!", reply_markup=kb([btn("🔙","transfer_weapons")])); return
        player["military"][wkey] = current - amount
        target["military"][wkey] = target["military"].get(wkey, 0) + amount
    data["players"][uid] = player
    data["players"][target_uid] = target
    save_data(data)
    # نام واقعی سلاح از دید فرستنده
    basket_str_sender = "\n".join([f"  {WEAPON_LABELS.get(k,k)} ({get_weapon_real_name(player,k)}): {v}" for k,v in basket.items()])
    # نام واقعی سلاح از دید گیرنده
    basket_str_recv = "\n".join([f"  {WEAPON_LABELS.get(k,k)} ({get_weapon_real_name(target,k)}): {v}" for k,v in basket.items()])
    context.user_data.pop("transfer_weapons_basket", None)
    await q.edit_message_text(
        f"✅ *انتقال تسلیحات ارسال شد!*\nبه: {target['country']}\n⏱ زمان تحویل: ۵ دقیقه\n\n{basket_str_sender}",
        parse_mode="Markdown",
        reply_markup=kb([btn("🏠 منو اصلی","resume")])
    )
    import asyncio
    async def deliver_weapons():
        await asyncio.sleep(300)  # 5 دقیقه
        try:
            await context.bot.send_message(target_uid,
                f"⚔️ *تسلیحات دریافت کردید!*\nاز: {player['country']}\n\n{basket_str_recv}",
                parse_mode="Markdown")
        except: pass
    asyncio.create_task(deliver_weapons())

# ──────────────────────────────────────────────
#  حمله
# ──────────────────────────────────────────────
async def attack_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    active = [(cid, p["country"]) for cid, p in data["players"].items() if cid != uid]
    if not active:
        await q.edit_message_text("⚠️ دشمنی نیست!", reply_markup=kb([BACK])); return
    rows = [[btn(cname, f"atk{cid}")] for cid, cname in active]
    rows.append([BACK])
    await q.edit_message_text("⚔️ *حمله – کشور هدف را انتخاب کنید:*", parse_mode="Markdown", reply_markup=kb(*rows))

def get_weapon_real_name(player, wkey):
    """نام واقعی سلاح بر اساس کشور بازیکن"""
    cname = player.get("country","")
    c = COUNTRIES.get(cname, {})
    w = c.get("weapons", {})
    mapping = {
        "soldiers":           w.get("rifle", "سرباز"),
        "tanks":              w.get("tank", "تانک"),
        "fighters":           w.get("fighter", "جنگنده"),
        "bombers":            w.get("bomber", "بمب‌افکن"),
        "helicopters":        "🚁 هلیکوپتر",
        "warships":           "🚢 کشتی جنگی",
        "aircraft_carriers":  "🛳️ ناو هواپیمابر",
        "submarines":         "🤿 زیردریایی",
        "missiles_cruise":    w.get("missile_cruise", "موشک کروز"),
        "missiles_ballistic": w.get("missile_ballistic", "موشک بالستیک"),
        "missiles_bunker":    w.get("missile_special", "موشک ویژه"),
        "drones_attack":      w.get("drone_attack", "پهپاد تخریبی"),
        "drones_recon":       w.get("drone_recon", "پهپاد شناسایی"),
        "drones_ewarf":       "پهپاد الکترونیک",
        "drones_mother":      w.get("drone_special", "پهپاد ویژه"),
        "air_defense":        w.get("air_defense", "پدافند"),
    }
    return mapping.get(wkey, wkey)

def get_weapon_step(wkey):
    """تعداد واحد اضافه‌شده با هر کلیک - موشک/پهپاد=۱۰تا، بقیه=۱تا"""
    # موشک و پهپاد ۱۰تا ۱۰تا انتخاب می‌شن، بقیه دونه‌دونه
    bulk = ["missiles_cruise","missiles_ballistic","missiles_bunker","drones_attack","drones_recon","drones_ewarf","drones_mother"]
    thousand = ["soldiers","rifles"]
    if wkey in bulk: return 10
    if wkey in thousand: return 1000
    return 1

async def show_attack_weapons(q, context, uid):
    data = load_data()
    player = get_player(data, uid)
    m = player["military"]
    target = context.user_data.get("attack_target", "؟")
    sel = context.user_data.get("attack_weapons", {})
    ATTACK_EXCLUDED = {"air_defense"}
    rows = []
    for wkey, label in WEAPON_LABELS.items():
        if wkey in ATTACK_EXCLUDED:
            continue
        avail = m.get(wkey, 0)
        if avail > 0:
            s = sel.get(wkey, 0)
            real_name = get_weapon_real_name(player, wkey)
            step = get_weapon_step(wkey)
            step_txt = f"+{step}" if step > 1 else "+۱"
            mark = f" ✅{s}" if s else ""
            rows.append([btn(f"{label} | {real_name} ({avail:,}){mark} [{step_txt}]", f"aw{wkey}")])
    if not rows:
        rows.append([btn("⚠️ تسلیحاتی ندارید!","attack_menu")])
    # نمایش انتخابی‌ها با نام واقعی
    sel_lines = []
    for k, v in sel.items():
        real = get_weapon_real_name(player, k)
        sel_lines.append(f"  {WEAPON_LABELS.get(k,k)} ({real}): {v}")
    sel_text = "\n".join(sel_lines) if sel_lines else "هیچ"
    rows.append([btn("✅ ارسال درخواست جنگ","submitatk"), btn("🔙 بازگشت","attack_menu")])
    await q.edit_message_text(
        f"⚔️ حمله به *{target}*\n\n"
        f"🪖 *تسلیحات انتخابی:*\n{sel_text}\n\n"
        f"💡 موشک/پهپاد = +۱۰ واحد | بقیه سلاح‌ها = +۱ واحد",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def attack_select_country(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("atk","",1)
    data = load_data()
    target_player = data["players"].get(target_uid)
    if not target_player:
        await q.answer("کشور یافت نشد!", show_alert=True); return
    context.user_data["attack_target"] = target_player["country"]
    context.user_data["attack_target_uid"] = target_uid
    context.user_data["attack_weapons"] = {}
    uid = str(q.from_user.id)
    await show_attack_weapons(q, context, uid)

async def attack_weapon_add(update, context):
    q = update.callback_query
    await q.answer()
    wkey = q.data.replace("aw","",1)
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    m = player["military"]
    sel = context.user_data.get("attack_weapons", {})
    avail = m.get(wkey, 0)
    current_sel = sel.get(wkey, 0)
    step = get_weapon_step(wkey)
    add = min(step, avail - current_sel)
    if add <= 0:
        await q.answer("موجودی کافی نیست!", show_alert=True); return
    sel[wkey] = current_sel + add
    context.user_data["attack_weapons"] = sel
    await show_attack_weapons(q, context, uid)

async def submit_attack(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    target = context.user_data.get("attack_target")
    target_uid = context.user_data.get("attack_target_uid", "")
    weapons = context.user_data.get("attack_weapons", {})
    if not player:
        await q.edit_message_text("❌ خطا!", reply_markup=kb([BACK])); return
    if not weapons:
        await q.edit_message_text("⚠️ هیچ تسلیحاتی انتخاب نکردید!\nبرگردید و سلاح انتخاب کنید.", reply_markup=kb([btn("🔙 بازگشت","attack_menu")])); return
    if not target:
        await q.edit_message_text("⚠️ هدف مشخص نیست!\nدوباره حمله را شروع کنید.", reply_markup=kb([btn("⚔️ حمله","attack_menu")])); return

    # چک پیمان صلح
    peace_treaties = data.get("peace_treaties", {})
    key1 = f"{uid}_{target_uid}"
    key2 = f"{target_uid}_{uid}"
    if key1 in peace_treaties or key2 in peace_treaties:
        await q.edit_message_text(
            f"🕊️ *پیمان صلح فعال است!*\n\n"
            f"شما با *{target}* پیمان صلح دارید و نمی‌توانید به آن اعلان جنگ کنید.\n"
            f"ابتدا باید پیمان را لغو کنید.",
            parse_mode="Markdown",
            reply_markup=kb([btn("🕊️ پیمان صلح", "peace_menu"), btn("🔙 بازگشت", "attack_menu")])
        ); return

    # چک: آیا جنگ فعالی بین این دو طرف وجود دارد؟ (مدافع می‌تونه بدون تأیید جنگ بده)
    active_wars = data.get("active_wars", {})
    war_id_as_defender = f"{target_uid}x{uid}"   # طرف مقابل مهاجم بوده
    war_id_as_attacker = f"{uid}x{target_uid}"   # خودم مهاجم بوده‌ام
    existing_war_id = None
    if war_id_as_defender in active_wars:
        existing_war_id = war_id_as_defender
    elif war_id_as_attacker in active_wars:
        existing_war_id = war_id_as_attacker

    if existing_war_id:
        # جنگ فعال → تجهیزات مستقیم ثبت و به سازمان ملل اطلاع داده میشه
        war_rec = active_wars[existing_war_id]
        is_defender = (existing_war_id == war_id_as_defender)
        role_txt = "مدافع" if is_defender else "مهاجم"
        # کم کردن تجهیزات از موجودی
        for wkey, amount in weapons.items():
            player["military"][wkey] = max(0, player["military"].get(wkey, 0) - amount)
        save_player(data, uid, player)
        # ثبت در رکورد جنگ
        if is_defender:
            for wkey, amount in weapons.items():
                war_rec["defender_weapons"][wkey] = war_rec["defender_weapons"].get(wkey, 0) + amount
        else:
            for wkey, amount in weapons.items():
                war_rec["attacker_weapons"][wkey] = war_rec["attacker_weapons"].get(wkey, 0) + amount
        active_wars[existing_war_id] = war_rec
        data["active_wars"] = active_wars
        save_data(data)
        # نام واقعی سلاح
        w_lines_d = []
        for k, v in weapons.items():
            real = get_weapon_real_name(player, k)
            w_lines_d.append(f"  {WEAPON_LABELS.get(k,k)} ({real}): {v:,}")
        w_text_d = "\n".join(w_lines_d)
        # پیام به سازمان ملل
        notif_msg = (
            f"⚔️ *پرتاب تجهیزات در جنگ*\n\n"
            f"🎯 کشور: *{player['country']}* ({role_txt})\n"
            f"🆚 طرف مقابل: *{target}*\n\n"
            f"🪖 *تجهیزات پرتاب‌شده:*\n{w_text_d}"
        )
        for admin_id in data.get("un_admins", []):
            try: await context.bot.send_message(admin_id, notif_msg, parse_mode="Markdown")
            except: pass
        context.user_data.pop("attack_weapons", None)
        context.user_data.pop("attack_target", None)
        context.user_data.pop("attack_target_uid", None)
        await q.edit_message_text(
            f"✅ *{player['country']}* این تجهیزات را در جنگ پرتاب کرد:\n\n{w_text_d}\n\nسازمان ملل اطلاع‌رسانی شد.",
            parse_mode="Markdown", reply_markup=kb([BACK])
        )
        return

    # نام واقعی سلاح در گزارش
    w_lines = []
    for k, v in weapons.items():
        real = get_weapon_real_name(player, k)
        w_lines.append(f"  {WEAPON_LABELS.get(k,k)} ({real}): {v}")
    w_text = "\n".join(w_lines)
    # تجهیزات رو از موجودی کم کن و در pending_war ذخیره کن
    for wkey, amount in weapons.items():
        player["military"][wkey] = max(0, player["military"].get(wkey, 0) - amount)
    save_player(data, uid, player)
    # ذخیره اطلاعات جنگ در انتظار برای برگشت در صورت رد
    data.setdefault("pending_wars", {})[uid] = {
        "weapons": weapons,
        "target_uid": target_uid,
        "target": target,
        "attacker_country": player["country"],
    }
    save_data(data)
    m_full = player["military"]
    # کل ارتش با نام واقعی
    full_army = (
        f"  👥 سرباز ({get_weapon_real_name(player,'soldiers')}): {m_full.get('soldiers',0):,}\n"
        f"  ⚙️ تانک ({get_weapon_real_name(player,'tanks')}): {m_full.get('tanks',0):,}\n"
        f"  ✈️ جنگنده ({get_weapon_real_name(player,'fighters')}): {m_full.get('fighters',0):,}\n"
        f"  💣 بمب‌افکن ({get_weapon_real_name(player,'bombers')}): {m_full.get('bombers',0):,}\n"
        f"  🚀 موشک کروز ({get_weapon_real_name(player,'missiles_cruise')}): {m_full.get('missiles_cruise',0):,}\n"
        f"  ☠️ موشک بالستیک ({get_weapon_real_name(player,'missiles_ballistic')}): {m_full.get('missiles_ballistic',0):,}\n"
        f"  💥 موشک ویژه ({get_weapon_real_name(player,'missiles_bunker')}): {m_full.get('missiles_bunker',0):,}\n"
        f"  🤖 پهپاد تخریبی ({get_weapon_real_name(player,'drones_attack')}): {m_full.get('drones_attack',0):,}\n"
        f"  📡 پهپاد شناسایی ({get_weapon_real_name(player,'drones_recon')}): {m_full.get('drones_recon',0):,}\n"
        f"  📻 پهپاد الکترونیک: {m_full.get('drones_ewarf',0):,}\n"
        f"  💀 پهپاد ویژه ({get_weapon_real_name(player,'drones_mother')}): {m_full.get('drones_mother',0):,}\n"
        f"  🛡️ پدافند ({get_weapon_real_name(player,'air_defense')}): {m_full.get('air_defense',0):,}"
    )
    msg = (
        f"🚨 *درخواست جنگ*\n\n"
        f"⚔️ مهاجم: {player['country']}\n"
        f"🎯 هدف: {target}\n\n"
        f"🪖 *تجهیزات مورد استفاده در حمله:*\n{w_text}\n\n"
        f"📊 *کل ارتش مهاجم:*\n{full_army}"
    )
    un_admins = data.get("un_admins", [])
    sent = 0
    un_msg_ids = []
    for admin_id in un_admins:
        try:
            sent_msg = await context.bot.send_message(
                admin_id, msg, parse_mode="Markdown",
                reply_markup=kb(
                    [btn("✅ تأیید جنگ", f"aprwar{uid}x{target_uid}"),
                     btn("❌ رد", f"rejwar{uid}")]
                )
            )
            un_msg_ids.append({"chat_id": admin_id, "message_id": sent_msg.message_id})
            sent += 1
        except Exception as e:
            logger.error(f"Failed to notify UN: {e}")
    # ذخیره ID پیام‌های سازمان ملل برای لغو احتمالی
    data["pending_wars"][uid]["un_msg_ids"] = un_msg_ids
    save_data(data)
    context.user_data.pop("attack_weapons", None)
    context.user_data.pop("attack_target", None)
    context.user_data.pop("attack_target_uid", None)
    if sent == 0:
        await q.edit_message_text(
            "⚠️ *سازمان ملل آنلاین نیست!*\nمنتظر حضور بازیگردان باشید.",
            parse_mode="Markdown", reply_markup=kb([BACK])
        )
    else:
        await q.edit_message_text(
            f"📨 *درخواست جنگ ارسال شد!*\n⚔️ {player['country']} ← {target}\nمنتظر تأیید سازمان ملل باشید.",
            parse_mode="Markdown", reply_markup=kb([BACK])
        )

# ──────────────────────────────────────────────
#  هسته‌ای
# ──────────────────────────────────────────────
async def launch_nuclear(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!", show_alert=True); return
    b = player["buildings"]
    if not b.get("nuclear_plant"):
        await q.edit_message_text("❌ نیروگاه هسته‌ای ندارید!", reply_markup=kb([BACK])); return
    if b.get("nuclear_active"):
        await q.edit_message_text("✅ نیروگاه هم‌اکنون فعال است!", reply_markup=kb([BACK])); return
    if not b.get("nuclear_approved"):
        await q.edit_message_text("⏳ نیروگاه هنوز تأیید سازمان ملل را دریافت نکرده!\nمنتظر تأیید باشید.", reply_markup=kb([BACK])); return
    if not b.get("uranium_mine"):
        uranium_owners = [p["country"] for p in data["players"].values() if p["buildings"].get("uranium_mine")]
        note = "\n".join(f"• {c}" for c in uranium_owners) if uranium_owners else "هیچ کشوری معدن اورانیوم نساخته"
        await q.edit_message_text(
            f"☢️ برای فعال‌سازی به معدن اورانیوم نیاز دارید.\n\nکشورهای دارای اورانیوم:\n{note}",
            reply_markup=kb([BACK])
        ); return
    player["buildings"]["nuclear_active"] = True
    save_player(data, uid, player)
    await q.edit_message_text("✅ *نیروگاه هسته‌ای فعال شد!*\n☢️ اکنون می‌توانید بمب اتم بسازید.", parse_mode="Markdown", reply_markup=kb([BACK]))

async def build_nuke(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!", show_alert=True); return
    b = player["buildings"]
    if not b.get("nuclear_plant") or not b.get("nuclear_active"):
        await q.edit_message_text("❌ نیروگاه هسته‌ای فعال ندارید!", reply_markup=kb([BACK])); return
    if player.get("nuclear_bomb"):
        await q.edit_message_text("✅ بمب اتم دارید!", reply_markup=kb([BACK])); return
    await q.edit_message_text(
        "☢️ *ساخت بمب اتم*\n\n⚠️ با ساخت بمب اتم:\n• تحریم می‌شوید\n• انتقال و معامله قطع می‌شود\n• سازمان ملل مطلع می‌شود\n\nمطمئن هستید؟",
        parse_mode="Markdown",
        reply_markup=kb([btn("✅ بله، بسازید!","confirm_nuke"), btn("❌ خیر","back_main")])
    )

async def confirm_nuke(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    player["nuclear_bomb"] = True
    player["banned"] = True
    save_player(data, uid, player)
    msg = f"☢️ *هشدار هسته‌ای!*\n{player['country']} بمب اتم ساخته و تحریم شده!"
    for admin_id in data.get("un_admins", []):
        try:
            await context.bot.send_message(admin_id, msg, parse_mode="Markdown")
        except: pass
    await q.edit_message_text("☢️ *بمب اتم ساخته شد!*\n⛔ شما تحریم شده‌اید.", parse_mode="Markdown", reply_markup=kb([BACK]))

# ──────────────────────────────────────────────
#  حمله سایبری
# ──────────────────────────────────────────────
async def cyber_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("ابتدا بازی کنید!", show_alert=True); return
    hack_list = player["buildings"].get("hack_rooms", [])
    if not hack_list and player["buildings"].get("hack_room", 0):
        hack_list = ["normal"] * player["buildings"]["hack_room"]
    hack_level = len(hack_list)
    if not hack_level:
        await q.edit_message_text("❌ *اتاق هک ندارید!*\nاز بخش نظامی اتاق هک بخرید.", parse_mode="Markdown", reply_markup=kb([btn("🪖 نظامی","mil_menu"), BACK])); return
    luxury_c = hack_list.count("luxury")
    normal_c = hack_list.count("normal")
    level_text = f"💻 {normal_c} معمولی + 💎 {luxury_c} لوکس" if luxury_c and normal_c else ("💎 همه لوکس" if luxury_c else "💻 همه معمولی")
    # تعداد هک باقیمانده امروز
    today_str = datetime.now().strftime("%Y-%m-%d")
    if player.get("hack_date") != today_str:
        hacks_used = 0
    else:
        hacks_used = player.get("hack_today", 0)
    hacks_left = max(0, 2 - hacks_used)
    active = [(cid, p["country"]) for cid, p in data["players"].items() if cid != uid]
    if not active:
        await q.edit_message_text("⚠️ کشوری فعال نیست!", reply_markup=kb([BACK])); return
    rows = [[btn(cname, f"cybtgt{cid}")] for cid, cname in active]
    rows.append([BACK])
    hack_status = f"✅ {hacks_left} حمله باقی‌مانده امروز" if hacks_left > 0 else "⛔ سقف روزانه تمام شد (فردا)"
    await q.edit_message_text(
        f"💻 *حمله سایبری* | {level_text}\n{hack_status}\n\n🎯 ابتدا کشور هدف را انتخاب کنید:",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def cyber_target_select(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    target_uid = q.data.replace("cybtgt","",1)
    data = load_data()
    player = get_player(data, uid)
    target = data["players"].get(target_uid)
    if not player or not target:
        await q.answer("خطا!", show_alert=True); return
    attacker_hack_list = player["buildings"].get("hack_rooms", [])
    if not attacker_hack_list and player["buildings"].get("hack_room", 0):
        attacker_hack_list = ["normal"] * player["buildings"]["hack_room"]
    target_hack_list = target["buildings"].get("hack_rooms", [])
    if not target_hack_list and target["buildings"].get("hack_room", 0):
        target_hack_list = ["normal"] * target["buildings"]["hack_room"]
    hack_level = len(attacker_hack_list)
    target_hack = len(target_hack_list)
    context.user_data["cyber_target_uid"] = target_uid

    def calc_rate(akey):
        a = CYBER_ATTACKS[akey]
        a_luxury = attacker_hack_list.count("luxury")
        a_normal = attacker_hack_list.count("normal")
        bonus = min(a_normal * 0.03 + a_luxury * 0.07, 0.25)
        rate = min(0.95, a["normal_success"] + bonus)
        if target_hack_list:
            t_luxury = target_hack_list.count("luxury")
            t_normal = target_hack_list.count("normal")
            reduce = min(t_normal * 0.08 + t_luxury * 0.15, 0.50)
            rate = max(0.05, rate - reduce)
        return int(rate * 100)

    defense_warn = ""
    if target_hack:
        t_lux = target_hack_list.count("luxury")
        t_nor = target_hack_list.count("normal")
        defense_warn = f"\n🛡️ هدف {t_nor} معمولی + {t_lux} لوکس اتاق هک دارد"

    await q.edit_message_text(
        f"💻 *حمله سایبری به {target['country']}*{defense_warn}\n\nنوع حمله را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=kb(
            [btn(f"💸 فلج اقتصادی | شانس: {calc_rate('eco')}%","cybdo_eco")],
            [btn(f"💰 هک دارایی‌ها | شانس: {calc_rate('steal')}%","cybdo_steal")],
            [btn(f"🔇 از کار انداختن تسلیحات | شانس: {calc_rate('dis')}%","cybdo_dis")],
            [btn(f"🕵️ جاسوسی اطلاعات | شانس: {calc_rate('spy')}%","cybdo_spy")],
            [btn("🔙 بازگشت","cyber_menu")]
        )
    )

async def cyber_do_attack(update, context):
    q = update.callback_query
    await q.answer()
    attack_type = q.data.replace("cybdo_","",1)
    attacker_uid = str(q.from_user.id)
    target_uid = context.user_data.get("cyber_target_uid")
    data = load_data()
    attacker = get_player(data, attacker_uid)
    target = data["players"].get(target_uid)
    ainfo = CYBER_ATTACKS.get(attack_type)
    if not attacker or not target or not ainfo:
        await q.answer("خطا!", show_alert=True); return
    hack_list = attacker["buildings"].get("hack_rooms", [])
    # سازگاری با سیستم قدیمی
    if not hack_list and attacker["buildings"].get("hack_room", 0):
        hack_list = ["normal"] * attacker["buildings"]["hack_room"]
    hack_level = len(hack_list)
    if not hack_level:
        await q.edit_message_text("❌ اتاق هک ندارید!", reply_markup=kb([BACK])); return

    # ── FIX: محدودیت ۲ هک در روز
    today_str = datetime.now().strftime("%Y-%m-%d")
    if attacker.get("hack_date") != today_str:
        attacker["hack_date"] = today_str
        attacker["hack_today"] = 0
    if attacker.get("hack_today", 0) >= 2:
        await q.edit_message_text(
            f"⛔ *سقف هک روزانه!*\n\nامروز ۲ حمله سایبری انجام داده‌اید.\nفردا دوباره امتحان کنید.",
            parse_mode="Markdown", reply_markup=kb([BACK])
        ); return
    attacker["hack_today"] = attacker.get("hack_today", 0) + 1
    data["players"][attacker_uid] = attacker
    save_data(data)
    # ── پایان محدودیت هک
    # شانس موفقیت: هر معمولی +3٪، هر لوکس +7٪
    luxury_count = hack_list.count("luxury")
    normal_count = hack_list.count("normal")
    bonus = min(normal_count * 0.03 + luxury_count * 0.07, 0.25)
    base_success = ainfo["normal_success"]
    base_effect = ainfo["normal_effect"]
    success_rate = min(0.95, base_success + bonus)
    effect = min(base_effect + bonus * 0.5, ainfo["luxury_effect"])
    target_hack_list = target["buildings"].get("hack_rooms", [])
    if not target_hack_list and target["buildings"].get("hack_room", 0):
        target_hack_list = ["normal"] * target["buildings"]["hack_room"]
    target_hack = len(target_hack_list)
    defense_note = ""
    if target_hack:
        # هر اتاق معمولی دشمن -8٪، هر لوکس -15٪
        t_luxury = target_hack_list.count("luxury")
        t_normal = target_hack_list.count("normal")
        reduce = min(t_normal * 0.08 + t_luxury * 0.15, 0.50)
        old_rate = success_rate
        success_rate = max(0.05, success_rate - reduce)
        defense_note = f"\n🛡️ دشمن {t_normal} معمولی + {t_luxury} لوکس اتاق هک دارد — شانس از {int(old_rate*100)}% به {int(success_rate*100)}% کاهش یافت"
    success = random.random() < success_rate
    result_text = ""
    notify_target = ""
    if success:
        if attack_type == "eco":
            target.setdefault("cyber_debuffs", {})["economy_reduce"] = {"value": effect, "days": 2}
            result_text = f"✅ *حمله موفق!*\n💸 اقتصاد {target['country']} برای ۲ روز {int(effect*100)}% فلج شد!"
            notify_target = f"⚠️ *هشدار سایبری!*\n💸 درآمد شما برای ۲ روز {int(effect*100)}% کاهش یافت!"
        elif attack_type == "steal":
            stolen = min(int(target["money"] * effect), target["money"])
            target["money"] -= stolen
            attacker["money"] += stolen
            result_text = f"✅ *هک موفق!*\n💰 {fmt(stolen)} از خزانه {target['country']} دزدیده شد!"
            notify_target = f"⚠️ *هشدار سایبری!*\n💰 {fmt(stolen)} از خزانه دزدیده شد!"
        elif attack_type == "dis":
            target.setdefault("cyber_debuffs", {})["weapons_reduce"] = {"value": effect, "days": 1}
            result_text = f"✅ *حمله موفق!*\n🔇 {int(effect*100)}% تسلیحات {target['country']} برای ۱ روز غیرفعال شد!"
            notify_target = f"⚠️ *هشدار سایبری!*\n🔇 {int(effect*100)}% تسلیحات شما برای ۱ روز غیرفعال است!"
        elif attack_type == "spy":
            m = target["military"]
            b = target["buildings"]
            spy_info = (
                f"🕵️ *گزارش اطلاعاتی – {target['country']}*\n\n"
                f"💰 موجودی: {fmt(target['money'])}\n"
                f"⭐ سطح: {LEVELS[target['level']]}\n\n"
                f"🪖 *ارتش:*\n"
                f"  👥 سرباز: {m.get('soldiers',0):,}\n"
                f"  ⚙️ تانک: {m.get('tanks',0):,}\n"
                f"  ✈️ جنگنده: {m.get('fighters',0):,}\n"
                f"  🚀 موشک کروز: {m.get('missiles_cruise',0):,}\n"
                f"  ☠️ موشک بالستیک: {m.get('missiles_ballistic',0):,}\n"
                f"  🤖 پهپاد: {m.get('drones_attack',0):,}\n"
                f"  🛡️ پدافند: {m.get('air_defense',0):,}\n\n"
                f"🏗️ *تأسیسات:*\n"
                f"  💻 اتاق هک: {'دارد' if b.get('hack_room') else 'ندارد'}\n"
                f"  ☢️ نیروگاه: {'فعال' if b.get('nuclear_active') else ('دارد' if b.get('nuclear_plant') else 'ندارد')}\n"
                f"  💣 بمب اتم: {'دارد' if target.get('nuclear_bomb') else 'ندارد'}"
            )
            data["players"][attacker_uid] = attacker
            data["players"][target_uid] = target
            save_data(data)
            context.user_data.pop("cyber_target_uid", None)
            await q.edit_message_text(spy_info, parse_mode="Markdown", reply_markup=kb([btn("💻 حمله دوباره","cyber_menu"), BACK]))
            try:
                await context.bot.send_message(target_uid, "⚠️ *هشدار سایبری!*\n🕵️ یک کشور ناشناس اطلاعات شما را جاسوسی کرد!", parse_mode="Markdown")
            except: pass
            return
    else:
        result_text = f"❌ *حمله ناموفق!*\n🛡️ سیستم‌های دفاعی {target['country']} حمله را دفع کرد!"
        notify_target = f"🛡️ *دفع حمله سایبری!*\nیک کشور ناشناس سعی کرد به شما حمله کند اما ناموفق بود!"
    data["players"][attacker_uid] = attacker
    data["players"][target_uid] = target
    save_data(data)
    context.user_data.pop("cyber_target_uid", None)
    if notify_target:
        try:
            await context.bot.send_message(target_uid, notify_target, parse_mode="Markdown")
        except: pass
    if attack_type != "spy":
        if success:
            un_msg = (
                f"🔔 *گزارش حمله سایبری موفق*\n\n"
                f"⚔️ مهاجم: {attacker['country']}\n"
                f"🎯 هدف: {target['country']}\n"
                f"💻 نوع: {CYBER_ATTACKS[attack_type]['name']}\n"
                f"✅ نتیجه: موفق"
            )
        else:
            un_msg = (
                f"🔔 *گزارش حمله سایبری ناموفق*\n\n"
                f"⚔️ مهاجم: {attacker['country']}\n"
                f"🎯 هدف: {target['country']}\n"
                f"💻 نوع: {CYBER_ATTACKS[attack_type]['name']}\n"
                f"❌ نتیجه: دفع شد"
            )
        for admin_id in data.get("un_admins", []):
            try:
                await context.bot.send_message(admin_id, un_msg, parse_mode="Markdown")
            except: pass
    await q.edit_message_text(
        result_text + defense_note,
        parse_mode="Markdown",
        reply_markup=kb([btn("💻 حمله دوباره","cyber_menu"), BACK])
    )

# ──────────────────────────────────────────────
#  معامله
# ──────────────────────────────────────────────
async def trade_menu(update, context):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "🤝 *معامله:*\nفروش تسلیحات به کشورهای دیگر", parse_mode="Markdown",
        reply_markup=kb([btn("💰 فروش","trade_sell"), BACK])
    )

async def trade_sell(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    if player.get("banned"):
        await q.edit_message_text("⛔ شما تحریم هستید و نمی‌توانید معامله کنید!", reply_markup=kb([BACK])); return
    m = player["military"]
    rows = []
    for wkey, label in WEAPON_LABELS.items():
        if m.get(wkey, 0) > 0:
            rows.append([btn(f"{label}: {m[wkey]:,}", f"tradewep_{wkey}")])
    if not rows:
        await q.edit_message_text("⚠️ تسلیحاتی ندارید!", reply_markup=kb([BACK])); return
    context.user_data["trade_basket"] = {}
    rows.append([btn("✅ ارسال پیشنهاد","trade_send"), btn("🔙","trade_menu")])
    context.user_data["trade_step"] = "select_weapon"
    await q.edit_message_text("⚔️ *تسلیحات برای فروش:*\nانتخاب کنید (هر بار ۱۰ واحد اضافه می‌شود)", parse_mode="Markdown", reply_markup=kb(*rows))

async def trade_add_item(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    wkey = q.data.replace("tradewep_","",1)
    data = load_data()
    player = get_player(data, uid)
    m = player["military"]
    basket = context.user_data.get("trade_basket", {})
    avail = m.get(wkey, 0)
    current = basket.get(wkey, 0)
    step = get_weapon_step(wkey)
    add = min(step, avail - current)
    if add <= 0:
        await q.answer("موجودی کافی نیست!", show_alert=True); return
    basket[wkey] = current + add
    context.user_data["trade_basket"] = basket
    basket_text = "\n".join([f"{WEAPON_LABELS.get(k,k)}: {v}" for k,v in basket.items()])
    rows = []
    for wk, label in WEAPON_LABELS.items():
        if m.get(wk, 0) > 0:
            s = basket.get(wk, 0)
            step_wk = get_weapon_step(wk)
            step_txt = f"+{step_wk}" if step_wk > 1 else "+۱"
            mark = f" ✅{s}" if s else ""
            rows.append([btn(f"{label} ({m[wk]:,}){mark} [{step_txt}]", f"tradewep_{wk}")])
    rows.append([btn("✅ ارسال پیشنهاد","trade_send"), btn("🔙","trade_menu")])
    await q.edit_message_text(
        f"🛒 *سبد معامله:*\n{basket_text if basket_text else 'خالی'}\n\n💡 موشک/پهپاد = +۱۰ | بقیه = +۱\nتسلیحات بیشتر اضافه کنید یا پیشنهاد بدهید:",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )

async def trade_select_target(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    basket = context.user_data.get("trade_basket", {})
    if not basket:
        await q.edit_message_text("⚠️ سبد خالی است!", reply_markup=kb([btn("🔙","trade_sell")])); return
    active = [(cid, p["country"]) for cid, p in data["players"].items() if cid != uid]
    if not active:
        await q.edit_message_text("⚠️ کشوری فعال نیست!", reply_markup=kb([BACK])); return
    rows = [[btn(cname, f"tradeto_{cid}")] for cid, cname in active]
    rows.append([btn("🔙","trade_sell")])
    await q.edit_message_text("🎯 *مقصد معامله:*", parse_mode="Markdown", reply_markup=kb(*rows))

async def trade_to_country(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("tradeto_","",1)
    context.user_data["trade_target_uid"] = target_uid
    context.user_data["awaiting"] = "trade_price"
    data = load_data()
    target = data["players"].get(target_uid)
    if not target:
        await q.answer("خطا!"); return
    await q.edit_message_text(
        f"💰 قیمت برای {target['country']} (میلیون دلار):\nتایپ کنید:",
        reply_markup=kb([btn("🔙","trade_sell")])
    )

# ──────────────────────────────────────────────
#  سازمان ملل (UN)
# ──────────────────────────────────────────────
async def un_menu(update, context):
    data = load_data()
    players_count = len(data["players"])
    text = (
        f"🇺🇳 *سازمان ملل متحد*\n\n"
        f"👥 تعداد بازیکنان: {players_count}\n"
        f"🌍 کشورهای فعال: {', '.join([p['country'] for p in data['players'].values()][:5])}{'...' if players_count>5 else ''}"
    )
    rows = [
        [btn("👥 مشاهده بازیکنان","un_players"), btn("🌍 همه کشورها","un_all")],
        [btn("⚔️ مدیریت درخواست‌های جنگ","un_wars")],
        [btn("💰 اهدای پول به کشورها","un_gift_menu")],
    ]
    # FIX: بررسی callback_query برای جلوگیری از خطا
    if update.callback_query:
        try:
            await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb(*rows))
        except Exception as e:
            logger.error(f"un_menu edit error: {e}")
            await update.callback_query.message.reply_text(text, parse_mode="Markdown", reply_markup=kb(*rows))
    else:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb(*rows))

async def un_players(update, context):
    q = update.callback_query
    await q.answer()
    data = load_data()
    if not data["players"]:
        await q.edit_message_text("⚠️ هیچ بازیکنی نیست!", reply_markup=kb([btn("🔙","un_menu_back")])); return
    rows = [[btn(f"{p['country']}", f"unview_{uid}")] for uid, p in data["players"].items()]
    rows.append([btn("🔙 سازمان ملل","un_menu_back")])
    await q.edit_message_text("👥 *انتخاب بازیکن:*", parse_mode="Markdown", reply_markup=kb(*rows))

async def un_gift_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    if uid not in data.get("un_admins", []):
        await q.answer("❌ فقط سازمان ملل!", show_alert=True); return
    context.user_data["awaiting"] = "gift_amount"
    await q.edit_message_text(
        "💰 *اهدای پول به کشورها*\n\nمقدار پول را به میلیون دلار وارد کنید:\n_(مثلاً ۷۰۰ = هفتصد میلیون دلار)_",
        parse_mode="Markdown",
        reply_markup=kb([btn("❌ لغو","un_menu_back")])
    )

async def un_wars(update, context):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "⚔️ *درخواست‌های جنگ*\n\nدرخواست‌های جنگ از طریق پیام مستقیم ارسال می‌شوند.\nبرای تأیید یا رد از دکمه‌های پیام استفاده کنید.",
        parse_mode="Markdown",
        reply_markup=kb([btn("🔙 سازمان ملل","un_menu_back")])
    )

async def un_all_countries(update, context):
    q = update.callback_query
    await q.answer()
    data = load_data()
    if not data["players"]:
        await q.edit_message_text("⚠️ هیچ بازیکنی نیست!", reply_markup=kb([btn("🔙","un_menu_back")])); return
    text = "🌍 *لیست همه کشورها*\n\n"
    for uid, p in data["players"].items():
        flag = COUNTRIES[p["country"]]["flag"]
        text += (
            f"{flag} *{p['country']}*\n"
            f"  💰 {fmt(p['money'])} | ⭐ {LEVELS[p['level']]}\n"
            f"  {'⛔ تحریم' if p.get('banned') else '✅ فعال'}"
            f"{'  ☢️ بمب اتم' if p.get('nuclear_bomb') else ''}\n\n"
        )
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb([btn("🔙","un_menu_back")]))

async def un_view_player(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("unview_","",1)
    data = load_data()
    p = data["players"].get(target_uid)
    if not p:
        try: await q.edit_message_text("⚠️ بازیکن یافت نشد!", reply_markup=kb([btn("🔙","un_players")]))
        except: await q.message.reply_text("⚠️ بازیکن یافت نشد!", reply_markup=kb([btn("🔙","un_players")]))
        return
    b = p["buildings"]; m = p["military"]; cname = p["country"]

    # ── متن کوتاه: فقط خلاصه وضعیت (بدون نام سلاح طولانی)
    status = "⛔ تحریم" if p.get("banned") else "✅ فعال"
    nuke_txt = " ☢️بمب" if p.get("nuclear_bomb") else ""
    hack_txt = f" 💻هک:{p.get('hack_today',0)}/2" if b.get("hack_room") else ""
    nuke_plant = ""
    if b.get("nuclear_plant"):
        nuke_plant = " | ☢️نیروگاه:✅" if b.get("nuclear_active") else " | ☢️نیروگاه:⏳"

    # شمارش ساختمان‌ها
    eco_count = sum(1 for k in ["central_bank","bitcoin_miner","money_printer","gas_field","oil_field",
        "power_plant","entertainment","gold_mine","copper_mine","silver_mine","uranium_mine",
        "oil_gas_refinery","coal_plant","medical","police","fire"] if b.get(k,0)>0)
    mil_build_count = sum(1 for k in ["bullet_factory","military_base","tank_factory","missile_factory",
        "air_factory","hack_room","defense_factory","nuclear_plant","research_lab","war_room","satellite"] if b.get(k))

    satisfaction = p.get("satisfaction", 50)
    sat_emoji = "😊" if satisfaction >= 70 else ("😐" if satisfaction >= 40 else "😢")
    text = (
        f"👤 *{cname}*\n"
        f"{status}{nuke_txt}{hack_txt}{nuke_plant}\n"
        f"💰 {fmt(p['money'])} | ⭐ {LEVELS[p['level']]}\n"
        f"{sat_emoji} رضایت مردم: {satisfaction}%\n"
        f"🏗️ ساختمان اقتصادی: {eco_count} | 🪖 نظامی: {mil_build_count}\n\n"
        f"⚔️ *ارتش:*\n"
        f"  👥{m.get('soldiers',0):,} سرباز\n"
        f"  ⚙️{m.get('tanks',0):,} تانک | ✈️{m.get('fighters',0):,} جنگنده | 💣{m.get('bombers',0):,} بمب‌افکن\n"
        f"  🚀{m.get('missiles_cruise',0):,} کروز | ☠️{m.get('missiles_ballistic',0):,} بالستیک | 💥{m.get('missiles_bunker',0):,} سنگرشکن\n"
        f"  🤖{m.get('drones_attack',0):,} پهپاد | 📡{m.get('drones_recon',0):,} شناسایی | 📻{m.get('drones_ewarf',0):,} الکترونیک | 💀{m.get('drones_mother',0):,} مادر\n"
        f"  🛡️{m.get('air_defense',0):,} پدافند"
    )

    rows = [
        [btn("💰 افزودن پول", f"unadd_{target_uid}"), btn("💸 کم کردن پول", f"unsub_{target_uid}")],
        [btn("⚔️ کم کردن تسلیحات", f"unmilsub_{target_uid}"), btn("🏗️ کم کردن ساختمان", f"unecosub_{target_uid}")],
        [btn("⭐ تغییر سطح", f"unlevel_{target_uid}"), btn("☢️ تأیید نیروگاه", f"unnuc_{target_uid}")],
        [btn(f"😊 تغییر رضایت ({satisfaction}%)", f"unsat_{target_uid}")],
        [btn("🗑️ حذف بازیکن", f"undel_{target_uid}")],
        [btn("🔙 بازگشت","un_players")],
    ]
    # همیشه پیام جدید بفرست - هیچوقت edit نکن تا مشکل "باز نمیشه" حل بشه
    await q.message.reply_text(text, parse_mode="Markdown", reply_markup=kb(*rows))

# ── کم کردن ساختمان (اقتصادی + نظامی)
async def un_eco_subtract(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("unecosub_","",1)
    context.user_data["un_target_uid"] = target_uid
    data = load_data()
    p = data["players"].get(target_uid)
    if not p: await q.answer("خطا!"); return
    b = p["buildings"]
    rows = []
    # ساختمان‌های اقتصادی
    for k, binfo in BUILDINGS.items():
        v = b.get(k, 0)
        if v and k != "treasury_deposits":
            rows.append([btn(f"{binfo['name']}: {v}", f"unecotype_{target_uid}_{k}")])
    # ساختمان‌های نظامی
    for k, binfo in MILITARY_BUILDINGS.items():
        v = b.get(k)
        if v:
            label_extra = ""
            if k == "missile_factory" and isinstance(v, str): label_extra = f"({'موشک' if v=='missile' else 'پهپاد'})"
            elif k == "air_factory" and isinstance(v, str): label_extra = f"({'جنگنده' if v=='fighter' else 'بمب‌افکن'})"
            elif k == "hack_room":
                hack_list = b.get("hack_rooms", [])
                if hack_list:
                    n = hack_list.count("normal")
                    lx = hack_list.count("luxury")
                    label_extra = f"({n} معمولی + {lx} لوکس)"
                else:
                    label_extra = f"({v} اتاق)"
            rows.append([btn(f"{binfo['name']} {label_extra}", f"unecotype_{target_uid}_{k}")])
    if not rows:
        await q.message.reply_text("⚠️ ساختمانی برای کم کردن نیست!", reply_markup=kb([btn("🔙",f"unview_{target_uid}")])); return
    rows.append([btn("🔙 بازگشت", f"unview_{target_uid}")])
    await q.message.reply_text(f"🏗️ *کم کردن ساختمان از {p['country']}*\nکدام؟", parse_mode="Markdown", reply_markup=kb(*rows))

async def un_eco_subtract_type(update, context):
    q = update.callback_query
    await q.answer()
    raw = q.data.replace("unecotype_","",1)
    parts = raw.split("_",1)
    target_uid = parts[0]; bkey = parts[1] if len(parts)>1 else ""
    data = load_data(); p = data["players"].get(target_uid)
    if not p: await q.answer("خطا!"); return
    b = p["buildings"]; current = b.get(bkey, 0)
    if not current:
        await q.answer("این ساختمان وجود ندارد!", show_alert=True); return
    # حذف یا کم کردن
    if bkey in ["bullet_factory","military_base"]:
        b[bkey] = max(0, current - 1)
        msg = f"✅ یک واحد {bkey} حذف شد. باقیمانده: {b[bkey]}"
    elif bkey in ["missile_factory","air_factory","hack_room"]:
        b[bkey] = None if bkey != "hack_room" else 0
        b[bkey] = 0
        msg = f"✅ {bkey} حذف شد."
    else:
        new_val = max(0, current - 1)
        b[bkey] = new_val
        msg = f"✅ یک واحد کم شد. باقیمانده: {new_val}"
    data["players"][target_uid] = p; save_data(data)
    try: await context.bot.send_message(target_uid, f"⚠️ سازمان ملل یک واحد از ساختمان‌های شما را حذف کرد!")
    except: pass
    await q.message.reply_text(msg, reply_markup=kb([btn("🔙 بازگشت", f"unecosub_{target_uid}")]))

async def un_mil_subtract(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("unmilsub_","",1)
    context.user_data["un_target_uid"] = target_uid
    data = load_data()
    p = data["players"].get(target_uid)
    if not p:
        await q.answer("خطا!"); return
    m = p["military"]
    cname = p["country"]
    c = COUNTRIES.get(cname, {})
    w = c.get("weapons", {})
    rows = []
    for wkey, label in WEAPON_LABELS.items():
        if m.get(wkey, 0) > 0:
            # نام واقعی سلاح
            real = get_weapon_real_name(p, wkey)
            rows.append([btn(f"{label} ({real}): {m[wkey]:,}", f"unmiltype_{target_uid}_{wkey}")])
    if not rows:
        await q.edit_message_text(f"⚠️ {p['country']} تسلیحاتی ندارد!", reply_markup=kb([btn("🔙",f"unview_{target_uid}")])); return
    rows.append([btn("🔙 بازگشت", f"unview_{target_uid}")])
    await q.edit_message_text(f"⚔️ *کم کردن تسلیحات {p['country']}*\nکدام سلاح؟", parse_mode="Markdown", reply_markup=kb(*rows))

async def un_mil_subtract_type(update, context):
    q = update.callback_query
    await q.answer()
    raw = q.data.replace("unmiltype_","",1)
    parts = raw.split("_",1)
    target_uid = parts[0]
    wkey = parts[1] if len(parts)>1 else ""
    context.user_data["un_target_uid"] = target_uid
    context.user_data["un_mil_wkey"] = wkey
    context.user_data["awaiting"] = "un_milsub_amount"
    data = load_data()
    p = data["players"].get(target_uid)
    label = WEAPON_LABELS.get(wkey, wkey)
    current = p["military"].get(wkey, 0) if p else 0
    cname = p["country"] if p else "؟"
    await q.edit_message_text(
        f"⚔️ *کم کردن {label} از {cname}*\nموجودی فعلی: {current:,}\nتعداد کم کردن را تایپ کنید:",
        parse_mode="Markdown",
        reply_markup=kb([btn("🔙", f"unmilsub_{target_uid}")])
    )

async def un_add_money(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("unadd_","",1)
    context.user_data["un_target_uid"] = target_uid
    context.user_data["awaiting"] = "un_addmoney"
    await q.edit_message_text("💰 مقدار افزودن (میلیون دلار):", reply_markup=kb([btn("🔙","un_players")]))

async def un_remove_money(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("unsub_","",1)
    context.user_data["un_target_uid"] = target_uid
    context.user_data["awaiting"] = "un_removemoney"
    await q.edit_message_text("💸 مقدار کم کردن (میلیون دلار):", reply_markup=kb([btn("🔙","un_players")]))

async def un_level(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("unlevel_","",1)
    context.user_data["un_target_uid"] = target_uid
    await q.edit_message_text(
        "⭐ سطح جدید:", parse_mode="Markdown",
        reply_markup=kb(
            [btn("🟫 مستعمره", f"unsetlvl_colony_{target_uid}"), btn("🟡 عادی", f"unsetlvl_normal_{target_uid}")],
            [btn("🟠 قدرتمند", f"unsetlvl_powerful_{target_uid}"), btn("🔴 ابرقدرت", f"unsetlvl_superpower_{target_uid}")],
            [btn("🔙","un_players")]
        )
    )

async def un_set_level(update, context):
    q = update.callback_query
    await q.answer()
    parts = q.data.replace("unsetlvl_","",1).split("_",1)
    level = parts[0]
    target_uid = parts[1] if len(parts)>1 else ""
    data = load_data()
    p = data["players"].get(target_uid)
    if not p:
        await q.answer("خطا!"); return
    p["level"] = level
    data["players"][target_uid] = p
    save_data(data)
    await q.edit_message_text(f"✅ سطح {p['country']} به {LEVELS[level]} تغییر یافت!", reply_markup=kb([btn("🔙","un_players")]))

async def un_nuclear_approve(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("unnuc_","",1)
    data = load_data()
    p = data["players"].get(target_uid)
    if not p:
        await q.answer("خطا!"); return
    current = p["buildings"].get("nuclear_approved", False)
    p["buildings"]["nuclear_approved"] = not current
    data["players"][target_uid] = p
    save_data(data)
    status = "تأیید شد ✅" if not current else "لغو شد ❌"
    await q.edit_message_text(f"☢️ نیروگاه {p['country']} {status}", reply_markup=kb([btn("🔙","un_players")]))
    try:
        msg = "✅ نیروگاه هسته‌ای شما تأیید شد!" if not current else "❌ تأیید نیروگاه هسته‌ای شما لغو شد!"
        await context.bot.send_message(target_uid, msg)
    except: pass

async def un_set_satisfaction(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("unsat_","",1)
    context.user_data["un_target_uid"] = target_uid
    context.user_data["awaiting"] = "un_set_satisfaction"
    data = load_data()
    p = data["players"].get(target_uid)
    if not p:
        await q.answer("خطا!"); return
    current_sat = p.get("satisfaction", 50)
    await q.message.reply_text(
        f"😊 *تغییر رضایت مردم {p['country']}*\nرضایت فعلی: {current_sat}%\n\nعدد جدید (۰ تا ۱۰۰) را وارد کنید:",
        parse_mode="Markdown",
        reply_markup=kb([btn("🔙","un_players")])
    )

async def un_delete_player(update, context):
    q = update.callback_query
    await q.answer()
    target_uid = q.data.replace("undel_","",1)
    data = load_data()
    p = data["players"].get(target_uid)
    if not p:
        await q.answer("خطا!"); return
    cname = p["country"]
    del data["players"][target_uid]
    # FIX: پاک کردن از taken_countries وقتی بازیکن حذف میشه
    if cname in data.get("taken_countries", []):
        data["taken_countries"].remove(cname)
    # FIX: پاک کردن از country_map در bot_data
    import hashlib
    ckey = hashlib.md5(cname.encode()).hexdigest()[:8]
    # نگه نداشتن در country_map چون کشور آزاد شده
    save_data(data)
    await q.edit_message_text(f"🗑️ بازیکن {cname} حذف شد!\n✅ کشور آزاد شد و قابل انتخاب مجدد است.", reply_markup=kb([btn("🔙","un_players")]))
    try:
        await context.bot.send_message(target_uid, "⛔ حساب شما در بازی حذف شد!")
    except: pass

async def un_approve_war(update, context):
    q = update.callback_query
    await q.answer()
    raw = q.data.replace("aprwar","",1)
    parts = raw.split("x")
    attacker_uid = parts[0]
    target_uid = parts[1] if len(parts)>1 else ""
    data = load_data()
    attacker = data["players"].get(attacker_uid)
    target = data["players"].get(target_uid)
    if not attacker or not target:
        await q.edit_message_text("⚠️ بازیکن یافت نشد!"); return
    # پاک کردن pending_war
    data.get("pending_wars", {}).pop(attacker_uid, None)

    # کاهش ۵۰٪ قیمت سهام کشور مهاجم و مدافع
    attacker_country = attacker["country"]
    target_country = target["country"]
    stocks = data.get("stocks", {})
    for war_country in [attacker_country, target_country]:
        if war_country in stocks:
            s = stocks[war_country]
            s["gain_pct"] = s.get("gain_pct", 0.0) - 50.0
            s["price"] = int(STOCK_BASE_PRICE * (1 + s["gain_pct"] / 100))
            if s["price"] < 1:
                s["price"] = 1
            stocks[war_country] = s
    data["stocks"] = stocks

    # لیست تسلیحات از pending_war (قبل از پاک کردن)
    pending_war_data = data.get("pending_wars", {}).get(attacker_uid, {})
    weapons_used = pending_war_data.get("weapons", {})
    w_lines = []
    for k, v in weapons_used.items():
        real = get_weapon_real_name(attacker, k)
        w_lines.append(f"  {WEAPON_LABELS.get(k,k)} ({real}): {v:,}")
    w_text = "\n".join(w_lines) if w_lines else "  (اطلاعات موجود نیست)"

    # ثبت جنگ فعال
    war_id = f"{attacker_uid}x{target_uid}"
    data.setdefault("active_wars", {})[war_id] = {
        "attacker_uid": attacker_uid,
        "target_uid": target_uid,
        "attacker_country": attacker_country,
        "target_country": target_country,
        "date": datetime.now().isoformat(),
        "attacker_weapons": weapons_used,
        "defender_weapons": {},
        "ceasefire_votes": {},   # uid: True
    }
    # تاریخچه جنگ‌ها
    data.setdefault("war_history", []).append({
        "war_id": war_id,
        "attacker": attacker_country,
        "defender": target_country,
        "date": datetime.now().strftime("%Y/%m/%d"),
        "result": "نامشخص",
        "winner": None,
    })

    save_data(data)
    await q.edit_message_text(
        f"✅ *جنگ تأیید شد!*\n\n"
        f"⚔️ مهاجم: *{attacker['country']}*\n"
        f"🎯 مدافع: *{target['country']}*\n\n"
        f"🪖 *تسلیحات استفاده‌شده در حمله:*\n{w_text}\n\n"
        f"دارایی‌های طرفین را از پنل مدیریت کنید.",
        parse_mode="Markdown",
        reply_markup=kb([btn("🇺🇳 سازمان ملل","un_menu_back")])
    )
    for nuid, role in [(attacker_uid, "مهاجم"), (target_uid, "مدافع")]:
        try:
            await context.bot.send_message(
                nuid,
                f"🚨 *اعلام جنگ!*\n⚔️ *{attacker['country']}* به *{target['country']}* حمله کرد!\n\n"
                f"📌 شما در این جنگ *{role}* هستید.\n"
                f"💡 می‌توانید از منوی حمله تجهیزات بفرستید — دیگر نیاز به تأیید سازمان ملل نیست!\n\n"
                f"🏳️ برای پیشنهاد آتش‌بس از دکمه زیر استفاده کنید:",
                parse_mode="Markdown",
                reply_markup=kb([btn("🏳️ پیشنهاد آتش‌بس", f"ceasefire_req_{war_id}")])
            )
        except: pass

async def un_reject_war(update, context):
    q = update.callback_query
    await q.answer()
    attacker_uid = q.data.replace("rejwar","",1)
    data = load_data()
    # برگشت تجهیزات به مهاجم
    pending = data.get("pending_wars", {}).pop(attacker_uid, None)
    attacker = data["players"].get(attacker_uid)
    returned_text = ""
    if pending and attacker:
        for wkey, amount in pending.get("weapons", {}).items():
            attacker["military"][wkey] = attacker["military"].get(wkey, 0) + amount
        data["players"][attacker_uid] = attacker
        returned_lines = [f"  {WEAPON_LABELS.get(k,k)}: {v:,}" for k, v in pending["weapons"].items()]
        returned_text = "\n🔄 *تجهیزات برگردانده شد:*\n" + "\n".join(returned_lines)
    save_data(data)
    await q.edit_message_text(
        f"❌ درخواست جنگ رد شد.{returned_text}",
        parse_mode="Markdown",
        reply_markup=kb([btn("🇺🇳 سازمان ملل","un_menu_back")])
    )
    try:
        await context.bot.send_message(
            attacker_uid,
            f"❌ *درخواست جنگ رد شد!*\nسازمان ملل درخواست جنگ شما را رد کرد.{returned_text}\nتجهیزات به ارتش شما بازگشت.",
            parse_mode="Markdown"
        )
    except: pass

async def show_country_info(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    cname = player["country"]
    c = COUNTRIES[cname]
    w = c["weapons"]
    text = (
        f"{c['flag']} *{cname}*\n"
        f"👤 رهبر: {c['leader']}\n"
        f"🏳️ گروه: {c['group']}\n"
        f"⭐ سطح: {LEVELS[c['level']]}\n"
        f"🌏 منابع: {', '.join(c['resources']) if c['resources'] else 'ندارد'}\n\n"
        f"🔫 تفنگ: {w['rifle']}\n"
        f"⚙️ تانک: {w['tank']}\n"
        f"✈️ جنگنده: {w['fighter']}\n"
        f"💣 بمب‌افکن: {w['bomber']}\n"
        f"🚀 موشک کروز: {w['missile_cruise']}\n"
        f"☠️ موشک بالستیک: {w['missile_ballistic']}\n"
        f"🤖 پهپاد حمله: {w['drone_attack']}\n"
        f"📡 پهپاد شناسایی: {w['drone_recon']}\n"
        f"🛡️ پدافند: {w['air_defense']}"
    )
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb([BACK]))

# ──────────────────────────────────────────────
#  درآمد روزانه
# ──────────────────────────────────────────────
async def daily_income(context):
    data = load_data()
    # اگه force_pay_now هست، پرداخت فوری انجام بده و فلگ رو پاک کن
    if data.get("force_pay_now"):
        data["force_pay_now"] = False
        save_data(data)
    # اگه skip فعاله و force نیست، این دوره رو رد کن
    elif data.get("skip_next_salary"):
        data["skip_next_salary"] = False
        save_data(data)
        return
    for uid, player in data["players"].items():
        income = 0
        b = player["buildings"]
        income += b.get("central_bank",0) * 100_000_000
        income += b.get("bitcoin_miner",0) * 300_000_000
        income += b.get("money_printer",0) * 150_000_000
        income += b.get("gas_field",0) * 10_000_000
        income += b.get("oil_field",0) * 10_000_000
        income += b.get("power_plant",0) * 10_000_000
        income += b.get("entertainment",0) * 50_000_000
        income += b.get("gold_mine",0) * 200_000_000
        income += b.get("copper_mine",0) * 40_000_000
        income += b.get("silver_mine",0) * 100_000_000
        income += b.get("uranium_mine",0) * 150_000_000
        income += b.get("oil_gas_refinery",0) * 200_000_000
        # درآمد کارخانه‌های غذایی
        for food_lvl in player.get("food_factories", []):
            finfo = FOOD_FACTORY_LEVELS.get(food_lvl, {})
            income += finfo.get("income", 0)
        if "treasury_deposits" not in b:
            b["treasury_deposits"] = []
        deposits = b["treasury_deposits"]
        today = datetime.now().date()
        still_pending = []
        treasury_income = 0
        for d in deposits:
            try:
                dep_date = datetime.fromisoformat(d["date"]).date()
                days_passed = (today - dep_date).days
                if days_passed >= 5:
                    treasury_income += d["amount"] * 2
                    player["treasury_sent"] = max(0, player.get("treasury_sent", 0) - d["amount"])
                else:
                    still_pending.append(d)
            except:
                still_pending.append(d)
        b["treasury_deposits"] = still_pending
        income += treasury_income
        debuffs = player.get("cyber_debuffs", {})
        if "economy_reduce" in debuffs:
            d = debuffs["economy_reduce"]
            income = int(income * (1 - d["value"]))
            d["days"] -= 1
            if d["days"] <= 0:
                del debuffs["economy_reduce"]
        if "weapons_reduce" in debuffs:
            d = debuffs["weapons_reduce"]
            d["days"] -= 1
            if d["days"] <= 0:
                del debuffs["weapons_reduce"]
        player["cyber_debuffs"] = debuffs
        m = player["military"]
        m["soldiers"] = m.get("soldiers",0) + 1000 * b.get("military_base",0)
        m["rifles"] = m.get("rifles",0) + 1000 * b.get("bullet_factory",0)
        tank_count = b.get("tank_factory", 0) if isinstance(b.get("tank_factory"), int) else (1 if b.get("tank_factory") else 0)
        if tank_count:
            m["tanks"] = m.get("tanks",0) + 10 * tank_count
        # کارخانه موشک → موشک ویژه (missiles_bunker) | کارخانه پهپاد → پهپاد ویژه (drones_mother)
        missile_val = b.get("missile_factory")
        if isinstance(missile_val, dict):
            m["missiles_bunker"] = m.get("missiles_bunker",0) + 5 * missile_val.get("missile", 0)
            m["drones_mother"] = m.get("drones_mother",0) + 5 * missile_val.get("drone", 0)
        elif isinstance(missile_val, str):
            if missile_val == "missile":
                m["missiles_bunker"] = m.get("missiles_bunker",0) + 5
            elif missile_val == "drone":
                m["drones_mother"] = m.get("drones_mother",0) + 5
        # کارخانه هوایی: جنگنده روزی ۱۰ تا | بمب‌افکن روزی ۲ تا
        air_val = b.get("air_factory")
        if isinstance(air_val, dict):
            m["fighters"] = m.get("fighters",0) + 10 * air_val.get("fighter", 0)
            m["bombers"] = m.get("bombers",0) + 2 * air_val.get("bomber", 0)
        elif isinstance(air_val, str):
            if air_val == "fighter":
                m["fighters"] = m.get("fighters",0) + 10
            elif air_val == "bomber":
                m["bombers"] = m.get("bombers",0) + 2
        defense_count = b.get("defense_factory", 0) if isinstance(b.get("defense_factory"), int) else (1 if b.get("defense_factory") else 0)
        if defense_count:
            m["air_defense"] = m.get("air_defense",0) + 10 * defense_count
        # هلیکوپترسازی
        heli_count = b.get("helicopter_factory", 0)
        if heli_count:
            m["helicopters"] = m.get("helicopters", 0) + 10 * heli_count
        # نیروی دریایی
        naval = b.get("naval_factory")
        if isinstance(naval, dict):
            m["warships"] = m.get("warships", 0) + 10 * naval.get("warship", 0)
            m["aircraft_carriers"] = m.get("aircraft_carriers", 0) + 1 * naval.get("carrier", 0)
            m["submarines"] = m.get("submarines", 0) + 20 * naval.get("submarine", 0)
        elif naval == "warship":
            m["warships"] = m.get("warships", 0) + 10
        elif naval == "carrier":
            m["aircraft_carriers"] = m.get("aircraft_carriers", 0) + 1
        elif naval == "submarine":
            m["submarines"] = m.get("submarines", 0) + 20
        # ریست پروپاگاندا و ماهواره روزانه
        player["propaganda_used_today"] = False
        player["satellite_used_today"] = 0
        # دانشگاه - باز کردن یک قابلیت محدود شده
        if b.get("university"):
            cname = player.get("country","")
            country = COUNTRIES.get(cname, {})
            can_build = country.get("can_build", [])
            RESTRICTED_BUILDINGS = ["air_factory", "defense_factory", "nuclear_plant", "missile_factory"]
            locked = [k for k in RESTRICTED_BUILDINGS if k not in can_build]
            unlocked = player.get("university_unlocked", [])
            still_locked = [k for k in locked if k not in unlocked]
            if still_locked:
                new_unlock = still_locked[0]
                player.setdefault("university_unlocked", []).append(new_unlock)
                bname = MILITARY_BUILDINGS.get(new_unlock, {}).get("name", new_unlock)
                try:
                    await context.bot.send_message(
                        uid,
                        f"🎓 *دانشگاه پیشرفت کرد!*\n✅ قابلیت جدید باز شد: {bname}",
                        parse_mode="Markdown"
                    )
                except: pass
        # بررسی رضایت مردم و تأثیر بر درآمد
        satisfaction = player.get("satisfaction", 50)
        revolution = False
        sat_income_msg = ""
        income_original = income

        if satisfaction >= 100:
            # ۱۰۰% و بالاتر → +۱۰۰% (دو برابر)
            income = int(income * 2.0)
            sat_income_msg = f"🌟 رضایت ۱۰۰%+: درآمد ۲ برابر!"
        elif satisfaction >= 90:
            # ۹۰ تا ۹۹
            income = int(income * 1.6)
            sat_income_msg = f"😍 رضایت ۹۰-۹۹%: درآمد +۶۰%!"
        elif satisfaction >= 80:
            # ۸۰ تا ۸۹
            income = int(income * 1.4)
            sat_income_msg = f"😊 رضایت ۸۰-۸۹%: درآمد +۴۰%!"
        elif satisfaction >= 70:
            # ۷۰ تا ۷۹
            income = int(income * 1.2)
            sat_income_msg = f"🙂 رضایت ۷۰-۷۹%: درآمد +۲۰%!"
        elif satisfaction >= 60:
            # ۶۰ تا ۶۹
            income = int(income * 1.1)
            sat_income_msg = f"😐 رضایت ۶۰-۶۹%: درآمد +۱۰%!"
        elif satisfaction >= 40:
            # ۴۰ تا ۵۹ - بدون تغییر (محدوده عادی)
            pass
        elif satisfaction >= 30:
            # ۳۰ تا ۳۹
            income = int(income * 0.9)
            sat_income_msg = f"😟 رضایت ۳۰-۳۹%: درآمد -۱۰%!"
        elif satisfaction >= 20:
            # ۲۰ تا ۲۹
            income = int(income * 0.8)
            sat_income_msg = f"😢 رضایت ۲۰-۲۹%: درآمد -۲۰%!"
        elif satisfaction >= 10:
            # ۱۰ تا ۱۹
            income = int(income * 0.6)
            sat_income_msg = f"😡 رضایت ۱۰-۱۹%: درآمد -۴۰%!"
        elif satisfaction >= 0:
            # ۰ تا ۹
            income = int(income * 0.5)
            sat_income_msg = f"💀 رضایت ۰-۹%: درآمد -۵۰%!"
        elif satisfaction >= -9:
            # -۹ تا -۱
            income = int(income * 0.4)
            sat_income_msg = f"☠️ رضایت -۱ تا -۹%: درآمد -۶۰%!"
        elif satisfaction >= -19:
            # -۱۹ تا -۱۰
            income = int(income * 0.2)
            sat_income_msg = f"💥 رضایت -۱۰ تا -۱۹%: درآمد -۸۰%!"
            try:
                await context.bot.send_message(
                    uid,
                    f"⚠️ *بحران شدید ملی!*\n😢 رضایت مردم به {satisfaction}% رسیده!\n"
                    f"درآمد ۸۰٪ کاهش یافت!\n⚠️ اگر رضایت به -۲۰ برسد، انقلاب خواهد شد!",
                    parse_mode="Markdown"
                )
            except: pass
        else:
            # satisfaction <= -20 → انقلاب
            revolution = True

        if sat_income_msg and not revolution:
            try:
                await context.bot.send_message(
                    uid,
                    f"📊 *وضعیت رضایت مردم*\n{sat_income_msg}\n"
                    f"رضایت: {satisfaction}% | درآمد پایه: {fmt(income_original)} → {fmt(income)}",
                    parse_mode="Markdown"
                )
            except: pass

        player["money"] += income
        # کسر خودکار قسط وام
        loan = player.get("loan")
        if loan and loan.get("installments_left", 0) > 0:
            installment = loan["installment"]
            deducted = min(installment, player["money"])
            player["money"] -= deducted
            loan["remaining"] = max(0, loan["remaining"] - deducted)
            loan["installments_left"] -= 1
            if loan["installments_left"] <= 0 or loan["remaining"] <= 0:
                player["loan"] = None
                player["loan_cooldown"] = True
                loan_msg = f"✅ قسط وام ({fmt(deducted)}) کسر شد. وام کاملاً تسویه شد! 🎉\n⏳ از حقوق بعدی می‌توانید وام جدید بگیرید."
            else:
                player["loan"] = loan
                loan_msg = f"🏦 قسط وام: {fmt(deducted)} کسر شد | مانده: {fmt(loan['remaining'])} | اقساط باقی: {loan['installments_left']}"
            try:
                await context.bot.send_message(uid, loan_msg)
            except: pass
        # برداشتن cooldown وام در حقوق بعدی
        elif player.get("loan_cooldown"):
            player["loan_cooldown"] = False
        player["military"] = m
        player["buildings"] = b
        data["players"][uid] = player

        # انقلاب - بعد از ذخیره سایر تغییرات
        if revolution:
            cname = player.get("country", "ناشناس")
            del data["players"][uid]
            if cname in data.get("taken_countries", []):
                data["taken_countries"].remove(cname)
            try:
                await context.bot.send_message(
                    uid,
                    f"💥 *انقلاب!*\n\nرضایت مردم {cname} به {satisfaction}% رسید!\n"
                    f"نارضایتی مردم به اوج رسید و انقلابی رخ داد!\n"
                    f"دولت سرنگون شد! حساب شما حذف شد.\n\n"
                    f"می‌توانید دوباره با کشور جدید شروع کنید.",
                    parse_mode="Markdown",
                    reply_markup=kb([btn("🎮 شروع مجدد","choose_group")])
                )
            except: pass
            # پیام انقلاب به همه بازیکنان
            revolution_msg = (
                f"🔴🔴🔴 *اطلاعیه فوری سازمان ملل* 🔴🔴🔴\n\n"
                f"💥 *انقلاب در {cname}!*\n\n"
                f"کشور {cname} دچار نارضایتی شدید مردم شد!\n"
                f"نارضایتی به حد بحرانی ({satisfaction}%) رسید و انقلابی رخ داد.\n"
                f"حکومت سقوط کرد! {cname} از بازی خارج شد.\n\n"
                f"⚠️ سایر کشورها هوشیار باشند!"
            )
            for other_uid in list(data["players"].keys()):
                try:
                    await context.bot.send_message(
                        other_uid,
                        revolution_msg,
                        parse_mode="Markdown"
                    )
                except: pass
            for admin_id in data.get("un_admins", []):
                try:
                    await context.bot.send_message(
                        admin_id,
                        revolution_msg,
                        parse_mode="Markdown"
                    )
                except: pass
            continue
        try:
            await context.bot.send_message(
                uid,
                f"🌙 *پایان روز – شارژ حساب*\n\n💰 درآمد امروز: {fmt(income)}\n💵 موجودی: {fmt(player['money'])}",
                parse_mode="Markdown"
            )
        except: pass
    # بررسی انقضای پیمان‌های صلح (۱ روز)
    now = datetime.now()
    peace_treaties = data.get("peace_treaties", {})
    expired_keys = []
    for key, treaty in peace_treaties.items():
        expires_at = treaty.get("expires_at")
        if expires_at:
            try:
                if now > datetime.fromisoformat(expires_at):
                    expired_keys.append(key)
            except: pass
        else:
            # پیمان‌های قدیمی بدون expires_at → یک روز از تاریخ ثبت
            try:
                date_str = treaty.get("date", "")
                treaty_date = datetime.fromisoformat(date_str)
                if (now - treaty_date).total_seconds() > 86400:
                    expired_keys.append(key)
            except: pass

    for key in expired_keys:
        treaty = peace_treaties.pop(key, {})
        c1 = treaty.get("country1", "؟")
        c2 = treaty.get("country2", "؟")
        uids_pair = key.split("_", 1)
        expire_msg = (
            f"💔 *پیمان صلح منقضی شد!*\n\n"
            f"پیمان صلح میان *{c1}* و *{c2}* به پایان رسید.\n"
            f"⚔️ اکنون اعلان جنگ امکان‌پذیر است."
        )
        for u in uids_pair:
            try:
                await context.bot.send_message(u, expire_msg, parse_mode="Markdown")
            except: pass

    if expired_keys:
        data["peace_treaties"] = peace_treaties

    # نوسان تصادفی روزانه بورس ±۱۰٪
    import random
    stocks = data.get("stocks", {})
    stock_changes = []
    for cname, s in stocks.items():
        fluctuation = random.uniform(-10.0, 10.0)
        s["gain_pct"] = s.get("gain_pct", 0.0) + fluctuation
        s["price"] = int(STOCK_BASE_PRICE * (1 + s["gain_pct"] / 100))
        if s["price"] < 1:
            s["price"] = 1
        arrow = "📈" if fluctuation >= 0 else "📉"
        stock_changes.append(f"  {arrow} {cname[:15]}: {fluctuation:+.1f}%")
    data["stocks"] = stocks

    # ارسال خلاصه نوسان بازار به همه بازیکن‌ها
    if stock_changes:
        market_msg = (
            "📊 *نوسان روزانه بازار بورس*\n\n"
            + "\n".join(stock_changes)
        )
        for uid in list(data.get("players", {}).keys()):
            portfolio = data["players"][uid].get("stock_portfolio", {})
            if any(v > 0 for v in portfolio.values()):
                try:
                    await context.bot.send_message(uid, market_msg, parse_mode="Markdown")
                except: pass

    save_data(data)

# ──────────────────────────────────────────────
#  پردازش پیام متنی
# ──────────────────────────────────────────────
async def handle_message(update, context):
    uid = str(update.effective_user.id)
    data = load_data()
    awaiting = context.user_data.get("awaiting")

    if awaiting == "msg_to_un" and (not update.message.text):
        player = get_player(data, uid)
        cname = player["country"] if player else "ناشناس"
        tg_user = update.effective_user
        uname = f"@{tg_user.username}" if tg_user.username else (tg_user.full_name or "ناشناس")
        caption_prefix = f"📨 پیام از {cname} | {uname}\n\n"
        for admin_id in data.get("un_admins", []):
            try:
                if update.message.photo:
                    await context.bot.send_photo(admin_id, update.message.photo[-1].file_id,
                        caption=caption_prefix + (update.message.caption or ""))
                elif update.message.video:
                    await context.bot.send_video(admin_id, update.message.video.file_id,
                        caption=caption_prefix + (update.message.caption or ""))
                elif update.message.document:
                    await context.bot.send_document(admin_id, update.message.document.file_id,
                        caption=caption_prefix + (update.message.caption or ""))
                elif update.message.voice:
                    await context.bot.send_voice(admin_id, update.message.voice.file_id)
                elif update.message.sticker:
                    await context.bot.send_sticker(admin_id, update.message.sticker.file_id)
            except: pass
        context.user_data.pop("awaiting", None)
        await update.message.reply_text("✅ پیام شما به سازمان ملل ارسال شد!")
        return

    if not update.message.text:
        return
    text = update.message.text.strip()

    # intercept مذاکره فعال - همه پیام‌ها به طرف مقابل میره
    neg = data.get("negotiations", {}).get(uid)
    if neg and not awaiting:
        partner_uid = neg["partner_uid"]
        partner = data["players"].get(partner_uid, {})
        player = get_player(data, uid)
        my_country = player.get("country","?") if player else "?"
        try:
            await context.bot.send_message(
                partner_uid,
                f"💬 *{my_country}:*\n{text}",
                parse_mode="Markdown",
                reply_markup=kb([btn("🔚 پایان مذاکره","negotiation_end")])
            )
            await update.message.reply_text("✅ پیام ارسال شد.", reply_markup=kb([btn("🔚 پایان مذاکره","negotiation_end")]))
        except:
            await update.message.reply_text("❌ خطا در ارسال پیام!")
        return

    if text == UN_CODE:
        un_admins = data.setdefault("un_admins", [])
        is_new = uid not in un_admins
        if uid not in un_admins:
            un_admins.append(uid)
            save_data(data)
        pending_msgs = data.get("pending_un_messages", [])
        if pending_msgs and is_new:
            await update.message.reply_text(f"📬 *{len(pending_msgs)} پیام در انتظار دارید:*", parse_mode="Markdown")
            for pm in pending_msgs:
                try:
                    await context.bot.send_message(
                        uid,
                        f"📨 *پیام از {pm['country']}* | {pm.get('username','')}\n🕐 {pm.get('time','')[:16]}\n\n{pm['text']}",
                        parse_mode="Markdown"
                    )
                except: pass
            data["pending_un_messages"] = []
            save_data(data)
        await un_menu(update, context)
        return

    if text == RESET_CODE:
        if uid in data.get("un_admins", []):
            admins = data.get("un_admins", [])
            save_data({"players": {}, "taken_countries": [], "un_admins": admins, "pending_trades": {}})
            await update.message.reply_text("🔄 بازی ریست شد!", reply_markup=kb([btn("🎮 شروع مجدد","choose_group")]))
        else:
            await update.message.reply_text("❌ شما دسترسی ندارید!")
        return

    if text == LEAVE_CODE:
        existing = get_player(data, uid)
        if existing:
            old_country = existing.get("country", "")
            if old_country in data.get("taken_countries", []):
                data["taken_countries"].remove(old_country)
            data["players"].pop(uid, None)
            if uid in data.get("un_admins", []):
                data["un_admins"].remove(uid)
            wars = data.get("wars", {})
            to_del = [k for k, v in wars.items() if v.get("attacker_uid") == uid or v.get("defender_uid") == uid]
            for k in to_del:
                wars.pop(k, None)
            save_data(data)
            await update.message.reply_text(
                f"🚪 *از کشور {old_country} خارج شدید.*\n\nاکنون می‌توانید کشور جدیدی انتخاب کنید.",
                parse_mode="Markdown",
                reply_markup=kb([btn("🎮 انتخاب کشور جدید", "choose_group")])
            )
        else:
            await update.message.reply_text(
                "⚠️ شما هنوز کشوری انتخاب نکرده‌اید!",
                reply_markup=kb([btn("🎮 شروع بازی", "choose_group")])
            )
        return

    # ──── رمز ارسال پیام همگانی ────
    if text == BROADCAST_CODE:
        context.user_data["awaiting"] = "broadcast_message"
        await update.message.reply_text(
            "📢 *ارسال پیام همگانی*\n\n"
            "پیام خود را بنویسید تا برای همه مشترکان ربات ارسال شود:\n"
            "_(برای لغو، /start را بزنید)_",
            parse_mode="Markdown"
        )
        return

    player = get_player(data, uid)

    if awaiting == "broadcast_message":
        players = data.get("players", {})
        sent_count = 0
        fail_count = 0
        broadcast_text = (
            f"📢 *پیام از سازمان ملل WW3*\n"
            f"{'─' * 30}\n"
            f"{text}\n"
            f"{'─' * 30}\n"
            f"🕐 {datetime.now().strftime('%H:%M')}"
        )
        for target_uid in players:
            try:
                await context.bot.send_message(
                    target_uid,
                    broadcast_text,
                    parse_mode="Markdown"
                )
                sent_count += 1
            except:
                fail_count += 1
        context.user_data.pop("awaiting", None)
        await update.message.reply_text(
            f"✅ *پیام همگانی ارسال شد!*\n"
            f"📨 ارسال موفق: {sent_count} نفر\n"
            f"❌ ارسال ناموفق: {fail_count} نفر",
            parse_mode="Markdown"
        )
        return

    if awaiting == "msg_to_un":
        cname = player["country"] if player else "ناشناس"
        tg_user = update.effective_user
        uname = f"@{tg_user.username}" if tg_user.username else (tg_user.full_name or "ناشناس")
        msg = f"📨 *پیام از {cname}* | {uname}\n\n{text}"
        sent = 0
        for admin_id in data.get("un_admins", []):
            try:
                await context.bot.send_message(admin_id, msg, parse_mode="Markdown")
                sent += 1
            except: pass
        context.user_data.pop("awaiting", None)
        if sent == 0:
            data.setdefault("pending_un_messages", []).append({
                "from_uid": uid,
                "country": cname,
                "username": uname,
                "text": text,
                "time": datetime.now().isoformat()
            })
            save_data(data)
            await update.message.reply_text("⚠️ سازمان ملل آفلاین است.\n📥 پیام شما ذخیره شد و به محض آنلاین شدن ارسال می‌شود!")
        else:
            await update.message.reply_text("✅ پیام شما به سازمان ملل ارسال شد!")
        return

    if awaiting == "loan_amount":
        try:
            amount = int(text.replace(",","").replace("،","")) * 1_000_000
            if amount <= 0: raise ValueError
            if not player:
                await update.message.reply_text("❌ ابتدا بازی را شروع کنید!"); return
            if player.get("loan"):
                await update.message.reply_text("❌ وام فعال دارید! ابتدا تسویه کنید."); return
            if player.get("loan_cooldown"):
                await update.message.reply_text("⏳ باید منتظر حقوق بعدی بمانید تا وام جدید بگیرید."); return
            if amount > 1_000_000_000:
                await update.message.reply_text(f"❌ حداکثر مبلغ وام ۱٬۰۰۰ میلیون دلار است!\nعدد کوچک‌تری وارد کنید:"); return
            context.user_data["loan_amount_value"] = amount
            context.user_data.pop("awaiting", None)
            await update.message.reply_text(
                f"🏦 *مبلغ وام: {fmt(amount)}*\n\nتعداد اقساط را انتخاب کنید:",
                parse_mode="Markdown",
                reply_markup=kb(
                    [btn("1️⃣ ۱ قسط | سود ۱۰%","loaninst_1")],
                    [btn("5️⃣ ۵ قسط | سود ۵۰%","loaninst_5")],
                    [btn("🔟 ۱۰ قسط | سود ۱۰۰%","loaninst_10")],
                    [btn("❌ لغو","back_main")]
                )
            )
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید (مثلاً: 100 یعنی صد میلیون دلار):")
        return

    if awaiting == "treasury_amount":
        try:
            amount = int(text.replace(",","").replace("،","")) * 1_000_000
            if amount <= 0: raise ValueError
            if not player:
                await update.message.reply_text("❌ ابتدا بازی را شروع کنید!"); return
            if player["money"] < amount:
                await update.message.reply_text(f"❌ موجودی کافی نیست! موجودی شما: {fmt(player['money'])}"); return
            player["money"] -= amount
            if "treasury_deposits" not in player["buildings"]:
                player["buildings"]["treasury_deposits"] = []
            player["buildings"]["treasury_deposits"].append({
                "amount": amount,
                "date": datetime.now().isoformat()
            })
            player["treasury_sent"] = player.get("treasury_sent", 0) + amount
            save_player(data, uid, player)
            context.user_data.pop("awaiting", None)
            await update.message.reply_text(
                f"✅ *{fmt(amount)}* به خزانه واریز شد!\n"
                f"📅 ۳ روز دیگر *{fmt(amount * 2)}* دریافت می‌کنید.\n"
                f"💰 موجودی فعلی: {fmt(player['money'])}",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Treasury error: {e}")
            await update.message.reply_text("❌ عدد معتبر وارد کنید (مثلاً: 100 یعنی صد میلیون دلار):")
        return

    elif awaiting == "transfer_money_amount":
        try:
            amount = int(text.replace(",","").replace("،","")) * 1_000_000
            if amount <= 0: raise ValueError
            target_uid = context.user_data.get("transfer_target_uid")
            target = data["players"].get(target_uid)
            if not player or not target:
                await update.message.reply_text("❌ خطا!"); return
            if player.get("banned"):
                await update.message.reply_text("⛔ شما تحریم هستید!"); return
            if player["money"] < amount:
                await update.message.reply_text("❌ موجودی کافی نیست!"); return
            player["money"] -= amount
            target["money"] += amount
            data["players"][uid] = player
            data["players"][target_uid] = target
            save_data(data)
            context.user_data.pop("awaiting", None)
            await update.message.reply_text(f"✅ {fmt(amount)} به {target['country']} منتقل شد!")
            try:
                await context.bot.send_message(target_uid, f"💰 {fmt(amount)} از {player['country']} دریافت کردید!")
            except: pass
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید (میلیون دلار):")
        return

    elif awaiting == "trade_price":
        try:
            price = int(text.replace(",","").replace("،","")) * 1_000_000
            if price <= 0: raise ValueError
            seller_uid = uid
            target_uid = context.user_data.get("trade_target_uid")
            basket = context.user_data.get("trade_basket", {})
            target = data["players"].get(target_uid)
            if not player or not target or not basket:
                await update.message.reply_text("❌ خطا!"); return
            basket_str = "\n".join([f"{WEAPON_LABELS.get(k,k)}: {v}" for k,v in basket.items()])
            data.setdefault("pending_trades",{})[seller_uid] = {
                "basket": basket, "price": price,
                "seller_country": player["country"], "buyer_uid": target_uid
            }
            save_data(data)
            context.user_data.pop("awaiting", None)
            await update.message.reply_text(f"📨 پیشنهاد به {target['country']} ارسال شد!")
            try:
                await context.bot.send_message(
                    target_uid,
                    f"🤝 *پیشنهاد معامله از {player['country']}*\n\n{basket_str}\n\nقیمت: {fmt(price)}",
                    parse_mode="Markdown",
                    reply_markup=kb([btn("✅ قبول", f"tradeacc_{seller_uid}"), btn("❌ رد", f"traderej_{seller_uid}")])
                )
            except: pass
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید (میلیون دلار):")
        return

    elif awaiting == "un_set_satisfaction":
        try:
            value = int(text.replace(",","").replace("،",""))
            if value < 0 or value > 100: raise ValueError
            target_uid = context.user_data.get("un_target_uid")
            p = data["players"].get(target_uid)
            if not p: await update.message.reply_text("❌ خطا!"); return
            p["satisfaction"] = value
            data["players"][target_uid] = p
            save_data(data)
            context.user_data.pop("awaiting", None)
            emoji = "😊" if value >= 70 else ("😐" if value >= 40 else "😢")
            await update.message.reply_text(f"✅ رضایت مردم {p['country']} به {value}% تغییر یافت! {emoji}")
            try: await context.bot.send_message(target_uid, f"📢 سازمان ملل رضایت مردم شما را به {value}% تغییر داد {emoji}")
            except: pass
        except:
            await update.message.reply_text("❌ عدد معتبر (۰-۱۰۰) وارد کنید:")
        return

    elif awaiting == "un_addmoney":
        try:
            amount = int(text.replace(",","").replace("،","")) * 1_000_000
            target_uid = context.user_data.get("un_target_uid")
            p = data["players"].get(target_uid)
            if not p: await update.message.reply_text("❌ خطا!"); return
            p["money"] += amount
            data["players"][target_uid] = p
            save_data(data)
            context.user_data.pop("awaiting", None)
            await update.message.reply_text(f"✅ {fmt(amount)} به {p['country']} افزوده شد!")
            try: await context.bot.send_message(target_uid, f"💰 سازمان ملل {fmt(amount)} به حساب شما افزود!")
            except: pass
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید:")
        return

    elif awaiting == "un_removemoney":
        try:
            amount = int(text.replace(",","").replace("،","")) * 1_000_000
            target_uid = context.user_data.get("un_target_uid")
            p = data["players"].get(target_uid)
            if not p: await update.message.reply_text("❌ خطا!"); return
            p["money"] = max(0, p["money"] - amount)
            data["players"][target_uid] = p
            save_data(data)
            context.user_data.pop("awaiting", None)
            await update.message.reply_text(f"✅ {fmt(amount)} از {p['country']} کم شد!")
            try: await context.bot.send_message(target_uid, f"⚠️ سازمان ملل {fmt(amount)} از حساب شما کسر کرد!")
            except: pass
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید:")
        return

    elif awaiting == "stock_sell_amount":
        try:
            qty = int(text.replace(",","").replace("،",""))
            if qty <= 0: raise ValueError
            cname = context.user_data.get("stock_sell_cname")
            sell_price = context.user_data.get("stock_sell_price", STOCK_BASE_PRICE)
            if not cname or not player:
                await update.message.reply_text("❌ خطا!"); return
            portfolio = get_player_stocks(player)
            owned = portfolio.get(cname, 0)
            if qty > owned:
                await update.message.reply_text(f"❌ فقط {owned} سهم دارید!"); return
            tax = int(sell_price * qty * 0.10)
            total_income = sell_price * qty - tax
            portfolio[cname] = owned - qty
            player["stock_portfolio"] = portfolio
            player["money"] += total_income
            stocks = data.get("stocks", {})
            s = stocks.get(cname, {})
            lost_gain = qty * 0.05
            s["gain_pct"] = s.get("gain_pct", 0.0) - lost_gain
            s["sold"] = max(0, s.get("sold", 0) - qty)
            s["price"] = int(STOCK_BASE_PRICE * (1 + s["gain_pct"] / 100))
            if s["price"] < 1: s["price"] = 1
            stocks[cname] = s
            data["stocks"] = stocks
            data["players"][uid] = player
            save_data(data)
            context.user_data.pop("awaiting", None)
            context.user_data.pop("stock_sell_cname", None)
            context.user_data.pop("stock_sell_price", None)
            await update.message.reply_text(
                f"✅ *فروش موفق!*\n\n"
                f"💰 {qty} سهم {cname} فروخته شد\n"
                f"💵 قیمت کل: {fmt(sell_price * qty)}\n"
                f"🏦 کارمزد (۱۰٪): {fmt(tax)}\n"
                f"💵 درآمد خالص: {fmt(total_income)}\n"
                f"💼 سهام باقی‌مانده: {portfolio[cname]}",
                parse_mode="Markdown",
                reply_markup=kb([btn("📈 بورس","stock_market"), btn("🏠 منو","resume")])
            )
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید:")
        return

    elif awaiting == "self_milsub_amount":
        try:
            amount = int(text.replace(",","").replace("،",""))
            if amount <= 0: raise ValueError
            wkey = context.user_data.get("self_mil_wkey")
            if not player or not wkey:
                await update.message.reply_text("❌ خطا!"); return
            current = player["military"].get(wkey, 0)
            if amount > current:
                await update.message.reply_text(f"❌ موجودی کافی نیست! دارید: {current:,}"); return
            player["military"][wkey] = current - amount
            save_player(data, uid, player)
            context.user_data.pop("awaiting", None)
            context.user_data.pop("self_mil_wkey", None)
            label = WEAPON_LABELS.get(wkey, wkey)
            await update.message.reply_text(
                f"✅ {amount:,} واحد {label} کم شد!\n"
                f"قبلاً: {current:,} → الان: {player['military'][wkey]:,}",
                reply_markup=kb([btn("💼 دارایی‌ها","assets"), btn("🏠 منو","resume")])
            )
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید:")
        return

    elif awaiting == "un_milsub_amount":
        try:
            amount = int(text.replace(",","").replace("،",""))
            if amount <= 0: raise ValueError
            target_uid = context.user_data.get("un_target_uid")
            wkey = context.user_data.get("un_mil_wkey")
            p = data["players"].get(target_uid)
            if not p or not wkey: await update.message.reply_text("❌ خطا!"); return
            current = p["military"].get(wkey, 0)
            p["military"][wkey] = max(0, current - amount)
            data["players"][target_uid] = p
            save_data(data)
            context.user_data.pop("awaiting", None)
            context.user_data.pop("un_mil_wkey", None)
            label = WEAPON_LABELS.get(wkey, wkey)
            await update.message.reply_text(
                f"✅ {amount:,} واحد {label} از {p['country']} کم شد!\n"
                f"قبلاً: {current:,} → الان: {p['military'][wkey]:,}"
            )
            try: await context.bot.send_message(target_uid, f"⚠️ سازمان ملل {amount:,} واحد {label} از ارتش شما کسر کرد!")
            except: pass
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید (تعداد):")
        return

    elif awaiting == "create_alliance_name":
        if player and player["country"] in ["🇨🇳 چین", "🇬🇧 انگلیس"]:
            alliance_name = text.strip()
            if len(alliance_name) < 2 or len(alliance_name) > 30:
                await update.message.reply_text("❌ نام باید بین ۲ تا ۳۰ کاراکتر باشد:"); return
            data["custom_alliance"] = {
                "name": alliance_name,
                "founder": uid,
                "members": [uid],
            }
            player["group"] = alliance_name
            save_player(data, uid, player)
            save_data(data)
            context.user_data.pop("awaiting", None)
            await update.message.reply_text(
                f"✅ *اتحاد {alliance_name} تأسیس شد!*\n\n"
                f"{player['country']} بنیانگذار و اولین عضو این اتحادیه است.\n"
                f"سایر کشورها می‌توانند از طریق «انتقال به اتحاد دیگر» درخواست عضویت بدهند.\n"
                f"شما به عنوان بنیانگذار درخواست‌های ورود را تأیید یا رد می‌کنید.",
                parse_mode="Markdown"
            )
        return

    if text.strip() == "cancelwar":
        pending = data.get("pending_wars", {}).pop(uid, None)
        if not pending:
            await update.message.reply_text("❌ درخواست جنگ فعالی ندارید!")
            return
        player = get_player(data, uid)
        # برگشت تجهیزات
        if player:
            for wkey, amount in pending.get("weapons", {}).items():
                player["military"][wkey] = player["military"].get(wkey, 0) + amount
            data["players"][uid] = player
        save_data(data)
        # حذف پیام از سازمان ملل
        for msg_info in pending.get("un_msg_ids", []):
            try:
                await context.bot.delete_message(
                    chat_id=msg_info["chat_id"],
                    message_id=msg_info["message_id"]
                )
            except: pass
        await update.message.reply_text("✅ درخواست جنگ لغو شد و تجهیزات برگشت داده شد.")
        return

    if text.strip() == "paynow":
        if data.get("skip_next_salary"):
            return
        data["skip_next_salary"] = True
        data["force_pay_now"] = True
        save_data(data)
        await daily_income(context)
        return

    if text.strip() == "fixuni":
        RESTRICTED_BUILDINGS = ["air_factory", "defense_factory", "nuclear_plant", "missile_factory"]
        fixed = []
        for pid, p in data["players"].items():
            if p["buildings"].get("university"):
                cname = p.get("country", "")
                can_build = COUNTRIES.get(cname, {}).get("can_build", [])
                locked = [k for k in RESTRICTED_BUILDINGS if k not in can_build]
                current_unlocked = p.get("university_unlocked", [])
                new_items = [k for k in locked if k not in current_unlocked]
                if new_items:
                    p.setdefault("university_unlocked", []).extend(new_items)
                    data["players"][pid] = p
                    fixed.append(cname)
        save_data(data)
        names = ", ".join(fixed) if fixed else "هیچکس"
        await update.message.reply_text(f"✅ دانشگاه‌های باز نشده درست شد:\n{names}")
        return

    if text.strip() == "rechg":
        player = get_player(data, uid)
        if not player:
            return
        player["hack_today"] = 0
        player["hack_date"] = ""
        save_player(data, uid, player)
        return


    if text.strip() == "stk0":
        stocks = data.get("stocks", {})
        for cname in stocks:
            stocks[cname]["display_gain_pct"] = 0.0
        data["stocks"] = stocks
        save_data(data)
        return

    if text.strip() == "stk1":
        stocks = data.get("stocks", {})
        for cname in stocks:
            if "display_gain_pct" in stocks[cname]:
                del stocks[cname]["display_gain_pct"]
        data["stocks"] = stocks
        save_data(data)
        return


    if awaiting == "gift_amount":
        if uid not in data.get("un_admins", []):
            context.user_data.pop("awaiting", None)
            return
        try:
            amount = int(text.replace(",","").replace("،","")) * 1_000_000
            if amount <= 0: raise ValueError
            context.user_data["gift_amount_value"] = amount
            context.user_data.pop("awaiting", None)
            # نمایش لیست کشورها
            all_players = [(cid, p["country"]) for cid, p in data["players"].items()]
            if not all_players:
                await update.message.reply_text("❌ هیچ بازیکنی وجود ندارد!"); return
            rows = [[btn(f"{'✅' if cid in context.user_data.get('gift_selected', []) else '⬜'} {cname}", f"giftsel_{cid}")] for cid, cname in all_players]
            context.user_data["gift_selected"] = []
            rows.append([btn("✅ تأیید و ارسال","gift_confirm"), btn("❌ لغو","back_main")])
            await update.message.reply_text(
                f"💰 مبلغ: *{fmt(amount)}* به هر کشور\n\nکشورهای مورد نظر را انتخاب کنید (می‌توانید چند تا انتخاب کنید):",
                parse_mode="Markdown",
                reply_markup=kb(*rows)
            )
        except:
            await update.message.reply_text("❌ عدد معتبر وارد کنید (مثلاً: 700):")
        return


async def trade_accept(update, context):
    q = update.callback_query
    await q.answer()
    seller_uid = q.data.replace("tradeacc_","",1)
    buyer_uid = str(q.from_user.id)
    data = load_data()
    pending = data.get("pending_trades",{}).get(seller_uid)
    seller = data["players"].get(seller_uid)
    buyer = data["players"].get(buyer_uid)
    if not pending or not seller or not buyer:
        await q.edit_message_text("⚠️ معامله منقضی شده!"); return
    price = pending["price"]
    basket = pending["basket"]
    if buyer["money"] < price:
        await q.edit_message_text("❌ موجودی کافی نیست!"); return
    buyer["money"] -= price
    seller["money"] += price
    for wkey, amount in basket.items():
        seller["military"][wkey] = max(0, seller["military"].get(wkey,0) - amount)
        buyer["military"][wkey] = buyer["military"].get(wkey,0) + amount
    data["players"][seller_uid] = seller
    data["players"][buyer_uid] = buyer
    data.get("pending_trades",{}).pop(seller_uid, None)
    save_data(data)
    await q.edit_message_text("✅ معامله انجام شد!")
    try:
        await context.bot.send_message(seller_uid, f"✅ {buyer['country']} معامله را قبول کرد! {fmt(price)} دریافت کردید.")
    except: pass

async def trade_reject(update, context):
    q = update.callback_query
    await q.answer()
    seller_uid = q.data.replace("traderej_","",1)
    data = load_data()
    data.get("pending_trades",{}).pop(seller_uid, None)
    save_data(data)
    await q.edit_message_text("❌ معامله رد شد!")
    try:
        await context.bot.send_message(seller_uid, "❌ طرف مقابل معامله را رد کرد.")
    except: pass

# ──────────────────────────────────────────────
#  بازگشت‌ها و ارتباط با UN
# ──────────────────────────────────────────────
async def msg_un(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    un_admins = data.get("un_admins", [])
    status = "🟢 آنلاین" if un_admins else "🔴 آفلاین (پیام ذخیره می‌شود)"
    context.user_data["awaiting"] = "msg_to_un"
    await q.edit_message_text(
        f"📨 *ارسال پیام به سازمان ملل*\n\nوضعیت: {status}\n\nمتن، عکس، فایل یا هر چیزی ارسال کنید.\n_پیام بعدی شما فوروارد می‌شود._",
        parse_mode="Markdown",
        reply_markup=kb([btn("❌ لغو","back_main")])
    )

# ──────────────────────────────────────────────
#  وام
# ──────────────────────────────────────────────
async def loan_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    loan = player.get("loan")
    if loan:
        remaining = loan.get("remaining", 0)
        installment = loan.get("installment", 0)
        installments_left = loan.get("installments_left", 0)
        await q.edit_message_text(
            f"🏦 *وام فعال*\n\n"
            f"💵 مانده کل: {fmt(remaining)}\n"
            f"📦 قسط هر بار: {fmt(installment)}\n"
            f"🔢 اقساط باقی‌مانده: {installments_left}\n\n"
            f"اقساط به صورت خودکار از حقوق کسر می‌شود.\nیا می‌توانید همین الان پرداخت کنید:",
            parse_mode="Markdown",
            reply_markup=kb(
                [btn(f"✅ پرداخت یک قسط ({fmt(installment)})","loan_pay")],
                [BACK]
            )
        )
    elif player.get("loan_cooldown"):
        await q.edit_message_text(
            f"⏳ *وام جدید در دسترس نیست*\n\n"
            f"شما تازه وام خود را تسویه کردید.\n"
            f"بعد از دریافت حقوق بعدی می‌توانید وام جدید بگیرید.",
            parse_mode="Markdown",
            reply_markup=kb([BACK])
        )
    else:
        context.user_data["awaiting"] = "loan_amount"
        await q.edit_message_text(
            f"🏦 *درخواست وام*\n\n"
            f"💰 موجودی فعلی: {fmt(player['money'])}\n"
            f"⚠️ حداکثر مبلغ وام: {fmt(1_000_000_000)}\n\n"
            f"مقدار وام را به میلیون دلار وارد کنید:\n_(مثلاً ۱۰۰ = صد میلیون دلار)_",
            parse_mode="Markdown",
            reply_markup=kb([BACK])
        )

async def loan_select_installments(update, context):
    q = update.callback_query
    await q.answer()
    raw = q.data.replace("loaninst_","",1)
    # raw = "1" or "5" or "10"
    installments = int(raw)
    uid = str(q.from_user.id)
    loan_amount = context.user_data.get("loan_amount_value", 0)
    if not loan_amount:
        await q.edit_message_text("❌ خطا! دوباره تلاش کنید.", reply_markup=kb([BACK])); return
    interest_map = {1: 10, 5: 50, 10: 100}
    interest_pct = interest_map.get(installments, 50)
    total = int(loan_amount * (1 + interest_pct / 100))
    installment_amount = total // installments
    context.user_data["loan_pending"] = {
        "amount": loan_amount,
        "installments": installments,
        "interest_pct": interest_pct,
        "total": total,
        "installment_amount": installment_amount,
    }
    await q.edit_message_text(
        f"🏦 *جزئیات وام*\n\n"
        f"💵 مبلغ وام: {fmt(loan_amount)}\n"
        f"📊 سود: {interest_pct}%\n"
        f"💳 جمع با سود: {fmt(total)}\n"
        f"🔢 تعداد اقساط: {installments}\n"
        f"📦 هر قسط: {fmt(installment_amount)}\n\n"
        f"آیا تأیید می‌کنید؟",
        parse_mode="Markdown",
        reply_markup=kb(
            [btn("✅ تأیید و دریافت وام","loan_confirm"), btn("❌ لغو","loan_menu")]
        )
    )

async def loan_confirm(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    pending = context.user_data.get("loan_pending")
    if not player or not pending:
        await q.edit_message_text("❌ خطا!", reply_markup=kb([BACK])); return
    if player.get("loan"):
        await q.edit_message_text("❌ وام فعال دارید! ابتدا وام قبلی را تسویه کنید.", reply_markup=kb([btn("🏦 وام","loan_menu")])); return
    if player.get("loan_cooldown"):
        await q.edit_message_text("⏳ باید منتظر حقوق بعدی بمانید تا وام جدید بگیرید.", reply_markup=kb([BACK])); return
    player["money"] += pending["amount"]
    player["loan"] = {
        "original": pending["amount"],
        "total": pending["total"],
        "remaining": pending["total"],
        "installment": pending["installment_amount"],
        "installments_left": pending["installments"],
        "interest_pct": pending["interest_pct"],
    }
    save_player(data, uid, player)
    context.user_data.pop("loan_pending", None)
    context.user_data.pop("loan_amount_value", None)
    await q.edit_message_text(
        f"✅ *وام دریافت شد!*\n\n"
        f"💵 {fmt(pending['amount'])} به حساب شما واریز شد.\n"
        f"📦 هر قسط {fmt(pending['installment_amount'])} از حقوق کسر می‌شود.\n"
        f"🔢 تعداد اقساط: {pending['installments']}",
        parse_mode="Markdown",
        reply_markup=kb([btn("🏠 منو اصلی","resume")])
    )

async def loan_pay(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return
    loan = player.get("loan")
    if not loan:
        await q.edit_message_text("✅ وامی ندارید!", reply_markup=kb([BACK])); return
    installment = loan["installment"]
    if player["money"] < installment:
        await q.edit_message_text(
            f"❌ موجودی کافی نیست!\nقسط: {fmt(installment)}\nموجودی: {fmt(player['money'])}",
            reply_markup=kb([btn("🏦 وام","loan_menu")])
        ); return
    player["money"] -= installment
    loan["remaining"] -= installment
    loan["installments_left"] -= 1
    if loan["installments_left"] <= 0 or loan["remaining"] <= 0:
        player["loan"] = None
        player["loan_cooldown"] = True
        msg = f"🎉 *وام کاملاً تسویه شد!*\n⏳ بعد از حقوق بعدی می‌توانید وام جدید بگیرید."
    else:
        player["loan"] = loan
        msg = (
            f"✅ *قسط پرداخت شد!*\n"
            f"📦 مبلغ: {fmt(installment)}\n"
            f"💵 مانده: {fmt(loan['remaining'])}\n"
            f"🔢 اقساط باقی‌مانده: {loan['installments_left']}"
        )
    save_player(data, uid, player)
    await q.edit_message_text(msg, parse_mode="Markdown", reply_markup=kb([btn("🏦 وام","loan_menu"), btn("🏠 منو","resume")]))

# ──────────────────────────────────────────────
#  پروپاگاندا
# ──────────────────────────────────────────────
async def gift_select(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    target_cid = q.data.replace("giftsel_","",1)
    data = load_data()
    selected = context.user_data.get("gift_selected", [])
    if target_cid in selected:
        selected.remove(target_cid)
    else:
        selected.append(target_cid)
    context.user_data["gift_selected"] = selected
    amount = context.user_data.get("gift_amount_value", 0)
    all_players = [(cid, p["country"]) for cid, p in data["players"].items()]
    rows = [[btn(f"{'✅' if cid in selected else '⬜'} {cname}", f"giftsel_{cid}")] for cid, cname in all_players]
    rows.append([btn(f"✅ تأیید ({len(selected)} کشور)","gift_confirm"), btn("❌ لغو","back_main")])
    await q.edit_message_text(
        f"💰 مبلغ: *{fmt(amount)}* به هر کشور\n\nکشورهای مورد نظر را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=kb(*rows)
    )

async def gift_confirm(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    selected = context.user_data.get("gift_selected", [])
    amount = context.user_data.get("gift_amount_value", 0)
    if not selected or not amount:
        await q.edit_message_text("❌ هیچ کشوری انتخاب نشده!", reply_markup=kb([btn("🔙","back_main")])); return
    data = load_data()
    sent_to = []
    for cid in selected:
        p = data["players"].get(cid)
        if p:
            p["money"] += amount
            data["players"][cid] = p
            sent_to.append(p["country"])
            try:
                await context.bot.send_message(cid, f"🎁 *پول دریافت کردید!*\n💰 {fmt(amount)} به حساب شما واریز شد!", parse_mode="Markdown")
            except: pass
    save_data(data)
    context.user_data.pop("gift_selected", None)
    context.user_data.pop("gift_amount_value", None)
    await q.edit_message_text(
        f"✅ *ارسال موفق!*\n💰 {fmt(amount)} به {len(sent_to)} کشور ارسال شد:\n" + "\n".join(f"• {c}" for c in sent_to),
        parse_mode="Markdown",
        reply_markup=kb([btn("🏠 منو","back_main")])
    )

async def propaganda_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player or not player["buildings"].get("propaganda"):
        await q.answer("شرکت پروپاگاندا ندارید!", show_alert=True); return
    if player.get("propaganda_used_today"):
        await q.edit_message_text(
            "📢 *شرکت پروپاگاندا*\n\n⏳ امروز حمله انجام شد.\nفردا دوباره در دسترس خواهد بود.",
            parse_mode="Markdown",
            reply_markup=kb([BACK])
        ); return
    active = [(cid, p["country"]) for cid, p in data["players"].items() if cid != uid]
    if not active:
        await q.edit_message_text("⚠️ کشوری فعال نیست!", reply_markup=kb([BACK])); return
    rows = [[btn(cname, f"prop_target_{cid}")] for cid, cname in active]
    rows.append([BACK])
    await q.edit_message_text(
        "📢 *شرکت پروپاگاندا*\n\n"
        "🎯 کاهش رضایت مردم هدف: ۵% تا ۲۰% (همیشه موفق)\n"
        "🛡️ اگر هدف هم شرکت داشته باشد: ۱۰% از نتیجه کم می‌شود\n\n"
        "کشور هدف را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=kb(*rows)
    )

async def propaganda_do(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    target_uid = q.data.replace("prop_target_","",1)
    data = load_data()
    player = get_player(data, uid)
    target = data["players"].get(target_uid)
    if not player or not target:
        await q.answer("خطا!"); return
    if player.get("propaganda_used_today"):
        await q.edit_message_text("⏳ امروز پروپاگاندا انجام دادید!", reply_markup=kb([BACK])); return

    player["propaganda_used_today"] = True

    # کاهش رضایت ۵ تا ۲۰ درصد (همیشه موفق)
    sat_reduce = random.randint(5, 20)

    # اگر هدف هم شرکت پروپاگاندا دارد، ۱۰ درصد از نتیجه کم می‌شود
    if target["buildings"].get("propaganda"):
        sat_reduce = max(1, int(sat_reduce * 0.9))
        shield_note = f"\n🛡️ هدف شرکت پروپاگاندا دارد — ۱۰٪ از اثر کاهش یافت"
    else:
        shield_note = ""

    old_sat = target.get("satisfaction", 50)
    target["satisfaction"] = max(-20, old_sat - sat_reduce)

    result = (
        f"✅ *پروپاگاندا انجام شد!*\n"
        f"🎯 هدف: {target['country']}\n"
        f"📉 کاهش رضایت: {sat_reduce}%{shield_note}\n"
        f"😢 رضایت هدف: {old_sat}% ← {target['satisfaction']}%"
    )
    target_msg = (
        f"⚠️ *هشدار پروپاگاندا!*\n"
        f"📢 یک کشور ناشناس علیه شما تبلیغات منفی اجرا کرد!\n"
        f"😢 رضایت مردم {sat_reduce}% کاهش یافت! (اکنون: {target['satisfaction']}%)"
    )

    data["players"][uid] = player
    data["players"][target_uid] = target
    save_data(data)

    await q.edit_message_text(result, parse_mode="Markdown", reply_markup=kb([btn("🏠 منو","resume")]))
    try:
        await context.bot.send_message(target_uid, target_msg, parse_mode="Markdown")
    except: pass

def _check_satisfaction_crisis(player, uid):
    """بررسی بحران رضایت - فقط علامت‌گذاری، اعمال در daily"""
    sat = player.get("satisfaction", 50)
    if sat <= 0 and not player.get("income_halved"):
        player["income_halved"] = True
    elif sat > 0:
        player["income_halved"] = False

# ──────────────────────────────────────────────
#  مذاکره
# ──────────────────────────────────────────────
async def negotiation_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return

    # اگر مذاکره فعال داره
    neg = data.get("negotiations", {}).get(uid)
    if neg:
        partner_uid = neg["partner_uid"]
        partner = data["players"].get(partner_uid, {})
        partner_name = partner.get("country", "ناشناس")
        await q.edit_message_text(
            f"🤲 *مذاکره فعال*\n\nدر حال مذاکره با: {partner_name}\n\nهر پیامی که بفرستید مستقیم به طرف مقابل می‌رسد.",
            parse_mode="Markdown",
            reply_markup=kb([btn("🔚 پایان مذاکره","negotiation_end")])
        ); return

    # لیست کشورهای گروه مخالف
    my_group = player["group"]
    opposite_group = "BRICS" if my_group == "NATO" else "NATO"
    rivals = [(cid, p["country"]) for cid, p in data["players"].items()
              if cid != uid and COUNTRIES.get(p["country"], {}).get("group") == opposite_group]
    if not rivals:
        await q.edit_message_text(
            f"⚠️ هیچ کشور {opposite_group} آنلاین نیست!",
            reply_markup=kb([BACK])
        ); return
    rows = [[btn(cname, f"neg_req_{cid}")] for cid, cname in rivals]
    rows.append([BACK])
    await q.edit_message_text(
        f"🤲 *درخواست مذاکره*\n\nشما عضو {my_group} هستید.\nکشور {opposite_group} مورد نظر را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=kb(*rows)
    )

async def negotiation_request(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    target_uid = q.data.replace("neg_req_","",1)
    data = load_data()
    player = get_player(data, uid)
    target = data["players"].get(target_uid)
    if not player or not target:
        await q.answer("خطا!"); return
    # چک مذاکره فعال
    if data.get("negotiations", {}).get(uid):
        await q.edit_message_text("❌ شما در حال حاضر مذاکره فعال دارید!", reply_markup=kb([btn("🤲 مذاکره","negotiation_menu")])); return
    if data.get("negotiations", {}).get(target_uid):
        await q.edit_message_text("❌ این کشور در مذاکره دیگری است!", reply_markup=kb([BACK])); return
    # ذخیره درخواست pending
    data.setdefault("pending_negotiations", {})[uid] = {
        "requester_uid": uid,
        "target_uid": target_uid,
        "requester_country": player["country"],
        "target_country": target["country"],
    }
    save_data(data)
    await q.edit_message_text(
        f"📨 درخواست مذاکره برای {target['country']} ارسال شد.\nمنتظر پاسخ بمانید...",
        reply_markup=kb([BACK])
    )
    try:
        await context.bot.send_message(
            target_uid,
            f"🤲 *درخواست مذاکره*\n\n{player['country']} درخواست مذاکره دارد.\nآیا قبول می‌کنید؟",
            parse_mode="Markdown",
            reply_markup=kb(
                [btn("✅ قبول","neg_accept"), btn("❌ رد","neg_reject")]
            )
        )
    except: pass

async def negotiation_accept(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)  # این target هست
    data = load_data()
    # پیدا کردن درخواست
    pending = None
    req_uid = None
    for r_uid, p in data.get("pending_negotiations", {}).items():
        if p["target_uid"] == uid:
            pending = p
            req_uid = r_uid
            break
    if not pending:
        await q.edit_message_text("⚠️ درخواست منقضی شده!"); return
    data.get("pending_negotiations", {}).pop(req_uid, None)
    # ایجاد مذاکره فعال برای هر دو طرف
    data.setdefault("negotiations", {})[req_uid] = {"partner_uid": uid}
    data["negotiations"][uid] = {"partner_uid": req_uid}
    save_data(data)
    requester = data["players"].get(req_uid, {})
    target = data["players"].get(uid, {})
    # پیام به هر دو
    for send_uid, other_name in [(req_uid, target.get("country","?")), (uid, requester.get("country","?"))]:
        try:
            await context.bot.send_message(
                send_uid,
                f"🤲 *مذاکره آغاز شد!*\n\nشما با {other_name} در مذاکره هستید.\nهر پیامی که بفرستید مستقیم به طرف مقابل می‌رسد.",
                parse_mode="Markdown",
                reply_markup=kb([btn("🔚 پایان مذاکره","negotiation_end")])
            )
        except: pass
    await q.edit_message_text(
        f"✅ مذاکره با {requester.get('country','?')} شروع شد!\nپیام‌های شما مستقیم ارسال می‌شود.",
        reply_markup=kb([btn("🔚 پایان مذاکره","negotiation_end")])
    )

async def negotiation_reject(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    req_uid = None
    pending = None
    for r_uid, p in data.get("pending_negotiations", {}).items():
        if p["target_uid"] == uid:
            pending = p
            req_uid = r_uid
            break
    if pending:
        data.get("pending_negotiations", {}).pop(req_uid, None)
        save_data(data)
        target_country = data["players"].get(uid, {}).get("country","?")
        try:
            await context.bot.send_message(req_uid, f"❌ {target_country} درخواست مذاکره را رد کرد.")
        except: pass
    await q.edit_message_text("❌ درخواست مذاکره رد شد.", reply_markup=kb([BACK]))

async def negotiation_end(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    neg = data.get("negotiations", {}).get(uid)
    if not neg:
        await q.edit_message_text("⚠️ مذاکره فعالی ندارید!", reply_markup=kb([BACK])); return
    partner_uid = neg["partner_uid"]
    partner = data["players"].get(partner_uid, {})
    partner_country = partner.get("country","?")
    my_country = data["players"].get(uid, {}).get("country","?")
    # پاک کردن هر دو طرف
    data.get("negotiations", {}).pop(uid, None)
    data.get("negotiations", {}).pop(partner_uid, None)
    save_data(data)
    await q.edit_message_text(
        f"🔚 مذاکره با {partner_country} پایان یافت.",
        reply_markup=kb([btn("🏠 منو","resume")])
    )
    try:
        await context.bot.send_message(
            partner_uid,
            f"🔚 *مذاکره پایان یافت.*\n{my_country} مذاکره را به پایان رساند.",
            parse_mode="Markdown",
            reply_markup=kb([btn("🏠 منو","resume")])
        )
    except: pass

# ──────────────────────────────────────────────
#  انتقال به اتحاد دیگر
# ──────────────────────────────────────────────
async def switch_alliance(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return

    current_group = player["group"]
    custom = data.get("custom_alliance")

    if data.get("pending_alliance", {}).get(uid):
        await q.edit_message_text(
            f"⏳ درخواست انتقال شما در انتظار تأیید است.",
            reply_markup=kb([BACK])
        ); return

    options = []
    if current_group != "NATO":
        options.append(btn("🔵 انتقال به NATO (تأیید اسرائیل)", "alliance_to_NATO"))
    if current_group != "BRICS":
        options.append(btn("🔴 انتقال به BRICS (تأیید روسیه)", "alliance_to_BRICS"))
    if custom and current_group != custom["name"]:
        founder_uid = custom.get("founder")
        founder_name = data["players"].get(founder_uid, {}).get("country", "بنیانگذار") if founder_uid else "بنیانگذار"
        options.append(btn(f"🌐 انتقال به {custom['name']}", f"alliance_to_CUSTOM"))

    rows = [[o] for o in options]
    rows.append([BACK])
    await q.edit_message_text(
        f"🔄 *انتقال به اتحاد دیگر*\n\nاتحاد فعلی: *{current_group}*\n\nمقصد را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=kb(*rows)
    )

async def alliance_req_confirm(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    # تشخیص مقصد از callback_data
    dest = q.data.replace("alliance_to_", "")  # NATO, BRICS, CUSTOM
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return

    current_group = player["group"]
    custom = data.get("custom_alliance")

    if dest == "CUSTOM":
        if not custom:
            await q.answer("اتحاد جدید وجود ندارد!", show_alert=True); return
        target_group = custom["name"]
        founder_uid = custom.get("founder")
        approver_country = data["players"].get(founder_uid, {}).get("country", "بنیانگذار") if founder_uid else None
        # approver_uid همون founder هست
        approver_uid = founder_uid
        if not approver_uid or approver_uid not in data["players"]:
            await q.edit_message_text("❌ بنیانگذار اتحاد یافت نشد!", reply_markup=kb([BACK])); return
        data.setdefault("pending_alliance", {})[uid] = {
            "requester_uid": uid,
            "requester_country": player["country"],
            "from_group": current_group,
            "to_group": target_group,
            "approver_uid": approver_uid,
        }
        save_data(data)
        await q.edit_message_text(
            f"📨 درخواست عضویت در *{target_group}* برای {approver_country} ارسال شد.\nمنتظر پاسخ بمانید...",
            parse_mode="Markdown", reply_markup=kb([BACK])
        )
        try:
            await context.bot.send_message(
                approver_uid,
                f"🔄 *درخواست عضویت در اتحاد {target_group}*\n\n"
                f"کشور {player['country']} می‌خواهد به اتحاد *{target_group}* بپیوندد.\n\n"
                f"آیا این درخواست را تأیید می‌کنید؟",
                parse_mode="Markdown",
                reply_markup=kb(
                    [btn(f"✅ تأیید", f"alliance_approve_{uid}")],
                    [btn(f"❌ رد", f"alliance_reject_{uid}")]
                )
            )
        except:
            data.get("pending_alliance", {}).pop(uid, None)
            save_data(data)
            await context.bot.send_message(uid, f"❌ خطا در ارسال پیام به {approver_country}.")
        return
    elif dest == "NATO":
        target_group = "NATO"
        approver_country = "🇮🇱 اسرائیل"
    else:
        target_group = "BRICS"
        approver_country = "🇷🇺 روسیه"

    # پیدا کردن UID تأییدکننده
    approver_uid = None
    for cid, p in data["players"].items():
        if p.get("country") == approver_country:
            approver_uid = cid
            break

    if not approver_uid:
        await q.edit_message_text(
            f"❌ {approver_country} هنوز وارد بازی نشده!\nوقتی بازیکن آن وارد شد دوباره امتحان کنید.",
            reply_markup=kb([BACK])
        ); return

    data.setdefault("pending_alliance", {})[uid] = {
        "requester_uid": uid,
        "requester_country": player["country"],
        "from_group": current_group,
        "to_group": target_group,
        "approver_uid": approver_uid,
    }
    save_data(data)

    await q.edit_message_text(
        f"📨 درخواست انتقال به *{target_group}* برای {approver_country} ارسال شد.\nمنتظر پاسخ بمانید...",
        parse_mode="Markdown",
        reply_markup=kb([BACK])
    )
    try:
        await context.bot.send_message(
            approver_uid,
            f"🔄 *درخواست انتقال اتحاد*\n\n"
            f"کشور {player['country']} می‌خواهد از *{current_group}* به *{target_group}* منتقل شود.\n\n"
            f"آیا این درخواست را تأیید می‌کنید؟",
            parse_mode="Markdown",
            reply_markup=kb(
                [btn(f"✅ تأیید انتقال", f"alliance_approve_{uid}")],
                [btn(f"❌ رد", f"alliance_reject_{uid}")]
            )
        )
    except:
        data.get("pending_alliance", {}).pop(uid, None)
        save_data(data)
        await context.bot.send_message(uid, f"❌ خطا در ارسال پیام به {approver_country}. دوباره تلاش کنید.")

async def alliance_approve(update, context):
    q = update.callback_query
    await q.answer()
    requester_uid = q.data.replace("alliance_approve_","",1)
    data = load_data()
    pending = data.get("pending_alliance", {}).get(requester_uid)
    if not pending:
        await q.edit_message_text("⚠️ درخواست منقضی شده!"); return

    requester = data["players"].get(requester_uid)
    if not requester:
        await q.edit_message_text("⚠️ بازیکن یافت نشد!"); return

    old_group = pending["from_group"]
    new_group = pending["to_group"]

    # تغییر گروه
    requester["group"] = new_group
    data["players"][requester_uid] = requester

    # اگه اتحاد custom هست اعضا رو آپدیت کن
    custom = data.get("custom_alliance")
    if custom:
        members = custom.get("members", [])
        # حذف از custom اگه داشت
        if requester_uid in members and new_group != custom["name"]:
            members.remove(requester_uid)
        # اضافه به custom اگه رفت
        if new_group == custom["name"] and requester_uid not in members:
            members.append(requester_uid)
        custom["members"] = members
        data["custom_alliance"] = custom

    data.get("pending_alliance", {}).pop(requester_uid, None)
    save_data(data)

    approver = data["players"].get(str(q.from_user.id), {})
    approver_name = approver.get("country","؟")

    await q.edit_message_text(
        f"✅ انتقال {requester['country']} از {old_group} به {new_group} تأیید شد!",
        reply_markup=kb([btn("🏠 منو","resume")])
    )
    try:
        await context.bot.send_message(
            requester_uid,
            f"🎉 *انتقال اتحاد تأیید شد!*\n\n"
            f"{approver_name} درخواست شما را تأیید کرد.\n"
            f"✅ شما اکنون عضو *{new_group}* هستید!",
            parse_mode="Markdown",
            reply_markup=kb([btn("🏠 منو","resume")])
        )
    except: pass

async def alliance_reject(update, context):
    q = update.callback_query
    await q.answer()
    requester_uid = q.data.replace("alliance_reject_","",1)
    data = load_data()
    pending = data.get("pending_alliance", {}).get(requester_uid)
    requester = data["players"].get(requester_uid, {})
    requester_name = requester.get("country","؟")

    data.get("pending_alliance", {}).pop(requester_uid, None)
    save_data(data)

    approver = data["players"].get(str(q.from_user.id), {})
    approver_name = approver.get("country","؟")

    await q.edit_message_text(
        f"❌ درخواست انتقال {requester_name} رد شد.",
        reply_markup=kb([btn("🏠 منو","resume")])
    )
    try:
        await context.bot.send_message(
            requester_uid,
            f"❌ *درخواست انتقال رد شد!*\n\n"
            f"{approver_name} درخواست شما را رد کرد.\n"
            f"شما همچنان عضو {pending.get('from_group','')} هستید.",
            parse_mode="Markdown",
            reply_markup=kb([btn("🏠 منو","resume")])
        )
    except: pass

async def create_alliance_menu(update, context):
    """چین و انگلیس می‌تونن اتحاد جدید بسازن"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    ALLOWED = ["🇨🇳 چین", "🇬🇧 انگلیس"]
    if not player or player["country"] not in ALLOWED:
        await q.answer("❌ شما دسترسی ندارید!", show_alert=True); return
    custom = data.get("custom_alliance")
    if custom:
        members = custom.get("members", [])
        member_names = [data["players"][m]["country"] for m in members if m in data["players"]]
        await q.edit_message_text(
            f"🌐 *اتحاد {custom['name']}*\n\n"
            f"👥 اعضا ({len(members)}):\n" + "\n".join(f"  • {n}" for n in member_names),
            parse_mode="Markdown",
            reply_markup=kb(
                [btn("💥 انحلال اتحاد", "dissolve_alliance")],
                [BACK]
            )
        ); return
    context.user_data["awaiting"] = "create_alliance_name"
    await q.edit_message_text(
        "🌐 *ساخت اتحاد جدید*\n\nنام اتحادیه جدید را وارد کنید:",
        parse_mode="Markdown",
        reply_markup=kb([btn("❌ لغو", "back_main")])
    )

async def dissolve_alliance(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player or player["country"] not in ["🇨🇳 چین", "🇬🇧 انگلیس"]:
        await q.answer("❌ شما دسترسی ندارید!", show_alert=True); return
    custom = data.get("custom_alliance")
    if not custom:
        await q.answer("اتحادی وجود ندارد!", show_alert=True); return
    alliance_name = custom["name"]
    members = custom.get("members", [])
    # همه اعضا رو برگردون به BRICS
    for m in members:
        p = data["players"].get(m)
        if p and p["group"] == alliance_name:
            p["group"] = "BRICS"
            data["players"][m] = p
            try:
                await context.bot.send_message(m, f"⚠️ اتحاد *{alliance_name}* منحل شد!\nشما به BRICS بازگشتید.", parse_mode="Markdown")
            except: pass
    data.pop("custom_alliance", None)
    save_data(data)
    await q.edit_message_text(f"✅ اتحاد {alliance_name} منحل شد.", reply_markup=kb([BACK]))

async def back_main(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    context.user_data.pop("awaiting", None)
    if player:
        await main_menu(update, context, player, edit=True)
    else:
        await q.edit_message_text("ابتدا بازی را شروع کنید!", reply_markup=kb([btn("🎮 شروع","choose_group")]))

async def back_start(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    text = "🌍 *WW3 CLUB*\n\nبه بازی جنگ جهانی سوم خوش آمدید!\n۲۴ کشور از NATO و BRICS رویاروی هم."
    if player:
        rows = [[btn("▶️ ادامه","resume"), btn("📖 راهنما","help")]]
    else:
        rows = [[btn("🎮 شروع","choose_group"), btn("📖 راهنما","help")]]
    await q.edit_message_text(text, reply_markup=kb(*rows), parse_mode="Markdown")

async def un_menu_back(update, context):
    await un_menu(update, context)

# ──────────────────────────────────────────────
#  main
# ──────────────────────────────────────────────
# ──────────────────────────────────────────────
# ──────────────────────────────────────────────
#  📈 بورس بین‌المللی
# ──────────────────────────────────────────────

STOCK_TOTAL_SHARES = 1000      # هر کشور ۱۰۰۰ سهم
STOCK_BASE_PRICE   = 1_000_000 # قیمت پایه هر سهم: ۱ میلیون
STOCK_HOURLY_GAIN  = 5.0       # هر ساعت ۵٪ سود روی سهم

def get_stock_data(data):
    """برگرداندن اطلاعات بورس — اگه نبود ایجاد می‌کنه"""
    if "stocks" not in data:
        data["stocks"] = {}
    stocks = data["stocks"]
    # برای هر کشور بازیکن که سهام ندارن init کن
    for uid, player in data.get("players", {}).items():
        cname = player.get("country", "")
        if cname and cname not in stocks:
            stocks[cname] = {
                "price": STOCK_BASE_PRICE,
                "gain_pct": 0.0,          # درصد سود/ضرر فعلی
                "sold": 0,                # سهام فروخته‌شده
                "last_update": datetime.now().isoformat(),
            }
    return stocks

def update_stock_prices(data):
    """به‌روزرسانی قیمت سهام بر اساس ساعت‌های گذشته"""
    stocks = get_stock_data(data)
    now = datetime.now()
    for cname, s in stocks.items():
        try:
            last = datetime.fromisoformat(s.get("last_update", now.isoformat()))
            hours = (now - last).total_seconds() / 3600
            if hours >= 1:
                hours_int = int(hours)
                # هر ساعت ۵٪ سود اضافه می‌شه
                s["gain_pct"] = s.get("gain_pct", 0.0) + hours_int * STOCK_HOURLY_GAIN
                s["price"] = int(STOCK_BASE_PRICE * (1 + s["gain_pct"] / 100))
                s["last_update"] = now.isoformat()
        except:
            s["last_update"] = now.isoformat()
    return stocks

def get_player_stocks(player):
    """برگرداندن پرتفوی سهام بازیکن"""
    return player.setdefault("stock_portfolio", {})

def stock_market_text(data):
    """متن وضعیت کل بازار"""
    stocks = update_stock_prices(data)
    lines = ["📈 *بورس بین‌المللی WW3*\n"]
    lines.append(f"{'کشور':<18} {'قیمت سهم':<14} {'سود/ضرر':<10} {'سهام باقی'}")
    lines.append("─" * 52)
    for cname, s in stocks.items():
        remaining = STOCK_TOTAL_SHARES - s.get("sold", 0)
        gain = s.get("display_gain_pct", s.get("gain_pct", 0.0))
        arrow = "📈" if gain >= 0 else "📉"
        price_m = s["price"] / 1_000_000
        lines.append(
            f"{cname[:15]:<16} {price_m:.1f}M$ {arrow}{gain:+.1f}%  {remaining}/{STOCK_TOTAL_SHARES}"
        )
    return "\n".join(lines)

async def stock_market(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("ابتدا بازی کنید!", show_alert=True); return

    # به‌روزرسانی قیمت‌ها
    update_stock_prices(data)
    save_data(data)

    portfolio = get_player_stocks(player)
    has_stocks = any(v > 0 for v in portfolio.values())

    text = stock_market_text(data)
    text += f"\n\n💼 *سبد سهام شما:*\n"
    if has_stocks:
        for cname, qty in portfolio.items():
            if qty > 0:
                price = data["stocks"].get(cname, {}).get("price", STOCK_BASE_PRICE)
                text += f"• {cname}: {qty} سهم | ارزش: {fmt(qty * price)}\n"
    else:
        text += "_هنوز سهامی نخریده‌اید_\n"

    rows = [
        [btn("🛒 خرید سهام", "stock_buy_menu")],
    ]
    if has_stocks:
        rows.append([btn("💰 فروش سهام", "stock_sell_menu")])
    rows.append([BACK])

    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb(*rows))

async def stock_buy_menu(update, context):
    """لیست کشورهای قابل خرید"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return

    stocks = update_stock_prices(data)
    save_data(data)

    # فقط کشورهایی که بازیکن دارن
    active_countries = {p["country"] for p in data["players"].values()}
    rows = []
    for cname in active_countries:
        if cname in stocks:
            s = stocks[cname]
            remaining = STOCK_TOTAL_SHARES - s.get("sold", 0)
            gain = s.get("display_gain_pct", s.get("gain_pct", 0.0))
            price_m = s["price"] / 1_000_000
            arrow = "📈" if gain >= 0 else "📉"
            label = f"{cname} | {price_m:.1f}M$ {arrow}{gain:+.1f}% | باقی:{remaining}"
            import hashlib
            ckey = hashlib.md5(cname.encode()).hexdigest()[:8]
            rows.append([btn(label, f"stock_view_{ckey}")])
    rows.append([btn("🔙 بازگشت", "stock_market")])

    await q.edit_message_text(
        "🛒 *خرید سهام*\nکشور مورد نظر را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=kb(*rows)
    )

async def stock_view_country(update, context):
    """نمایش سهام یک کشور و دکمه‌های خرید"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    ckey = q.data.replace("stock_view_", "", 1)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return

    # پیدا کردن نام کشور از hash
    import hashlib
    cname = None
    for name in [p["country"] for p in data["players"].values()]:
        if hashlib.md5(name.encode()).hexdigest()[:8] == ckey:
            cname = name
            break
    if not cname:
        await q.answer("کشور یافت نشد!", show_alert=True); return

    stocks = update_stock_prices(data)
    s = stocks.get(cname, {"price": STOCK_BASE_PRICE, "gain_pct": 0.0, "sold": 0})
    remaining = STOCK_TOTAL_SHARES - s.get("sold", 0)
    gain = s.get("display_gain_pct", s.get("gain_pct", 0.0))
    price = s["price"]
    portfolio = get_player_stocks(player)
    owned = portfolio.get(cname, 0)

    arrow = "📈" if gain >= 0 else "📉"
    text = (
        f"📊 *سهام {cname}*\n\n"
        f"💵 قیمت هر سهم: {fmt(price)}\n"
        f"{arrow} سود/ضرر: {gain:+.1f}%\n"
        f"📦 سهام باقی: {remaining}/{STOCK_TOTAL_SHARES}\n"
        f"💼 سهام شما: {owned}\n"
        f"💰 موجودی شما: {fmt(player['money'])}\n\n"
        f"چند سهم خریداری کنید؟"
    )

    rows = []
    for qty in [1, 10, 100]:
        cost = price * qty
        if remaining >= qty:
            rows.append([btn(f"🛒 خرید {qty} سهم | {fmt(cost)}", f"stock_buy_{ckey}_{qty}")])
    rows.append([btn("🔙 بازگشت", "stock_buy_menu")])

    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb(*rows))

async def stock_buy_action(update, context):
    """انجام خرید سهام"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    parts = q.data.replace("stock_buy_", "", 1).rsplit("_", 1)
    if len(parts) != 2:
        await q.answer("خطا!"); return
    ckey, qty_str = parts
    qty = int(qty_str)

    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return

    import hashlib
    cname = None
    for name in [p["country"] for p in data["players"].values()]:
        if hashlib.md5(name.encode()).hexdigest()[:8] == ckey:
            cname = name
            break
    if not cname:
        await q.answer("کشور یافت نشد!", show_alert=True); return

    stocks = update_stock_prices(data)
    s = stocks.setdefault(cname, {"price": STOCK_BASE_PRICE, "gain_pct": 0.0, "sold": 0})
    remaining = STOCK_TOTAL_SHARES - s.get("sold", 0)
    price = s["price"]
    total_cost = price * qty

    if remaining < qty:
        await q.answer(f"فقط {remaining} سهم باقی مانده!", show_alert=True); return
    if player["money"] < total_cost:
        await q.answer("موجودی کافی نیست!", show_alert=True); return

    # خرید
    player["money"] -= total_cost
    portfolio = get_player_stocks(player)
    portfolio[cname] = portfolio.get(cname, 0) + qty
    player["stock_portfolio"] = portfolio

    # افزایش قیمت: هر سهم خریداری شده ۰.۱٪ سود اضافه می‌کنه
    added_gain = qty * 0.05
    s["gain_pct"] = s.get("gain_pct", 0.0) + added_gain
    s["sold"] = s.get("sold", 0) + qty
    s["price"] = int(STOCK_BASE_PRICE * (1 + s["gain_pct"] / 100))

    # خرید سهام → ۲٪ سود اضافه به قیمت (علاوه بر ۰.۱٪ هر سهم)
    s["gain_pct"] = s.get("gain_pct", 0.0) + 2.0
    s["price"] = int(STOCK_BASE_PRICE * (1 + s["gain_pct"] / 100))

    data["stocks"] = stocks
    data["players"][uid] = player
    save_data(data)

    await q.edit_message_text(
        f"✅ *خرید موفق!*\n\n"
        f"🛒 {qty} سهم {cname}\n"
        f"💵 هزینه: {fmt(total_cost)}\n"
        f"💼 سهام شما از این کشور: {portfolio[cname]}\n"
        f"💰 موجودی باقی: {fmt(player['money'])}",
        parse_mode="Markdown",
        reply_markup=kb([btn("📈 بورس","stock_market"), btn("🏠 منو","resume")])
    )

async def stock_sell_menu(update, context):
    """منوی فروش — لیست سهام‌های بازیکن"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return

    portfolio = get_player_stocks(player)
    owned = {k: v for k, v in portfolio.items() if v > 0}
    if not owned:
        await q.answer("سهامی ندارید!", show_alert=True); return

    stocks = update_stock_prices(data)
    rows = []
    import hashlib
    for cname, qty in owned.items():
        price = stocks.get(cname, {}).get("price", STOCK_BASE_PRICE)
        value = fmt(qty * price)
        ckey = hashlib.md5(cname.encode()).hexdigest()[:8]
        rows.append([btn(f"{cname} | {qty} سهم | ارزش: {value}", f"stock_sell_select_{ckey}")])
    rows.append([btn("🔙 بازگشت", "stock_market")])

    await q.edit_message_text(
        "💰 *فروش سهام*\nسهام مورد نظر برای فروش را انتخاب کنید:",
        parse_mode="Markdown",
        reply_markup=kb(*rows)
    )

async def stock_sell_select(update, context):
    """انتخاب کشور برای فروش — از بازیکن می‌خوایم عدد تایپ کنه"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    ckey = q.data.replace("stock_sell_select_", "", 1)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!"); return

    import hashlib
    cname = None
    portfolio = get_player_stocks(player)
    for name in portfolio.keys():
        if hashlib.md5(name.encode()).hexdigest()[:8] == ckey:
            cname = name
            break
    if not cname:
        await q.answer("خطا!", show_alert=True); return

    stocks = update_stock_prices(data)
    price = stocks.get(cname, {}).get("price", STOCK_BASE_PRICE)
    owned = portfolio.get(cname, 0)

    context.user_data["awaiting"] = "stock_sell_amount"
    context.user_data["stock_sell_cname"] = cname
    context.user_data["stock_sell_price"] = price

    await q.edit_message_text(
        f"💰 *فروش سهام {cname}*\n\n"
        f"💼 سهام شما: {owned}\n"
        f"💵 قیمت هر سهم: {fmt(price)}\n\n"
        f"تعداد سهم برای فروش را تایپ کنید:",
        parse_mode="Markdown",
        reply_markup=kb([btn("❌ لغو", "stock_sell_menu")])
    )


#  📰 سیستم خبر تصادفی
# ──────────────────────────────────────────────

NEWS_TEMPLATES = [
    # 🤣 طنز و عجیب‌غریب
    "🗞️ خبر فوری: رئیس‌جمهور {country} امروز هنگام افتتاح کارخانه جدید، روبان را اشتباه برید و انگشتش را هم با آن قطع کرد!",
    "🗞️ خبر فوری: در {country} یک گاو فراری وارد پارلمان شد و یک ساعت کامل در صندلی نخست‌وزیر نشست. نمایندگان جرئت بیرون کردنش را نداشتند.",
    "🗞️ خبر فوری: یک شهروند {country} ادعا کرد با کمربندش UFO را سرنگون کرده. دولت هنوز در حال بررسی است.",
    "🗞️ خبر فوری: در {country} یک مرغ فراری چهار ساعت ترافیک اتوبان اصلی را مسدود کرد. پلیس مجبور شد مذاکره‌کننده بفرستد.",
    "🗞️ خبر فوری: وزیر دفاع {country} در جلسه مهم امنیتی خوابش برد و خروپف می‌کشید. دوربین‌ها همه چیز را ضبط کردند.",
    "🗞️ خبر فوری: در {country} کشف شد که یکی از مقامات ارشد سال‌هاست به جای امضا، نقش گربه می‌کشد. همه اسناد رسمی همچنان معتبرند.",
    "🗞️ خبر فوری: رئیس بانک مرکزی {country} اعتراف کرد که حسابداری را از یوتیوب یاد گرفته.",
    "🗞️ خبر فوری: شهردار پایتخت {country} برای کاهش ترافیک پیشنهاد داد همه با الاغ به سرکار بروند. کابینه هنوز در حال بررسی است.",
    "🗞️ خبر فوری: در {country} یک موش آموزش‌دیده مدت سه هفته به جای مأمور گمرک کار کرده بود. کسی متوجه نشده بود.",
    "🗞️ خبر فوری: مجلس {country} امروز یک ساعت کامل درباره اینکه آیا سوپ آبکی است یا نه بحث کرد. نتیجه‌گیری نشد.",
    "🗞️ خبر فوری: در {country} معلوم شد وزیر خارجه تمام مذاکرات دیپلماتیک را با گوگل ترنسلیت انجام می‌داده.",
    "🗞️ خبر فوری: ژنرال ارشد {country} در مانور نظامی اشتباهی وارد مزرعه مرغداری شد. مرغ‌ها متفرق شدند.",
    "🗞️ خبر فوری: در {country} یک اتوبوس شهری ۴ سال بود روی مسیر اشتباه می‌رفت. مسافران می‌گویند بهتر بود.",
    "🗞️ خبر فوری: دولت {country} اعلام کرد برنامه فضایی‌شان را با تلسکوپی که از بازار دست‌دوم خریده‌اند پیش می‌برند.",
    "🗞️ خبر فوری: در {country} یک پیرمرد ۸۷ ساله بدون مجوز یک باند فرودگاه کوچک در حیاطش ساخت. هواپیماها هنوز دارند فرود می‌آیند.",

    # 🏅 ورزشی مسخره
    "🗞️ خبر ورزشی: تیم ملی فوتبال {country} در یک بازی دوستانه با ۱۷ بر صفر باخت. مربی گفت «نتیجه مهم نیست، تجربه مهم است».",
    "🗞️ خبر ورزشی: قهرمان ملی کشتی {country} امروز در مسابقه به حریفش دست داد و گفت زشت است کتکش بزند.",
    "🗞️ خبر ورزشی: در المپیک محلی {country} برای اولین بار رشته «سریع‌ترین خوردن کباب» به برنامه اضافه شد.",
    "🗞️ خبر ورزشی: تیم ملی شطرنج {country} اعلام کرد از این پس همه مسابقات را چشم‌بسته بازی می‌کند تا جذاب‌تر باشد.",
    "🗞️ خبر ورزشی: دروازه‌بان تیم ملی {country} در جریان بازی مهم خوابش برد. گل خورده شد ولی او بیدار نشد.",

    # 🌍 سیاسی طنز
    "🗞️ خبر سیاسی: رهبر {country} در نشست بین‌المللی اشتباهی میکروفن کشور همسایه را برداشت و یک ربع سخنرانی کرد. کسی چیزی نگفت.",
    "🗞️ خبر سیاسی: وزیر اقتصاد {country} اعلام کرد راه‌حل تورم را در خواب دیده. جزئیات محرمانه است.",
    "🗞️ خبر سیاسی: {country} اعلام کرد سفیر جدیدش را از بین برندگان یک مسابقه تلویزیونی انتخاب می‌کند.",
    "🗞️ خبر سیاسی: پارلمان {country} به خاطر اختلاف نظر درباره رنگ پرده‌های ساختمان، سه روز تعطیل شد.",
    "🗞️ خبر سیاسی: رئیس‌جمهور {country} در سفر رسمی چمدانش را جا گذاشت. تیم امنیتی سه ساعت فکر کردند بمب است.",
    "🗞️ خبر سیاسی: {country} اعلام کرد می‌خواهد اولین کشور جهان باشد که پایتختش را به کره ماه منتقل کند.",
    "🗞️ خبر سیاسی: وزارت خارجه {country} به اشتباه به جای بیانیه رسمی، دستور پیتزا را منتشر کرد.",

    # 💰 اقتصادی مضحک
    "🗞️ خبر اقتصادی: بانک مرکزی {country} اعلام کرد ذخایر طلای کشور را «جای امنی» گذاشته ولی آدرسش را فراموش کرده.",
    "🗞️ خبر اقتصادی: وزیر اقتصاد {country} پیشنهاد داد ارز ملی را با مرغ و تخم‌مرغ تاخت بزنند. بورس ۲ درصد افت کرد.",
    "🗞️ خبر اقتصادی: در {country} کشف شد یک کارمند خزانه‌داری ۱۲ سال است بازنشسته شده ولی هنوز سرکار می‌آید چون کلید دارد.",
    "🗞️ خبر اقتصادی: شرکت دولتی {country} اعلام کرد امسال سود بی‌سابقه‌ای داشته، بعداً مشخص شد حسابدار صفر اضافی زده بود.",

    # 🔬 علمی عجیب
    "🗞️ خبر علمی: دانشمندان {country} ادعا کردند اختراعی کرده‌اند که آب را به نفت تبدیل می‌کند. جزئیات: «هنوز کار می‌کنیم رویش».",
    "🗞️ خبر علمی: مؤسسه تحقیقاتی {country} پنج سال روی این موضوع تحقیق کرد که «چرا گربه‌ها از آب می‌ترسند». نتیجه: نامشخص.",
    "🗞️ خبر علمی: دانشگاه ملی {country} اعلام کرد برنامه هسته‌ای‌شان را یک دانشجوی ترم دو طراحی کرده.",

    # 🪖 نظامی طنز
    "🗞️ خبر نظامی: ارتش {country} اعلام کرد جدیدترین تانکش را با آجر نما کرده تا «دشمن فکر کند ساختمان است».",
    "🗞️ خبر نظامی: رزمایش سالانه {country} به خاطر باران لغو شد. فرمانده گفت: «سربازها سرما می‌خورند».",
    "🗞️ خبر نظامی: نیروی هوایی {country} اعلام کرد پایلوت‌هایش را با بازی موبایل آموزش می‌دهد. «نتایج امیدوارکننده است».",
    "🗞️ خبر نظامی: زیردریایی {country} سه روز گم شد. بعداً معلوم شد خدمه اشتباهی وارد یک خلیج آرام شده و ماهیگیری می‌کردند.",

    # 🌦️ آب‌وهوا و طبیعت
    "🗞️ خبر آب‌وهوا: در {country} برف تابستانی باریده و دولت آن را «پیروزی دیپلماسی آب‌وهوایی» نامید.",
    "🗞️ خبر محیط‌زیست: {country} اعلام کرد برای مقابله با آلودگی هوا از این پس همه مردم باید نفس کمتر بکشند.",
    "🗞️ خبر محیط‌زیست: دولت {country} اعلام کرد درختان بیشتری خواهد کاشت، وقتی از آن‌ها پرسیدند کجا گفتند: «جای خوبی».",

    # ——— ۱۰۰ خبر جدید ———

    # 😂 طنز روزمره
    "🗞️ خبر داغ: نانوای محله مرکزی پایتخت {country} اعلام کرد نان‌هایش را دیگر نمی‌پزد چون «مردم قدر نمی‌دانند».",
    "🗞️ خبر شگفت‌انگیز: در {country} یک مرد ۶ ماه است با چراغ قرمز بحث می‌کند. تاکنون نتیجه نداده.",
    "🗞️ خبر فوری: راننده تاکسی در {country} مسیر فرودگاه را بلد نبود. مسافر خودش راند.",
    "🗞️ خبر عجیب: در {country} یک پسربچه ۹ ساله در مسابقه شطرنج وزیر اعظم را مات کرد. وزیر هنوز در شوک است.",
    "🗞️ خبر روز: دولت {country} برای صرفه‌جویی در برق اعلام کرد جلسات کابینه در تاریکی برگزار می‌شود.",
    "🗞️ خبر فوری: در {country} یک آسانسور ۳ روز است بین دو طبقه گیر کرده. سرنشینان کارت بازی می‌کنند.",
    "🗞️ خبر شگفت‌انگیز: رئیس اتحادیه کارگری {country} در اعتصاب علیه کارفرمایش شرکت کرد و بعد فهمید خودش کارفرماست.",
    "🗞️ خبر داغ: شهردار {country} برای باز کردن گره ترافیک شهر پیشنهاد داد همه ماشین‌ها همزمان پارک کنند.",
    "🗞️ خبر عجیب: در {country} یک مرد ادعا کرد پشه‌ای که زده بود سری باهوش‌تر از وزیر اقتصاد داشت. دادگاه در حال بررسی است.",
    "🗞️ خبر روز: کارمند اداره پست {country} نامه‌ای را که ۱۴ سال پیش گم کرده بود امروز از زیر میزش پیدا کرد. تحویل داد.",

    # 🏛️ سیاسی مسخره
    "🗞️ خبر سیاسی: نخست‌وزیر {country} در نشست سازمان ملل اشتباهی دکمه میکروفن کشور همسایه را زد و ۲۰ دقیقه صحبت کرد. هیچ‌کس چیزی نگفت.",
    "🗞️ خبر سیاسی: وزارت خارجه {country} نامه اعتراضی را به اشتباه برای خودشان فرستادند و پاسخ دادند.",
    "🗞️ خبر سیاسی: رئیس‌جمهور {country} در مصاحبه زنده فراموش کرد اسم کشور خودش را و یک دقیقه مکث کرد.",
    "🗞️ خبر سیاسی: پارلمان {country} پس از ۶ ساعت بحث تصویب کرد که جلسات بعدی کوتاه‌تر باشد. جلسه ۸ ساعت طول کشید.",
    "🗞️ خبر سیاسی: وزیر ارتباطات {country} برای اعلام قطعی اینترنت پیام صوتی فرستاد.",
    "🗞️ خبر سیاسی: {country} اعلام کرد سفارت جدیدش را در کوه‌های دورافتاده می‌سازد چون «آرامش بیشتری دارد».",
    "🗞️ خبر سیاسی: مشاور ارشد رئیس‌جمهور {country} استعفا داد چون صندلی دفترش ناراحت بود. درخواست قبول شد.",
    "🗞️ خبر سیاسی: دولت {country} اعلام کرد از این پس مالیات را فقط به صورت کالا قبول می‌کند. گاو و گوسفند هم قبول است.",
    "🗞️ خبر سیاسی: نماینده {country} در سازمان ملل به اشتباه له قطعنامه‌ای رأی داد که علیه کشورش بود. گفت «خواب بودم».",
    "🗞️ خبر سیاسی: وزیر بهداشت {country} در کنفرانس خبری سرفه کرد و گفت «نگران نباشید، من خودم دکترم». دکتر دندانپزشک است.",

    # 💰 اقتصادی خنده‌دار
    "🗞️ خبر اقتصادی: بورس {country} امروز ۳ درصد رشد کرد چون یکی از معامله‌گران اشتباه دکمه خرید را زد.",
    "🗞️ خبر اقتصادی: بانک مرکزی {country} اعلام کرد برای کنترل تورم از این پس قیمت‌ها را با مداد می‌نویسند تا راحت پاک شود.",
    "🗞️ خبر اقتصادی: شرکت نفتی {country} اعلام کرد چاه نفت جدیدی کشف کرده؛ بعداً مشخص شد چاه آب بوده.",
    "🗞️ خبر اقتصادی: وزیر اقتصاد {country} برای کاهش فقر پیشنهاد داد همه فقرا ثروتمند شوند. جزئیات اجرایی در دست بررسی است.",
    "🗞️ خبر اقتصادی: شرکت بزرگ {country} اعلام ورشکستگی کرد ولی مدیرعاملش همان روز ماشین جدید خرید.",
    "🗞️ خبر اقتصادی: در {country} کشف شد حسابدار ارشد خزانه‌داری ۸ سال است با حساب‌کتاب انگشتی کار می‌کند.",
    "🗞️ خبر اقتصادی: دولت {country} اعلام کرد بدهی خارجی‌اش را با شعر و داستان پرداخت خواهد کرد.",
    "🗞️ خبر اقتصادی: تحلیلگران پیش‌بینی کردند اقتصاد {country} رشد می‌کند. تحلیلگران ۱۲ سال پیش هم همین را گفته بودند.",
    "🗞️ خبر اقتصادی: گزارش جدید نشان می‌دهد نیمی از بودجه {country} صرف خرید کاغذ برای گزارش‌های مالی می‌شود.",
    "🗞️ خبر اقتصادی: بانک {country} اعلام کرد نرخ بهره را «حس می‌کند» نه محاسبه. کارشناسان متعجب‌اند.",

    # 🪖 نظامی خنده‌دار
    "🗞️ خبر نظامی: ارتش {country} در رزمایش سالانه‌اش فراموش کرد مهمات واقعی بیاورد. از صدای دهان استفاده کردند.",
    "🗞️ خبر نظامی: هواپیمای جنگنده {country} به خاطر کمبود سوخت روی جاده فرود آمد. راننده‌ها شاکی شدند.",
    "🗞️ خبر نظامی: ارتش {country} اعلام کرد قوی‌ترین سلاحش «روحیه سربازان» است. بودجه خرید سلاح صفر شد.",
    "🗞️ خبر نظامی: ناوگان دریایی {country} در دریاچه‌ای که به دریا راه ندارد مانور داد.",
    "🗞️ خبر نظامی: پهپاد جدید {country} در اولین پرواز آزمایشی به درخت خورد. درخت آسیب ندید.",
    "🗞️ خبر نظامی: سرباز {country} در دوره آموزشی از کلاس فرار کرد تا از دست آموزش فرار کردن در رزمایش فرار کند.",
    "🗞️ خبر نظامی: وزارت دفاع {country} اعلام کرد برای صرفه‌جویی تانک‌ها را با دوچرخه جایگزین می‌کند.",
    "🗞️ خبر نظامی: یگان ویژه {country} در عملیات شبانه به اشتباه وارد یک عروسی شد. تا صبح ماندند.",
    "🗞️ خبر نظامی: کشتی جنگی {country} در بندر به خاطر بدهی پارکینگ توقیف شد.",
    "🗞️ خبر نظامی: سربازان {country} در مانور زمستانی به خاطر سرما اعتصاب کردند.",

    # 🏅 ورزشی
    "🗞️ خبر ورزشی: تیم ملی {country} برای جام جهانی آماده می‌شود؛ مربی گفت «اگر گل نخوریم می‌بریم».",
    "🗞️ خبر ورزشی: قهرمان دو ماراتن {country} مسیر را اشتباه رفت و زودتر از بقیه به خط پایان رسید.",
    "🗞️ خبر ورزشی: فدراسیون شنا {country} اعلام کرد استخر ندارد ولی قهرمان جهانی خواهد شد.",
    "🗞️ خبر ورزشی: داور بازی {country} کارت قرمز را به خودش نشان داد و از زمین خارج شد.",
    "🗞️ خبر ورزشی: باشگاه فوتبال {country} بازیکن ستاره‌اش را با یک دوچرخه معاوضه کرد. بازیکن گفت قبول است.",
    "🗞️ خبر ورزشی: تیم بسکتبال {country} برای بلندتر کردن بازیکنانش آن‌ها را روی کفش‌های پاشنه‌بلند گذاشت.",
    "🗞️ خبر ورزشی: مربی ملی {country} در نیمه بازی خوابید. تیم ۳ بر صفر برد.",
    "🗞️ خبر ورزشی: در {country} مسابقه «سریع‌ترین خوردن چلوکباب» رسماً ورزش ملی شد.",
    "🗞️ خبر ورزشی: رکورددار پرش ارتفاع {country} در مسابقه از زیر میله رد شد. داوران گیج شدند.",
    "🗞️ خبر ورزشی: تیم ملی {country} برای بهبود نتایج، پیراهن‌هایشان را عوض کردند. نتیجه تغییر نکرد.",

    # 🔬 علمی و فناوری
    "🗞️ خبر علمی: دانشمندان {country} ادعا کردند ماده‌ای کشف کرده‌اند که به هیچ چیز شبیه نیست. عکسش را گم کرده‌اند.",
    "🗞️ خبر فناوری: وزارت فناوری {country} اعلام کرد اینترنت ملی را راه‌اندازی می‌کند که فقط در ساعات اداری کار می‌کند.",
    "🗞️ خبر علمی: پژوهشگران {country} ثابت کردند که خوابیدن باعث خواب‌آلودگی می‌شود. مقاله در مجله معتبر چاپ شد.",
    "🗞️ خبر فناوری: شرکت هوش مصنوعی {country} ربات جدیدی ساخت که فقط بلد است بگوید «نمی‌دانم».",
    "🗞️ خبر علمی: دانشگاه ملی {country} اعلام کرد ۱۵ سال روی اثبات این که آفتاب از شرق طلوع می‌کند تحقیق کرده. تأیید شد.",
    "🗞️ خبر فناوری: اپلیکیشن ملی {country} پس از ۳ سال توسعه منتشر شد. فقط روی یک گوشی کار می‌کند.",
    "🗞️ خبر علمی: آزمایشگاه {country} موشکی طراحی کرد که به هر جا بخواهند نمی‌رود ولی همیشه برمی‌گردد.",
    "🗞️ خبر فناوری: {country} اعلام کرد اولین ماهواره‌اش را پرتاب کرد. ماهواره هنوز پیدا نشده.",
    "🗞️ خبر علمی: محققان {country} داروی جدیدی ساختند که عوارض جانبی‌اش جالب‌تر از خود دارو است.",
    "🗞️ خبر فناوری: سایت دولتی {country} هک شد. هکر پیامی گذاشت: «رمز عبورتان را عوض کنید». توصیه رعایت نشد.",

    # 🌍 روابط بین‌الملل
    "🗞️ خبر دیپلماتیک: {country} به کشور همسایه اعتراض کرد که بادشان به سمت آن‌ها می‌وزد.",
    "🗞️ خبر دیپلماتیک: سفیر {country} در مذاکره مهم زبانش را گاز گرفت و نتوانست صحبت کند. مذاکره موفق بود.",
    "🗞️ خبر دیپلماتیک: {country} اعلام کرد با کشوری که وجود ندارد قرارداد همکاری امضا کرده.",
    "🗞️ خبر دیپلماتیک: هیئت دیپلماتیک {country} در سفر رسمی اشتباهی به کشور اشتباه رفت. میزبان گفت اشکالی ندارد.",
    "🗞️ خبر دیپلماتیک: {country} برای حل اختلاف مرزی پیشنهاد داد مرز را هر روز ۵۰ سانتی‌متر جابجا کنند.",

    # 🐾 حیوانات و طبیعت عجیب
    "🗞️ خبر عجیب: در {country} یک گربه ولگرد به مدت دو هفته روی صندلی وزیر نشست. بهره‌وری اداره ۴۰ درصد افزایش یافت.",
    "🗞️ خبر عجیب: ارتش {country} اعلام کرد از کبوتران نامه‌بر به عنوان پشتیبان ارتباطی استفاده می‌کند. کبوتران آموزش می‌بینند.",
    "🗞️ خبر عجیب: در {country} یک اسب فراری وارد کافه‌ای شد و یک فنجان قهوه خورد. صاحب کافه پول نگرفت.",
    "🗞️ خبر عجیب: پلیس {country} یک ببر فراری را با پیتزا به دام انداخت. روش رسمی شد.",
    "🗞️ خبر عجیب: در {country} یک طوطی آموزش‌دیده در جلسه دادگاه شهادت داد. قاضی گفت «معتبرترین شاهد تاکنون».",
    "🗞️ خبر عجیب: گله گوسفند {country} به اشتباه وارد ساختمان پارلمان شد. نمایندگان گفتند تفاوتی احساس نکردند.",
    "🗞️ خبر عجیب: یک خرس در {country} وارد سوپرمارکت شد و فقط عسل خرید. صادرانه پول داد.",

    # 🎭 فرهنگی و هنری
    "🗞️ خبر فرهنگی: فیلم جدید {country} در جشنواره جهانی جایزه گرفت. کارگردان گفت دوربین را اشتباه نگه داشته بود.",
    "🗞️ خبر فرهنگی: موزه ملی {country} اعلام کرد گران‌بهاترین اثرش را گم کرده. «احتمالاً جابجا شده».",
    "🗞️ خبر فرهنگی: نقاش مشهور {country} آخرین اثرش را تحویل داد؛ یک بوم سفید. خریداران صف کشیدند.",
    "🗞️ خبر فرهنگی: ارکستر ملی {country} در کنسرت مهم نت‌های اشتباه نواخت. تماشاگران گفتند بهتر بود.",
    "🗞️ خبر فرهنگی: رمان پرفروش امسال {country} درباره مردی است که تمام روز چیزی نمی‌کند. ۲ میلیون نسخه فروخت.",

    # 🏗️ ساخت‌وساز و شهری
    "🗞️ خبر شهری: پل جدید {country} افتتاح شد ولی به هیچ جا وصل نیست. مهندس گفت «فاز دوم».",
    "🗞️ خبر شهری: خیابان اصلی {country} ۱۲ بار در یک سال آسفالت شد. هنوز چاله دارد.",
    "🗞️ خبر شهری: برج جدید {country} به جای ۵۰ طبقه، ۵۱ طبقه شد. طبقه اضافه اتفاقی بود. نگه داشتند.",
    "🗞️ خبر شهری: شهرداری {country} برای حل مشکل پارکینگ اعلام کرد از این پس ماشین‌ها باید معلق باشند.",
    "🗞️ خبر شهری: فرودگاه جدید {country} افتتاح شد ولی جاده دسترسی هنوز ساخته نشده. «به زودی» گفتند.",

    # 😴 روزمره عجیب
    "🗞️ خبر داغ: در {country} یک مرد برای اعتراض به گرانی به مدت ۳ روز در سوپرمارکت نشست. صاحب مغازه چای آورد.",
    "🗞️ خبر داغ: زن {country} که ۱۵ سال دنبال شوهرش گشته بود فهمید او همسایه دیوار به دیواری‌شان است.",
    "🗞️ خبر داغ: در {country} کسی برای دریافت جایزه «وقت‌شناس‌ترین شهروند» دیر آمد.",
    "🗞️ خبر داغ: مردی در {country} ادعا کرد ۳۰ سال است بدون قهوه بیدار می‌شود. تحقیقات علمی آغاز شد.",
    "🗞️ خبر داغ: در {country} یک پیرزن ۹۰ ساله در مسابقه استارتاپ جوان اول شد. ایده‌اش: فروش چای خانگی.",
    "🗞️ خبر داغ: کودک ۴ ساله در {country} اشتباهی مالیات کل شهر را آنلاین پرداخت کرد. سیستم قبول کرد.",
    "🗞️ خبر داغ: در {country} یک راننده ۴۰ سال بدون گواهینامه رانندگی کرد. وقتی فهمیدند جریمه‌اش را بخشیدند چون «خوب بلد بود».",
    "🗞️ خبر داغ: فروشگاه بزرگ {country} اعلام کرد حراج ۹۰ درصدی دارد. همه جنس‌ها تمام شده بود.",
    "🗞️ خبر داغ: در {country} یک موبایل ۲۰ سال در گم‌وگور بود. پیدا شد، باتریش هنوز ۳ درصد داشت.",
    "🗞️ خبر داغ: رستوران معروف {country} رتبه یک جهانی گرفت. آشپزش گفت هنوز نمی‌داند چرا.",
]

async def broadcast_news(context):
    """ارسال یک خبر تصادفی به همه بازیکنان"""
    data = load_data()
    players = data.get("players", {})
    if not players:
        return

    # انتخاب یک کشور تصادفی از بازیکنان فعال
    active = [(uid, p) for uid, p in players.items() if p.get("country")]
    if not active:
        return

    target_uid, target_player = random.choice(active)
    country_name = target_player["country"]

    # انتخاب یک خبر تصادفی
    template = random.choice(NEWS_TEMPLATES)
    # فقط اسم کشور بدون ایموجی و پرچم برای داخل جمله
    country_clean = country_name.split(" ", 1)[-1] if " " in country_name else country_name
    news_text = template.replace("{country}", country_clean)

    full_msg = (
        f"📡 *خبرگزاری WW3*\n"
        f"{'─' * 30}\n"
        f"{news_text}\n"
        f"{'─' * 30}\n"
        f"🕐 {datetime.now().strftime('%H:%M')}"
    )

    # ارسال به همه بازیکنان
    for uid in players:
        try:
            await context.bot.send_message(uid, full_msg, parse_mode="Markdown")
        except:
            pass


# ──────────────────────────────────────────────
#  🕊️ پیمان صلح
# ──────────────────────────────────────────────

async def peace_menu(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!", show_alert=True); return

    # پیمان‌های فعال این بازیکن
    peace_treaties = data.get("peace_treaties", {})
    my_treaties = []
    for key, treaty in peace_treaties.items():
        uids = key.split("_")
        if uid in uids:
            partner_uid = uids[1] if uids[0] == uid else uids[0]
            partner = data["players"].get(partner_uid, {})
            cname = partner.get("country", "؟")
            expires_at = treaty.get("expires_at", "")
            try:
                exp_str = datetime.fromisoformat(expires_at).strftime("%H:%M")
                my_treaties.append(f"{cname} (تا ساعت {exp_str})")
            except:
                my_treaties.append(cname)

    text = "🕊️ *پیمان صلح*\n\n"
    if my_treaties:
        text += "📜 *پیمان‌های فعال شما (مدت: ۱ روز):*\n"
        for c in my_treaties:
            text += f"  ✅ {c}\n"
        text += "\n"
    else:
        text += "پیمان صلح فعالی ندارید.\n\n"
    text += "با کشور مورد نظر پیمان صلح ببندید:"

    # لیست کشورهای دیگه (به جز خودش و کسایی که قبلاً پیمان دارن)
    others = []
    for cid, p in data["players"].items():
        if cid == uid:
            continue
        key1 = f"{uid}_{cid}"
        key2 = f"{cid}_{uid}"
        if key1 in peace_treaties or key2 in peace_treaties:
            continue
        others.append((cid, p["country"]))

    rows = [[btn(cname, f"peace_req_{cid}")] for cid, cname in others]
    rows.append([BACK])

    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb(*rows))


async def peace_request(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    target_uid = q.data.replace("peace_req_", "", 1)
    data = load_data()
    player = get_player(data, uid)
    target = data["players"].get(target_uid)
    if not player or not target:
        await q.answer("خطا!", show_alert=True); return

    # چک پیمان تکراری
    key1 = f"{uid}_{target_uid}"
    key2 = f"{target_uid}_{uid}"
    if key1 in data.get("peace_treaties", {}) or key2 in data.get("peace_treaties", {}):
        await q.answer("قبلاً با این کشور پیمان صلح دارید!", show_alert=True); return

    # چک درخواست تکراری
    if data.get("pending_peace", {}).get(uid):
        await q.answer("درخواست صلح در انتظار دارید!", show_alert=True); return

    await q.edit_message_text(
        f"🕊️ *ارسال پیمان صلح*\n\n"
        f"کشور مقصد: *{target['country']}*\n\n"
        f"⚠️ در صورت تأیید، هیچ‌کدام از دو طرف نمی‌توانند به دیگری اعلان جنگ کنند.\n\n"
        f"آیا درخواست ارسال شود؟",
        parse_mode="Markdown",
        reply_markup=kb(
            [btn("✅ بله، ارسال شود", f"peace_confirm_{target_uid}")],
            [btn("❌ لغو", "peace_menu")]
        )
    )


async def peace_confirm(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    target_uid = q.data.replace("peace_confirm_", "", 1)
    data = load_data()
    player = get_player(data, uid)
    target = data["players"].get(target_uid)
    if not player or not target:
        await q.answer("خطا!", show_alert=True); return

    # ذخیره درخواست pending
    data.setdefault("pending_peace", {})[uid] = {
        "requester_uid": uid,
        "target_uid": target_uid,
        "requester_country": player["country"],
        "target_country": target["country"],
    }
    save_data(data)

    await q.edit_message_text(
        f"📨 درخواست پیمان صلح برای *{target['country']}* ارسال شد.\nمنتظر پاسخ بمانید...",
        parse_mode="Markdown",
        reply_markup=kb([BACK])
    )

    try:
        await context.bot.send_message(
            target_uid,
            f"🕊️ *درخواست پیمان صلح*\n\n"
            f"کشور *{player['country']}* پیشنهاد پیمان صلح داده است.\n\n"
            f"در صورت تأیید، هیچ‌کدام نمی‌توانید به دیگری اعلان جنگ کنید.",
            parse_mode="Markdown",
            reply_markup=kb(
                [btn("✅ تأیید پیمان", f"peace_accept_{uid}")],
                [btn("❌ رد", f"peace_reject_{uid}")]
            )
        )
    except:
        data.get("pending_peace", {}).pop(uid, None)
        save_data(data)
        await context.bot.send_message(uid, "❌ خطا در ارسال پیام. دوباره تلاش کنید.")


async def peace_accept(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)  # این target هست
    requester_uid = q.data.replace("peace_accept_", "", 1)
    data = load_data()

    pending = data.get("pending_peace", {}).get(requester_uid)
    if not pending or pending["target_uid"] != uid:
        await q.edit_message_text("⚠️ درخواست منقضی شده!", reply_markup=kb([BACK])
        ); return

    requester = data["players"].get(requester_uid, {})
    target = data["players"].get(uid, {})

    # ثبت پیمان صلح
    treaty_key = f"{requester_uid}_{uid}"
    expires_at = (datetime.now().replace(hour=23, minute=59, second=59) ).isoformat()
    data.setdefault("peace_treaties", {})[treaty_key] = {
        "country1": requester.get("country", "؟"),
        "country2": target.get("country", "؟"),
        "date": datetime.now().isoformat(),
        "expires_at": expires_at,
    }
    data.get("pending_peace", {}).pop(requester_uid, None)
    save_data(data)

    treaty_text = (
        f"📜 *پیمان‌نامه صلح*\n"
        f"{'═' * 28}\n\n"
        f"🕊️ این پیمان میان:\n\n"
        f"  🏳️ *{requester.get('country','؟')}*\n"
        f"  🏳️ *{target.get('country','؟')}*\n\n"
        f"منعقد گردید.\n\n"
        f"📌 *مفاد پیمان:*\n"
        f"• هیچ‌یک از طرفین حق اعلان جنگ به دیگری را ندارد.\n"
        f"• این پیمان به مدت *۱ روز* معتبر است و پس از آن به‌طور خودکار منقضی می‌شود.\n\n"
        f"📅 تاریخ انعقاد: {datetime.now().strftime('%Y/%m/%d')}\n"
        f"{'═' * 28}"
    )

    await q.edit_message_text(treaty_text, parse_mode="Markdown",
                               reply_markup=kb([btn("🏠 منو", "resume")]))
    try:
        await context.bot.send_message(requester_uid, treaty_text,
                                        parse_mode="Markdown",
                                        reply_markup=kb([btn("🏠 منو", "resume")]))
    except:
        pass


async def peace_reject(update, context):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    requester_uid = q.data.replace("peace_reject_", "", 1)
    data = load_data()

    pending = data.get("pending_peace", {}).get(requester_uid, {})
    requester_country = data["players"].get(requester_uid, {}).get("country", "؟")
    my_country = data["players"].get(uid, {}).get("country", "؟")

    data.get("pending_peace", {}).pop(requester_uid, None)
    save_data(data)

    await q.edit_message_text(
        f"❌ پیمان صلح رد شد.",
        reply_markup=kb([btn("🏠 منو", "resume")])
    )
    try:
        await context.bot.send_message(
            requester_uid,
            f"❌ *{my_country}* پیمان صلح را رد کرد.",
            parse_mode="Markdown",
            reply_markup=kb([btn("🏠 منو", "resume")])
        )
    except:
        pass


def migrate_hack_rooms():
    """مهاجرت داده قدیمی: hack_room عددی → hack_rooms لیست"""
    data = load_data()
    changed = False
    for uid, player in data["players"].items():
        b = player.get("buildings", {})
        # اگه hack_rooms لیست ندارن ولی hack_room عددی دارن
        if "hack_rooms" not in b and b.get("hack_room", 0):
            old_val = b["hack_room"]
            if old_val == 2:
                b["hack_rooms"] = ["luxury"]
            elif old_val == 1:
                b["hack_rooms"] = ["normal"]
            else:
                b["hack_rooms"] = ["normal"] * int(old_val)
            player["buildings"] = b
            data["players"][uid] = player
            changed = True
    if changed:
        save_data(data)
        print(f"✅ Migration: hack_rooms updated for players")


# ──────────────────────────────────────────────
#  🏳️ آتش‌بس
# ──────────────────────────────────────────────
async def ceasefire_request(update, context):
    """یک طرف پیشنهاد آتش‌بس می‌دهد"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    war_id = q.data.replace("ceasefire_req_", "", 1)
    data = load_data()
    war = data.get("active_wars", {}).get(war_id)
    if not war:
        await q.answer("⚠️ این جنگ دیگر فعال نیست!", show_alert=True); return
    # ثبت رأی
    war.setdefault("ceasefire_votes", {})[uid] = True
    data["active_wars"][war_id] = war
    # طرف مقابل
    attacker_uid = war["attacker_uid"]
    target_uid = war["target_uid"]
    other_uid = target_uid if uid == attacker_uid else attacker_uid
    player = get_player(data, uid)
    other = data["players"].get(other_uid, {})
    my_country = player["country"] if player else "؟"
    # اگر هر دو رأی دادن → جنگ پایان
    if attacker_uid in war["ceasefire_votes"] and target_uid in war["ceasefire_votes"]:
        # پایان جنگ - برنده را سازمان ملل تعیین می‌کند
        active_wars = data.get("active_wars", {})
        active_wars.pop(war_id, None)
        data["active_wars"] = active_wars
        save_data(data)
        end_msg = (
            f"🏳️ *آتش‌بس!*\n\n"
            f"⚔️ *{war['attacker_country']}* vs *{war['target_country']}*\n\n"
            f"هر دو طرف آتش‌بس را پذیرفتند.\n"
            f"جنگ پایان یافت — سازمان ملل برنده را تعیین می‌کند."
        )
        for nuid in [attacker_uid, target_uid]:
            try: await context.bot.send_message(nuid, end_msg, parse_mode="Markdown")
            except: pass
        # اطلاع به سازمان ملل با دکمه‌های اعلام برنده
        for admin_id in data.get("un_admins", []):
            try:
                await context.bot.send_message(
                    admin_id,
                    f"🏳️ *آتش‌بس پذیرفته شد!*\n\n"
                    f"⚔️ {war['attacker_country']} vs {war['target_country']}\n\n"
                    f"برنده جنگ کیست؟",
                    parse_mode="Markdown",
                    reply_markup=kb(
                        [btn(f"🏆 {war['attacker_country']}", f"war_winner_{war_id}_atk")],
                        [btn(f"🏆 {war['target_country']}", f"war_winner_{war_id}_def")],
                        [btn("🤝 مساوی / بدون برنده", f"war_winner_{war_id}_draw")]
                    )
                )
            except: pass
        await q.edit_message_text(end_msg, parse_mode="Markdown")
        return
    save_data(data)
    # اطلاع به طرف مقابل
    await q.edit_message_text(
        f"🏳️ پیشنهاد آتش‌بس شما ارسال شد.\nمنتظر پاسخ *{other.get('country','طرف مقابل')}* باشید.",
        parse_mode="Markdown"
    )
    try:
        await context.bot.send_message(
            other_uid,
            f"🏳️ *{my_country}* پیشنهاد آتش‌بس داده است!\n\nآیا آتش‌بس را می‌پذیرید؟",
            parse_mode="Markdown",
            reply_markup=kb(
                [btn("✅ بله، آتش‌بس", f"ceasefire_req_{war_id}")],
                [btn("❌ خیر، جنگ ادامه دارد", f"ceasefire_no_{war_id}")]
            )
        )
    except: pass


async def ceasefire_reject(update, context):
    """رد پیشنهاد آتش‌بس"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    war_id = q.data.replace("ceasefire_no_", "", 1)
    data = load_data()
    war = data.get("active_wars", {}).get(war_id)
    if not war:
        await q.answer("جنگ فعال نیست!", show_alert=True); return
    # پاک کردن رأی طرف مقابل اگه داده بود
    attacker_uid = war["attacker_uid"]
    target_uid = war["target_uid"]
    other_uid = target_uid if uid == attacker_uid else attacker_uid
    war.get("ceasefire_votes", {}).pop(other_uid, None)
    data["active_wars"][war_id] = war
    save_data(data)
    player = get_player(data, uid)
    my_country = player["country"] if player else "؟"
    await q.edit_message_text(f"❌ *{my_country}* آتش‌بس را رد کرد. جنگ ادامه دارد!", parse_mode="Markdown")
    try:
        await context.bot.send_message(
            other_uid,
            f"❌ *{my_country}* پیشنهاد آتش‌بس را رد کرد. جنگ ادامه دارد!",
            parse_mode="Markdown",
            reply_markup=kb([btn("🏳️ پیشنهاد آتش‌بس مجدد", f"ceasefire_req_{war_id}")])
        )
    except: pass


async def war_winner_select(update, context):
    """سازمان ملل برنده جنگ را تعیین می‌کند"""
    q = update.callback_query
    await q.answer()
    raw = q.data.replace("war_winner_", "", 1)
    # فرمت: war_id_atk یا war_id_def یا war_id_draw
    last_part = raw.rsplit("_", 1)
    war_id = last_part[0]
    result_type = last_part[1]  # atk / def / draw
    data = load_data()
    war = {}
    # پیدا کردن در تاریخچه
    for entry in data.get("war_history", []):
        if entry["war_id"] == war_id and entry["result"] == "نامشخص":
            war = data.get("active_wars", {}).get(war_id, {})
            attacker_c = entry.get("attacker", war.get("attacker_country", "؟"))
            defender_c = entry.get("defender", war.get("target_country", "؟"))
            if result_type == "atk":
                entry["result"] = f"برنده: {attacker_c}"
                entry["winner"] = attacker_c
                winner_txt = attacker_c
            elif result_type == "def":
                entry["result"] = f"برنده: {defender_c}"
                entry["winner"] = defender_c
                winner_txt = defender_c
            else:
                entry["result"] = "مساوی"
                entry["winner"] = "مساوی"
                winner_txt = "مساوی"
            break
    else:
        attacker_c = "؟"; defender_c = "؟"; winner_txt = "؟"
        war = {}

    # برگردوندن تجهیزات به هر دو طرف
    attacker_weapons = war.get("attacker_weapons", {})
    defender_weapons = war.get("defender_weapons", {})
    attacker_uid_w = war.get("attacker_uid")
    defender_uid_w = war.get("target_uid")
    returned_lines = []

    if attacker_uid_w and attacker_uid_w in data.get("players", {}):
        ap = data["players"][attacker_uid_w]
        atk_fighters = attacker_weapons.get("fighters", 0)
        if atk_fighters:
            ap["military"]["fighters"] = ap["military"].get("fighters", 0) + atk_fighters
        data["players"][attacker_uid_w] = ap
        if atk_fighters:
            returned_lines.append(f"↩️ تجهیزات {attacker_c} برگشت داده شد")

    if defender_uid_w and defender_uid_w in data.get("players", {}):
        dp = data["players"][defender_uid_w]
        def_fighters = defender_weapons.get("fighters", 0)
        if def_fighters:
            dp["military"]["fighters"] = dp["military"].get("fighters", 0) + def_fighters
        data["players"][defender_uid_w] = dp
        if def_fighters:
            returned_lines.append(f"↩️ تجهیزات {defender_c} برگشت داده شد")

    # پاک کردن از active_wars
    data.get("active_wars", {}).pop(war_id, None)
    save_data(data)
    returned_txt = ("\n" + "\n".join(returned_lines)) if returned_lines else ""
    await q.edit_message_text(
        f"✅ *نتیجه جنگ ثبت شد!*\n\n"
        f"⚔️ {attacker_c} vs {defender_c}\n"
        f"🏆 نتیجه: *{winner_txt}*{returned_txt}",
        parse_mode="Markdown"
    )
    # اطلاع به طرفین
    parts = war_id.split("x")
    atk_weapons_str = f"  ✈️ جنگنده: +{attacker_weapons.get('fighters',0):,}" if attacker_weapons.get("fighters") else ""
    def_weapons_str = f"  ✈️ جنگنده: +{defender_weapons.get('fighters',0):,}" if defender_weapons.get("fighters") else ""

    for nuid in parts:
        is_atk = (nuid == attacker_uid_w)
        w_str = atk_weapons_str if is_atk else def_weapons_str
        ret_msg = f"\n\n↩️ *تجهیزات برگشت داده شد:*\n{w_str}" if w_str else ""
        try:
            await context.bot.send_message(
                nuid,
                f"📜 *نتیجه جنگ اعلام شد!*\n\n⚔️ {attacker_c} vs {defender_c}\n🏆 نتیجه: *{winner_txt}*{ret_msg}",
                parse_mode="Markdown"
            )
        except: pass


async def war_history_menu(update, context):
    """نمایش تاریخچه جنگ‌ها"""
    q = update.callback_query
    await q.answer()
    data = load_data()
    history = data.get("war_history", [])
    if not history:
        await q.edit_message_text("📜 تاریخچه جنگی وجود ندارد!", reply_markup=kb([BACK])); return
    text = "📜 *تاریخچه جنگ‌ها*\n\n"
    for i, entry in enumerate(reversed(history[-20:]), 1):  # آخرین ۲۰ جنگ
        result = entry.get("result", "نامشخص")
        text += (
            f"{i}. ⚔️ *{entry.get('attacker','؟')}* vs *{entry.get('defender','؟')}*\n"
            f"   📅 {entry.get('date','؟')} | 🏆 {result}\n\n"
        )
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb([BACK]))


# ──────────────────────────────────────────────
#  🛰️ ماهواره - جاسوسی نظامی
# ──────────────────────────────────────────────
async def satellite_spy_menu(update, context):
    """انتخاب کشور هدف برای جاسوسی ماهواره‌ای"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    data = load_data()
    player = get_player(data, uid)
    if not player:
        await q.answer("خطا!", show_alert=True); return
    if not player["buildings"].get("satellite"):
        await q.answer("❌ ماهواره ندارید!", show_alert=True); return
    if player.get("satellite_used_today", 0) >= 2:
        await q.edit_message_text(
            "🛰️ *ماهواره*\n\n⏳ امروز ۲ بار استفاده کردید.\nفردا دوباره در دسترس است.",
            parse_mode="Markdown", reply_markup=kb([BACK])
        ); return
    # لیست کشورهای دیگه
    others = [(cid, p["country"]) for cid, p in data["players"].items() if cid != uid]
    if not others:
        await q.edit_message_text("⚠️ کشور دیگری فعال نیست!", reply_markup=kb([BACK])); return
    rows = [[btn(cname, f"satspy_{cid}")] for cid, cname in others]
    rows.append([BACK])
    await q.edit_message_text(
        "🛰️ *ماهواره نظامی*\n\nکشور هدف را برای جاسوسی انتخاب کنید:\n⚠️ بدون اطلاع آن‌ها!",
        parse_mode="Markdown", reply_markup=kb(*rows)
    )


async def satellite_spy_result(update, context):
    """نمایش تجهیزات نظامی کشور هدف"""
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    target_uid = q.data.replace("satspy_", "", 1)
    data = load_data()
    player = get_player(data, uid)
    target = data["players"].get(target_uid)
    if not player or not target:
        await q.answer("خطا!", show_alert=True); return
    if not player["buildings"].get("satellite"):
        await q.answer("❌ ماهواره ندارید!", show_alert=True); return
    if player.get("satellite_used_today", 0) >= 2:
        await q.answer("⏳ امروز ۲ بار استفاده کردید!", show_alert=True); return
    # افزایش شمارنده استفاده امروز
    player["satellite_used_today"] = player.get("satellite_used_today", 0) + 1
    save_player(data, uid, player)
    m = target["military"]
    target_cname = target["country"]
    text = (
        f"🛰️ *اطلاعات نظامی {target_cname}*\n"
        f"_(اسکن ماهواره‌ای - محرمانه)_\n\n"
        f"👥 سرباز: {m.get('soldiers',0):,}\n"
        f"🔫 اسلحه: {m.get('rifles',0):,}\n"
        f"⚙️ تانک: {m.get('tanks',0):,}\n"
        f"✈️ جنگنده: {m.get('fighters',0):,}\n"
        f"💣 بمب‌افکن: {m.get('bombers',0):,}\n"
        f"🚁 هلیکوپتر: {m.get('helicopters',0):,}\n"
        f"🚢 کشتی جنگی: {m.get('warships',0):,}\n"
        f"🛳️ ناو هواپیمابر: {m.get('aircraft_carriers',0):,}\n"
        f"🤿 زیردریایی: {m.get('submarines',0):,}\n"
        f"🚀 موشک کروز: {m.get('missiles_cruise',0):,}\n"
        f"☠️ موشک بالستیک: {m.get('missiles_ballistic',0):,}\n"
        f"💥 موشک ویژه: {m.get('missiles_bunker',0):,}\n"
        f"🤖 پهپاد تخریبی: {m.get('drones_attack',0):,}\n"
        f"📡 پهپاد شناسایی: {m.get('drones_recon',0):,}\n"
        f"📻 پهپاد الکترونیک: {m.get('drones_ewarf',0):,}\n"
        f"💀 پهپاد ویژه: {m.get('drones_mother',0):,}\n"
        f"🛡️ پدافند: {m.get('air_defense',0):,}"
    )
    await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb([BACK]))


def main():
    migrate_hack_rooms()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    static = [
        ("help", help_text), ("choose_group", choose_group), ("resume", resume),
        ("back_main", back_main), ("back_start", back_start), ("un_menu_back", un_menu_back),
        ("eco_menu", eco_menu), ("mil_menu", mil_menu), ("assets", assets_menu),
        ("self_mil_subtract", self_mil_subtract),
        ("transfer_menu", transfer_menu), ("transfer_money", transfer_money_countries),
        ("transfer_weapons", transfer_weapons_countries), ("trade_menu", trade_menu),
        ("trade_sell", trade_sell), ("trade_select_target", trade_select_target),
        ("trade_send", trade_select_target),
        ("tw_select_target", transfer_weapon_target),
        ("un_wars", un_wars), ("war_history", war_history_menu), ("satellite_spy", satellite_spy_menu),
        ("attack_menu", attack_menu), ("cyber_menu", cyber_menu),
        ("submitatk", submit_attack), ("ready_missiles", ready_missiles_menu),
        ("ready_drones", ready_drones_menu), ("confirm_buy", confirm_buy),
        ("confirm_mil_buy", confirm_mil_buy), ("treasury", treasury_menu),
        ("food_factory_menu", food_factory_menu),
        ("loan_menu", loan_menu), ("loan_confirm", loan_confirm), ("loan_pay", loan_pay),
        ("propaganda_menu", propaganda_menu),
        ("gift_confirm", gift_confirm),
        ("negotiation_menu", negotiation_menu),
        ("negotiation_end", negotiation_end),
        ("neg_accept", negotiation_accept),
        ("neg_reject", negotiation_reject),
        ("switch_alliance", switch_alliance),
        ("create_alliance_menu", create_alliance_menu),
        ("dissolve_alliance", dissolve_alliance),
        ("alliance_to_NATO", alliance_req_confirm),
        ("alliance_to_BRICS", alliance_req_confirm),
        ("alliance_to_CUSTOM", alliance_req_confirm),
        ("stock_market", stock_market),
        ("stock_buy_menu", stock_buy_menu),
        ("stock_sell_menu", stock_sell_menu),
        ("peace_menu", peace_menu),
        ("alliance_req_confirm", alliance_req_confirm),
        ("build_nuke", build_nuke), ("confirm_nuke", confirm_nuke),
        ("launch_nuclear", launch_nuclear), ("country_info", show_country_info),
        ("un_players", un_players), ("un_all", un_all_countries),
        ("msg_un", msg_un), ("un_gift_menu", un_gift_menu),
        ("un_reset_prompt", lambda u,c: u.callback_query.answer("برای ریست کد 194545 را ارسال کنید.", show_alert=True)),
    ]
    for pattern, handler in static:
        app.add_handler(CallbackQueryHandler(handler, pattern=f"^{pattern}$"))

    app.add_handler(CallbackQueryHandler(buy_food_factory,        pattern=r"^buy_food_"))
    app.add_handler(CallbackQueryHandler(un_set_satisfaction,     pattern=r"^unsat_"))
    app.add_handler(CallbackQueryHandler(loan_select_installments,pattern=r"^loaninst_"))
    app.add_handler(CallbackQueryHandler(gift_select,             pattern=r"^giftsel_"))
    app.add_handler(CallbackQueryHandler(gift_confirm,            pattern=r"^gift_confirm$"))
    app.add_handler(CallbackQueryHandler(negotiation_request,     pattern=r"^neg_req_"))
    app.add_handler(CallbackQueryHandler(alliance_approve,        pattern=r"^alliance_approve_"))
    app.add_handler(CallbackQueryHandler(alliance_reject,         pattern=r"^alliance_reject_"))
    app.add_handler(CallbackQueryHandler(naval_factory_type,      pattern=r"^nf_"))
    app.add_handler(CallbackQueryHandler(propaganda_do,           pattern=r"^prop_target_"))

    # FIX: pattern انتخاب کشور - hash هست نه index عددی
    app.add_handler(CallbackQueryHandler(choose_country,         pattern=r"^group_"))
    app.add_handler(CallbackQueryHandler(select_country,         pattern=r"^select_[a-f0-9]+$"))  # FIX: hex hash
    app.add_handler(CallbackQueryHandler(buy_building,           pattern=r"^buy_(?!rm_|rd_)"))
    app.add_handler(CallbackQueryHandler(buy_ready_missile,      pattern=r"^buyrm_"))
    app.add_handler(CallbackQueryHandler(buy_ready_drone,        pattern=r"^buyrd_"))
    app.add_handler(CallbackQueryHandler(mil_buy,                pattern=r"^mil_buy_"))
    app.add_handler(CallbackQueryHandler(missile_factory_type,   pattern=r"^mf_"))
    app.add_handler(CallbackQueryHandler(air_factory_type,       pattern=r"^af_"))
    app.add_handler(CallbackQueryHandler(hack_type,              pattern=r"^hack_"))
    app.add_handler(CallbackQueryHandler(attack_select_country,  pattern=r"^atk\d+$"))
    app.add_handler(CallbackQueryHandler(attack_weapon_add,      pattern=r"^aw(?!ait)"))
    app.add_handler(CallbackQueryHandler(transfer_money_select,  pattern=r"^tm_"))
    app.add_handler(CallbackQueryHandler(transfer_weapon_add,    pattern=r"^twtype_"))     # FIX: هندلر انتقال تسلیحات
    app.add_handler(CallbackQueryHandler(transfer_weapon_confirm,pattern=r"^twdest_"))     # FIX: هندلر مقصد انتقال تسلیحات
    app.add_handler(CallbackQueryHandler(trade_add_item,         pattern=r"^tradewep_"))
    app.add_handler(CallbackQueryHandler(trade_to_country,       pattern=r"^tradeto_"))
    app.add_handler(CallbackQueryHandler(trade_accept,           pattern=r"^tradeacc_"))
    app.add_handler(CallbackQueryHandler(trade_reject,           pattern=r"^traderej_"))
    app.add_handler(CallbackQueryHandler(cyber_target_select,    pattern=r"^cybtgt"))
    app.add_handler(CallbackQueryHandler(cyber_do_attack,        pattern=r"^cybdo_"))
    app.add_handler(CallbackQueryHandler(un_view_player,         pattern=r"^unview_"))
    app.add_handler(CallbackQueryHandler(un_add_money,           pattern=r"^unadd_"))
    app.add_handler(CallbackQueryHandler(un_remove_money,        pattern=r"^unsub_"))
    app.add_handler(CallbackQueryHandler(un_level,               pattern=r"^unlevel_"))
    app.add_handler(CallbackQueryHandler(un_set_level,           pattern=r"^unsetlvl_"))
    app.add_handler(CallbackQueryHandler(un_nuclear_approve,     pattern=r"^unnuc_"))
    app.add_handler(CallbackQueryHandler(un_delete_player,       pattern=r"^undel_"))
    app.add_handler(CallbackQueryHandler(un_mil_subtract,        pattern=r"^unmilsub_"))
    app.add_handler(CallbackQueryHandler(un_mil_subtract_type,   pattern=r"^unmiltype_"))
    app.add_handler(CallbackQueryHandler(un_eco_subtract,        pattern=r"^unecosub_"))
    app.add_handler(CallbackQueryHandler(un_eco_subtract_type,   pattern=r"^unecotype_"))
    app.add_handler(CallbackQueryHandler(self_mil_subtract_type, pattern=r"^selfmiltype_"))
    app.add_handler(CallbackQueryHandler(un_approve_war,         pattern=r"^aprwar"))
    app.add_handler(CallbackQueryHandler(un_reject_war,          pattern=r"^rejwar"))
    app.add_handler(CallbackQueryHandler(ceasefire_request,      pattern=r"^ceasefire_req_"))
    app.add_handler(CallbackQueryHandler(ceasefire_reject,       pattern=r"^ceasefire_no_"))
    app.add_handler(CallbackQueryHandler(war_winner_select,      pattern=r"^war_winner_"))
    app.add_handler(CallbackQueryHandler(war_history_menu,       pattern=r"^war_history$"))
    app.add_handler(CallbackQueryHandler(satellite_spy_menu,      pattern=r"^satellite_spy$"))
    app.add_handler(CallbackQueryHandler(satellite_spy_result,    pattern=r"^satspy_"))
    app.add_handler(CallbackQueryHandler(peace_request,          pattern=r"^peace_req_"))
    app.add_handler(CallbackQueryHandler(peace_confirm,          pattern=r"^peace_confirm_"))
    app.add_handler(CallbackQueryHandler(peace_accept,           pattern=r"^peace_accept_"))
    app.add_handler(CallbackQueryHandler(peace_reject,           pattern=r"^peace_reject_"))
    app.add_handler(CallbackQueryHandler(stock_view_country,     pattern=r"^stock_view_"))
    app.add_handler(CallbackQueryHandler(stock_buy_action,       pattern=r"^stock_buy_[a-f0-9]+_\d+$"))
    app.add_handler(CallbackQueryHandler(stock_sell_select,      pattern=r"^stock_sell_select_"))
    app.add_handler(CommandHandler("daily", manual_daily))
    app.add_handler(CommandHandler("news", manual_news))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    app.job_queue.run_daily(daily_income, time=dtime(hour=20, minute=30))
    app.job_queue.run_repeating(broadcast_news, interval=3600, first=300)  # هر ۱ ساعت، اول بار بعد از ۵ دقیقه

    print("🌍 WW3 CLUB Bot started!")
    app.run_polling()

# دستور واریز دستی حقوق
async def manual_daily(update, context):
    await daily_income(context)
    await update.message.reply_text("✅ حقوق همه بازیکنان واریز شد!")
    
async def manual_news(update, context):
    await broadcast_news(context)
    await update.message.reply_text("📡 خبر ارسال شد!")

if __name__ == "__main__":
    main()
