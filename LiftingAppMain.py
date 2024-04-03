import pandas as pd
from kivy.app import App
from kivy.uix.textinput import TextInput
import math
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
import os

class Main(object):
    
    def __init__(self):
        self._day = int(pd.read_csv('currentday.csv').iloc[0][0])
        try:
            self._rep_df = pd.read_csv('rep_tracker.csv', index_col=[0,1])

        except:
            cols = []
            for i in range(4):
                w, _ = self.get_todays_arrays(i)
                cols += w
            cols = set(cols)
            cols = list(cols)
            
            indexes = [*range(len(self.days))]*2
            indexes.sort()
            wr = ['weight', 'reps']*len(self.days)
            arrays = [indexes, wr]
            tuples = list(zip(*arrays))
            index = pd.MultiIndex.from_tuples(tuples, names=['first', 'second'])
            self._rep_df = pd.DataFrame(float(0), index=index, columns = cols)
            self._rep_df.to_csv('rep_tracker.csv')
        

    def getWorkout():
        df = pd.read_excel("Hypertrophy_Program_3_6_24.xlsx")
        df.columns = range(1,65)
        df.index = df.index + 2
        days = []
        for d in range(0,20):
            days.append({})
            for w in range(1,9):
                try:
                    if math.isnan(df.loc[w+11,4+3*d]):
                        break
                    days[d].update({df.loc[w+11,3+3*d]: df.loc[w+11,4+3*d]})
                except:
                    break
        return days  

    days = getWorkout()     

    def get_day(self):
        return self._day
    
    def set_day(self, val):
        self._day = val
        main.day_tracker()

    day = property(get_day, set_day)

    def get_todays_arrays(self, day):
        today = Main.days[day]
        workouts = list(today.keys())
        sets = list(today.values())
        return workouts, sets

    def day_tracker(self):
        df = pd.DataFrame(data = [main.day])
        df.to_csv('currentday.csv', index = False)

    def set_reps(self, day, workout, value, worr):
        self._rep_df.at[(day, worr), workout] = float(value)
        self._rep_df.to_csv('rep_tracker.csv')


    def get_reps(self, day, workout, worr):
        return self._rep_df.loc[(day, worr), workout]
        


class IntroWindow(Screen):
    def goto_day(self):
        chosenday = self.ids.specific_workout.text
        try:
            main.day = int(chosenday)-2
            lam.nextDay()
            sm.current = 'main'
        except:
            self.ids.input_label.text = 'Input must be an integer: '

class SecondWindow(Screen):

    def previousDay(self):
        sm.current = 'main'

    def reset_csv(self):
        os.remove('rep_tracker.csv')
        cols = []
        for i in range(4):
            w, _ = main.get_todays_arrays(i)
            cols += w
        cols = set(cols)
        cols = list(cols)
        
        indexes = [*range(len(main.days))]*2
        indexes.sort()
        wr = ['weight', 'reps']*len(main.days)
        arrays = [indexes, wr]
        tuples = list(zip(*arrays))
        index = pd.MultiIndex.from_tuples(tuples, names=['first', 'second'])
        main._rep_df = pd.DataFrame(float(0), index=index, columns = cols)
        main._rep_df.to_csv('rep_tracker.csv')

    def to_stats(self):
        sm.current = 'stats'
        stats.fill_main_stats_block()

class StatsWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fill_main_stats_block()
    current = 0

    def fill_main_stats_block(self):
        self.ids.main_stats.clear_widgets()
        w, _ = main.get_todays_arrays(self.current)
        for i, wo in enumerate(w):
            self.ids.main_stats.add_widget(Label(
                text = wo,
                size_hint = (.2, .075),
                pos_hint = {'x':.1, 'y': .7 - (.075*i)},
            ))
            df_length = (main._rep_df.index.size/2 ) - 4 + self.current
            #Fill weight differences:
            weight_dif = (float(main.get_reps(df_length, wo, 'weight')) - float(main.get_reps(0, wo, 'weight'))) * 100
            if weight_dif > 0:
                self.ids.main_stats.add_widget(Label(
                    text = '+' + str(weight_dif) + '%',
                    size_hint = (.2, .075),
                    pos_hint = {'x':.3, 'y': .7 - (.075*i)},
                    color= 'green'
                ))
            else:
                self.ids.main_stats.add_widget(Label(
                    text = str(weight_dif) + '%',
                    size_hint = (.2, .075),
                    pos_hint = {'x':.3, 'y': .7 - (.075*i)},
                    color= 'red'
                ))
                #Fill Rep Differences:
            rep_dif = (float(main.get_reps(df_length, wo, 'reps')) - float(main.get_reps(0, wo, 'reps'))) * 100
            if rep_dif > 0:
                self.ids.main_stats.add_widget(Label(
                    text = '+' + str(rep_dif) + '%',
                    size_hint = (.2, .075),
                    pos_hint = {'x':.5, 'y': .7 - (.075*i)},
                    color= 'green'
                ))
            else:
                self.ids.main_stats.add_widget(Label(
                    text = str(rep_dif) + '%',
                    size_hint = (.2, .075),
                    pos_hint = {'x':.5, 'y': .7 - (.075*i)},
                    color= 'red'
                ))

    def next_stat(self):
        if self.current >= 3:
            sm.current = 'second'
        else:
            self.current += 1
            self.fill_main_stats_block()

    def previous_stat(self):
        if self.current <= 0:
            sm.current = 'second'
        else:
            self.current -= 1
            self.fill_main_stats_block()

    
