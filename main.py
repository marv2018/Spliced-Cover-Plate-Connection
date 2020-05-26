import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from gui import Ui_MainWindow
import constants

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        # Callback functions
        self.pushButton_calculate.clicked.connect(self.calculate)

        # Beam
        self.combo_beam_size.currentIndexChanged.connect(self.beamChange)

        self.combo_steal_grade_beam.currentIndexChanged.connect(self.steel_beam_change)
        self.combo_steel_thickness_beam.currentIndexChanged.connect(
            self.steel_beam_change
        )

        #Plate
        self.combo_steel_grade_plate.currentIndexChanged.connect(
            self.steel_plate_change
        )
        self.combo_steel_thickness_plate.currentIndexChanged.connect(
            self.steel_plate_change
        )

        # Update pictures based on column_row
        self.spinBox_columns.valueChanged.connect(self.column_row_change)
        self.spinBox_rows.valueChanged.connect(self.column_row_change)


        # Fill beams
        for key, value in constants.beams.items():
            self.combo_beam_size.addItem(key)

        # Update fields, a bit strange way of doing it ? ...
        self.steel_beam_change()
        self.steel_plate_change()

        pixmap = QtGui.QPixmap("media/2x2.jpeg")
        height_of_label = 200
        self.label_diagram.resize(400, height_of_label)
        self.label_diagram.setPixmap(
            pixmap.scaled(self.label_diagram.size(), QtCore.Qt.IgnoreAspectRatio)
        )

    def calculate(self):
        # Iweb = tw *tw^3 / 12
        iw = (float((self.lineEdit_web_thickness.text()))*(float(self.lineEdit_web_height.text()))**3) / 12
        self.lineEdit_second_web_moment.setText(str(int(iw)))


        ip = float(self.lineEdit_plate_thickness.text()) * float(self.lineEdit_plate_depth.text())**3 / 12

        self.lineEdit_second_moment_cover.setText(str(int(ip)))



    def column_row_change(self):
        # get current row and column from spinbox
        row = self.spinBox_rows.text()
        column = self.spinBox_columns.text()

        pixmap = QtGui.QPixmap(f"media/{row}x{column}.jpeg")

        self.label_diagram.setPixmap(
            pixmap.scaled(self.label_diagram.size(), QtCore.Qt.IgnoreAspectRatio)
        )


    def steel_beam_change(self):
        current_beam_grade = self.combo_steal_grade_beam.currentText()
        current_beam_thickness = self.combo_steel_thickness_beam.currentText()

        self.beam_yield_strength.setText(
            str(constants.steel[(current_beam_grade, current_beam_thickness)][0])
        )
        self.beam_ultimate_strength.setText(
            (str(constants.steel[(current_beam_grade, current_beam_thickness)][1]))
        )

    def steel_plate_change(self):

        current_plate_grade = self.combo_steel_grade_plate.currentText()
        current_plate_thickness = self.combo_steel_thickness_plate.currentText()

        self.lineEdit_plate_yield_strength.setText(
            str(constants.steel[(current_plate_grade, current_plate_thickness)][0])
        )
        self.lineEdit_plate_ultimate_strength.setText(
            (str(constants.steel[(current_plate_grade, current_plate_thickness)][1]))
        )

    def beamChange(self):
        current_value = self.combo_beam_size.currentText()
        beam_params = constants.beams.get(current_value)
        self.beam_depth.setText(str(beam_params[0]))
        self.lineEdit_web_thickness.setText(str(beam_params[1]))
        self.flange_thickness.setText(str(beam_params[2]))
        self.root_radius.setText(str(beam_params[3]))
        self.second_moment_area.setText(str(beam_params[4]))
        #
        self.lineEdit_second_moment_single_pfc.setText(str(beam_params[4]))

        # Calculate Web Height
        web_height_value = beam_params[0] - 2 * beam_params[2]
        self.lineEdit_web_height.setText(str(web_height_value))

        # Calcualte Depth between flange fillets
        depth_flange_fillets_value = beam_params[0] - 2 * (
            beam_params[2] + beam_params[3]
        )

        self.depth_flange_fillets.setText(str(depth_flange_fillets_value))


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
