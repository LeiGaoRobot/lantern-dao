// audio.js — everything is synthesised with WebAudio, no sample files.
let ctx = null, master = null, sfxBus = null, musicBus = null, ambBus = null;
let enabled = true, started = false;
let rainGain = null, rainNode = null, windGain = null;
let musicTimer = null;

export function audioEnabled() { return enabled; }
export function setEnabled(v) {
  enabled = v;
  if (master) master.gain.setTargetAtTime(v ? 0.8 : 0, ctx.currentTime, 0.05);
}
export function ensureAudio() {
  if (started) return;
  started = true;
  try {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
  } catch (e) { started = false; return; }
  master = ctx.createGain(); master.gain.value = enabled ? 0.8 : 0; master.connect(ctx.destination);
  sfxBus = ctx.createGain(); sfxBus.gain.value = 0.55; sfxBus.connect(master);
  musicBus = ctx.createGain(); musicBus.gain.value = 0.28; musicBus.connect(master);
  ambBus = ctx.createGain(); ambBus.gain.value = 0.5; ambBus.connect(master);
  startAmbience();
  startMusic();
}
export function resume() { if (ctx && ctx.state === 'suspended') ctx.resume(); }

// ---------------------------------------------------------------- helpers
function noiseBuffer(seconds = 2) {
  const n = Math.floor(ctx.sampleRate * seconds);
  const b = ctx.createBuffer(1, n, ctx.sampleRate);
  const d = b.getChannelData(0);
  for (let i = 0; i < n; i++) d[i] = Math.random() * 2 - 1;
  return b;
}
let _noise = null;
function noise() { return _noise || (_noise = noiseBuffer(2)); }
function env(g, t, a, d, peak = 1, sustain = 0) {
  g.gain.cancelScheduledValues(t);
  g.gain.setValueAtTime(0.0001, t);
  g.gain.exponentialRampToValueAtTime(peak, t + a);
  g.gain.exponentialRampToValueAtTime(Math.max(sustain, 0.0001), t + a + d);
}
function tone(type, f0, f1, dur, vol, bus = sfxBus, attack = 0.005) {
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.type = type;
  const t = ctx.currentTime;
  o.frequency.setValueAtTime(f0, t);
  if (f1 !== f0) o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
  env(g, t, attack, dur, vol);
  o.connect(g); g.connect(bus);
  o.start(t); o.stop(t + dur + 0.05);
}
function burst(dur, vol, filt = 'bandpass', f0 = 1200, f1 = 300, q = 0.8, bus = sfxBus) {
  const s = ctx.createBufferSource(); s.buffer = noise(); s.loop = true;
  const f = ctx.createBiquadFilter(); f.type = filt; f.Q.value = q;
  const t = ctx.currentTime;
  f.frequency.setValueAtTime(f0, t); f.frequency.exponentialRampToValueAtTime(Math.max(30, f1), t + dur);
  const g = ctx.createGain(); env(g, t, 0.004, dur, vol);
  s.connect(f); f.connect(g); g.connect(bus);
  s.start(t); s.stop(t + dur + 0.05);
}

