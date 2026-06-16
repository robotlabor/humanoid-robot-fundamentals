#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from stable_baselines3 import PPO
from envs.g1_fixed_body_throw_env import G1FixedBodyThrowEnv
if __name__=='__main__':
    env=G1FixedBodyThrowEnv(xml_path=str(ROOT/'assets'/'unitree_g1'/'scene_throw.xml')); model=PPO.load(str(ROOT/'policies'/'g1_fixed_body_throw_ppo.zip'))
    best=[]; final=[]
    for _ in range(50):
        obs,_=env.reset(); done=False; info={}
        while not done:
            action,_=model.predict(obs,deterministic=True); obs,reward,terminated,truncated,info=env.step(action); done=terminated or truncated
        best.append(info.get('best_dist',np.inf)); final.append(info.get('dist_to_target',np.inf))
    best=np.array(best); final=np.array(final)
    print('G1 fixed-body throw evaluation'); print('-----------------------------')
    print(f'Mean best distance:   {best.mean():.3f} m'); print(f'Median best distance: {np.median(best):.3f} m'); print(f'Hit rate < 50 cm:     {100*np.mean(best<0.50):.1f}%'); print(f'Hit rate < 30 cm:     {100*np.mean(best<0.30):.1f}%')
