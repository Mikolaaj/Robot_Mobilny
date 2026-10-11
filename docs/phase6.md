# Faza 6 — odometria Ackermanna i TF

## Implementacja

Węzeł C++ ackermann_odometry w amr_control odbiera /joint_states.
Kolejność przegubów jest dowolna: pomiary są wyszukiwane po nazwie.
Prędkość środka tylnej osi jest średnią prędkości tylnych kół pomnożoną
przez promień. Krzywizna wynika ze zmierzonych kątów przednich zwrotnic:

- k_left = tan(delta_left) / (L + T * tan(delta_left) / 2)
- k_right = tan(delta_right) / (L - T * tan(delta_right) / 2)
- v = r * (omega_rear_left + omega_rear_right) / 2
- yaw_rate = v * (k_left + k_right) / 2

Pozycja x, y i yaw jest całkowana po dokładnym łuku dla stałej prędkości
w przedziale pomiarowym. Używany jest czas z nagłówka JointState, zgodny
z czasem Gazebo. /cmd_vel nie jest wejściem odometrii.

Publikowane są nav_msgs/Odometry na /odom i TF odom -> base_link.
robot_state_publisher publikuje dalej ramy kół i podwozia.
Początek odom to pierwsza poprawna próbka: pozycja lokalna wynosi zero.
Nie jest to pozycja globalna mapy ani lokalizacja SLAM.

## Uruchamianie

Terminal 1:

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
cd ros2_ws
python -m colcon build --symlink-install \
  --packages-select amr_control amr_description amr_simulation \
  --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash
ros2 launch amr_simulation simulation.launch.py rviz:=true
```

Launch uruchamia Gazebo, most, sterownik, odometrię i opcjonalny RViz.
W widoku RViz Fixed Frame jest odom; dostępne są robot, TF i Odometry.
Bez RViz pomiń rviz:=true. Bez GUI Gazebo dodaj gz_args:="-r -s".

Terminal 2 — sterowanie:

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
ros2 topic pub --rate 10 /cmd_vel geometry_msgs/msg/Twist \
  "{linear: {x: 0.2}, angular: {z: 0.1}}"
```

Ctrl+C kończy komendy; sterownik zatrzymuje napęd po 0.5 s.
Dla jazdy prosto użyj z: 0.0, dla prawego łuku z: -0.1.
Dla cofania na wprost użyj x: -0.2 i z: 0.0.

Terminal 3 — pomiary:

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
ros2 topic echo /odom --once
ros2 run tf2_ros tf2_echo odom base_link
```

/odom zawiera pozycję w odom, quaternion orientacji i prędkość w base_link.
W chwili zatrzymania pozycja zostaje zachowana. map -> odom pojawi się w SLAM.
Nie uruchamiaj równocześnie GUI joint_state_publisher z fazy 4.

## Parametry i ograniczenia

Parametry węzła: wheel_radius=0.10, wheel_track=0.40, wheelbase=0.60,
max_dt=0.5 s. Wymiary muszą odpowiadać modelowi i sterownikowi.
Brak wymaganych nazw, tablic lub wartości skończonych powoduje pominięcie
próbki. Powtórzony timestamp nie jest całkowany. Cofnięcie czasu resetuje
pozycję; luka dłuższa niż max_dt nie jest ekstrapolowana.
Po utracie pomiarów odometria nie przewiduje dalszego ruchu.

To odometria kołowa bez wykrywania poślizgu i bez IMU. Nie mierzy bezpośrednio
ruchu nadwozia: zablokowane lub ślizgające się koła mogą generować błędny tor.
Kowariancje są roboczymi, stałymi oszacowaniami, nie kalibracją sensorów.
Pełna fuzja, sensory i korekcja globalna należą do kolejnych faz.

## Testy i CI

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
cd ros2_ws
python -m colcon test --packages-select amr_control amr_simulation \
  --event-handlers console_direct+
python -m colcon test-result --verbose
```

odometry_math sprawdza kinematykę odwrotną i całkowanie łuku.
odometry_integration sprawdza pomiary ROS, cofanie, łuk, powtórzenia czasu,
luki i reset oraz ramy i zgodność TF z /odom.
Test Gazebo porównuje przemieszczenie odometrii z pozycją modelu przy jeździe
na wprost. /gazebo/poses jest wyłącznie źródłem referencyjnym do walidacji;
nie jest wejściem estymatora i nie publikuje dodatkowego odom -> base_link.
CI instaluje zależności, sprawdza formatowanie i uruchamia testy przez colcon.

Branch: ackermann-odometry. Po lokalnych testach: commit/push, PR, zielone CI,
przegląd i merge. Stan GitHub Actions potwierdzamy po wysłaniu zmian.

## Wynik lokalny

Zbudowano pakiety i uruchomiono testy ROS: wynik colcon to 22 testy,
0 błędów i 0 niepowodzeń. Porównanie z Gazebo dotyczy krótkiego odcinka
jazdy na wprost, z tolerancją 0.08 m; nie jest walidacją wszystkich torów
ani warunków poślizgu. Widok RViz jest skonfigurowany, testy działają bez GUI.

Pozycję referencyjną publikuje [PosePublisher Gazebo Harmonic](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1PosePublisher.html).
