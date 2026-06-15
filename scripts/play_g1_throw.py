#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import time, mujoco, mujoco.viewer
from stable_baselines3 import PPO
from envs.g1_fixed_body_throw_env import G1FixedBodyThrowEnv
if __name__=='__main__':
    env=G1FixedBodyThrowEnv(xml_path=str(ROOT/'assets'/'unitree_g1_throw'/'scene_throw.xml'))
    path=ROOT/'policies'/'g1_fixed_body_throw_ppo.zip'
    if not path.exists(): raise FileNotFoundError('Train first with: python scripts/train_g1_throw.py')
    model=PPO.load(str(path)); obs,info=env.reset()
    with mujoco.viewer.launch_passive(env.model,env.data) as viewer:
        while viewer.is_running():
            action,_=model.predict(obs,deterministic=True); obs,reward,terminated,truncated,info=env.step(action); viewer.sync(); time.sleep(env.control_dt)
            if terminated or truncated: print(info); obs,info=env.reset()
