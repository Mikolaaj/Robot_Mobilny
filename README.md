# Robot Mobilny — AMR Robotics Lab

Projekt edukacyjny robota mobilnego 4WD: cztery koła napędowe, dwa przednie skrętne (Ackermann).
Rozwijamy go etapami: podstawy, ROS 2, model robota, Gazebo, SLAM i nawigacja,
a następnie CAN, MQTT, gRPC i percepcja.

## Środowisko — faza 0

Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic, C++17 i systemowy Python 3.12.
Nie używaj Pythona 3.14 z pyenv do uruchamiania pakietów ROS Jazzy.
ROS i Gazebo instalujemy przez apt; środowisko wirtualne korzysta z bibliotek
systemowych, w tym ROS po załadowaniu setup.bash.

Utworzenie środowiska na nowym komputerze:

```bash
sudo apt install python3-venv python3-colcon-common-extensions python3-rosdep build-essential ninja-build clang-format ros-jazzy-ros-gz ros-jazzy-xacro ros-jazzy-robot-state-publisher ros-jazzy-teleop-twist-keyboard
cd ~/Desktop/Robot_Mobilny
/usr/bin/python3 -m venv --system-site-packages .venv
```

Aktywacja w każdym nowym terminalu:

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
python --version
python -c "import rclpy; print('ROS Python OK')"
python -m colcon --help
```

Oczekiwany wynik: Python 3.12.x, ROS Python OK i pomoc colcon.
Samo importowanie rclpy nie sprawdza jeszcze komunikacji DDS.

Sprawdzenie symulatora:

```bash
ros2 launch ros_gz_sim gz_sim.launch.py gz_args:="-r empty.sdf"
```

Powinno otworzyć się okno Gazebo z pustym światem. Zakończ przez Ctrl+C.
Jeżeli wystąpi błąd, zachowaj komunikaty z terminala do diagnostyki.
Użytkownik potwierdził uruchomienie pustego świata w GUI Gazebo.

`.venv`, cache oraz katalogi build/install/log są ignorowane przez Git.
Na tym etapie nie dodajemy zależności pip: przyszłe zależności projektowe
zapiszemy w repozytorium, gdy dany etap będzie ich potrzebować.
Docker jest opcjonalny; jego daemon nie był uruchomiony podczas diagnostyki.
Pakiet edukacyjny ROS znajduje się w ros2_ws/src/amr_learning. Model robota i sterownik powstaną w kolejnych fazach.

## Aktualny stan i konstrukcja

Fazy 0–2 ukończone. Następna jest osobna faza 3: CI/CD na GitHubie.
Przykład kinematyki został dostosowany do Ackermanna 4WD.
Komendy określają prędkość środka tylnej osi i prędkość obrotu robota.
Robot nie obraca się w miejscu; każde koło dostaje własne RPM.
Założenia oraz plan wszystkich faz: [docs/architecture.md](docs/architecture.md).

## Faza 1

Przykłady C++/Python i dokładne instrukcje: [docs/phase1.md](docs/phase1.md).

## Faza 2

Pakiet amr_learning: [instrukcja ROS 2](docs/phase2.md).
