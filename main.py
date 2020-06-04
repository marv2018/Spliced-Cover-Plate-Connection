import sys
from PyQt5 import QtCore, QtGui, QtWidgets

from gui import Ui_MainWindow
import constants


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.row = 0
        self.column = 0

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

        # Bolt
        self.comboBox_bolt_class.currentIndexChanged.connect(self.boltChange)
        self.comboBox_bolt_shank_diameter.currentIndexChanged.connect(self.boltChange)

        # Update pictures based on column/row
        self.spinBox_columns.valueChanged.connect(self.column_row_change)
        self.spinBox_rows.valueChanged.connect(self.column_row_change)

        # Fill beams
        for key, value in constants.beams.items():
            self.combo_beam_size.addItem(key)

        # Update fields, a bit strange way of doing it ? ...
        self.steel_beam_change()
        self.steel_plate_change()
        self.boltChange()

        pixmap = QtGui.QPixmap("media/2x2.jpeg")
        height_of_label = 301
        self.label_diagram.resize(741, height_of_label)
        self.label_diagram.setPixmap(
            pixmap.scaled(self.label_diagram.size(), QtCore.Qt.IgnoreAspectRatio)
        )

    def calculate(self):
        # -----------------------------------------------------------------------------
        # BEAM GEOMETRY

        # Iweb = tw *tw^3 / 12
        iw = (
            float((self.lineEdit_web_thickness.text()))
            * (float(self.lineEdit_web_height.text())) ** 3
        ) / 12
        self.lineEdit_second_web_moment.setText(str(iw))

        ip = (
            float(self.lineEdit_plate_thickness.text())
            * float(self.lineEdit_plate_depth.text()) ** 3
            / 12
        )
        ratio_bm = ip / float(self.lineEdit_second_moment_single_pfc.text())
        m_ratio = float(self.lineEdit_axial_force.text()) * ratio_bm

        self.lineEdit_second_moment_cover.setText(str(ip))
        self.lineEdit_ratio_bm.setText(str(ratio_bm))

        self.lineEdit_bending_moment_cover.setText(str(m_ratio))

        # --------------------BOLTS AND FORCES TAB---------------------------------------------------------
        self.lineEdit_bolts_mratio.setText(str(m_ratio))

        f_ved = float(self.lineEdit_shear_force.text()) / (self.column*self.row)

        self.lineEdit_f_ved.setText(str(f_ved))

        p0 = float(self.lineEdit_p0.text())
        p1 = float(self.lineEdit_p1.text())
        p2 = float(self.lineEdit_p2.text())
        e1 = float(self.lineEdit_e1.text())
        e2 = float(self.lineEdit_e2.text())

        m_add = float(self.lineEdit_shear_force.text()) * (p0 + (p1*(self.column - 1)/2))
        self.lineEdit_madd.setText(str(m_add))

        # --------------------WEB SPLICE TAB-------------------------------------------------
        fb= 2.5* float(self.lineEdit_beam_ultimate_strength.text()) * float(self.comboBox_bolt_shank_diameter.currentText())
        self.lineEdit_fb.setText(str(fb))

        sum, comb = calc_axis(self.column,self.row,p1,p2)

        self.lineEdit_i_bolt.setText(str(sum))

        test = ""
        abc = ' + '.join(comb)

        self.label_ibolt.setText(abc)

        print(comb)


        # -----------------------------------------------------------------------------


    def column_row_change(self):
        # get current row and column from spinbox
        self.row = int(self.spinBox_rows.text())
        self.column = int(self.spinBox_columns.text())

        pixmap = QtGui.QPixmap(f"media/{self.row}x{self.column}.jpeg")

        self.label_diagram.setPixmap(
            pixmap.scaled(self.label_diagram.size(), QtCore.Qt.IgnoreAspectRatio)
        )

    def steel_beam_change(self):
        current_beam_grade = self.combo_steal_grade_beam.currentText()
        current_beam_thickness = self.combo_steel_thickness_beam.currentText()

        self.beam_yield_strength.setText(
            str(constants.steel[(current_beam_grade, current_beam_thickness)][0])
        )
        self.lineEdit_beam_ultimate_strength.setText(
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

    def boltChange(self):

        current_bolt_class = self.comboBox_bolt_class.currentText()
        current_bolt_shank_diameter = self.comboBox_bolt_shank_diameter.currentText()

        self.lineEdit_bolt_shear.setText(
            str(constants.bolt[(current_bolt_class, current_bolt_shank_diameter)][0])
        )
        self.lineEdit_bolt_diameter.setText(
            str(constants.bolt[(current_bolt_class, current_bolt_shank_diameter)][1])
        )


def calc_axis(x, y, p1, p2):
    # Used for storing components for printing to the user
    x_components = []
    y_components = []

    # Axial components of the polar moment of inertia of the bolt group
    x_total = 0
    y_total = 0

    # Calculate axis components
    x_total, x_components = calc_i_bolt(x, y, p1)
    print(f"X Total:{x_total} X components:{x_components}")

    y_total, y_components = calc_i_bolt(y, x, p2)
    print(f"Y Total:{y_total} Y:components{y_components}")

    sum = x_total + y_total
    print(f"Total (X+Y): {sum}")

    combined_equation = x_components + y_components

    return sum, combined_equation


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
