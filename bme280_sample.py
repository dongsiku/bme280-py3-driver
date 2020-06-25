from time import sleep

from bme280_driver import BME280


def main(number):  # Get data per 1 second
    print("If you want to stop this script, press Ctrl+C")
    print("Num, Temperature(degreeC), Pressure(hPa), Humidity(%)")
    for i in range(number):
        bme280 = BME280()
        temperature, pressure, humidity = bme280.readData()
        print(f"{i+1:3d}, {temperature:5.2f}, {pressure:7.2f}, {humidity:5.2f}")
        sleep(1)


if __name__ == "__main__":
    main(number=100)  # Get 100 data