class LiftingAppMain(Screen):
    global main
    main = Main()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fill_main_block()

    def get_weekandday():
        weekandday = 'Week: ' + str(1+(math.floor((main.day)/4))) + ' Day: ' + (str((main.day+1)%4) if (main.day+1)%4 != 0 else '4')
        return weekandday
    
    weekandday = get_weekandday()
    
    def nextDay(self):
        if (main.day >= len(main.days)-1):
            sm.current = 'second'
        else:
            main.day += 1
            self.ids.header_label.text = LiftingAppMain.get_weekandday()
            self.fill_main_block()

    def previousDay(self):
        if (main.day == 0):
            sm.current = 'intro'
        else:
            main.day -= 1
            self.ids.header_label.text = LiftingAppMain.get_weekandday()
            self.fill_main_block()

    def fill_main_block(self):
        self.ids.main_block.clear_widgets()
        workouts, sets = main.get_todays_arrays(main.day)
        global weight_widgets
        global rep_widgets
        weight_widgets = []
        rep_widgets = []
        for i in range(len(workouts)):
            self.ids.main_block.add_widget(Label(text=workouts[i],
                                           size_hint = (.2,.075),
                                           pos_hint = {'x':.1, 'y': .7 - (.075*i)}))
            self.ids.main_block.add_widget(Label(text=str(sets[i]),
                                           size_hint = (.2,.075),
                                           pos_hint = {'x':.3, 'y': .7 - (.075*i)}))
    
            weight_input = TextInput()
            weight_input.id = str(i)
            weight_input.bind(on_text_validate = (lambda x: self.submit_weights(workouts)))
            weight_input.multiline = False
            weight_input.size_hint = (.2, .075)
            weight_input.pos_hint = {'x':.5, 'y': .7 - (.075*i)}
            if main.day > 3 and (main.get_reps(main.day - 4, workouts[i], 'weight') != 0):
                weight_input.text = str(main.get_reps(main.day-4, workouts[i], 'weight'))
            weight_widgets.append(weight_input)
            self.ids.main_block.add_widget(weight_input)

            rep_input = TextInput()
            rep_input.id = str(i)
            rep_input.bind(on_text_validate = (lambda x: self.submit_reps(workouts)))
            rep_input.multiline = False
            rep_input.size_hint = (.2, .075)
            rep_input.pos_hint = {'x':.7, 'y': .7 - (.075*i)}
            if main.day > 3 and (main.get_reps(main.day - 4, workouts[i], 'reps') != 0):
                rep_input.text = str(main.get_reps(main.day-4, workouts[i], 'reps'))
            rep_widgets.append(rep_input)
            self.ids.main_block.add_widget(rep_input)

            
            
    def submit_reps(self, workouts):
        for i, w in enumerate(rep_widgets):
            if w.text != '':
                try:
                    main.set_reps(main.day, workouts[i], float(w.text), 'reps')
                except:
                    w.text = 'Must be float value!'
        
    def submit_weights(self, workouts):
        for i, w in enumerate(weight_widgets):
            t = w.text
            if t != '':
                try:
                    main.set_reps(main.day, workouts[i], float(w.text), 'weight')
                except:
                    w.text = 'Must be float value!'



    
class LiftingApp(App):
    def build(self):
        global sm
        global lam
        global stats
        lam = LiftingAppMain(name = 'main')
        sm = ScreenManager()
        stats = StatsWindow(name = 'stats')
        sm.add_widget(IntroWindow(name = 'intro'))
        sm.add_widget(lam)
        sm.add_widget(SecondWindow(name = 'second'))
        sm.add_widget(stats)
        return sm

if __name__ == "__main__":
    LiftingApp().run()