// ---------------------------------------------------------------- pentatonic helpers (D gong: gong D, shang E, jue F#, zhi A, yu B)
const PENTA = [146.83, 164.81, 185.00, 220.00, 246.94];   // D3 E3 F#3 A3 B3
function pnote(deg, oct = 0) { const i = ((deg % 5) + 5) % 5; return PENTA[i] * Math.pow(2, oct + Math.floor(deg / 5)); }
let zhengGain = null, xiaoGain = null;
// guzheng pluck: three decaying partials + a short pick transient
function pluck(f, vol = 0.18, dur = 1.1, bus = null) {
  const b = bus || zhengGain || sfxBus; const t = ctx.currentTime;
  for (const [mult, v, d] of [[1, 1, dur], [2, 0.42, dur * 0.5], [3, 0.18, dur * 0.3]]) {
    const o = ctx.createOscillator(); o.type = 'triangle'; o.frequency.value = f * mult;
    const g = ctx.createGain(); g.gain.setValueAtTime(vol * v, t); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    o.connect(g); g.connect(b); o.start(t); o.stop(t + d + 0.05);
  }
  const s = ctx.createBufferSource(); s.buffer = noise();
  const bf = ctx.createBiquadFilter(); bf.type = 'bandpass'; bf.frequency.value = Math.min(12000, f * 4); bf.Q.value = 2;
  const ng = ctx.createGain(); ng.gain.setValueAtTime(vol * 0.5, t); ng.gain.exponentialRampToValueAtTime(0.0001, t + 0.04);
  s.connect(bf); bf.connect(ng); ng.connect(b); s.start(t); s.stop(t + 0.1);
}
// xiao (bamboo flute): sine with slow attack, vibrato and a little breath noise
function xiao(f, dur = 2.4, vol = 0.09, bus = null) {
  const b = bus || xiaoGain || sfxBus; const t = ctx.currentTime;
  const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f;
  const lfo = ctx.createOscillator(); lfo.frequency.value = 5.2; const lg = ctx.createGain(); lg.gain.value = f * 0.006; lfo.connect(lg); lg.connect(o.frequency);
  const br = ctx.createBufferSource(); br.buffer = noise(); br.loop = true;
  const bf = ctx.createBiquadFilter(); bf.type = 'bandpass'; bf.frequency.value = f * 2; bf.Q.value = 6;
  const bg = ctx.createGain(); bg.gain.value = 0.25;
  const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol, t + 0.35);
  g.gain.setValueAtTime(vol, t + Math.max(0.4, dur - 0.5)); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
  o.connect(g); br.connect(bf); bf.connect(bg); bg.connect(g); g.connect(b);
  lfo.start(t); o.start(t); br.start(t); o.stop(t + dur + 0.1); lfo.stop(t + dur + 0.1); br.stop(t + dur + 0.1);
}
// temple bell: inharmonic partials with long decay
function bell(f = 392, vol = 0.3, dur = 2.6, bus = null) {
  const b = bus || sfxBus; const t = ctx.currentTime;
  for (const [mult, v, d] of [[1, 1, dur], [1.5, 0.5, dur * 0.7], [2.68, 0.35, dur * 0.45], [4.02, 0.18, dur * 0.3]]) {
    const o = ctx.createOscillator(); o.type = 'sine'; o.frequency.value = f * mult;
    const g = ctx.createGain(); g.gain.setValueAtTime(0.0001, t); g.gain.exponentialRampToValueAtTime(vol * v, t + 0.01); g.gain.exponentialRampToValueAtTime(0.0001, t + d);
    o.connect(g); g.connect(b); o.start(t); o.stop(t + d + 0.05);
  }
}

