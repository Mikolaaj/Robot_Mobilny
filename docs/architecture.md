# Robot Mobilny — aktualna architektura

## Robot i układy odniesienia

Cztery koła napędowe (4WD), przednie lewe i prawe skrętne: Ackermann.
Nie stosujemy koła podporowego ani sterowania skid-steer.
Każde koło otrzymuje własną komendę prędkości obrotowej.
Docelowo: cztery przeguby napędowe i dwa przeguby skrętu przednich kół.
base_link planujemy w środku tylnej osi; tam definiujemy linear.x i angular.z.
Koła: front_left_wheel_link, front_right_wheel_link,
rear_left_wheel_link, rear_right_wheel_link. Dodatkowe steering links ustalimy
w fazie URDF. Pozostałe ramy: map, odom, laser_link, camera_link, imu_link.

Robocze wymiary: promień koła 0.10 m, rozstaw kół 0.40 m,
rozstaw osi 0.60 m, limit skrętu każdego koła 0.60 rad.
Robot nie wykonuje obrotów w miejscu; teleoperacja i Nav2 muszą to respektować.

## Stan implementacji

0. Gotowe: Ubuntu, Python 3.12/.venv, ROS Jazzy, Gazebo Harmonic.
1. Gotowe: samodzielne obliczenia Ackermanna C++/Python i testy jednostkowe.
2. Gotowe: edukacyjny amr_learning — tematy, parametr, usługa, akcja,
   test integracyjny. Nie jest jeszcze sterownikiem robota.
3. Następne: osobna faza CI/CD, GitHub Actions i Docker.

## Dalsze fazy i technologie

4. URDF/Xacro, RViz, TF: cztery koła napędowe i dwa przednie przeguby skrętu.
5. Gazebo magazyn, ros_gz/ROS ↔ Gazebo Transport, teleoperacja Ackermanna.
   Sterownik musi obsługiwać cztery RPM i dwa kąty; nie zakładamy, że gotowy
   ackermann_steering_controller obsłuży napęd 4WD bez rozszerzenia.
6. Odometria Ackermanna i TF odom → base_link, pomiary kół i skrętu.
7. LiDAR, IMU, kamera, sensor_msgs, fuzja odometrii/IMU.
8. slam_toolbox, mapowanie i zapis mapy; TF map → odom.
9. Nav2/AMCL/costmaps/BT: planowanie z ograniczeniem promienia skrętu,
   kontroler dla pojazdu samochodowego; bez zachowań obrotu w miejscu.
10. SocketCAN/vcan: cztery silniki oraz sterowanie/status skrętu.
    Poprzedni projekt protokołu z dwiema komendami silników jest zastąpiony;
    identyfikatory, skalowanie, timeouty i potwierdzenia ustalimy w tej fazie.
11. DDS/QoS: eksperymenty reliability, durability, depth i wykrywanie.
12. MQTT/Mosquitto: telemetria ROS ↔ broker, pozycja i status napędu/skretu.
13. gRPC/Protobuf/HTTP2: zewnętrzne API przez ROS, cele i anulowanie Nav2.
14. OpenCV i backendy inferencji, przygotowanie do Jetson/CUDA/TensorRT.
15. Integracja całości, testy systemowe i rozszerzenie CI/CD.

## Przepływ docelowy — jeszcze niezaimplementowany

Teleoperacja lub Nav2 → komenda ruchu → kinematyka Ackermanna
→ 4 prędkości kół + 2 kąty skrętu → Gazebo lub CAN/hardware.
Enkodery i kąty skrętu → odometria; odometria + IMU → fuzja → TF.
LiDAR + TF → SLAM/AMCL → mapa/lokalizacja → Nav2.
Kamera → percepcja. ROS → MQTT. Klient gRPC → ROS → Nav2.

Źródło referencyjne:
https://control.ros.org/jazzy/doc/ros2_controllers/ackermann_steering_controller/doc/userdoc.html
Gotowy kontroler opisuje dwa wejścia napędowe i dwa wejścia skrętu;
nie stanowi jeszcze naszego sterownika czterech napędzanych kół.
