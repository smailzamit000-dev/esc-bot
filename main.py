from scraper import fetch_latest_opportunities
from telegram_bot import send_telegram_message

def run():
    print("🔍 جاري البحث عن أحدث فرص ESC الأوروبية...")
    opportunities = fetch_latest_opportunities()
    
    if opportunities:
        for opp in opportunities:
            # تنسيق رسالة تليجرام
            msg = (
                f"🇪🇺 <b>فرصة جديدة في ESC!</b>\n\n"
                f"📝 <b>العنوان:</b> {opp['title']}\n\n"
                f"🔗 <b>رابط التقديم والتفاصيل:</b>\n{opp['link']}"
            )
            send_telegram_message(msg)
        print("✅ تم إرسال جميع الفرص إلى تليجرام بنجاح!")
    else:
        print("ℹ️ لم يتم العثور على تحديثات جديدة حالياً.")

if __name__ == "__main__":
    run()