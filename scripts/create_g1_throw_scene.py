#!/usr/bin/env python3
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[1]
BALL_XML='''
    <body name="throw_ball" pos="0.35 -0.30 1.20">
      <freejoint name="throw_ball_free"/>
      <geom name="throw_ball_geom" type="sphere" size="0.045" mass="0.08" rgba="0.9 0.2 0.1 1"/>
    </body>
    <body name="throw_target" pos="2.0 -0.25 1.0">
      <geom name="throw_target_geom" type="sphere" size="0.10" contype="0" conaffinity="0" rgba="0.1 0.8 0.2 0.45"/>
    </body>
'''
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--hand-body',required=True); args=ap.parse_args()
    src=ROOT/'assets'/'unitree_g1'/'scene.xml'; out=ROOT/'assets'/'unitree_g1_throw'/'scene_throw.xml'
    if not src.exists(): raise FileNotFoundError('Copy Unitree G1 assets to assets/unitree_g1 first.')
    text=src.read_text(encoding='utf-8')
    if '</worldbody>' not in text or '</mujoco>' not in text: raise RuntimeError('Could not find required MJCF closing tags.')
    text=text.replace('</worldbody>',BALL_XML+'\n  </worldbody>',1)
    eq=f'''
  <equality>
    <weld name="hold_throw_ball" body1="{args.hand_body}" body2="throw_ball" relpose="0.08 0 0 1 0 0 0" active="true" solref="0.002 1" solimp="0.95 0.99 0.001"/>
  </equality>
'''
    text=text.replace('</mujoco>',eq+'\n</mujoco>',1); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding='utf-8')
    print(f'Wrote: {out}')
    print("Test with: python -c \"import mujoco; mujoco.MjModel.from_xml_path('assets/unitree_g1_throw/scene_throw.xml'); print('G1 throw XML OK')\"")
if __name__=='__main__': main()
