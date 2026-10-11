# Faza 5 — Gazebo i sterownik Ackermanna 4WD

## Stan

Gałąź: gazebo-simulation. Implementacja lokalna i rozszerzenie CI są gotowe; pozostaje commit,
zielony wynik GitHub Actions i scalenie PR. Lokalny test control_integration przeszedł.
Ręcznie potwierdzono jazdę, skręt, cofanie oraz zatrzymanie po utracie komend.

## Co działa i jakie technologie wykorzystujemy

Gazebo Harmonic oblicza fizykę modelu z masami, bezwładnością i kolizjami.
amr_simulation uruchamia warehouse.sdf (podłoże, światło i dwa uproszczone regały z kolizjami),
robot_state_publisher, utworzenie robota, ros_gz_bridge i amr_control.
ROS 2 używa DDS; most tłumaczy wiadomości ROS na Gazebo Transport.
CAN, MQTT i gRPC będą dodawane w osobnych fazach.

Sterownik C++ odbiera geometry_msgs/Twist na /cmd_vel. linear.x to m/s
w środku tylnej osi, angular.z to rad/s obrotu pojazdu. Korzysta z
examples/phase1/kinematics.hpp. RPM przelicza na rad/s dla czterech napędów;
dwa kąty skrętu przekazuje w radianach jako std_msgs/Float64.
Gazebo przekazuje /clock i /joint_states do ROS.

## Budowanie

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
python -m pip install -r requirements-dev.txt
cd ros2_ws
python -m colcon build --symlink-install \
  --packages-select amr_description amr_control amr_simulation \
  --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash
```

Na nowym komputerze potrzebne są pakiety ROS Jazzy ros-gz, xacro,
robot-state-publisher, geometry-msgs, std-msgs i rclpy, oprócz narzędzi
budowania opisanych w README.

## Terminal 1 — uruchomienie całości

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
ros2 launch amr_simulation simulation.launch.py
```

Nie uruchamiaj dodatkowej kopii ackermann_controller.

## Terminal 2 — komendy

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.0}}"
```

Po kilku sekundach Ctrl+C w terminalu 2 kończy komendy. Działający
sterownik zatrzymuje napęd i prostuje koła po 0.5 s bez komend.
Dla skrętu w lewo ustaw angular.z: 0.1, dla prawego: -0.1.
Dla cofania na wprost ustaw linear.x: -0.2 i angular.z: 0.0.
Robot nie obraca się w miejscu: komenda x: 0.0, z: 0.2 jest odrzucana.
Nie wysyłaj bezpośrednich komend przegubów równocześnie ze sterownikiem.

## Odczyt i testy

```bash
ros2 topic echo /joint_states --once
ros2 topic echo /clock --once
```

Po zatrzymaniu prędkości są bliskie zeru; pozycje obrotu kół pozostają.

Test sterownika nie wymaga Gazebo:

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
cd ros2_ws
python -m colcon test --packages-select amr_control \
  --event-handlers console_direct+
python -m colcon test-result --verbose
```

Test uruchamia osobny proces sterownika w domenie ROS 88. Sprawdza sześć
komend, skręt w obie strony, cofanie, timeout, odrzucenie obrotu w miejscu,
powrót do jazdy i zatrzymanie. Nie jest testem fizyki ani mostu Gazebo.

## Ograniczenia i prace pozostałe

Kontrolery Gazebo realizują zadane prędkości i pozycje; to uproszczony model
napędu. Wymiary i timeout sterownika są obecnie stałymi w kodzie.
Timeout działa przy uruchomionym sterowniku. Launch po zakończeniu procesu
sterownika zamyka całą symulację. To zabezpieczenie sesji, nie niezależny
watchdog sprzętowy. Uruchomienie sterownika poza tym launch nie ma tej ochrony.
Pozostają przegląd, wynik CI na GitHubie oraz PR do main. Odometria, sensory i nawigacja
należą do kolejnych faz. Docker i publikacja obrazu CD nadal są osobnym zadaniem.

## Test Gazebo i obsługa awarii

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
cd ros2_ws
python -m colcon test --packages-select amr_simulation --event-handlers console_direct+
python -m colcon test-result --verbose
```

Test gazebo_integration uruchamia prawdziwy serwer Gazebo bez GUI w osobnej
partycji Transport i domenie ROS 89. Sprawdza zegar, most, obrót czterech kół,
rzeczywiste kąty skrętu oraz zatrzymanie po utracie komend. Następnie zabija
wyłącznie własny proces sterownika i sprawdza zakończenie launch.
Test nie ocenia jeszcze odometrii, dokładności toru jazdy ani unikania przeszkód.
CI uruchamia ten test przez colcon, oprócz testów sterownika i faz poprzednich.

Ręczne uruchomienie bez GUI:

```bash
ros2 launch amr_simulation simulation.launch.py gz_args:="-r -s"
```
