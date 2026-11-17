from backend.scripture import VerseParser, explicit_reference

def test_arabic_reference():
    assert explicit_reference('اشرح يوحنا ٣:١٦')['chapter'] == 3
    assert explicit_reference('فسر يعقوب 1:19-20')['end'] == 20

def test_notes_not_in_verse():
    parser = VerseParser()
    parser.feed('<span class="verse" id="V16">16</span>Original <a class="notemark"><span>note</span></a> text.<span class="verse" id="V17">17</span>Next')
    assert parser.verses[16] == 'Original  text.'

def test_invalid_url_is_not_reference():
    assert explicit_reference('https://evil.example/') is None
