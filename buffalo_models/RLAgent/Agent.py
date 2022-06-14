import sys
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
import random
import string


def sample_action(action_probs):
    action = np.random.choice(len(action_probs), p = action_probs)
    return action


def mask_actions(legal_actions, action_probs):
    masked_action_probs = np.multiply(legal_actions, action_probs)
    masked_action_probs = masked_action_probs / np.sum(masked_action_probs)
    return masked_action_probs
    

class Agent():
    def __init__(self, name, model = None):
        self.name = name
        self.id = self.name + '_' + ''.join(random.choice(string.ascii_lowercase) for x in range(5))
        self.model = model
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