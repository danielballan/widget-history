import time
import IPython.html.widgets
from IPython.display import display


class WidgetHistory:
    """
    With a button click, save the state of all other widgets to a file.
    Review past states using a slider.
    
    Parameters
    ----------
    history : history.History
        a dictionary-like object that retains the history of each key,
        backed by a sqlite db
    widgets : list, optional
        list of widgets to capture; if None, use all Widget instances
    """
    def __init__(self, history, widgets=None):
        self._history = history
        self._widgets = widgets
        self._state_key = 'WIDGET_STATE'
        
        # History slider
        self.slider = IPython.html.widgets.IntSlider()
        self.slider.max = 0
        self.slider.min = 0
        self.slider.description = 'history'
        self.slider.on_trait_change(self.load_state, 'value')
        self._locate_beginning()

        # Save button
        def save_callback(_):
            return self.save_all_widgets()
        
        self.save_button = IPython.html.widgets.Button()
        self.save_button.on_click(save_callback)
        self.save_button.description = 'Save State'
    
        # Playback button
        def play_callback(_):
            return self.playback(1)
        
        self.play_button = IPython.html.widgets.Button()
        self.play_button.on_click(play_callback)
        self.play_button.description = 'Playback'

        # boxed group of widgets
        self.box = IPython.html.widgets.HBox([self.slider, self.save_button, self.play_button])
        
    @property
    def widgets(self):
        if self._widgets is not None:
            return self._widgets
        else:
            return IPython.html.widgets.Widget.__dict__['widgets']
    
    @widgets.setter
    def widgets(self, val):
        self._widgets = val
        
    def load_state(self, _):
        state = self._history.past(self._state_key, -self.slider.value)
        for model_id, widget in list(self.widgets.items()):
            if model_id == self.slider.model_id:
                # Don't manipulate the history widget itself, of course.
                continue
            if model_id not in state:
                # No state has been saved for this widget at this point in
                # history.
                continue
            for key, value in state[model_id].items():
                setattr(widget, key, value)

    def save_all_widgets(self):
        state = {}
        for key, w in self.widgets.items():
            state[key] = w.get_state()
            if key == self.slider.model_id:
                continue
        self._history[self._state_key] = state
        self._locate_beginning()
        self.slider.value = 0
        
    def playback(self, delay, step=1):
        while not (self.slider.value > -1):
            self.slider.value += step
            time.sleep(delay)
    
    def _locate_beginning(self):
        while True:
            try:
                self._history.past(self._state_key, -self.slider.min + 1)
            except ValueError:
                break
            except KeyError:
                # no value self._state_key
                break
            else:
                self.slider.min -= 1
        self.slider.disabled = self.slider.min == 0

    def _repr_html_(self):
        display(self.box)
