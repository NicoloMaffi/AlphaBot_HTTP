# AlphaBot_HTTP <img alt="ICON" src="https://github.com/NicoloMaffi/AlphaBot_HTTP/blob/main/res/favicon.ico" width="30">
AlphaBot remote controller with Flask via HTTP.

<hr>

## New User Interface

### Log In Section
<img alt="log_in_img" src="https://github.com/nikmaffi/AlphaBot_HTTP/blob/main/docs/ui/log_in.png" width="1000">

### Sign In Section
<img alt="sign_up_img" src="https://github.com/nikmaffi/AlphaBot_HTTP/blob/main/docs/ui/sign_up.png" width="1000">

### Controller Section
<img alt="controller_img" src="https://github.com/nikmaffi/AlphaBot_HTTP/blob/main/docs/ui/controller.png" width="1000">

<hr>

## User Authentication Aanagement

### Database Entity-Relationship Scheme
<img alt="er_scheme" src="https://github.com/nikmaffi/AlphaBot_HTTP/blob/main/docs/db/er.png" width="800">

<hr>

## API System

### AlphaBot Sensors API
URL:  **http://<alphabot_ip_addr>:<http_port>/api/v1/sensors/obstacles** <br><br>

The API returns a dictionary with the keys **left** and **right**. Each key can have a value **0** or **1**. A 0 value means that an obstacle has been detected by the sensor while a 1 value means that the sensor did not detected any obstacles.

### AlphaBot Motors
Motor | URL
------|----
Left  | http://<alphabot_ip_addr>:<http_port>/api/v1/motors/left?pwm=<pwm_value>&time=<execution_time>
Right | http://<alphabot_ip_addr>:<http_port>/api/v1/motors/right?pwm=<pwm_value>&time=<execution_time>
Both  | http://<alphabot_ip_addr>:<http_port>/api/v1/motors/both?pwmL=<left_motor_pwm_value>&pwmR=<right_motor_pwm_value>&time=<execution_time>

The API returns a dictionary with the key **status**. The key can have a value **0** or **1**. A 0 value means that an error has been occured during the operation while a 1 value means that the operation was successful.
