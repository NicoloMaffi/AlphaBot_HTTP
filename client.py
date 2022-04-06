import sys
import requests
import time

def move(url, direction):

    while True:
        data = requests.get(url + "/api/v1/sensors/obstacles").json()

        if 0 not in data.values():
            # vai dritto
            requests.get(url + "/api/v1/motors/both?pwmL=-40&pwmR=40&time=0.5")
        else:
            requests.get(url + "/api/v1/motors/both?pwmL=-0&pwmR=0&time=0.5")
            requests.get(url + "/api/v1/motors/both?pwmL=25&pwmR=-25&time=0.5")

            if direction == "r":
                #vai a destra
                requests.get(url + "/api/v1/motors/both?pwmL=0&pwmR=30&time=1")
            elif direction == "l":
                #vai a sinistra
                requests.get(url + "/api/v1/motors/both?pwmL=-30&pwmR=0&time=1")
            
def main():
    move(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()