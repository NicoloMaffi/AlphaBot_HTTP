import sys
import requests
import time

def move(url, direction):

    while True:
        data = requests.get(url + "/api/v1/sensors/obstacles").json()

        if 0 not in data.values():
            # vai dritto
            requests.get(url + "/api/v1/motors/both?pwmL=-50&pwmR=60&time=0.2")
        else:
            requests.get(url + "/api/v1/motors/both?pwmL=-0&pwmR=0&time=0.1")
            requests.get(url + "/api/v1/motors/both?pwmL=50&pwmR=-60&time=0.2")

            if direction == "r":
                #vai a destra
                requests.get(url + "/api/v1/motors/both?pwmL=0&pwmR=27&time=1")
            elif direction == "l":
                #vai a sinistra
                requests.get(url + "/api/v1/motors/both?pwmL=-27&pwmR=0&time=1")
            
def main():
    move(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()