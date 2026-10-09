# Faza 1 — kinematyka i narzędzia

Zbudowaliśmy samodzielny przykład C++17/Python, bez transportu ROS.
Jego zadaniem jest zamiana polecenia jazdy na obroty kół.
Później sterownik ROS będzie odbierał v i omega z geometry_msgs/Twist.

Przepływ: v [m/s], omega [rad/s] → kinematyka → lewe/prawe RPM → przyszły napęd.
Zakładamy płaski teren, identyczne koła i brak poślizgu. Nie wyznaczamy jeszcze
odometrii ani nie symulujemy dynamiki silników.

## Równania i kod

L oznacza odległość między kołami, r ich promień:

- v_left = v - omega * L / 2
- v_right = v + omega * L / 2
- RPM = prędkość liniowa koła * 60 / (2 * pi * r)

Dodatnia omega oznacza obrót w lewo. Przy obrocie w miejscu lewe koło
jedzie do tyłu, a prawe do przodu. RPM to obroty na minutę.

`examples/phase1/kinematics.py`: typowany interfejs funkcji i niezmienny
wynik dataclass. Walidacja chroni przed zerowym promieniem i NaN.
`kinematics.hpp`: identyczne obliczenia w C++, struktura wyniku,
namespace amr, const i constexpr. Zwracanie małej struktury przez wartość
nie wymaga wskaźników ani zarządzania pamięcią. inline pozwala umieścić
funkcję w nagłówku używanym przez więcej niż jeden plik.
`main.cpp`: wywołuje funkcję i formatuje wynik; auto wyprowadza typ wyniku.
`CMakeLists.txt`: deklaruje program C++17 i test CTest.
`test_kinematics.py` i `test_kinematics.cpp`: sprawdzają znane przypadki
fizyczne, kierunek skrętu i niepoprawną geometrię. Python używa na razie
standardowego unittest; pytest i GoogleTest wprowadzimy później.

## Budowanie, uruchamianie i testowanie

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

Oba programy wypisują:

```text
left=28.648 RPM, right=66.845 RPM
```

CTest: 100% tests passed. unittest: 4 testy, OK.
CMake konfiguruje budowanie; Ninja kompiluje źródła i łączy program.
CTest uruchamia skompilowany test; unittest wykonuje testy Pythona.

Diagnostyka: `which python`, `python --version`, `cmake --build build/phase1 --verbose`.
Jeśli Ninja nie jest dostępna, zainstaluj ninja-build.
Jeśli katalog build skonfigurowano z innym generatorem, użyj nowego katalogu
budowania zamiast zmieniać źródła.

Ćwiczenie: zmień v na 0, a omega na 1 w obu przykładach. Przewidź znaki
RPM przed uruchomieniem. Następnie sprawdź jazdę do tyłu: v=-0.5, omega=0.

Po tym etapie powinieneś rozumieć jednostki, geometrię napędu różnicowego,
funkcje, struktury/dataclass, walidację, kompilację i testy.

Propozycja commita po sprawdzeniu:
`git add README.md .gitignore tools examples docs`
`git commit -m "Add development environment and differential drive basics"`

Następny etap: Python publisher → C++ subscriber i odwrotnie w ROS 2.
