from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QShortcut
from scipy.signal import freqz, lfilter, zpk2tf, filtfilt
from gui import Ui_MainWindow
import numpy as np
import pyqtgraph as pg
from scipy.signal import freqz
import pandas as pd
import os
import scipy
import scipy.signal
import math
from numpy import *
from numpy.random import *
from scipy.signal import *

class DigitalFilterDesigner(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(DigitalFilterDesigner, self).__init__()
        self.setupUi(self)
        self.viewports = [self.plot_unitCircle, self.plot_magResponse, self.plot_phaseResponse,
                          self.plot_allPass, self.plot_realtimeInput, self.plot_realtimeFilter, self.plot_mouseInput]
        self.plotTitles = ['Zero/Pole Plot', 'Magnitude Response', 'Phase Response', 'All Pass Response','Realtime Input', 'Filtered Output', 'Mouse Input']
        self.init_UI()

    def customize_plot(self, plot, title):
        plot.getPlotItem().showGrid(True, True)
        plot.getPlotItem().setTitle(title)
        plot.setMenuEnabled(False)

    def init_UI(self):
        # Customize the appearance of the plots using the new function
        for view, title in zip(self.viewports, self.plotTitles):
            self.customize_plot(view, title)


        self.zeros = []
        self.poles = []

        self.added = "Zeros"

        self.current_index = 0
        self.animation_speed = 1
        self.is_animation_running = False
        self.is_signal_ended = False

        self.toggle_rm = True

        self.x_last, self.y_last = None, None
        self.x_last_pair, self.y_last_pair = None, None

        self.point_moving = None

        self.point_selected = False


        self.pair_mode = False

        self.data_dict = {
            "Zeros": [],
            "Poles": [],
        }
        self.data_brush = {
            "Zeros": 'g',
            "Poles": 'r',
        }
        self.data_symbol = {
            "Zeros": 'o',
            "Poles": 'x',
        }
        self.data_plots = {
            "Data" : self.plot_realtimeInput,
            "Data_modified" : self.plot_realtimeFilter,
        }

        self.data = []
        self.data_modified = []

        self.all_pass_a = 1

        self.signalItemInput = pg.PlotDataItem([], pen = 'b', width = 2)
        self.signalItemFiltered = pg.PlotDataItem([], pen = 'b', width = 2)
        self.plot_realtimeInput.addItem(self.signalItemInput)
        self.plot_realtimeFilter.addItem(self.signalItemFiltered)
        

        self.allpass_en = False

        self.selected_point = None
        self.pair_selected = None
        self.selected_point_index = None

        self.data_opened = False

        self.moved = "Zeros"

        self.moved_last_x = 0
        self.moved_last_y = 0

        self.mouse_loc_circle = None

        self.mouse_enable = False

        self.checked_coeffs = [0.0]

        self.frequencies = 0
        self.mag_response = 0
        self.phase_response = 0
        
        self.total_phase = 0

        self.colors = ['#FF0000', '#FFA500', '#FFFF00', '#00FF00', '#00FFFF', '#0000FF', '#800080', '#FF00FF', '#FF1493', '#00FF7F', '#FFD700', '#FF6347', '#48D1CC', '#8A2BE2', '#20B2AA']



        self.btn_addZeros.clicked.connect(lambda: self.set_added("Zeros"))
        self.btn_addPoles.clicked.connect(lambda: self.set_added("Poles"))
        self.btn_RemoveZeros.clicked.connect(lambda: self.remove_points("Zeros"))
        self.btn_removePoles.clicked.connect(lambda: self.remove_points("Poles"))
        self.btn_removeAll.clicked.connect(self.remove_all)

        # Consolidate signal connections
        self.btn_addCoeff.clicked.connect(self.add_coefficient)
        self.btn_removeCoeff.clicked.connect(self.remove_coefficient)
        self.btn_openFile.clicked.connect(self.open_file)
        self.pair_mode_toggle.stateChanged.connect(self.toggle_pair_mode)
        self.all_pass_enable.stateChanged.connect(self.toggle_all_pass)


        # self.actionImport.triggered.connect(self.open_zeros_poles)
        # self.actionExport.triggered.connect(self.save_zeros_poles)

        self.btn_play.clicked.connect(self.toggle_animation)

        self.mouse_en.stateChanged.connect(self.toggle_mouse_drawing)

        self.btn_addCoeff.clicked.connect(self.update_plot_allpass)
        self.btn_removeCoeff.clicked.connect(self.update_plot_allpass)
        self.table_coeff.itemChanged.connect(self.update_plot_allpass)


    


        self.speed_slider.valueChanged.connect(self.set_animation_speed) # Set Animation speed when slide is changed


        self.btnClr.clicked.connect(self.clear_plots)

        self.move_clicked = False

        # Create circle ROIs to show the unit circle and an additional circle of radius 2 
        self.roi_unitCircle = pg.CircleROI([-1, -1], [2, 2], pen=pg.mkPen('r',width=2), movable=False, resizable=False, rotatable = False)
        
            
        # Set the origin point to the center of the widget
        self.plot_unitCircle.setYRange(-1.1, 1.1, padding=0)
        self.plot_unitCircle.setXRange(-1.1, 1.1, padding=0)
        self.plot_unitCircle.setMouseEnabled(x=False, y=False)


        self.plot_unitCircle.addItem(self.roi_unitCircle)    
        self.roi_unitCircle.removeHandle(0)

        self.plot_unitCircle.scene().sigMouseClicked.connect(self.on_click)

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)

        self.counter_max = 1
        self.counter_min = 0
    

        # Connect the sigMouseMoved signal to the on_mouse_move method in init_UI
        self.plot_mouseInput.scene().sigMouseMoved.connect(self.on_mouse_move)

        self.plot_unitCircle.scene().sigMouseMoved.connect(self.drag_point)
    
        
    # Handling Animation 
    def set_play_button_state(self):
        state_dict = {
            True: "Stop",
            False: "Play",
        }
        self.btn_play.setText(state_dict[self.is_animation_running])

    def set_animation_speed(self):
        self.animation_speed = int(self.speed_slider.value())
        self.lbl_speed.setText(f"Speed: {self.animation_speed}")

    def play_animation(self):
        if self.is_signal_ended:
            print("Signal Ended")
            self.current_index = 0
            self.reset_viewport_range()
            self.is_signal_ended = False
        print("animation playing")
        self.animation_timer.start(30)
        self.is_animation_running = True
        self.set_play_button_state()

    def stop_animation(self):
        print("animation stopped")
        self.animation_timer.stop()
        self.is_animation_running = False
        self.set_play_button_state()
    
    def toggle_animation(self):
        self.is_animation_running = not self.is_animation_running
    
        if self.is_animation_running:
            self.filter_data()
            self.play_animation()
        else:
            self.stop_animation()

    def update_animation(self):
        x_min , x_max = self.viewports[4].viewRange()[0]
        self.signalItemInput.setData(self.data[0:self.current_index])
        self.signalItemFiltered.setData(self.data_modified[0:self.current_index])

        if self.current_index > x_max:   
            for viewport in [self.plot_realtimeInput, self.plot_realtimeFilter]:
                viewport.setLimits(xMax = self.current_index)
                viewport.getViewBox().translateBy(x = self.animation_speed)
       
        if self.current_index >= len(self.data)-1:
            self.stop_animation()
            self.is_signal_ended = True
        
        self.current_index += self.animation_speed # Convert the speed value to integer
        QApplication.processEvents()

        
    # Adding and Removing the All Pass Coefficients
    def add_coefficient(self):
        # Create a QTableWidgetItem
        coeff_item = QTableWidgetItem(self.comboBox.currentText())
        coeff_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        coeff_item.setCheckState(Qt.CheckState.Checked)
        
        # Insert the item into the table widget
        self.table_coeff.insertRow(self.table_coeff.rowCount())
        self.table_coeff.setItem(self.table_coeff.rowCount()-1, 0, coeff_item)
        

    # Removes the selected row from the table widget
    def remove_coefficient(self):
        self.table_coeff.removeRow(self.table_coeff.currentRow()) 
        

    # Opening New File 
    def open_file(self):
        try:
            self.clear_plots()
            # Get the script directory and set the initial folder for file dialog
            script_directory = os.path.dirname(os.path.abspath(__file__))
            initial_folder = os.path.join(script_directory, "Data")

            # Display the file dialog to get the selected file
            file_name, _ = QFileDialog.getOpenFileName(
                self, 'Open File', initial_folder, "CSV files (*.csv)"
            )
            
            # Check if the user canceled the file dialog
            if not file_name:
                return

            # Read the CSV file using pandas
            df = pd.read_csv(file_name)

            # Specify the column containing data
            data_col = 'Data'

            # Extract data from the specified column
            self.data = df[data_col].values

            # Create a copy of the original data for modification
            self.data_modified = self.data.copy()

            # Set the flag indicating that data has been opened
            self.data_opened = True

            # Reset the viewport range and update the plotted data
            self.reset_viewport_range()
            self.signalItemInput.setData(self.data[0:self.current_index])
            self.signalItemFiltered.setData(self.data_modified[0:self.current_index])

        except Exception as e:
            print(f"Error: {e}")


    # Handling on Click 
    def on_click(self, event):
        if event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.ControlModifier:
                self.add_point(self.mouse_loc_circle, self.added)
                self.update_plot()
            else:
                self.move_clicked = True
                self.move_point(self.mouse_loc_circle)

        elif event.button() == Qt.RightButton:
            if self.x_last is not None and self.point_selected:
                self.unselect_moving_point()
            else:
                self.remove_point(self.mouse_loc_circle)
    
    def unselect_moving_point(self):
        self.remove_point(self.point_moving)
        point = pg.Point(self.x_last, self.y_last)
        self.add_point(point, self.moved)
        if self.pair_selected:
            self.remove_point(self.point_moving_pair)
            point = pg.Point(self.x_last, -self.y_last)
            self.add_point(point, self.moved)
        self.update_plot()
        self.x_last, self.y_last, self.point_selected, self.pair_selected, self.move_clicked = None, None, False, False, False



    # Moving point 
    def move_point(self, pos_data):
        if self.x_last is not None and self.point_selected:
            self.x_last, self.y_last, self.point_selected, self.pair_selected, self.move_clicked = None, None, False, False, False

        else:
            for dict_name in ["Zeros", "Poles"]:
                self.move_point_from_list(dict_name, pos_data)

    def move_point_from_list(self, dict_name, point_data):
        point_list = self.data_dict[dict_name].copy()
        for point in point_list:
            if np.allclose([point.x(), point.y()], [point_data.x(), point_data.y()], atol=0.03):
                self.x_last, self.y_last = point.x(), point.y()
                point_pair = pg.Point(point.x(), -point.y())

                self.moved = dict_name
                
                self.point_selected = True
                if point_pair in self.data_dict[self.moved]:
                    self.pair_selected = True

                self.point_moving = pg.Point(self.x_last, self.y_last)
                self.point_moving_pair = pg.Point(self.x_last, -self.y_last)
                break

    def drag_point(self, pos):
        pos = self.plot_unitCircle.getViewBox().mapSceneToView(pos)

        self.mouse_loc_circle = pg.Point(pos.x(), pos.y())
        self.mouse_loc_circle_pair = pg.Point(pos.x(), -pos.y())

        if self.move_clicked and self.point_selected:
            self.remove_point(self.point_moving)
            self.add_point(self.mouse_loc_circle, self.moved)
            if self.pair_selected:
                self.remove_point(self.point_moving_pair)
                self.add_point(self.mouse_loc_circle_pair, self.moved)

            self.update_plot()
            self.point_moving = self.mouse_loc_circle
            self.point_moving_pair = self.mouse_loc_circle_pair


    # Adding point 
    def create_point(self, x, y):
        return pg.Point(x, y)

    def add_point(self, point, dict):
        # Assuming x and y are coordinates
        point = self.create_point(point.x(), point.y())

        if self.pair_mode:
            point_pair = self.create_point(point.x(), -point.y())
            self.add_points_to_dict(point, point_pair, dict)
        else:
            self.add_points_to_dict(point, None, dict)

    def add_points_to_dict(self, point, point_pair, dict):
        self.data_dict[dict].append(point)
        if point_pair is not None:
            self.data_dict[dict].append(point_pair)


    # Removing point 
    def remove_point(self, point_data):
        for dict_name in ["Zeros", "Poles"]:
            if self.remove_point_from_list(self.data_dict[dict_name], point_data, atol_cof = 0):
                break
            elif self.remove_point_from_list(self.data_dict[dict_name], point_data):
                break
        
    def remove_point_from_list(self, point_list, point_data, atol_cof = 0.03):
        for point in point_list.copy():
            if np.allclose([point.x(), point.y()], [point_data.x(), point_data.y()], atol = atol_cof):
                point_list.remove(point)
                point_pair = pg.Point(point.x(), -point.y())
                if point_pair in point_list:
                    point_list.remove(point_pair)
                self.update_plot()
                return True
        self.update_plot()
        return False

    
    def clear_plots(self):
        self.data = [0, 0]
        self.data_modified = [0, 0]
        self.signalItemInput.setData([0])
        self.signalItemFiltered.setData([0])
        self.current_index = 0


    # Update Zeros, Poles Plotting
    def update_plot(self):
        self.plot_unitCircle.clear()

        for point_type in ["Zeros", "Poles"]:
            self.plot_points(self.data_dict[point_type], point_type)
        self.plot_unitCircle.addItem(self.roi_unitCircle)

        self.update_response_plots()
        self.update_plot_allpass()
    
    def plot_points(self, data, point_type):
        for point in data:
            small_circle = pg.ScatterPlotItem(pos=[(point.x(), point.y())], brush = self.data_brush[point_type], size=10, symbol = self.data_symbol[point_type])
            self.plot_unitCircle.addItem(small_circle)
        


    # Update the Magnitude and Phase Response
    def update_response_plots(self):
        # Combine zeros and poles
        z, p, z_allpass, p_allpass = self.get_all_pass_filter()

        # Calculate frequency response
        w, h = freqz(np.poly(z), np.poly(p))

        # Update class attributes
        self.frequencies, self.mag_response, self.phase_response = w, np.abs(h), self.fix_phase(h)


        # Plot magnitude response
        self.plot_response(self.plot_magResponse, self.frequencies, self.mag_response, pen='b', label='Magnitude', units='Linear', unit_bot = "Radians")

        # Plot phase response
        self.plot_response(self.plot_phaseResponse, self.frequencies, self.phase_response, pen='r', label='Phase', units='Degrees', unit_bot = "Radians" , name = "Normal Phase Response")
        
        w, h = freqz(np.poly(z_allpass), np.poly(p_allpass))
        self.frequencies, self.mag_response, self.phase_response = w, np.abs(h), self.fix_phase(h)
        self.plot_phaseResponse.plot(x=self.frequencies, y=self.phase_response, pen='y', name = "AllPass Phase Response")


    def plot_response(self, plot, x, y, pen, label, units, unit_bot, name = ""):
        plot.clear()
        plot.plot(x, y, pen=pen, name = name)
        plot.setLabel('left', label, units=units)
        plot.setLabel('bottom', label, units=unit_bot)
        self.plot_phaseResponse.addLegend()


    
    def fix_phase(self, h):
        phase_response_deg = np.rad2deg(np.angle(h))
        phase_response_constrained  = np.where(phase_response_deg < 0, phase_response_deg + 360, phase_response_deg)
        phase_response_constrained  = np.where(phase_response_constrained  > 180, phase_response_constrained  - 360, phase_response_constrained )
        
        return phase_response_constrained 
    

    # Check All Pass filter and filter the phase 
    def get_all_pass_filter(self):
        self.checked_coeffs = [0.0] # List to hold the selected coefficient values
        
        for row in range(self.table_coeff.rowCount()):
            item = self.table_coeff.item(row, 0) 
            if item.checkState() == Qt.CheckState.Checked:
                self.checked_coeffs.append(float(item.text()))  
        
        if not self.allpass_en:
            self.checked_coeffs = [0.0]

        self.all_pass_zeros = self.data_dict["Zeros"].copy()
        self.all_pass_poles = self.data_dict["Poles"].copy()

        w, all_pass_phs = 0, 0
        self.plot_allPass.clear()

        for i in range(len(self.checked_coeffs)):
            a = self.checked_coeffs[i]

            if a ==1:
                a= 0.99999999
            a = complex(a, 0)
            
            # Check if denominator is not zero before performing division
            if np.abs(a) > 0:
                a_conj = 1 / np.conj(a)

                w, h = freqz([-np.conj(a), 1.0], [1.0, -a])
                all_pass_phs = np.add(np.angle(h), all_pass_phs)
                self.plot_allPass.plot(w, np.angle(h), pen=self.colors[i % len(self.colors)], name = f'All pass{a.real}')
                self.plot_allPass.setLabel('left', 'All Pass Phase', units='degrees')
                
                # Add points to lists
                self.all_pass_poles.append(pg.Point(a.real, a.imag))
                self.all_pass_zeros.append(pg.Point(a_conj.real, a_conj.imag))
        
        self.plot_unitCircle.clear()
        self.plot_points(self.all_pass_zeros, "Zeros")
        self.plot_points(self.all_pass_poles, "Poles")
        self.plot_unitCircle.addItem(self.roi_unitCircle)

        
        if len(self.checked_coeffs) > 1:
            self.plot_allPass.plot(w, all_pass_phs, pen=self.colors[-1], name = 'All pass Total')
        self.plot_allPass.addLegend()

        # Combine zeros and poles
        z_allpass = np.array([complex(zero.x(), zero.y()) for zero in self.all_pass_zeros])
        p_allpass = np.array([complex(pole.x(), pole.y()) for pole in self.all_pass_poles])

        z = np.array([complex(zero.x(), zero.y()) for zero in self.data_dict["Zeros"]])
        p = np.array([complex(pole.x(), pole.y()) for pole in self.data_dict["Poles"]])

        return z, p, z_allpass, p_allpass
    

    def update_plot_allpass(self):
        self.update_response_plots()
        _, _, z, p = self.get_all_pass_filter()
        # Calculate frequency response
        w, h = freqz(np.poly(z), np.poly(p))
        self.phase_response = self.fix_phase(h)
    
   
    # Real Time Data Filtering
    def filter_data(self):
        _,_, z, p = self.get_all_pass_filter()
        numerator, denominator = zpk2tf(z, p, 1)
        self.data_modified = np.real(lfilter(numerator, denominator, self.data))
        
    # def filter_data_point_by_point(self, new_data_point):
    #     _, _, z, p = self.get_all_pass_filter()
    #     numerator, denominator = zpk2tf(z, p, 1)

    #     # Update data_modified point by point
    #     filtered_point = np.real(lfilter(numerator, denominator, [new_data_point]))[0]
    #     self.data_modified.append(filtered_point)
  


    # Draw Data Using Mouse Movement
    def on_mouse_move(self, pos):
        if  self.mouse_enable:
            if not self.data_opened:
                self.data = []
                self.data_modified = []
                self.data_opened = True

            # Convert the click position to data coordinates
            pos = self.plot_unitCircle.getViewBox().mapSceneToView(pos)

            # Convert x-coordinate to a signal value (adjust the scaling factor as needed)
            signal_value = np.sqrt(pos.x()**2 + pos.y()**2)

            self.counter_max += 1

            # Append the signal value to self.data
            self.data.append(signal_value)

            # Update the filtered data
            self.filter_data()

            # Update signalItemInput and signalItemFiltered data
            self.signalItemInput.setData(self.data[:self.counter_max])
            self.signalItemFiltered.setData(self.data_modified[:self.counter_max])

            # Adjust x_min and x_max for plotting
            x_max = len(self.data)
            x_min = max(0, x_max - 200)

            # SetRange for real-time plots
            self.plot_realtimeInput.setRange(xRange=[x_min, x_max])
            self.plot_realtimeFilter.setRange(xRange=[x_min, x_max])

            
        self.prev_mouse_pos = pos



    def reset_viewport_range(self):
        for plot in [self.plot_realtimeInput, self.plot_realtimeFilter]:
            plot.setRange(xRange=[0, 1000])
    

    def remove_all(self):
        self.data_dict["Zeros"].clear()
        self.data_dict["Poles"].clear()
        self.data_modified = self.data
        self.update_plot()

    def remove_points(self, point_type):
        self.data_dict[point_type].clear()
        self.update_plot()


    def set_added(self, point_type):
        self.added = point_type

    
    
    def toggle_pair_mode(self):
        self.pair_mode = not self.pair_mode
    
    
    def toggle_all_pass(self):
        self.allpass_en = not self.allpass_en
        self.update_plot_allpass()
        self.update_response_plots()

    def toggle_mouse_drawing(self):
        self.mouse_enable = not self.mouse_enable
        self.reset_viewport_range()


        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    MainWindow = DigitalFilterDesigner()
    MainWindow.show()
    sys.exit(app.exec_())
