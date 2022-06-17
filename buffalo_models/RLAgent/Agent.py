import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import random
import string

from pychain_utils import download
from stable_baselines.ppo1 import PPO1

from TicTacToeEnv import TicTacToeEnv


ENV_NAME_TO_CLS = {
    'TicTacToeEnv': TicTacToeEnv
}


def load_model(env, name):
    path = download(name)
    filename = os.path.join(path, env.name, name)
    if os.path.exists(filename):
        logger.info(f'Loading {name}')
        cont = True
        while cont:
            try:
                ppo_model = PPO1.load(filename, env=env)
                cont = False
            except Exception as e:
                time.sleep(5)
                print(e)

    else:
        raise Exception(f'\n{filename} not found')

    return ppo_model


def sample_action(action_probs):
    action = np.random.choice(len(action_probs), p = action_probs)
    return action


def mask_actions(legal_actions, action_probs):
    masked_action_probs = np.multiply(legal_actions, action_probs)
    masked_action_probs = masked_action_probs / np.sum(masked_action_probs)
    return masked_action_probs


class Agent():
    def __init__(self, name=None, env_name=None, weights_path=None):
        self.name = name
        self.env_name = env_name
        self.env = None
        if self.env_name:
            self.env = ENV_NAME_TO_CLS.get(env_name)()
        self.id = self.name + '_' + ''.join(random.choice(string.ascii_lowercase) for x in range(5))
        self.weights_path = weights_path
        self.model = None
        if self.weights_path and self.env
            self.model = load_model(self.env, weights_path)
        self.points = 0

    def return_top_actions(self, action_probs):
        top5_action_idx = np.argsort(-action_probs)[:5]
        top5_actions = action_probs[top5_action_idx]
        return top5_actions

    def choose_action(self, env, choose_best_action, mask_invalid_actions):
        if self.name == 'rules':
            action_probs = np.array(env.rules_move())
            value = None
        else:
            action_probs = self.model.action_probability(env.observation)
            value = self.model.policy_pi.value(np.array([env.observation]))[0]

        top5_actions = self.return_top_actions(action_probs)

        if mask_invalid_actions:
            action_probs = mask_actions(env.legal_actions, action_probs)
            top5_actions = self.return_top_actions(action_probs)

        action = np.argmax(action_probs)

        if not choose_best_action:
            action = sample_action(action_probs)

        return action

    def run(self, address, game_id, seed=123):
        self.env.seed(seed)

        _ = self.env.reset(address=address, game_id=game_id)

        action = self.choose_action(self.env, choose_best_action=True, mask_invalid_actions=True)

        #obs, reward, done, _ = env.step(action)

        return action
