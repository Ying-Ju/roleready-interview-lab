"""Browser-side Gemini Live audio component."""

from __future__ import annotations

import html
import json


def live_component_html(*, token: str, model: str, duration_minutes: int = 10) -> str:
    token_js = json.dumps(token)
    model_js = json.dumps(model)
    duration_js = max(1, min(int(duration_minutes), 10))
    return f"""
<!doctype html><html><head><meta charset="utf-8"><style>
body {{ font-family: Arial,sans-serif; color:#172033; margin:0; background:#fff; }}
.panel {{ border:1px solid #dbe0e8; border-radius:14px; padding:18px; }}
.status {{ padding:10px 12px; background:#f4f6f9; border-radius:8px; margin-bottom:12px; }}
.status.error {{ background:#fdecec; color:#a12622; }}
button {{ padding:10px 18px; border-radius:8px; border:0; cursor:pointer; font-weight:650; }}
#start {{ background:#ce1141; color:white; }} #stop {{ background:#e5e9ef; margin-left:8px; }}
#transcript {{ margin-top:14px; height:260px; overflow:auto; background:#fafbfc; padding:12px; border-radius:8px; }}
.user {{ color:#004b87; }} .ai {{ color:#172033; }} .label {{ font-weight:bold; }}
</style></head><body><div class="panel">
<div id="status" class="status">Ready. Select Start voice interview and allow microphone access.</div>
<button id="start">Start voice interview</button><button id="stop" disabled>End interview</button>
<div id="transcript" aria-live="polite"><em>Live transcript will appear here.</em></div>
</div><script>
const TOKEN={token_js}, MODEL={model_js}, DURATION_MINUTES={duration_js};
const statusEl=document.getElementById('status'), transcriptEl=document.getElementById('transcript');
const startBtn=document.getElementById('start'), stopBtn=document.getElementById('stop');
let ws, stream, ctx, processor, source, silentGain, outputNode, workletUrl, sessionTimer, modelSpeakingUntil=0, started=false, lastRole='', lastTextNode=null;
function setStatus(t,isError=false){{statusEl.textContent=t;statusEl.classList.toggle('error',isError);}}
function fail(prefix,error){{const detail=error?.message||String(error||'Unknown error');setStatus(prefix+' '+detail,true);startBtn.disabled=false;stopBtn.disabled=true;}}
function addLine(role,text){{if(!text||!text.trim())return;if(!started){{transcriptEl.innerHTML='';started=true;}}
 if(role!==lastRole||!lastTextNode){{const p=document.createElement('p');p.className=role==='You'?'user':'ai';const label=document.createElement('span');label.className='label';label.textContent=role+': ';lastTextNode=document.createTextNode('');p.appendChild(label);p.appendChild(lastTextNode);transcriptEl.appendChild(p);lastRole=role;}}
 const clean=text.trim(),current=lastTextNode.nodeValue||'',separator=current&&!/\s$/.test(current)&&!/^[.,!?;:]/.test(clean)?' ':'';lastTextNode.nodeValue=current+separator+clean;transcriptEl.scrollTop=transcriptEl.scrollHeight;}}
function b64(bytes){{let s='';for(let i=0;i<bytes.length;i+=0x8000)s+=String.fromCharCode(...bytes.subarray(i,i+0x8000));return btoa(s);}}
function downsample(input,inRate,outRate){{const ratio=inRate/outRate,n=Math.round(input.length/ratio),out=new Int16Array(n);
 for(let i=0;i<n;i++){{const v=Math.max(-1,Math.min(1,input[Math.floor(i*ratio)]));out[i]=v<0?v*32768:v*32767;}}return new Uint8Array(out.buffer);}}
async function initAudio(){{
 ctx=new AudioContext({{sampleRate:24000}});
 const workletCode=`class PcmQueueProcessor extends AudioWorkletProcessor {{
  constructor() {{ super(); this.queue=[]; this.offset=0; this.queued=0; this.playing=false; this.port.onmessage=e=>{{if(e.data==='reset'){{this.queue=[];this.offset=0;this.queued=0;this.playing=false;}}else{{this.queue.push(e.data);this.queued+=e.data.length;}}}}; }}
  process(inputs,outputs) {{ const out=outputs[0][0]; out.fill(0); if(!this.playing){{if(this.queued<2400)return true;this.playing=true;}}
   let pos=0; while(pos<out.length&&this.queue.length){{const chunk=this.queue[0],available=chunk.length-this.offset,take=Math.min(out.length-pos,available);out.set(chunk.subarray(this.offset,this.offset+take),pos);pos+=take;this.offset+=take;this.queued-=take;if(this.offset>=chunk.length){{this.queue.shift();this.offset=0;}}}}
   if(pos<out.length)this.playing=false; return true; }}
 }} registerProcessor('pcm-queue',PcmQueueProcessor);`;
 workletUrl=URL.createObjectURL(new Blob([workletCode],{{type:'application/javascript'}}));
 await ctx.audioWorklet.addModule(workletUrl);outputNode=new AudioWorkletNode(ctx,'pcm-queue');outputNode.connect(ctx.destination);
}}
function playAudio(base64){{const raw=atob(base64),bytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
 const view=new DataView(bytes.buffer),samples=new Float32Array(Math.floor(raw.length/2));for(let i=0;i<samples.length;i++)samples[i]=view.getInt16(i*2,true)/32768;
 modelSpeakingUntil=performance.now()+350;outputNode.port.postMessage(samples,[samples.buffer]);}}
async function beginMic(){{stream=await navigator.mediaDevices.getUserMedia({{audio:{{channelCount:1,echoCancellation:true,noiseSuppression:true}}}});
 await initAudio();source=ctx.createMediaStreamSource(stream);processor=ctx.createScriptProcessor(2048,1,1);
 processor.onaudioprocess=e=>{{if(ws?.readyState!==1||performance.now()<modelSpeakingUntil)return;const pcm=downsample(e.inputBuffer.getChannelData(0),ctx.sampleRate,16000);
 ws.send(JSON.stringify({{realtimeInput:{{audio:{{data:b64(pcm),mimeType:'audio/pcm;rate=16000'}}}}}}));}};
 silentGain=ctx.createGain();silentGain.gain.value=0;source.connect(processor);processor.connect(silentGain);silentGain.connect(ctx.destination);}}
function finish(){{try{{if(sessionTimer)clearTimeout(sessionTimer);processor?.disconnect();silentGain?.disconnect();outputNode?.disconnect();source?.disconnect();stream?.getTracks().forEach(t=>t.stop());ctx?.close();if(workletUrl)URL.revokeObjectURL(workletUrl);ws?.close();}}catch(e){{}}
 startBtn.disabled=true;stopBtn.disabled=true;setStatus('Interview ended.');}}
startBtn.onclick=async()=>{{
 try{{
  startBtn.disabled=true;setStatus('Step 1 of 3: opening the secure connection...');
  if(!window.isSecureContext)throw new Error('Microphone access requires localhost or an HTTPS address.');
  if(!navigator.mediaDevices?.getUserMedia)throw new Error('This browser cannot provide microphone access here.');
  const url='wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContentConstrained?access_token='+encodeURIComponent(TOKEN);
  ws=new WebSocket(url);
  ws.onopen=()=>{{setStatus('Step 2 of 3: configuring the interviewer...');ws.send(JSON.stringify({{setup:{{model:'models/'+MODEL,generationConfig:{{responseModalities:['AUDIO']}},inputAudioTranscription:{{}},outputAudioTranscription:{{}},sessionResumption:{{}},contextWindowCompression:{{slidingWindow:{{}}}}}}}}));}};
  ws.onmessage=async ev=>{{let msg;try{{
   const payload=ev.data instanceof Blob ? await ev.data.text() : ev.data;
   msg=JSON.parse(payload);
  }}catch(e){{fail('The interviewer returned an unreadable response.',e);return;}}
   if(msg.setupComplete){{try{{setStatus('Step 3 of 3: waiting for microphone permission...');await beginMic();stopBtn.disabled=false;setStatus('Interview in progress — '+DURATION_MINUTES+' minute limit. Speak naturally.');sessionTimer=setTimeout(()=>{{finish();setStatus('Time limit reached. The interview has ended.');}},DURATION_MINUTES*60*1000);
   ws.send(JSON.stringify({{clientContent:{{turns:[{{role:'user',parts:[{{text:'Begin the interview now with your opening and first planned question.'}}]}}],turnComplete:true}}}}));}}catch(e){{fail('Microphone access was not available.',e);}}}}
   const sc=msg.serverContent;if(sc?.inputTranscription?.text)addLine('You',sc.inputTranscription.text);if(sc?.outputTranscription?.text)addLine('Interviewer',sc.outputTranscription.text);
   for(const part of (sc?.modelTurn?.parts||[]))if(part.inlineData?.data)playAudio(part.inlineData.data);if(sc?.interrupted){{outputNode?.port.postMessage('reset');modelSpeakingUntil=0;}}}};
  ws.onerror=()=>setStatus('The live connection failed. Create a fresh voice session and try again.',true);
  ws.onclose=e=>{{if(!stopBtn.disabled||e.code!==1000)setStatus('The live connection closed (code '+e.code+'). '+(e.reason||'Create a fresh session and try again.'),e.code!==1000);stopBtn.disabled=true;}};
 }}catch(e){{fail('The voice interview could not start.',e);}}
}};
stopBtn.onclick=finish;
</script></body></html>
"""
