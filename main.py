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

        # Plate
        self.combo_steel_grade_plate.currentIndexChanged.connect(
            self.steel_plate_change
        )
        self.combo_steel_thickness_plate.currentIndexChanged.connect(
            self.steel_plate_change
        )

        # Update pictures based on column/row
        self.spinBox_columns.valueChanged.connect(self.column_row_change)
        self.spinBox_rows.valueChanged.connect(self.column_row_change)

        # Fill beams
        for key, value in constants.beams.items():
            self.combo_beam_size.addItem(key)

        # Update fields, a bit strange way of doing it ? ...
        self.steel_beam_change()
        self.steel_plate_change()

        pixmap = QtGui.QPixmap("media/2x2.jpeg")
        height_of_label = 250
        self.label_diagram.resize(400, height_of_label)
        self.label_diagram.setPixmap(
            pixmap.scaled(self.label_diagram.size(), QtCore.Qt.IgnoreAspectRatio)
        )

    def calculate(self):
        # Iweb = tw *tw^3 / 12
        iw = (
            float((self.lineEdit_web_thickness.text()))
            * (float(self.lineEdit_web_height.text())) ** 3
        ) / 12
        self.lineEdit_second_web_moment.setText(str(int(iw)))

        ip = (
            float(self.lineEdit_plate_thickness.text())
            * float(self.lineEdit_plate_depth.text()) ** 3
            / 12
        )
        Rbm = ip / float(self.lineEdit_second_moment_single_pfc.text())
        Mratio = float(self.lineEdit_axial_force.text()) * Rbm

        self.lineEdit_second_moment_cover.setText(str(int(ip)))
        self.lineEdit_ratio_bm.setText(str(int(Rbm)))

        self.lineEdit_bending_moment_cover.setText(str(int(Mratio)))

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


def calc_axis(x, y, p1, p2):
    # Used for storing components for printing to the user
    x_components = []
    y_components = []

    # Axial components of the polar moment of inertia of the bolt group
    x_total = 0
    y_total = 0

    # Calculate X axis components
    x_total, x_components = calc_i_bolt(x, y, p1)
    print(f"X Total:{x_total} X components:{x_components}")

    y_total, y_components = calc_i_bolt(y, x, p2)
    print(f"Y total:{y_total} X:components{y_components}")

    print(f"Total (X+Y): {x_total + y_total}")


def calc_i_bolt(axis1, axis2, distance):
    axis_components = []
    total = 0

    # Even numbers of rows/columns
    if axis1 % 2 == 0:

        # First term
        i = 2
        # Difference between terms
        z = 1.5

        while i <= axis1:
            p_i_coeff = i - z

            # Number of bolts on each side - number of adjacent axis*2
            Pi_times_distance = (p_i_coeff * distance) ** 2
            bolts_times_coeff = axis2 * 2 * Pi_times_distance
            axis_components.append(f"{2 * axis2}*({p_i_coeff}*{distance})^2")

            total += bolts_times_coeff

            i = i + 2
            z = z + 1

        return total, axis_components

    # ODD numbers of rows/columns
    else:
        # First term
        i = 3
        # Difference between terms
        z = 2

        while i <= axis1:
            p_i_coeff = i - z

            # Number of bolts on each side - number of adjacent axis*2
            Pi_times_distance = (p_i_coeff * distance) ** 2
            bolts_times_coeff = axis2 * 2 * Pi_times_distance
            axis_components.append(f"{2 * axis2}*({p_i_coeff}*{distance})^2")

            total += bolts_times_coeff

            i = i + 2
            z = z + 1

        return total, axis_components


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
