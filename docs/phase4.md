# Faza 4 — model robota i podgląd w RViz

## Co działa

Pakiet amr_description opisuje podwozie, cztery koła i dwa przeguby skrętu
przednich kół. URDF został poprawnie zweryfikowany, pakiet zbudowany,
a użytkownik potwierdził podgląd w RViz i wyprostowanie kół.
To model wizualny i kinematyczny. Nie zawiera jeszcze fizyki Gazebo,
mas/bezwładności, sterownika napędu ani sensorów. Cztery napędy są założeniem
konstrukcji, nie działającą na tym etapie symulacją silników.

Robocze wymiary: podwozie 0.80 × 0.30 × 0.12 m, promień koła 0.10 m,
szerokość koła 0.05 m, rozstaw kół 0.40 m, rozstaw osi 0.60 m.
Limit skrętu każdego przedniego koła ±0.60 rad.
base_link znajduje się w środku tylnej osi na wysokości osi kół.

## Pliki i przepływ

- ros2_ws/src/amr_description/package.xml: zależności uruchomienia i testów.
- CMakeLists.txt: instaluje urdf, launch i rviz do share/amr_description.
- urdf/robot.urdf.xacro: parametry, kolory, podwozie oraz makra kół.
  Link opisuje część lub układ odniesienia. Joint łączy linki.
  fixed: sztywne połączenie; continuous: pełny obrót koła;
  revolute: skręt z ograniczeniem kąta. visual służy do wyświetlania,
  collision opisuje geometrię kolizji. inercję dodamy przed symulacją fizyki.
- launch/display.launch.py: przetwarza Xacro na URDF i uruchamia trzy węzły.
- rviz/: miejsce na konfigurację widoku; obecnie launch nie ładuje jej z pliku.

Przepływ: Xacro → robot_description → robot_state_publisher → TF → RViz.
joint_state_publisher_gui → /joint_states → robot_state_publisher.
GUI publikuje pozycje, nie RPM ani moment silnika. RViz nie jest symulatorem
fizyki i przesuwanie suwaków nie przemieszcza robota po świecie.

robot_state_publisher publikuje sztywne połączenia na /tf_static,
a transformacje ruchomych przegubów na /tf na podstawie /joint_states.
Nie mamy jeszcze map → odom ani odom → base_link.

## Zależności — pierwszy raz

```bash
sudo apt install ros-jazzy-xacro ros-jazzy-robot-state-publisher ros-jazzy-joint-state-publisher-gui ros-jazzy-rviz2 liburdfdom-tools
```

## Budowanie — pierwszy raz i po zmianach konfiguracji pakietu

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
cd ros2_ws
python -m colcon build --symlink-install --packages-select amr_description --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
```

Oczekiwane: Finished <<< amr_description i 1 package finished.

## Uruchamianie — każdy nowy terminal

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
ros2 launch amr_description display.launch.py
```

Otworzą się RViz i Joint State Publisher GUI. W RViz:

1. Global Options → Fixed Frame: base_link. Nie myl z Reference Frame w Grid.
2. Add → RobotModel → OK.
3. RobotModel → Description Source: Topic.
4. Description Topic: /robot_description.
5. Rozwiń Description Topic → Durability Policy: Transient Local.
6. Views → Distance: 2; Focal Point: X=0.3, Y=0, Z=0.1.
7. W GUI kliknij Center: oba steering_joint powinny mieć 0.00.

Oczekiwane: niebieskie podwozie, cztery czarne koła, RobotModel Status: OK.
Transient Local pozwala odebrać opis robota opublikowany przed dołączeniem
RViz. GUI może zmieniać każdy przegub osobno i nie wymusza Ackermanna.
Przy skręcie jazdy oba przednie koła powinny skręcać w tę samą stronę,
a wewnętrzne mocniej. Prawidłowe komendy wylicza przykład z fazy 1;
nie jest on jeszcze połączony z GUI. Randomize może ustawić koła niezgodnie
z kinematyką. Center przywraca pozycje zerowe.
Zakończenie wszystkich procesów: Ctrl+C w terminalu launch.

## Walidacja modelu i diagnostyka

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
xacro ros2_ws/src/amr_description/urdf/robot.urdf.xacro -o /tmp/amr_robot.urdf
check_urdf /tmp/amr_robot.urdf
ruff check ros2_ws/src/amr_description
ruff format --check ros2_ws/src/amr_description
```

Oczekiwane: Successfully Parsed XML, base_link ma pięcioro dzieci:
chassis_link, dwa tylne koła i dwie zwrotnice. Każda zwrotnica ma przednie
koło jako dziecko. To walidacja struktury, nie test fizyki lub napędu.

W drugim terminalu, gdy launch działa:

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
ros2 node list
ros2 topic echo /joint_states --once
ros2 run tf2_ros tf2_echo base_link front_left_wheel_link
```

Brak modelu: sprawdź Fixed Frame, temat, Transient Local i rozwiń Status.
Koła pod kątem: Center i wartości przegubów skrętu 0.00.
Package not found: source ros2_ws/install/setup.bash po poprawnym build.
Niewłaściwa wielkość widoku: ustaw Distance i Focal Point.
Komunikat Stereo is NOT SUPPORTED sam w sobie nie oznacza błędu modelu.

## Kolejne kroki przed zamknięciem fazy

1. Zapisz widok przez RViz File → Save Config As do
   ros2_ws/src/amr_description/rviz/robot.rviz.
2. W kolejnym kroku dodamy ładowanie tego pliku do launch przez argument -d.
   Sam zapis konfiguracji nie zmienia jeszcze działania launch.
3. Rozszerz CI: obecny workflow obejmuje amr_learning i fazę 1, nie sprawdza
   jeszcze amr_description. Dodamy zależności, budowanie i walidację Xacro/URDF.
4. Uruchom lokalne testy pakietu i popraw ewentualne uwagi ament_lint.
5. Commit/push gałęzi robot-description, PR, zielone CI, merge do main.

Ćwiczenie: zmień tylko front_left_steering_joint i obserwuj, że obraca się
lewe przednie koło, a nie podwozie. Na koniec kliknij Center.
Po etapie rozumiesz link, joint, osie, origin, Xacro, robot_description,
joint_states, TF, widok RViz oraz ograniczenia ręcznego GUI.

Propozycja commita po dokończeniu etapu:

```bash
git add README.md docs/phase4.md docs/architecture.md ros2_ws/src/amr_description
git commit -m "Add four wheel Ackermann robot description and RViz guide"
git push
```

Dalszy etap: Gazebo i napęd (faza 5). Docker/CD z fazy 3 pozostaje osobnym
niedokończonym zadaniem.
