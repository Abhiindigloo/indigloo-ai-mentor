"""Conservative lexical retrieval over an illustrative bilingual lesson pack."""
import json
import re
import unicodedata

from .config import curriculum_path

LESSONS = json.loads(curriculum_path().read_text(encoding='utf-8'))
BY_ID = {d['id']: d for d in LESSONS}
STOP = set('a an the is are was were why what how do does in to of for and i me please explain tell about can you this that it with from का की के क्या कैसे क्यों है हैं में से को और मुझे समझाओ बताओ'.split())
FOLLOW = re.compile(r"^(why|how|again|simpler|explain again|i (?:do not|don't) understand|give (?:me )?an example|show (?:the )?answer|समझ नहीं आया|फिर से|आसान भाषा में|उदाहरण दो|जवाब दिखाओ)[?!.।\s]*$", re.I)
OFF = {'en': 'I cannot find that question in this sample lesson pack. Please ask your teacher or choose a lesson.', 'hi': 'यह प्रश्न इस नमूना पाठ में नहीं मिला। अपने शिक्षक से पूछो या कोई पाठ चुनो।'}

def tokens(text):
    # Preserve combining marks in Hindi; Python \w alone splits Devanagari words.
    text = unicodedata.normalize('NFC', text).lower()
    clean = ''.join(c if unicodedata.category(c)[0] in 'LMN' else ' ' for c in text)
    return {w for w in clean.split() if len(w) > 1 and w not in STOP}

def retrieve(question, band):
    q = tokens(question)
    ranked = []
    for d in LESSONS:
        if d['band'] != band:
            continue
        vocabulary = tokens(d['title']+' '+d['kw']+' '+d['text']+' '+d['answer']['hi'])
        overlap = q & vocabulary
        coverage = len(overlap)/max(len(q), 1)
        if overlap and coverage >= 0.5:
            ranked.append((coverage, len(q & tokens(d['title'])), len(overlap), d))
    ranked.sort(key=lambda v: (v[0], v[1], v[2]), reverse=True)
    return ranked[0][3] if ranked else None

def answer(question, band, lang, mode='hint', previous=None):
    d = BY_ID.get(previous) if previous and FOLLOW.fullmatch(question.strip()) else retrieve(question, band)
    if d and d['band'] != band:
        d = None
    if not d:
        return dict(answer=OFF[lang], lesson_id=None, source=None, engine='sample-pack', grounded=False)
    if mode == 'hint':
        reply = d['hints'][lang][0]
    elif mode == 'steps':
        reply = '\n'.join(f'{i+1}. {h}' for i,h in enumerate(d['hints'][lang]))
    elif mode == 'example':
        reply = d['example'][lang]
    else:
        reply = d['answer'][lang]+'\n\n'+d['example'][lang]
    return dict(answer=reply, lesson_id=d['id'], source=dict(title=d['title'], grade=d['grade'], kind='illustrative sample'), engine='sample-pack', grounded=True)
