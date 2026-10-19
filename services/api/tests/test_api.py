import json
import pytest
from fastapi.testclient import TestClient
from mentor_api.config import REPO_ROOT
from mentor_api.app import app, db, digest
from mentor_api.tutor import answer, tokens

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('DATABASE_PATH',str(tmp_path/'test.db'))
    monkeypatch.delenv('MODEL_BASE_URL',raising=False)
    monkeypatch.delenv('MODEL_NAME',raising=False)
    with TestClient(app) as c: yield c

def register(c,name='learner'):
    r=c.post('/v1/auth/register',json=dict(username=name,password='a-long-test-password'))
    assert r.status_code==201,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}
def session(c,h,**kw):
    r=c.post('/v1/sessions',headers=h,json=kw)
    assert r.status_code==201
    return r.json()['id']
def chat(c,h,s,q,**kw):
    return c.post('/v1/chat',headers=h,json=dict(session_id=s,question=q,**kw))

def test_complete_flow(client):
    h=register(client);s=session(client,h)
    r=chat(client,h,s,'Why are leaves green?',mode='answer').json()
    assert r['lesson_id']=='green-leaves'
    assert r['source']['kind']=='illustrative sample'
    assert client.get('/v1/progress',headers=h).json()['lessons'][0]['visits']==1
    assert len(client.get(f'/v1/sessions/{s}/messages',headers=h).json()['messages'])==1
    with db() as c:
        row=c.execute('SELECT * FROM users').fetchone()
        assert row['password']!='a-long-test-password'
        assert c.execute('SELECT hash FROM tokens').fetchone()[0]==digest(h['Authorization'][7:])
    assert client.post('/v1/auth/logout',headers=h).status_code==204
    assert client.get('/v1/me',headers=h).status_code==401

def test_unrelated_after_grounded_is_declined(client):
    h=register(client);s=session(client,h)
    assert chat(client,h,s,'Why are leaves green?').json()['lesson_id']
    assert chat(client,h,s,'explain again',mode='example').json()['lesson_id']
    r=chat(client,h,s,'Who won the 2011 cricket world cup?').json()
    assert r['lesson_id'] is None
    assert chat(client,h,s,'explain again').json()['lesson_id'] is None

def test_cross_account_isolation_and_cascade(client):
    h=register(client);other=register(client,'other');s=session(client,h)
    chat(client,h,s,'Why are leaves green?')
    assert client.get(f'/v1/sessions/{s}/messages',headers=other).status_code==404
    assert chat(client,other,s,'Why are leaves green?').status_code==404
    assert client.delete('/v1/me',headers=h).status_code==204
    assert client.get('/v1/me',headers=h).status_code==401
    with db() as c:
        for table in ('sessions','turns','progress'):
            assert c.execute(f'SELECT count(*) FROM {table}').fetchone()[0]==0
    assert client.get('/v1/me',headers=other).status_code==200

def test_validation_and_limits(client):
    assert client.post('/v1/auth/register',json={'username':'a','password':'short'}).status_code==422
    assert client.post('/v1/auth/register',content=b'x'*17000).status_code==413
    assert client.post('/v1/auth/register',content=iter([b'x'*9000,b'y'*9000])).status_code==413
    assert client.get('/v1/progress').status_code==401
    h=register(client);s=session(client,h)
    assert chat(client,h,s,' ').status_code==422
    for i in range(30): assert chat(client,h,s,'Why are leaves green?').status_code==200
    assert chat(client,h,s,'Why are leaves green?').status_code==429

def test_hindi_and_grade():
    assert 'पत्तियाँ' in tokens('हरी पत्तियाँ')
    assert answer('क्लोरोफिल','nova','hi','answer')['lesson_id']
    assert answer('quadratic discriminant','koko','en')['lesson_id'] is None

def test_model_fallback_and_unverified_label(client,monkeypatch):
    h=register(client);s=session(client,h)
    r=chat(client,h,s,'Why are leaves green?',use_model=True).json()
    assert r['model_status']=='unavailable_used_sample'
    async def generated(*args): return 'A generated explanation.'
    monkeypatch.setattr('mentor_api.app.model_explanation',generated)
    r=chat(client,h,s,'Why are leaves green?',use_model=True).json()
    assert r['engine']=='server-model' and r['grounded'] is False
    assert r['notice']
    r=chat(client,h,s,'Who won the 2011 cricket world cup?',use_model=True).json()
    assert r['model_status']=='declined_before_model'

def test_auth_duplicate_expiry(client):
    h=register(client)
    assert client.post('/v1/auth/register',json=dict(username='LEARNER',password='a-long-test-password')).status_code==409
    assert client.post('/v1/auth/login',json=dict(username='learner',password='bad-long-password')).status_code==401
    assert client.post('/v1/auth/login',json=dict(username='learner',password='a-long-test-password')).status_code==200
    with db() as c: c.execute('UPDATE tokens SET expires=0')
    assert client.get('/v1/me',headers=h).status_code==401

def test_web_and_contract(client):
    assert client.get('/app/').status_code==200
    assert "frame-ancestors 'none'" in client.get('/app/').headers['content-security-policy']
    assert len(client.get('/v1/lessons').json()['lessons'])==15
    assert client.get('/v1/capabilities').json()['on_device_llm'] is False
    schema=client.get('/openapi.json').json()
    collection=json.loads((REPO_ROOT/'packages'/'contracts'/'postman'/'AI-Mentor.postman_collection.json').read_text(encoding='utf-8'))
    assert len(collection['item'])>=12
    assert '/v1/chat' in schema['paths']

def test_stale_model_reply_does_not_overwrite_newer_context(client,monkeypatch):
    """A slow model reply must not restore a topic after a newer request changed it."""
    import asyncio
    import httpx
    h=register(client);s=session(client,h)
    async def scenario():
        gate=asyncio.Event()
        async def slow(question,*args):
            await gate.wait()
            return 'A generated explanation.'
        monkeypatch.setattr('mentor_api.app.model_explanation',slow)
        transport=httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport,base_url='http://test') as ac:
            send=lambda q,**kw: ac.post('/v1/chat',headers=h,json=dict(session_id=s,question=q,**kw))
            older=asyncio.create_task(send('Why are leaves green?',use_model=True))
            await asyncio.sleep(0.2)                         # older request is now waiting on the model
            newer=await send('Who won the 2011 cricket world cup?')
            assert newer.json()['lesson_id'] is None         # newer request clears the topic
            gate.set()
            assert (await older).json()['lesson_id']=='green-leaves'
            follow=await send('explain again')
            return follow.json()
    follow=asyncio.run(scenario())
    assert follow['lesson_id'] is None, 'stale reply restored the old topic'

def test_existing_database_gains_session_seq_column(tmp_path,monkeypatch):
    import sqlite3
    path=tmp_path/'old.db'
    old=sqlite3.connect(path)
    old.execute('CREATE TABLE sessions(id TEXT PRIMARY KEY, user_id TEXT, band TEXT, lang TEXT, last_lesson TEXT)')
    old.execute("INSERT INTO sessions VALUES('s1','u1','nova','en','green-leaves')")
    old.commit();old.close()
    monkeypatch.setenv('DATABASE_PATH',str(path))
    with db() as c:
        row=c.execute("SELECT last_lesson,seq FROM sessions WHERE id='s1'").fetchone()
    assert row['last_lesson']=='green-leaves' and row['seq']==0
