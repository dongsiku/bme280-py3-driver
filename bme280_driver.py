from smbus2 import SMBus

"""
This script is derived from https://github.com/SWITCHSCIENCE/samplecodes/tree/master/BME280

The License of the project is as follows:

Copyright (c) 2018 Switch Science
Released under the MIT license
https://github.com/SWITCHSCIENCE/samplecodes/blob/master/LICENSE
"""


class BME280:
    def __init__(self, t_sb=5, filter_bme280=0, spi3w_en=0,
                 osrs_t=1, osrs_p=1, mode=3, osrs_h=1):
        """The initial settings of BME280
        Reference: http://trac.switch-science.com/wiki/BME280

        Args:
            t_sb (int, optional): Tstandby 1000ms. Defaults to 5.
            filter_bme280 (int, optional): Filter off. Defaults to 0.
            spi3w_en (int, optional): 3-wire SPI Disable. Defaults to 0.
            osrs_t (int, optional): Temperature oversampling x 1. Defaults to 1.
            osrs_p (int, optional): Pressure oversampling x 1. Defaults to 1.
            mode (int, optional): Normal mode. Defaults to 3.
            osrs_h (int, optional): Humidity oversampling x 1. Defaults to 1.
        """
        BUS_NUMBER = 1
        self.I2C_ADDRESS = 0x76
        self.BUS = SMBus(BUS_NUMBER)
        self.digT, self.digP, self.digH = [], [], []

        CTRL_MEAS_REG =\
            (osrs_t << 5) | (osrs_p << 2) |\
            mode
        CONFIG_REG = (t_sb << 5) | (filter_bme280 << 2) | spi3w_en
        CTRL_HUM_REG = osrs_h

        self.writeReg(0xF2, CTRL_HUM_REG)
        self.writeReg(0xF4, CTRL_MEAS_REG)
        self.writeReg(0xF5, CONFIG_REG)

        calib = []
        for i in range(24):
            calib.append(self.BUS.read_byte_data(self.I2C_ADDRESS, i + 0x88))
        calib.append(self.BUS.read_byte_data(self.I2C_ADDRESS, 0xA1))
        for i in range(7):
            calib.append(self.BUS.read_byte_data(self.I2C_ADDRESS, i + 0xE1))

        for i in range(3):
            self.digT.append((calib[i * 2 + 1] << 8) | calib[i * 2])
        for i in range(9):
            self.digP.append((calib[i * 2 + 7] << 8) | calib[i * 2 + 6])
        self.digH.append(calib[24])
        self.digH.append((calib[26] << 8) | calib[25])
        self.digH.append(calib[27])
        self.digH.append((calib[28] << 4) | (0x0F & calib[29]))
        self.digH.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
        self.digH.append(calib[31])

        for i in range(2):
            if self.digT[i + 1] & 0x8000:
                self.digT[i + 1] = (-self.digT[i + 1] ^ 0xFFFF) + 1
        for i in range(8):
            if self.digP[i + 1] & 0x8000:
                self.digP[i + 1] = (-self.digP[i + 1] ^ 0xFFFF) + 1
        for i in range(6):
            if self.digH[i] & 0x8000:
                self.digH[i] = (-self.digH[i] ^ 0xFFFF) + 1

    def writeReg(self, reg_address, data):
        self.BUS.write_byte_data(self.I2C_ADDRESS, reg_address, data)

    def readData(self):
        data = []
        for i in range(8):
            data.append(self.BUS.read_byte_data(self.I2C_ADDRESS, i + 0xF7))
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        hum_raw = (data[6] << 8) | data[7]

        temperature = self.compensate_T(temp_raw)
        pressure = self.compensate_P(pres_raw)
        humidity = self.compensate_H(hum_raw)
        return temperature, pressure, humidity

    def compensate_T(self, adc_T):
        v1 = ((adc_T >> 3) - (self.digT[0] << 1)) * self.digT[1] >> 11
        v2 = (((((adc_T >> 4) - self.digT[0]) *
                ((adc_T >> 4) - self.digT[0])) >> 12) * self.digT[2]) >> 14
        self.t_fine = v1 + v2
        temperature = (self.t_fine * 5 + 128) >> 8
        temperature = temperature / 100

        return temperature

    def compensate_P(self, adc_P):
        v1 = (self.t_fine >> 1) - 64000
        v2 = (((v1 >> 2) ** 2) >> 11) * self.digP[5]
        v2 += ((v1 * self.digP[4]) << 1)
        v2 = (v2 >> 2) + (self.digP[3] << 16)
        v1 = (((self.digP[2] * (((v1 >> 2) ** 2) >> 13)) >> 3) +
              ((self.digP[1] * v1) >> 1)) >> 18
        v1 = ((32768 + v1) * self.digP[0]) >> 15

        if v1 == 0:
            return 0

        pressure = ((1048576 - adc_P) - (v2 >> 12)) * 3125
        if pressure < 0x80000000:
            pressure = (pressure << 1) // v1
        else:
            pressure = (pressure // v1) * 2
        v1 = (self.digP[8] * (((pressure >> 3)**2) >> 13)) >> 12
        v2 = ((pressure >> 2) * self.digP[7]) >> 13
        pressure = (pressure + ((v1 + v2 + self.digP[6]) >> 4)) / 100
        return pressure

    def compensate_H(self, adc_H):
        v_x1 = self.t_fine - 76800
        v_x1 = ((((adc_H << 14) - (self.digH[3] << 20) - (self.digH[4] * v_x1)) + 16384) >> 15) * (
            ((((((v_x1 * self.digH[5]) >> 10) * (((v_x1 * self.digH[2]) >> 11) + 32768)) >> 10) + 2097152) * self.digH[1] + 8192) >> 14)
        v_x1 -= ((((v_x1 >> 15) ** 2) >> 7) * self.digH[0]) >> 4

        if v_x1 < 0:
            v_x1 = 0
        elif v_x1 > 419430400:
            v_x1 = 419430400

        humidity = (v_x1 >> 12) / 1024
        return humidity


if __name__ == "__main__":
    def print_tph(temperature, pressure, humidity):
        print("temperature: {:4.2f} degreeC".format(temperature))
        print("pressure: {:4.2f} hPa".format(pressure))
        print("humidity: {:4.2f} %".format(humidity))

    bme280 = BME280()
    temperature, pressure, humidity = bme280.readData()

    print_tph(temperature, pressure, humidity)
