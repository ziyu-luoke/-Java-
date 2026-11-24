"""等长替换 xiaozhi-ai jar 中 VolcengineTtsService 的 seed-tts-2.0 -> seed-icl-2.0。
仅改字节码常量，不改结构；同时移除 Spring Boot 签名文件避免校验冲突。
输入: server.jar / dialogue.jar  ->  输出: server.patched.jar / dialogue.patched.jar
"""
import zipfile, io, os, shutil

BASE = os.path.dirname(os.path.abspath(__file__))
OLD = b'seed-tts-2.0'
NEW = b'seed-icl-2.0'
AI_JAR = 'BOOT-INF/lib/xiaozhi-ai-6.1.0.jar'
CLS = 'com/xiaozhi/ai/tts/providers/VolcengineTtsService.class'

assert len(OLD) == len(NEW) == 12, '必须等长'

def patch_ai_jar(ai_bytes):
    zin = zipfile.ZipFile(io.BytesIO(ai_bytes))
    raw = zin.read(CLS)
    assert raw.count(OLD) == 1, f'期望 1 处 seed-tts-2.0, 实际 {raw.count(OLD)}'
    patched = raw.replace(OLD, NEW)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = patched if item.filename == CLS else zin.read(item.filename)
            zout.writestr(item, data)
    return buf.getvalue()

def patch_fat_jar(src, dst):
    zin = zipfile.ZipFile(src, 'r')
    buf = io.BytesIO()
    removed = []
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            name = item.filename
            # 移除签名文件，避免改造后签名校验失败
            if name.startswith('META-INF/') and name.upper().endswith(('.SF', '.RSA', '.DSA')):
                removed.append(name)
                continue
            data = zin.read(name)
            if name == AI_JAR:
                data = patch_ai_jar(data)
                print(f'  [{os.path.basename(src)}] 已改造 {AI_JAR}')
            zout.writestr(item, data)
    with open(dst, 'wb') as f:
        f.write(buf.getvalue())
    print(f'  [{os.path.basename(src)}] 移除签名: {removed}')
    print(f'  -> {os.path.basename(dst)} ({len(buf.getvalue())} 字节)')

for name in ('server', 'dialogue'):
    src = os.path.join(BASE, f'{name}.jar')
    dst = os.path.join(BASE, f'{name}.patched.jar')
    if not os.path.exists(src):
        print(f'跳过 {src} (不存在)')
        continue
    patch_fat_jar(src, dst)
print('完成')
