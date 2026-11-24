import websocket, json, time
DEVICE="3c:dc:75:fb:1e:cc"
ws_url=f"ws://127.0.0.1:8092/ws/xiaozhi/v1/?deviceId={DEVICE}"
ws=websocket.create_connection(ws_url, timeout=20)
print("connected")
def send(**kw):
    ws.send(json.dumps(kw)); print(">>>", json.dumps(kw,ensure_ascii=False)[:110])
send(type="hello", version=1, transport="websocket", audio_params={"format":"opus","sample_rate":16000,"channels":1,"frame_duration":60})
t0=time.time()
while time.time()-t0<6:
    raw=ws.recv()
    if isinstance(raw,bytes): continue
    msg=json.loads(raw); print("<<<", json.dumps(msg,ensure_ascii=False)[:150])
    if msg.get("type")=="hello": break
send(type="listen", state="start", mode="auto")
send(type="listen", state="stop", text="你好,请介绍一下你自己")
t0=time.time(); audio=0; states=[]
while time.time()-t0<30:
    try: raw=ws.recv()
    except Exception as e: print("recv end:",e); break
    if isinstance(raw,bytes): audio+=1; continue
    msg=json.loads(raw); t=msg.get("type")
    if t=="tts":
        st=msg.get("state"); states.append(st); print("<<< TTS:",st,"text:",str(msg.get('text',''))[:50])
    elif t=="stt": print("<<< STT:",msg.get("text"))
    else: print("<<<",json.dumps(msg,ensure_ascii=False)[:130])
    if "stop" in states and audio>0: break
print("=== TTS状态:",states," 音频帧:",audio," ===")
ws.close()
