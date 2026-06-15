#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import time, numpy as np, mujoco, mujoco.viewer
from envs.three_link_throw_env import ThreeLinkThrowEnv
if __name__ == '__main__':
    env=ThreeLinkThrowEnv(xml_path=str(ROOT/'assets'/'three_link_throw.xml')); obs,info=env.reset()
    with mujoco.viewer.launch_passive(env.model,env.data) as viewer:
        while viewer.is_running():
            t=env.step_count*env.control_dt
            action=np.array([np.sin(4*t),np.sin(5*t+0.8),np.sin(6*t+1.5),0.0],dtype=np.float32)
            obs,reward,terminated,truncated,info=env.step(action); viewer.sync(); time.sleep(env.control_dt)
            if terminated or truncated: print(info); obs,info=env.reset()
