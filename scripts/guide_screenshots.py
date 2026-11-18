"""Regenerate the Ah-Eh Sayacı user-guide screenshots (ah-eh-sayaci/kilavuz/img) with fictional names.

Needs Python Playwright with Chromium: pip install playwright && playwright install chromium
Run: python scripts/guide_screenshots.py
"""
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent / "ah-eh-sayaci"
OUT = ROOT / "kilavuz" / "img"
OUT.mkdir(parents=True, exist_ok=True)

AGENDA = """ANADOLU TOASTMASTERS
TOPLANTI #302
24 Kasım 2026
Başkan: ........ Deniz Arslan
Toplantı Ustası: ........ Selin Yıldız
Zaman Tutucu: ........ Burak Demir
“Ah-Eh” Sayıcı: ........ Ece Kaya
Kelime Ustası: ........ Mert Aydın
HAZIRLIKLI KONUŞMACILAR
Zeynep Çelik - Patika: Etkili Sunum / Seviye 1
Can Öztürk - Patika: Liderlik Gelişimi / Seviye 2
DOĞAÇLAMA KONUŞMALAR
DEĞERLENDİRME OTURUMU
Ayşe Koç (2-3 dakika) - 1. Değerlendirici
Emre Şahin (2-3 dakika) - 2. Değerlendirici
"""

COUNTS = {"Deniz Arslan": 2, "Selin Yıldız": 5, "Burak Demir": 0, "Ece Kaya": 1, "Mert Aydın": 3,
          "Zeynep Çelik": 4, "Can Öztürk": 7, "Ayşe Koç": 0, "Emre Şahin": 2, "Lale Güneş": 1, "Kerem Polat": 6}

def shot(target, name):
    target.screenshot(path=str(OUT / f"{name}.png"))
    print("saved", name)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1240, "height": 860}, device_scale_factor=2, color_scheme="light",
                            locale="tr-TR", timezone_id="Europe/Istanbul")
    url = (ROOT / "index.html").as_uri()
    page.goto(url)
    page.evaluate("localStorage.clear()")
    page.reload()

    page.evaluate("state.date = '2026-11-24'; save(); syncHeader();")

    # 2. Agenda import with preview.
    page.set_viewport_size({"width": 1240, "height": 1500})
    page.click("#importBtn")
    page.fill("#importText", AGENDA)
    page.click("#parseBtn")
    page.wait_for_timeout(200)
    shot(page.locator("#importDialog"), "01-ajanda")
    page.click("#importConfirm")
    page.set_viewport_size({"width": 1240, "height": 860})

    # 3. Adding a guest by hand.
    page.select_option("#newCategory", "guest")
    page.fill("#newName", "Lale Güneş")
    page.click("#addForm button[type=submit]")

    # 4. Impromptu quick pick.
    page.select_option("#newCategory", "impromptu")
    page.wait_for_timeout(100)
    page.click("#quickChips button:has-text('Mert Aydın')")
    page.fill("#newName", "Kerem Polat")
    page.click("#addForm button[type=submit]")
    page.fill("#newName", "")
    page.locator("#newName").blur()
    shot(page.locator("section.panel"), "02-dogaclama")

    # 5. Mid-meeting board.
    page.evaluate("""(counts) => {
      for (const s of state.speakers) s.count = counts[s.name] ?? 0;
      state.history = [];
      state.currentId = state.speakers.find(s => s.name === 'Zeynep Çelik').id;
      state.lastCategory = 'prepared';
      save(); syncHeader(); render(); setStatus('');
    }""", COUNTS)
    page.evaluate("window.scrollTo(0, 0)")
    shot(page, "03-toplanti")

    # 6. Card close-up.
    shot(page.locator("#board .card.current"), "05-kart")

    # 7. Name search.
    page.click("#currentSearch")
    page.fill("#currentSearch", "ay")
    page.wait_for_timeout(150)
    box = page.locator("#nowPanel").bounding_box()
    page.screenshot(path=str(OUT / "04-arama.png"),
                    clip={"x": box["x"] - 8, "y": box["y"] - 8, "width": box["width"] + 16, "height": 330})
    print("saved 04-arama")
    page.keyboard.press("Escape")

    # 8. Report.
    page.set_viewport_size({"width": 1240, "height": 1500})
    page.click("#reportBtn")
    page.wait_for_timeout(200)
    shot(page.locator("#reportDialog"), "06-rapor")

    page.evaluate("localStorage.clear()")
    browser.close()
