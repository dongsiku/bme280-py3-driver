# BME280 Driver for Python3

This script is the BME280 driver for Python3 in Raspberry Pi. 

## Environment

This script is confirmed the operation in the following environment in Raspberry Pi 3B. 

```shell-session:environment
$ cat /etc/os-release
PRETTY_NAME="Raspbian GNU/Linux 10 (buster)"
NAME="Raspbian GNU/Linux"
VERSION_ID="10"
VERSION="10 (buster)"
VERSION_CODENAME=buster
ID=raspbian
ID_LIKE=debian
HOME_URL="http://www.raspbian.org/"
SUPPORT_URL="http://www.raspbian.org/RaspbianForums"
BUG_REPORT_URL="http://www.raspbian.org/RaspbianBugs"

$ python3 --version
Python 3.7.3
```

## Installation

This session describes how to use this driver with Raspberry Pi connected with BME280 using I2C. 

1. Connect BME280 with Raspberry Pi using I2C.

1. Install `i2c-tools` and `python3-smbus` using apt command.
   
    ```shell-session:install-i2c-tools-and-python3-smbus
    sudo apt install -y i2c-tools python3-smbus
    ```

1. Check the I2C connection between Raspberry Pi and BME280.
  
    ```shell-session:check-the-I2C-connection
    $ sudo i2cdetect -y 1
        0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
    00:          -- -- -- -- -- -- -- -- -- -- -- -- -- 
    10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
    70: -- -- -- -- -- -- 76 --                         
    ```

1. Install Python Packages using PyPI.
   
    ```shell-session:install-python-packages
    cd samplecodes/BME280/Python37/ # Move to this directory
    python3 -m venv .env        # If you want to create virtual environment (optional)
    source .env/bin/activate    # If you want to create virtual environment (optional)
    pip install -U pip          # Upgrade pip (optional)
    pip install smbus2          # Install smbus (required)
    pip install -r requirements.txt # If you want to install Python packages using requirements.txt (optional)
    ```

1. Check the driver works well. 
   
    ```shell-session:check-bme280_driver
    $ python3 bme280_driver.py
    temperature: 28.94 degreeC
    pressure: 1006.39 hPa
    humidity: 51.63 %
    ```

1. You can apply this driver to your own applications using the following script. 
    
    ```python:how-to-apply-this-driver-to-your-apps
    from bme280_driver import BME280
    bme280 = BME280()
    temperature, pressure, humidity = bme280.readData()
    ```

## Additional Settings for BME280

If you want to change the configuration of this driver, use the following arguments in `BME280()`. 

```text:bme280-settings
t_sb (int, optional): Tstandby 1000ms. Defaults to 5.
filter_bme280 (int, optional): Filter off. Defaults to 0.
spi3w_en (int, optional): 3-wire SPI Disable. Defaults to 0.
osrs_t (int, optional): Temperature oversampling x 1. Defaults to 1.
osrs_p (int, optional): Pressure oversampling x 1. Defaults to 1.
mode (int, optional): Normal mode. Defaults to 3.
osrs_h (int, optional): Humidity oversampling x 1. Defaults to 1.
```

There is the detailed explanation of these arguments in the following web site: [BME280搭載　温湿度・気圧センサモジュールの使い方](http://trac.switch-science.com/wiki/BME280)

## Reference

[第39回「ラズベリーパイで温度・湿度・気圧をまとめて取得！AE-BME280でIC2通信」](https://deviceplus.jp/hobby/raspberrypi_entry_039/) 