// ---------------------------------------------------------------- sfx
const SFX = {
  swing() { burst(0.16, 0.25, 'bandpass', 900, 2400, 1.2); },
  sword() { tone('triangle', 2200, 4600, 0.12, 0.14); burst(0.14, 0.18, 'highpass', 2500, 6500, 1); },                       // flying sword: bright sweep
  talisman() { tone('sine', 320, 120, 0.18, 0.16); [0, 40, 90].forEach((ms) => setTimeout(() => burst(0.05, 0.22, 'highpass', 3000, 5200, 1), ms)); },  // paper burning crackle
  pearl() { tone('sine', 1760, 1760, 0.28, 0.1); tone('sine', 2637, 2637, 0.18, 0.05); },                                    // small bell
  bow() { burst(0.12, 0.25, 'bandpass', 600, 3200, 1); tone('triangle', 180, 90, 0.1, 0.14); },                              // string twang
  cord() { burst(0.2, 0.3, 'bandpass', 700, 200, 1.5); tone('square', 140, 70, 0.15, 0.1); },                                // rope and rings
  heavy() { burst(0.32, 0.45, 'lowpass', 1800, 200, 0.7); tone('triangle', 1400, 200, 0.3, 0.2); tone('sine', 180, 60, 0.3, 0.3); },
  hit() { burst(0.08, 0.3, 'bandpass', 1800, 500, 1.5); tone('square', 220, 90, 0.07, 0.12); },
  crit() { burst(0.12, 0.4, 'highpass', 1200, 3000, 1); tone('triangle', 660, 220, 0.15, 0.2); },
  kill() { burst(0.22, 0.35, 'lowpass', 1400, 120, 0.8); tone('sawtooth', 160, 40, 0.25, 0.12); },
  ember() { tone('sine', 880, 1320, 0.09, 0.18); },                                                                          // spirit stone
  shard() { tone('sine', 1568, 1568, 0.18, 0.16); tone('sine', 2489, 2489, 0.14, 0.09); tone('sine', 3520, 3520, 0.1, 0.05); },   // spirit crystal
  heart() { tone('sine', 1046, 1568, 0.12, 0.2); tone('sine', 392, 392, 0.3, 0.14); },                                        // elixir pill
  hurt() { burst(0.18, 0.5, 'lowpass', 600, 80, 0.5); tone('sine', 120, 50, 0.2, 0.4); },
  dash() { burst(0.22, 0.32, 'bandpass', 500, 3200, 0.6); },                                                                  // cloud step
  nova() { burst(0.7, 0.7, 'lowpass', 3000, 100, 0.4); tone('sine', 90, 30, 0.7, 0.6); bell(784, 0.2, 1.4); },                // spirit burst
  levelup() { bell(392, 0.32, 2.8); [0, 3, 4, 5].forEach((d, i) => setTimeout(() => pluck(pnote(d, 1), 0.2, 1.0, sfxBus), 120 + i * 110)); },   // breakthrough: bell + rising run
  forge() { tone('square', 660, 660, 0.08, 0.15); setTimeout(() => { burst(0.2, 0.35, 'highpass', 3000, 6000, 1); bell(1568, 0.16, 0.9); }, 80); },
  spit() { burst(0.16, 0.25, 'bandpass', 350, 900, 2); tone('sine', 240, 90, 0.12, 0.1); },                                    // toad venom
  roar() { tone('sawtooth', 70, 45, 1.4, 0.5); burst(1.2, 0.5, 'lowpass', 500, 120, 0.4); },
  slam() { burst(0.08, 0.9, 'highpass', 4000, 900, 1); burst(0.5, 0.8, 'lowpass', 900, 60, 0.5); tone('sine', 60, 25, 0.6, 0.8); },   // tribulation lightning
  ui() { tone('sine', 740, 740, 0.06, 0.12); },
  district() { [0, 3, 6].forEach((d, i) => setTimeout(() => pluck(pnote(d, 1), 0.22, 1.2, sfxBus), i * 130)); },               // three pentatonic notes
  thunder() { burst(0.12, 0.7, 'highpass', 3000, 700, 1, ambBus); burst(2.2, 0.9, 'lowpass', 700, 40, 0.3, ambBus); setTimeout(() => burst(1.4, 0.5, 'lowpass', 300, 40, 0.3, ambBus), 300); },
  win() { bell(392, 0.3, 3.2); [0, 1, 2, 3, 4, 5].forEach((d, i) => setTimeout(() => pluck(pnote(d, 1), 0.22, 1.3, sfxBus), 150 + i * 150)); },
  lose() { [4, 3, 1, 0].forEach((d, i) => setTimeout(() => xiao(pnote(d, 1), 1.4, 0.16, sfxBus), i * 420)); },
};
let lastAt = {};
export function sfx(name, minGap = 0.03) {
  if (!ctx || !enabled) return;
  const now = ctx.currentTime;
  if (lastAt[name] && now - lastAt[name] < minGap) return;
  lastAt[name] = now;
  try { SFX[name](); } catch (e) { if (window.__emberLog) window.__emberLog('sfx', name + ': ' + e.message); }
}

