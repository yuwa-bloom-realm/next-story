# 書き換えノートのデモ版（説明会用）を index.html から作る
import re, sys
src = '/home/claude/next-story/kakikae-note/index.html'
dst = '/home/claude/next-story/kakikae-note/demo.html'
s = open(src, encoding='utf-8').read()
s = s.replace('<script src="https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js" defer></script>', '')
s = s.replace('<link rel="manifest" href="manifest.json">', '')
s = s.replace('<title>書き換えノート</title>', '<title>書き換えノート（デモ）</title>\n<meta name="robots" content="noindex">')
mock = r'''<script>
/* ===== デモ用：記録はどこにも保存されません（再読みこみで最初から） ===== */
(function(){
  const mem = {};
  const fake = { getItem:k => (k in mem ? mem[k] : null), setItem:(k,v) => { mem[k] = String(v); }, removeItem:k => { delete mem[k]; },
    clear:() => { for (const k in mem) delete mem[k]; }, key:i => Object.keys(mem)[i] || null, get length(){ return Object.keys(mem).length; } };
  try { Object.defineProperty(window, 'localStorage', { value: fake, configurable: true }); } catch (e) {}
  fake.setItem('kn_key', 'DEMO');
  window.KAKIKAE_CONFIG = { GAS_URL: 'demo://', ONESIGNAL_APP_ID: '' };

  const pad = n => String(n).padStart(2, '0');
  const dayKey = (off) => { const d = new Date(Date.now() + (9 - 4) * 3600e3 + (off || 0) * 864e5); return d.getUTCFullYear() + '-' + pad(d.getUTCMonth() + 1) + '-' + pad(d.getUTCDate()); };
  const TODAY = dayKey(0);
  // 3枚完成・4枚目はあと1ピース・書いた日は99日（次で100日の扉）
  const opened4 = []; for (let i = 0; i < 25; i++) if (i !== 12) opened4.push(i);
  const ST = { userId: 'demo', name: 'あなた', pic: 4, opened: opened4, bank: 0, done: [1, 2, 3], picCount: 16, pieces: 25, lastPic: 16,
    notifyOn: true, notifyHour: 21, expires: '2027-12-31', expired: false, daysLeft: 398 };
  const notes = {
    [dayKey(-1)]: { a: '朝から雨で、洗濯物が乾かなかった。', b: '部屋の中でゆっくりできる日だったのかも。', c: '明日は好きな紅茶を飲む。', h: '温かいものでも飲んで、ひと息つこうか。' },
    [dayKey(-2)]: { a: '仕事でミスして落ち込んだ。', b: 'あわてずに対応できた自分もいた。', c: '次は確認を1回ふやす。', h: '誰にだって、うまくいかない日はあるよ。次、どうしようか？' },
    [dayKey(-3)]: { a: '友達とランチ。すごくおいしかった！', b: '', c: 'また誘ってみよう。', h: 'おいしいものを食べる幸せ！たまらんよねー！' }
  };
  const WORDS = [
    [/疲|つかれ|しんど|眠/, '今日は自分に、ちょっと甘くしてあげようよ。'],
    [/嬉|うれし|楽し|よかった|できた/, 'わあ！それは嬉しいね！私まで嬉しくなっちゃう！'],
    [/不安|心配|こわ|怖/, '心配なこと、ここに書いていっていいからね。'],
    [/失敗|ミス|落ち込/, '失敗したっていいじゃない。そんな日だってあるよ！'],
    [/イライラ|腹|ムカ/, 'たまには『もう知らん！』って言いたくなる日もあるよね！'],
    [/おいし|美味|ご飯|ランチ/, 'おいしいものを食べる幸せ！たまらんよねー！']
  ];
  const UNI = ['今日も、あなたの1ページをありがとう！', 'こうして毎日、少しずつ自分の物語が増えていくんだね。', '今日のページも、ちゃんとここに残ったね。'];
  const obj = (d, n) => ({ day: d, a: n.a || '', b: n.b || '', c: n.c || '', delivered: !!n.h, hitokoto: n.h || '' });
  const st = () => JSON.parse(JSON.stringify(ST));
  function handle(req){
    const a = req.action;
    if (a === 'login' || a === 'notify' || a === 'townSave') return { ok: true, today: TODAY, state: st() };
    if (a === 'townGet') return { ok: true, today: TODAY, town: '', state: st() };
    if (a === 'today') return { ok: true, today: TODAY, entry: notes[TODAY] ? obj(TODAY, notes[TODAY]) : null, state: st() };
    if (a === 'history') return { ok: true, today: TODAY, list: Object.keys(notes).sort().reverse().map(d => obj(d, notes[d])), state: st() };
    if (a === 'save' || a === 'deliver') {
      const n = notes[TODAY] || (notes[TODAY] = {});
      n.a = req.a || ''; n.b = req.b || ''; n.c = req.c || '';
      const out = { ok: true, today: TODAY };
      if (a === 'deliver') {
        if (n.h) { out.already = true; out.hitokoto = n.h; }
        else {
          if (!(n.a || n.b || n.c)) return { ok: false, error: 'empty' };
          const t = n.a + n.b + n.c, hit = WORDS.find(w => w[0].test(t));
          n.h = hit ? hit[1] : UNI[Math.floor(Math.random() * UNI.length)];
          const rest = []; for (let i = 0; i < 25; i++) if (ST.opened.indexOf(i) < 0) rest.push(i);
          const p = rest[Math.floor(Math.random() * rest.length)];
          ST.opened.push(p); out.piece = p; out.completed = null; out.banked = false;
          if (ST.opened.length >= 25) { out.completed = ST.pic; ST.done.push(ST.pic); ST.pic++; ST.opened = []; }
          out.hitokoto = n.h;
        }
      }
      out.entry = obj(TODAY, n); out.state = st(); return out;
    }
    return { ok: false, error: 'unknown' };
  }
  const realFetch = window.fetch.bind(window);
  window.fetch = async (url, opt) => {
    if (String(url).indexOf('demo://') !== 0) return realFetch(url, opt);
    await new Promise(r => setTimeout(r, 350));
    const res = handle(JSON.parse((opt && opt.body) || '{}'));
    return { ok: true, json: async () => res };
  };
})();
</script>
<style>
  .demo-ribbon{position:fixed;z-index:9999;top:calc(6px + env(safe-area-inset-top));right:8px;padding:4px 12px;border-radius:999px;
    font-size:12px;letter-spacing:.15em;color:#141733;background:linear-gradient(180deg,#fff0c4,#d8b465);box-shadow:0 2px 8px rgba(0,0,0,.3);pointer-events:none}
</style>'''
s = s.replace('<script src="config.js"></script>', mock)
s = s.replace('<body>', '<body>\n<div class="demo-ribbon">デモ</div>', 1)
assert 'demo://' in s and 'OneSignalSDK.page.js' not in s
open(dst, 'w', encoding='utf-8').write(s)
print('ok')
