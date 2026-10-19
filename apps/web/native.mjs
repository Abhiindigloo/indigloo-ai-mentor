export const android=!!globalThis.MentorNative;
const waiting=new Map();
if(android)globalThis.mentorNativeResult=(id,ok,value)=>{const p=waiting.get(id);if(!p)return;clearTimeout(p.timer);waiting.delete(id);ok?p.resolve(value):p.reject(Error(value||'Android action failed'));};
export function nativeCall(action,payload={},timeout=120000){if(!android)return Promise.reject(Error('Available in the Android app'));return new Promise((resolve,reject)=>{const id=crypto.randomUUID();const timer=setTimeout(()=>{waiting.delete(id);reject(Error('This operation took too long. Try again.'));},timeout);waiting.set(id,{resolve,reject,timer});try{MentorNative.request(JSON.stringify({id,action,payload}));}catch(e){clearTimeout(timer);waiting.delete(id);reject(e);}});}
