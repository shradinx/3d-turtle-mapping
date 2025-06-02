from ursina import *
import async_util as au


def get_buttons(loop):
    for k, v in au.buttonActions.items():
        yield Button(
            text=v,
            scale=(0.25, 0.075),
            on_click=lambda k=k: au.sendActionAsync(au.sendAction(k), loop)
        )


def get_wip_buttons():
    for k, v in au.WIP_actions.items():
        yield Button(
            text=v,
            scale=(0.25, 0.075)
            # on_click=lambda k=k: sendActionAsync(sendAction(k), loop)
        )


action_text = {}


def populate_action_text():
    action_text.update({
        (-0.54, 0): Text(text="Use W,S for forward/back movement...", scale=1),
        (-0.55, 0): Text(text="Use A,S for left/right rotation...", scale=1)
    })


def get_action_text():
    return action_text


def center_action_text():
    for k, v in action_text.items():
        v.origin = k


""" 
WIP Buttons -> WindowPanel.content

Text(text="WIP Buttons", origin=(0, 0), scale=1),
*get_wip_buttons() 
"""