// ---------------------------------------------------------------- ambience (rain / wind), driven by weather each frame
function startAmbience() {
  const s = ctx.createBufferSource(); s.buffer = noiseBuffer(4); s.loop = true;
  const f = ctx.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 2400; f.Q.value = 0.5;
  rainGain = ctx.createGain(); rainGain.gain.value = 0;
  s.connect(f); f.connect(rainGain); rainGain.connect(ambBus); s.start();
  rainNode = f;
  const w = ctx.createBufferSource(); w.buffer = noiseBuffer(4); w.loop = true;
  const wf = ctx.createBiquadFilter(); wf.type = 'lowpass'; wf.frequency.value = 320; wf.Q.value = 0.7;
  windGain = ctx.createGain(); windGain.gain.value = 0;
  w.connect(wf); wf.connect(windGain); windGain.connect(ambBus); w.start();
  const lfo = ctx.createOscillator(); lfo.frequency.value = 0.11; const lg = ctx.createGain(); lg.gain.value = 120;
  lfo.connect(lg); lg.connect(wf.frequency); lfo.start();
}
export function setAmbience(rain, wind) {
  if (!rainGain) return;
  const t = ctx.currentTime;
  rainGain.gain.setTargetAtTime(rain * 0.5, t, 0.8);
  windGain.gain.setTargetAtTime(wind * 0.35, t, 1.2);
}

