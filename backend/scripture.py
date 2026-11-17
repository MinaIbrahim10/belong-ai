"""Read-only scripture retrieval. URLs are constructed solely from validated canon IDs."""
import asyncio
import re
import time
from html.parser import HTMLParser

import httpx

# Names and chapter counts are fixed. No model-controlled URLs are fetched.
BOOK_DATA = """GEN|التكوين|Genesis|50
EXO|الخروج|Exodus|40
LEV|اللاويين|Leviticus|27
NUM|العدد|Numbers|36
DEU|التثنية|Deuteronomy|34
JOS|يشوع|Joshua|24
JDG|القضاة|Judges|21
RUT|راعوث|Ruth|4
1SA|صموئيل الأول|1 Samuel|31
2SA|صموئيل الثاني|2 Samuel|24
1KI|الملوك الأول|1 Kings|22
2KI|الملوك الثاني|2 Kings|25
1CH|أخبار الأيام الأول|1 Chronicles|29
2CH|أخبار الأيام الثاني|2 Chronicles|36
EZR|عزرا|Ezra|10
NEH|نحميا|Nehemiah|13
EST|أستير|Esther|10
JOB|أيوب|Job|42
PSA|المزامير|Psalms|150
PRO|الأمثال|Proverbs|31
ECC|الجامعة|Ecclesiastes|12
SNG|نشيد الأنشاد|Song of Songs|8
ISA|إشعياء|Isaiah|66
JER|إرميا|Jeremiah|52
LAM|مراثي إرميا|Lamentations|5
EZK|حزقيال|Ezekiel|48
DAN|دانيال|Daniel|12
HOS|هوشع|Hosea|14
JOL|يوئيل|Joel|3
AMO|عاموس|Amos|9
OBA|عوبديا|Obadiah|1
JON|يونان|Jonah|4
MIC|ميخا|Micah|7
NAM|ناحوم|Nahum|3
HAB|حبقوق|Habakkuk|3
ZEP|صفنيا|Zephaniah|3
HAG|حجي|Haggai|2
ZEC|زكريا|Zechariah|14
MAL|ملاخي|Malachi|4
MAT|متى|Matthew|28
MRK|مرقس|Mark|16
LUK|لوقا|Luke|24
JHN|يوحنا|John|21
ACT|أعمال الرسل|Acts|28
ROM|رومية|Romans|16
1CO|كورنثوس الأولى|1 Corinthians|16
2CO|كورنثوس الثانية|2 Corinthians|13
GAL|غلاطية|Galatians|6
EPH|أفسس|Ephesians|6
PHP|فيلبي|Philippians|4
COL|كولوسي|Colossians|4
1TH|تسالونيكي الأولى|1 Thessalonians|5
2TH|تسالونيكي الثانية|2 Thessalonians|3
1TI|تيموثاوس الأولى|1 Timothy|6
2TI|تيموثاوس الثانية|2 Timothy|4
TIT|تيطس|Titus|3
PHM|فليمون|Philemon|1
HEB|العبرانيين|Hebrews|13
JAS|يعقوب|James|5
1PE|بطرس الأولى|1 Peter|5
2PE|بطرس الثانية|2 Peter|3
1JN|يوحنا الأولى|1 John|5
2JN|يوحنا الثانية|2 John|1
3JN|يوحنا الثالثة|3 John|1
JUD|يهوذا|Jude|1
REV|رؤيا يوحنا|Revelation|22"""
BOOKS = {row.split('|')[0]: row.split('|')[1:] for row in BOOK_DATA.splitlines()}
CACHE = {}


def normalize(text):
    return re.sub(r'[\u064b-\u065fـ]', '', text).replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا').lower()


def explicit_reference(text):
    text = normalize(text)
    # Longer book names must win before John / Samuel etc.
    names = sorted(((normalize(name), code) for code, data in BOOKS.items() for name in data[:2]), reverse=True, key=lambda item: len(item[0]))
    for name, code in names:
        match = re.search(re.escape(name) + r'\s+(\d{1,3})\s*[:：]\s*(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?', text)
        if match:
            chapter, start = int(match[1]), int(match[2])
            return {'book': code, 'chapter': chapter, 'start': start, 'end': int(match[3] or start)}
    return None


class VerseParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.verses = {}
        self.current = None
        self.verse_number = False
        self.skip_depth = 0
        self.stopped = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.skip_depth:
            self.skip_depth += 1
            return
        if tag == 'a' and 'notemark' in attrs.get('class', ''):
            self.skip_depth = 1
            return
        if tag == 'div' and 'footnote' in attrs.get('class', ''):
            self.stopped = True
        if tag == 'span' and 'verse' in attrs.get('class', '').split():
            verse_id = attrs.get('id', '')
            if re.fullmatch(r'V[1-9][0-9]*', verse_id):
                self.current = int(verse_id[1:])
                self.verses[self.current] = ''
                self.verse_number = True

    def handle_endtag(self, tag):
        if self.skip_depth:
            self.skip_depth -= 1
        elif tag == 'span' and self.verse_number:
            self.verse_number = False

    def handle_data(self, data):
        if self.current and not self.skip_depth and not self.verse_number and not self.stopped:
            self.verses[self.current] += data


async def passage(reference):
    try:
        book = reference['book']
        chapter, start, end = (int(reference[key]) for key in ('chapter', 'start', 'end'))
        if book not in BOOKS or not 1 <= chapter <= int(BOOKS[book][2]) or not 1 <= start <= end <= start + 11:
            return None
    except (KeyError, TypeError, ValueError):
        return None
    key = (book, chapter)
    url = f'https://ebible.org/eng-web/{book}{chapter:02d}.htm'
    cached = CACHE.get(key)
    if cached and cached[0] > time.monotonic():
        verses = cached[1]
    else:
        try:
            async with httpx.AsyncClient(timeout=7, follow_redirects=False) as client:
                async with client.stream('GET', url) as response:
                    response.raise_for_status()
                    chunks = []
                    size = 0
                    async for chunk in response.aiter_bytes():
                        size += len(chunk)
                        if size > 500000:
                            return None
                        chunks.append(chunk)
            parser = VerseParser()
            parser.feed(b''.join(chunks).decode('utf-8'))
            verses = parser.verses
            if len(CACHE) >= 128:
                CACHE.pop(next(iter(CACHE)))
            CACHE[key] = (time.monotonic() + 3600, verses)
        except (httpx.HTTPError, UnicodeError):
            return None
    if any(number not in verses for number in range(start, end + 1)):
        return None
    # Remove page navigation after the last verse, if present.
    text = ' '.join(f'{number} ' + re.sub(r'\s+', ' ', verses[number]).strip() for number in range(start, end + 1))
    text = text.split('The World English Bible')[0]
    label = f'{BOOKS[book][0]} {chapter}:{start}' + (f'–{end}' if end != start else '')
    return {'reference': label, 'url': url, 'text': text[:10000]}
