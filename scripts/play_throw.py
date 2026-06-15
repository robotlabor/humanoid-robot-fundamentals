#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import time, mujoco, mujoco.viewer
from stable_baselines3 import PPO
from envs.three_link_throw_env import ThreeLinkThrowEnv
if __name__ == '__main__':
    env=ThreeLinkThrowEnv(xml_path=str(ROOT/'assets'/'three_link_throw.xml'))
    model_path=ROOT/'policies'/'three_link_throw_ppo.zip'
    if not model_path.exists(): raise FileNotFoundError('Train first with: python scripts/train_throw.py')
    model=PPO.load(str(model_path)); obs,info=env.reset()
    with mujoco.viewer.launch_passive(env.model,env.data) as viewer:
        while viewer.is_running():
            action,_=model.predict(obs,deterministic=True); obs,reward,terminated,truncated,info=env.step(action); viewer.sync(); time.sleep(env.control_dt)
            if terminated or truncated: print(info); obs,info=env.reset()