// ---------------------------------------------------------------- music: pentatonic pad + guzheng + xiao, mode shifts with tension
// chords as scale degrees; gong mode (calm) rooted on D, yu mode (danger) rooted on B
const CHORDS_GONG = [[0, 3, 6, 9], [1, 4, 8, 10], [3, 6, 9, 11], [0, 4, 6, 8]];
const CHORDS_YU = [[-1, 1, 3, 4], [-1, 2, 4, 6], [-3, -1, 1, 4], [-1, 0, 3, 6]];
let padOsc = [], padFilter = null, chordIdx = 0, tension = 0, beat = 0;
let bassGain = null, arpGain = null, layerTargets = { zheng: 0, xiao: 0, bass: 0, arp: 0 };
function chordSet() { return tension >= 0.45 ? CHORDS_YU : CHORDS_GONG; }
function startMusic() {
  padFilter = ctx.createBiquadFilter(); padFilter.type = 'lowpass'; padFilter.frequency.value = 520; padFilter.Q.value = 0.5;
  const padGain = ctx.createGain(); padGain.gain.value = 0.2;
  padFilter.connect(padGain); padGain.connect(musicBus);
  const lfo = ctx.createOscillator(); lfo.frequency.value = 0.06; const lg = ctx.createGain(); lg.gain.value = 180;
  lfo.connect(lg); lg.connect(padFilter.frequency); lfo.start();
  for (let i = 0; i < 4; i++) {
    for (const det of [-5, 5]) {
      const o = ctx.createOscillator(); o.type = i % 2 ? 'triangle' : 'sine'; o.detune.value = det;
      const g = ctx.createGain(); g.gain.value = 0.11;
      o.connect(g); g.connect(padFilter); o.start();
      padOsc.push({ o, g, voice: i });
    }
  }
  zhengGain = ctx.createGain(); zhengGain.gain.value = 0.22; zhengGain.connect(musicBus);
  xiaoGain = ctx.createGain(); xiaoGain.gain.value = 0.09; xiaoGain.connect(musicBus);
  // danger layer: low drum pulse
  bassGain = ctx.createGain(); bassGain.gain.value = 0; bassGain.connect(musicBus);
  const bass = ctx.createOscillator(); bass.type = 'sine'; bass.frequency.value = 55;
  const bassEnv = ctx.createGain(); bassEnv.gain.value = 0.4;
  const pulse = ctx.createOscillator(); pulse.type = 'square'; pulse.frequency.value = 2; const pg = ctx.createGain(); pg.gain.value = 0.35;
  pulse.connect(pg); pg.connect(bassEnv.gain);
  bass.connect(bassEnv); bassEnv.connect(bassGain); bass.start(); pulse.start();
  // tribulation layer: fast zheng run
  arpGain = ctx.createGain(); arpGain.gain.value = 0; arpGain.connect(musicBus);
  layerTargets = { zheng: 0.22, xiao: 0.09, bass: 0, arp: 0 };
  setInterval(() => {
    if (!ctx || !enabled) return;
    beat++;
    const ch = chordSet()[chordIdx];
    // guzheng phrase: sparse in calm, denser under threat
    const density = tension >= 0.9 ? 0.25 : tension >= 0.45 ? 0.45 : 0.55;
    if (Math.random() < density && layerTargets.zheng > 0) pluck(pnote(ch[Math.floor(Math.random() * ch.length)] + (Math.random() < 0.3 ? 1 : 0), Math.random() < 0.35 ? 2 : 1), 1, 0.9 + Math.random() * 0.6);
    // xiao: a long note every few beats while calm
    if (beat % 5 === 0 && layerTargets.xiao > 0 && Math.random() < 0.7) xiao(pnote(ch[1 + Math.floor(Math.random() * 3)], 2), 2.2 + Math.random() * 1.2, 1);
    // tribulation run: eighth-note plucks climbing the chord
    if (layerTargets.arp > 0) { for (let k = 0; k < 2; k++) setTimeout(() => pluck(pnote(ch[(beat * 2 + k) % ch.length], 1 + ((beat >> 2) % 2)), 1, 0.35, arpGain), k * 260); }
  }, 520);
  setChord(0);
  musicTimer = setInterval(() => setChord((chordIdx + 1) % 4), 8000);
}
export function layerState() { return Object.assign({}, layerTargets, { tension, mode: tension >= 0.45 ? 'yu' : 'gong' }); }
function setChord(i) {
  chordIdx = i;
  const t = ctx.currentTime;
  const ch = chordSet()[i];
  for (const p of padOsc) p.o.frequency.setTargetAtTime(pnote(ch[p.voice], 0) * (tension >= 0.9 ? 0.5 : 1), t, 1.5);
}
export function setTension(v) {
  // 0..1 - threat / low health / boss: mode shift, pad opens, drum and zheng-run layers
  const wasMode = tension >= 0.45; tension = v;
  if (!padFilter) return;
  padFilter.frequency.setTargetAtTime(520 + v * 1400, ctx.currentTime, 2);
  layerTargets = v >= 0.9 ? { zheng: 0.1, xiao: 0, bass: 0.2, arp: 0.14 } : v >= 0.45 ? { zheng: 0.16, xiao: 0, bass: 0.16, arp: 0 } : { zheng: 0.22, xiao: 0.09, bass: 0, arp: 0 };
  zhengGain.gain.setTargetAtTime(layerTargets.zheng, ctx.currentTime, 1.0);
  xiaoGain.gain.setTargetAtTime(layerTargets.xiao, ctx.currentTime, 1.0);
  bassGain.gain.setTargetAtTime(layerTargets.bass, ctx.currentTime, 1.5);
  arpGain.gain.setTargetAtTime(layerTargets.arp, ctx.currentTime, 1.0);
  if (wasMode !== (v >= 0.45)) setChord(chordIdx);
}
export function musicVolume(v) { if (musicBus) musicBus.gain.setTargetAtTime(v, ctx.currentTime, 0.5); }
export function sfxVolume(v) { if (sfxBus) sfxBus.gain.setTargetAtTime(v, ctx.currentTime, 0.1); }
