import * as THREE from 'three';
import { ctx, clamp, lerp, seg, eo, eio, eob } from './core/lib.js';
import { L, Wd, T } from './core/timing.js';
import { camera } from './core/engine.js';
import * as WD from './core/world.js';
import * as PR from './core/props.js';
import { Toon, PROPS } from './core/toon.js';

const V3 = (x, y, z) => new THREE.Vector3(x, y, z);
const mix = (a, b, k) => a.clone().lerp(b, k);
const talk = (t, on = 1) => (on ? 0.25 + 0.75 * Math.abs(Math.sin(t * 13)) * (0.6 + 0.4 * Math.sin(t * 5.3)) : 0);
const blink = (t, off = 0) => (((t + off) % 3.3) < 0.12 ? 1 : 0);

const LOOK = {
  hero: { body: '#7FC8E8', hat: 'bow', hatCol: '#D8343F', hairCol: '#7A4A2E', kid: true, neck: 'collar' },
};
const person = (k, opts) => new Toon({ ...LOOK[k], extra: [...(LOOK[k].extra || [])] }, opts);

export function buildShots(E) {
  const S = [], CUES = [], add = (o) => (S.push(o), o), cue = (t, type, o = {}) => CUES.push({ t: +t.toFixed(3), type, ...o });
  const cut = (i) => (i === 0 ? 0 : L(i) - 0.06);
  const cam = camera(36);
  const LOOKS = { room: { bloom: 0.3, aperture: 0.001, maxblur: 0.008 } };

  const IN = WD.interior(E, { wall: '#2F6B5A', motif: '#3B7D69', ceiling: '#5A3A2A', signText: 'PORTAL ROOM', picture: false });
  const hero = person('hero');
  IN.scene.add(hero.group);

  // 4 lines total
  // Line 0: What if scrolling for just two minutes before getting up
  // Line 1: accidentally opens a doorway into another world?
  // Line 2: Where one extra video costs thirty real world minutes
  // Line 3: before you finally snap back.

  { const st = cut(0);
    add({ id: 'S01', at: st, note: 'Sitting on the edge of the bed with a phone', draw(lt, d, t, blit) {
      const k = eio(clamp(lt / d));
      hero.at(0, 0, -2);
      shoot_scene(IN.scene, [hero], V3(0, 2, 2), V3(0, 1.5, -2), k);
      blit();
    } });
    cue(st, 'whoosh');
  }

  { const st = cut(1);
    add({ id: 'S02', at: st, note: 'Tapping one more video pulls you through a doorway', draw(lt, d, t, blit) {
      const k = eio(clamp(lt / d));
      hero.at(0, 0, -2);
      shoot_scene(IN.scene, [hero], V3(0, 2, 1), V3(0, 1.5, -2), k);
      blit();
    } });
    cue(st, 'whoosh');
  }

  { const st = cut(2);
    add({ id: 'S03', at: st, note: 'Surreal tall-tale doorway where time warps fast', draw(lt, d, t, blit) {
      const k = eio(clamp(lt / d));
      hero.at(0, 0, -2);
      shoot_scene(IN.scene, [hero], V3(1, 2, 0), V3(0, 1.5, -2), k);
      blit();
    } });
    cue(st, 'whoosh');
  }

  { const st = cut(3);
    add({ id: 'S04', at: st, note: 'Snapping back realizing thirty minutes vanished', draw(lt, d, t, blit) {
      const k = eio(clamp(lt / d));
      hero.at(0, 0, -2);
      shoot_scene(IN.scene, [hero], V3(0, 2, 2), V3(0, 1.5, -2), k);
      blit();
    } });
    cue(st, 'whoosh');
  }

  function shoot_scene(scene, people, from, at, k) {
    cam.position.copy(from);
    cam.lookAt(at);
    people.forEach((p) => p.face(cam));
    E.render(scene, cam, LOOKS.room);
  }

  return { shots: S, cues: CUES };
}
