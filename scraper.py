from playwright.sync_api import sync_playwright

def fetch_latest_opportunities():
    print("⏳ جاري جفل أحدث فرص ESC والتحقق الصارم جداً من وجود شرط (المغرب / Morocco)...")
    opportunities = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                locale="en-US",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()

            # الانتقال لصفحة الفرص الرسمية
            page.goto("https://youth.europa.eu/go-abroad/volunteering/opportunities_en", wait_until="networkidle", timeout=60000)
            page.mouse.wheel(0, 1000)
            page.wait_for_timeout(5000)

            # استخراج روابط الفرص الأولية من القائمة
            links_data = page.evaluate("""
                () => {
                    const results = [];
                    const links = Array.from(document.querySelectorAll('a[href*="/solidarity/opportunity/"]'));
                    for (const a of links) {
                        const href = a.getAttribute('href') || a.href || '';
                        const card = a.closest('article') || a.closest('.ecl-card') || a.parentElement.parentElement;
                        let title = "";
                        if (card) {
                            const titleEl = card.querySelector('h2, h3, h4, .ecl-card__title, [class*="title"]');
                            if (titleEl) title = titleEl.innerText.trim();
                        }
                        if (!title || title === "Read more") {
                            title = a.innerText.trim();
                        }
                        if (href && title && title !== "Read more") {
                            results.push({ href, title });
                        }
                    }
                    return results;
                }
            """)

            seen_links = set()
            
            # فحص كل فرصة للتأكد من ذكر المغرب بوضوح
            for item in links_data:
                if len(opportunities) >= 5: # جلب 5 فرص مستوفية تماماً
                    break

                href = item["href"]
                full_link = href if href.startswith("http") else f"https://youth.europa.eu{href}"

                if full_link in seen_links:
                    continue
                seen_links.add(full_link)

                title = item["title"].replace("\n", " ").strip()

                # فتح صفحة الفرصة التفصيلية للفحص
                detail_page = context.new_page()
                try:
                    detail_page.goto(full_link, wait_until="domcontentloaded", timeout=30000)
                    detail_page.wait_for_timeout(2000)
                    
                    page_text = detail_page.evaluate("() => document.body.innerText").lower()

                    # 1. استبعاد الفرص الممتلئة أو المغلقة
                    if "this activity is full" in page_text or "cannot apply" in page_text or "application closed" in page_text:
                        detail_page.close()
                        continue

                    # 2. استبعاد رسائل عدم الأهلية العامة
                    if "you cannot apply for this activity because you do not meet the eligibility criteria" in page_text:
                        detail_page.close()
                        continue

                    # 3. الشرط الصارم الأساسي: يجب أن تكون كلمة "morocco" موجودة صراحة في تفاصيل الفرصة
                    if "morocco" not in page_text:
                        detail_page.close()
                        continue # تخطي أي فرصة لا تذكر المغرب صراحة

                    detail_page.close()

                    # إذا ذكرت المغرب صراحة وهي متاحة وممولة
                    opportunities.append({
                        "title": title if len(title) > 5 else "فرصة تطوعية جديدة عبر ESC",
                        "link": full_link
                    })

                except Exception as ex:
                    detail_page.close()
                    continue

            browser.close()

            if opportunities:
                print(f"\n✅ تم العثور على {len(opportunities)} فرص تذكر المغرب صراحة ومتاحة للتقديم!\n")
                return opportunities
            else:
                print("\n⚠️ لا توجد فرص في هذه الدفعة تذكر اسم (المغرب) صراحة، سنستمر بالبحث...\n")
                return []

    except Exception as e:
        print(f"\n[!] حدث خطأ أثناء الفحص: {e}")
        return []

if __name__ == "__main__":
    results = fetch_latest_opportunities()
    for index, res in enumerate(results, start=1):
        print(f"📌 الفرصة #{index}: {res['title']}")
        print(f"🔗 الرابط المباشر: {res['link']}\n" + "-"*50)