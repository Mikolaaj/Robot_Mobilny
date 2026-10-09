# Faza 1 — kinematyka Ackermanna 4WD

Robot ma cztery koła napędowe; tylko dwa przednie skręcają.
Sterowanie: v [m/s], omega [rad/s] → cztery RPM i dwa kąty skrętu [rad].
Obliczenia są samodzielnym przykładem C++17/Python, jeszcze bez sterowania ROS.

## Geometria i równania

Oś x do przodu, y w lewo, dodatnia omega obraca w lewo.
v jest prędkością środka tylnej osi. L=wheelbase to odległość między osiami,
T=track to rozstaw lewego i prawego koła (jednakowy dla obu osi), r=radius.

Dla v różnego od zera:

```text
k = omega / v
A_left = 1 - k*T/2
A_right = 1 + k*T/2
B = k*L
rear_left_speed = v*A_left
rear_right_speed = v*A_right
front_left_speed = v*sqrt(A_left²+B²)
front_right_speed = v*sqrt(A_right²+B²)
delta_left = atan2(B, A_left)
delta_right = atan2(B, A_right)
RPM = wheel_speed * 60/(2*pi*r)
```

Koła przednie obracają się wokół wspólnego środka skrętu wraz z tylnymi;
wewnętrzne przednie koło skręca mocniej. Przednie i tylne koło po tej samej
stronie nie mają identycznej prędkości. Cofanie daje ujemne RPM; dla tego
samego ustawienia kierownicy zmienia się znak omega.

Założenia: płaski teren, sztywna geometria, identyczne promienie i idealne
toczenie bez poślizgu. Model nie zawiera dynamiki ani ograniczenia RPM.
Przy v=0 i omega=0 zwracamy postój z prostymi kołami. v=0 i omega!=0 jest
odrzucane: robot nie obraca się w miejscu. Nadmierny skręt też jest odrzucany,
bez cichego przycinania komendy. max_steering dotyczy każdego przedniego koła.

Robocze wymiary: r=0.10 m, T=0.40 m, L=0.60 m, maksymalny kąt=0.60 rad.
To parametry przykładu, nie pomiary istniejącego robota.

## Ważne pliki

- examples/phase1/kinematics.py: funkcja wheel_commands, typowany interfejs,
  niezmienny dataclass WheelCommands z sześcioma wynikami i ValueError.
- kinematics.hpp: ta sama funkcja w C++, struktura WheelCommands, const,
  namespace amr, inline i std::invalid_argument. Nie potrzebujemy tu sterty.
- main.cpp: wywołanie obliczeń i wypisywanie wyniku; auto wyprowadza typ.
- CMakeLists.txt: budowanie C++17 przez CMake/Ninja i rejestracja testu CTest.
- test_kinematics.py / test_kinematics.cpp: postój, prosta, znany łuk skrętu,
  symetria skrętu, cofanie i niepoprawne/niewykonalne polecenia.
  Na tym etapie używamy unittest i CTest; pytest/GoogleTest dołączymy później.

## Budowanie i uruchamianie

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
cmake -S examples/phase1 -B build/phase1 -G Ninja
cmake --build build/phase1
./build/phase1/kinematics_demo
python examples/phase1/kinematics.py
ctest --test-dir build/phase1 --output-on-failure
python -m unittest discover -s examples/phase1 -v
```

Oba programy mają pokazać takie same cztery RPM i dwa kąty.
Komenda przykładowa to v=0.5 m/s, omega=0.3 rad/s: skręt w lewo.
Prawe koła jadą szybciej; lewe przednie koło ma większy kąt skrętu.
Testy: CTest 100% tests passed; Python 6 testów, OK.
CMake konfiguruje projekt, Ninja kompiluje i łączy program, CTest go testuje.

Diagnostyka: python --version, which python,
cmake --build build/phase1 --verbose. ValueError/invalid_argument przy obrocie
w miejscu lub ciasnym skręcie oznacza niewykonalną komendę dla tej geometrii.

Ćwiczenie: ustaw omega=0 i przewidź RPM oraz kąty. Potem zmień jednocześnie
znaki v i omega — kąty zostają takie same, a RPM zmieniają znaki.

Po etapie rozumiesz jednostki, promienie łuków, geometrię Ackermanna,
struktury/dataclass, walidację, kompilację oraz testy jednostkowe.

```bash
git add README.md docs examples/phase1
git commit -m "Switch robot kinematics to four wheel drive Ackermann steering"
```

Faza 2 dotyczy komunikacji ROS i pozostaje niezależna od kinematyki.
