#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from envs.three_link_throw_env import ThreeLinkThrowEnv

def make_env(rank, learned_release=False):
    def _init(): return ThreeLinkThrowEnv(xml_path=str(ROOT/'assets'/'three_link_throw.xml'), learned_release=learned_release)
    return _init
if __name__ == '__main__':
    check_env(make_env(0)(), warn=True); num_envs=4; learned_release=False
    env=DummyVecEnv([make_env(0,learned_release)]) if num_envs==1 else SubprocVecEnv([make_env(i,learned_release) for i in range(num_envs)])
    model=PPO('MlpPolicy',env,learning_rate=3e-4,n_steps=128,batch_size=256,gamma=0.98,gae_lambda=0.95,clip_range=0.2,policy_kwargs=dict(net_arch=[128,128]),verbose=1,tensorboard_log=str(ROOT/'logs'/'tb'))
    (ROOT/'policies').mkdir(exist_ok=True)
    try: model.learn(total_timesteps=300_000)
    except KeyboardInterrupt: print('\nTraining interrupted. Saving current policy...')
    model.save(str(ROOT/'policies'/'three_link_throw_ppo')); print('Saved policy to policies/three_link_throw_ppo.zip')
