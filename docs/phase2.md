# Faza 2 — komunikacja ROS 2

## Cel i architektura

Tworzymy edukacyjny pakiet amr_learning. Nie steruje jeszcze robotem.
Docelowy robot to Ackermann 4WD (cztery koła napędowe, dwa przednie skrętne);
przykłady komunikacji są niezależne od rodzaju podwozia.
Python publikuje wiadomość co sekundę, C++ odbiera ją i publikuje odpowiedź,
a Python odbiera odpowiedź. Oddzielne tematy zapobiegają pętli odpowiedzi.

```text
python_peer → /phase2/python_message → cpp_peer
python_peer ← /phase2/cpp_message    ← cpp_peer
klient usługi → /phase2/status → cpp_peer → odpowiedź z licznikiem
klient akcji ↔ /phase2/fibonacci ↔ fibonacci_server
```

Aplikacja → rclcpp/rclpy → rcl → rmw → implementacja DDS → sieć.
DDS wykrywa uczestników i przenosi dane po dopasowaniu tematu, typu i QoS.
ROS daemon wspiera narzędzia CLI; nie jest centralnym brokerem wiadomości.
QoS obu peerów: RELIABLE, VOLATILE, KEEP_LAST, depth=10. RELIABLE zapewnia
mechanizmy ponawiania transmisji; VOLATILE nie odtwarza historii nowym
subskrybentom. To inne pojęcia niż MQTT QoS.

Temat przenosi strumień wiadomości. Usługa ma żądanie i odpowiedź.
Akcja ma cel, feedback, wynik i anulowanie — później użyjemy jej w Nav2.
Parametr jest ustawieniem konkretnego węzła.

## Pliki i ważne linie

- package.xml: nazwa, typ budowania i zależności pakietu. Dane maintenera są
  przykładowe; uzupełnij je przed publicznym wydaniem.
- CMakeLists.txt: buduje cpp_peer w C++17 i instaluje skrypty oraz launch.
  Skrypty mają shebang /usr/bin/python3, zgodny z systemowym ROS Jazzy.
- src/cpp_peer.cpp: klasa dziedziczy po Node, tworzy publisher, subscription
  i usługę Trigger. Lambda [this] korzysta ze stanu węzła. ConstSharedPtr
  udostępnia wiadomość bez jej modyfikowania. SharedPtr utrzymuje obiekty
  ROS przy życiu. Jednowątkowy spin wykonuje callbacki kolejno, dlatego
  licznik nie wymaga tutaj mutexa.
- scripts/python_peer: timer wywołuje publish_message co sekundę. Parametr
  message_prefix jest odczytywany przy każdej publikacji, więc zmiana działa
  bez restartu. spin przetwarza zdarzenia, a finally zwalnia węzeł.
- scripts/fibonacci_server: zadanie przyjmuje order od 2 do 20 — u nas jest
  to liczba elementów wyniku. MultiThreadedExecutor i ReentrantCallbackGroup
  pozwalają obsłużyć anulowanie podczas obliczeń. Lock chroni flagę busy;
  drugi równoczesny cel jest odrzucany. Krótkie sleep to wyłącznie demonstracja
  postępu zadania, nie wzorzec sterowania czasu rzeczywistego.
- launch/communication.launch.py: uruchamia trzy procesy jedną komendą.
- test/integration.py: uruchamia rzeczywiste procesy i sprawdza DDS roundtrip,
  zmianę parametru, usługę, wynik/feedback akcji, odrzucenie celu i anulowanie.
  Ma limity czasu i kończy własne procesy. Używa domeny 87 i LOCALHOST;
  nie uruchamiaj równocześnie drugiej kopii testu w tej samej domenie.

## Zależności i budowanie

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
# Zainstaluj tylko, jeśli brakuje przykładów akcji:
sudo apt install ros-jazzy-action-tutorials-interfaces
cd ros2_ws
python -m colcon build --symlink-install --packages-select amr_learning --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash
```

colcon znajduje package.xml i wywołuje CMake dla pakietu. CMake kompiluje C++
i instaluje pliki; source install/setup.bash dodaje workspace do środowiska.
Oczekiwane: Finished <<< amr_learning, Summary: 1 package finished.

## Uruchomienie — terminal A

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
ros2 launch amr_learning communication.launch.py
```

Po wykryciu peerów zobaczysz Sent: hello #N, Received: hello #N w C++
i Received: C++ reply: hello #N w Pythonie. Pierwsza wiadomość może zostać
wysłana przed wykryciem subskrybenta. Numery zależą od czasu uruchomienia.

## Obserwacja — terminal B

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
ros2 node list
ros2 topic list
ros2 topic info /phase2/python_message --verbose
ros2 topic echo /phase2/cpp_message
```

Oczekiwane węzły: /python_peer, /cpp_peer, /fibonacci_server.
Echo zakończ Ctrl+C; nie kończy to węzłów z terminala A.

## Parametr, usługa i akcja — terminal B

```bash
ros2 param set /python_peer message_prefix robot01
ros2 service call /phase2/status std_srvs/srv/Trigger '{}'
ros2 action send_goal /phase2/fibonacci action_tutorials_interfaces/action/Fibonacci '{order: 6}' --feedback
```

Zobaczysz wiadomości robot01 #N; usługa zwróci success=true i received=N;
akcja zwróci SUCCEEDED i sequence=[0, 1, 1, 2, 3, 5] oraz feedback w trakcie.
Order=0 zostanie odrzucony. Automatyczny test weryfikuje anulowanie;
Ctrl+C w kliencie CLI nie traktuj jako dowodu anulowania celu na serwerze.

## Test integracyjny

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
source ros2_ws/install/setup.bash
cd ros2_ws
python -m colcon test --packages-select amr_learning --event-handlers console_direct+
python -m colcon test-result --verbose
```

Oczekiwane: communication_integration Passed i 0 failures, 0 errors.
To test integracyjny; testy jednostkowe kinematyki z fazy 1 zostają osobno.

## Diagnostyka, ćwiczenie i commit

Jeśli pakiet nie został znaleziony, wykonaj source ros2_ws/install/setup.bash.
Jeśli rclpy nie działa, sprawdź python --version oraz echo "$VIRTUAL_ENV".
Jeśli brak wiadomości: ros2 node list, ros2 topic info --verbose i printenv
ROS_DOMAIN_ID — terminale muszą mieć zgodną domenę i QoS. Sprawdź także,
czy procesy rzeczywiście działają. Logi budowania: ros2_ws/log/latest_build.
Jeśli stary daemon CLI pokazuje inną domenę: ros2 daemon stop, następnie
ponownie uruchom ros2 node list z właściwym środowiskiem.

Ćwiczenie: ustaw message_prefix na swoje imię. Przewidź, które procesy
pokażą zmienioną wiadomość. Następnie zatrzymaj launch przez Ctrl+C i sprawdź
listę węzłów ponownie.

Po etapie rozumiesz node, topic, typ String, publisher/subscriber, callback,
timer, parametr, service, action, executor, callback group i podstawy QoS.
Faza jest zaliczona po obserwacji obu kierunków oraz przejściu testu.

```bash
git add README.md docs ros2_ws/src/amr_learning
git commit -m "Add ROS 2 Python C++ communication and integration test"
```

Następnie osobna faza 3: GitHub Actions, testy i CI/CD.
