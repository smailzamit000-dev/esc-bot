import os
import json
import time
import schedule
import requests
from scraper import fetch_latest_opportunities

TELEGRAM_BOT_TOKEN = "8255301755:AAEdMdhP1W4_IuiU9uo6PusTxq-VJMsHxZ4"
TELEGRAM_CHAT_ID = "6920635281"

HISTORY_FILE = "sent_opportunities.json"

def load_sent_opportunities():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_sent_opportunity(link):
    sent = load_sent_opportunities()
    if link not in sent:
        sent.append(link)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(sent, f, ensure_ascii=False, indent=4)

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        print("Telegram API Response:", data)
        return data.get("ok", False)
    except Exception as e:
        print(f"[!] خطأ في إرسال الرسالة عبر تيليجرام: {e}")
        return False

def job():
    print("\n🚀 جاري فحص المنصة للبحث عن فرص جديدة تدعم المغرب...")
    opportunities = fetch_latest_opportunities()
    sent_links = load_sent_opportunities()
    
    new_found = 0
    for res in opportunities:
        link = res["link"]
        title = res["title"]
        
        if link not in sent_links and "🔍" not in title:
            new_found += 1
            msg = f"🔥 فرصة تطوعية جديدة عبر ESC!\n\n📌 العنوان: {title}\n\n🔗 الرابط المباشر: {link}"
            
            success = send_telegram_message(msg)
            if success:
                save_sent_opportunity(link)
                print(f"تم إرسال وحفظ الفرصة بنجاح: {title}")
            else:
                print(f"❌ فشل إرسال الفرصة: {title}")
            
    if new_found == 0:
        print("📭 لا توجد فرص جديدة مطابقة حالياً.")
    else:
        print(f"✅ تمت معالجة وإرسال {new_found} فرصة جديدة!")

if __name__ == "__main__":
    print("🤖 البوت يعمل الآن بشكل تلقائي في الخلفية...")
    
    job()
    
    schedule.every(2).hours.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)